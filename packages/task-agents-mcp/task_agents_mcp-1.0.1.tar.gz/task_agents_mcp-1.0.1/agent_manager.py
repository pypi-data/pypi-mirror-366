"""
Agent Manager for Task-Agents MCP Server

Handles agent discovery, selection, and task execution via Claude Code CLI.
"""

import os
import re
import yaml
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    name: str  # File name (for internal use)
    agent_name: str  # Display name for the agent
    description: str
    tools: List[str]
    model: str
    cwd: str
    system_prompt: str
    

class AgentManager:
    """Manages agent configurations and task delegation."""
    
    def __init__(self, configs_dir: str = "configs"):
        self.configs_dir = Path(configs_dir)
        self.agents: Dict[str, AgentConfig] = {}
        
    def load_agents(self) -> None:
        """Load all agent configurations from the configs directory."""
        if not self.configs_dir.exists():
            logger.warning(f"Configs directory not found: {self.configs_dir}")
            return
            
        for config_file in self.configs_dir.glob("*.md"):
            try:
                agent = self._parse_agent_config(config_file)
                if agent:
                    self.agents[agent.name] = agent
                    logger.info(f"Loaded agent: {agent.name}")
            except Exception as e:
                logger.error(f"Error loading agent config {config_file}: {e}")
                
    def _parse_agent_config(self, config_path: Path) -> Optional[AgentConfig]:
        """Parse a single agent configuration file."""
        content = config_path.read_text()
        
        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not frontmatter_match:
            logger.error(f"Invalid config format in {config_path}")
            return None
            
        try:
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            system_prompt_section = frontmatter_match.group(2)
            
            # Extract system prompt
            system_prompt_match = re.search(r'System-prompt:\s*\n(.*)$', system_prompt_section, re.DOTALL)
            system_prompt = system_prompt_match.group(1).strip() if system_prompt_match else ""
            
            # Validate required fields
            required_fields = ['agent-name', 'description', 'tools', 'model', 'cwd']
            for field in required_fields:
                if field not in frontmatter:
                    logger.error(f"Missing required field '{field}' in {config_path}")
                    return None
            
            # Parse tools list
            tools = frontmatter['tools']
            if isinstance(tools, str):
                tools = [t.strip() for t in tools.split(',')]
            
            # Expand environment variables in cwd
            cwd = os.path.expandvars(frontmatter.get('cwd', '.'))
            
            # Keep cwd as-is for now - it will be resolved during execution
            # This allows for different behaviors based on the execution context
            
            return AgentConfig(
                name=config_path.stem,
                agent_name=frontmatter['agent-name'],
                description=frontmatter['description'],
                tools=tools,
                model=frontmatter['model'],
                cwd=cwd,
                system_prompt=system_prompt
            )
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            return None
            
        
    def get_agent_by_display_name(self, display_name: str) -> Optional[AgentConfig]:
        """Get agent by its display name (agent-name field)."""
        for agent in self.agents.values():
            if agent.agent_name == display_name:
                return agent
        return None
        
    def get_agents_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents."""
        return {
            agent.agent_name: {
                'description': agent.description,
                'model': agent.model,
                'internal_name': name
            }
            for name, agent in self.agents.items()
        }
        
    async def execute_task(self, selected_agent: Dict[str, Any], task_description: str) -> str:
        """Execute a task using the selected agent via Claude Code CLI."""
        agent_config = selected_agent['config']
        
        # Get claude executable path from environment or use default
        claude_path = os.environ.get('CLAUDE_EXECUTABLE_PATH', '/Users/vredrick/.claude/local/claude')
        
        # Start building the command
        cmd = [
            claude_path,
            '-p', task_description,
            '--system-prompt', agent_config.system_prompt,
            '--output-format', 'text',
            '--allowedTools', *agent_config.tools,  # Unpack list for space-separated tools
            '--model', agent_config.model
        ]
        
        try:
            # Resolve the working directory from agent config
            cwd = agent_config.cwd
            
            
            # If cwd is '.', use the parent directory of the task-agents folder
            if cwd == '.':
                # The task-agents folder is always at configs_dir
                # We want to go to the parent directory of the task-agents folder
                task_agents_dir = Path(self.configs_dir).resolve()
                # Always go up one level from the task-agents directory
                cwd = str(task_agents_dir.parent)
                logger.info(f"Agent cwd was '.', resolved to: {cwd}")
            
            # Expand environment variables and make absolute
            working_dir = os.path.abspath(os.path.expandvars(cwd))
            
            # Add --add-dir flag to ensure Claude has access to the working directory
            cmd.extend(['--add-dir', working_dir])
            
            # Append system prompt instruction to use the working directory
            working_dir_instruction = f"\n\nIMPORTANT: You are currently working in the directory: {working_dir}\nWhen creating or saving files without an explicit path, always save them in the current working directory using relative paths (e.g., ./filename). Only save files elsewhere if the user explicitly specifies a different path."
            
            # Combine the original system prompt with the working directory instruction
            combined_system_prompt = agent_config.system_prompt + working_dir_instruction
            
            # Update the command to use the combined system prompt
            # Find and replace the system prompt in the command
            for i, arg in enumerate(cmd):
                if arg == '--system-prompt' and i + 1 < len(cmd):
                    cmd[i + 1] = combined_system_prompt
                    break
            
            # Log the full command for debugging
            logger.info(f"Agent config cwd: {agent_config.cwd}")
            logger.info(f"Resolved cwd: {cwd}")
            logger.info(f"Final working directory: {working_dir}")
            logger.info(f"Appending working directory instruction to system prompt")
            logger.info(f"Executing command: {' '.join(cmd)}")
            logger.info(f"Using model: {agent_config.model}")
            
            # Verify the working directory exists
            if not os.path.exists(working_dir):
                logger.error(f"Working directory does not exist: {working_dir}")
                return f"Error: Working directory does not exist: {working_dir}"
            
            # Run the command asynchronously with a timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL  # Ensure no interactive input is expected
            )
            
            # Wait for the command to complete - no timeout
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                stdout_msg = stdout.decode('utf-8') if stdout else ""
                logger.error(f"Claude CLI error (return code {process.returncode}): {error_msg}")
                if stdout_msg:
                    logger.error(f"Claude CLI stdout: {stdout_msg}")
                return f"Error executing Claude CLI (return code {process.returncode}): {error_msg}"
                
            result = stdout.decode('utf-8').strip()
            if not result:
                logger.warning("Claude CLI returned empty output")
                stderr_msg = stderr.decode('utf-8') if stderr else ""
                if stderr_msg:
                    logger.warning(f"Claude CLI stderr: {stderr_msg}")
                return "Claude CLI returned empty output. The command may have completed without generating a response."
            
            return result
            
        except FileNotFoundError:
            return "Error: Claude CLI not found. Please ensure 'claude' is installed and in PATH."
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            return f"Error executing task: {str(e)}"