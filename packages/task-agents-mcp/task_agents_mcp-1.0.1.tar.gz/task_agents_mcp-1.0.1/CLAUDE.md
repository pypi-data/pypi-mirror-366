# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Task-Agents is a Model Context Protocol (MCP) server that delegates tasks to specialized Claude Code CLI instances with custom configurations. It creates a team of AI agents (code reviewer, debugger, test runner, etc.) accessible through any MCP-compatible client.

**Important**: This repository was moved from `/Volumes/vredrick2/Claude Code Projects/task-agents` to `/Volumes/vredrick2/Claude-Code-Projects/task-agents` (removed spaces in path for better compatibility).

## Commands

### Running the Server
```bash
# Development mode (with environment setup)
./run_server.sh

# Direct execution
python server.py

# With custom Claude path
CLAUDE_EXECUTABLE_PATH=/path/to/claude python server.py
```

### Adding to Claude Code CLI (Project Scope)
```bash
# Using uvx (Recommended - includes default agents)
claude mcp add task-agents -s project uvx task-agents-mcp

# Using Python directly
claude mcp add task-agents -s project python3.11 /Volumes/vredrick2/Claude-Code-Projects/task-agents/server.py
```

### Testing
```bash
# Run all tests
python test_server.py

# Test specific agent execution (requires Claude CLI)
python -c "import asyncio; from agent_manager import AgentManager; 
manager = AgentManager(); manager.load_agents(); 
asyncio.run(manager.execute_task({'name': 'debugger', 'config': manager.agents['debugger']}, 'test task'))"
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install as package
pip install -e .
```

## Architecture

### Core Components

1. **MCP Server (`server.py`)**
   - FastMCP server exposing single tool: `task_agents`
   - Dynamically generates tool description with available agents
   - Handles MCP protocol communication

2. **Agent Manager (`agent_manager.py`)**
   - Loads agent configurations from markdown files with YAML frontmatter
   - Provides agent lookup by display name (agent-name field)
   - Executes tasks by constructing Claude Code CLI commands:
     ```bash
     claude -p "task" --system-prompt "..." --model opus --allowedTools Read Write Edit --output-format text
     ```

3. **Agent Configurations (`task-agents/*.md`)**
   - Markdown files with YAML frontmatter defining agent behavior
   - Required fields: agent-name, description, tools, model, cwd
   - System prompt section contains detailed agent instructions

### Key Design Decisions

1. **Agent Selection**: LLM client selects agent based on display names and descriptions.

2. **Tool Restriction**: Each agent specifies allowed tools as space-separated arguments to Claude CLI.


3. **Working Directory Resolution**: 
   - **The `cwd` field in agent .md files is the ONLY source of truth for working directory**
   - `cwd: .` **always** resolves to the parent directory of the task-agents folder
   - **Claude Desktop mode**: If TASK_AGENTS_PATH="/path/to/task-agents", agents run in "/path/to/"
   - **Claude Code CLI mode**: If task-agents is in "/project/task-agents/", agents run in "/project/"
   - **Consistent behavior** across ALL clients (Claude Desktop, Claude Code CLI, etc.)
   - Perfect for project-specific usage - just drop task-agents folder into any project
   - Supports absolute paths (e.g., `cwd: /specific/path`) and environment variables (e.g., `cwd: ${HOME}/projects`)
   - **Agents are instructed to save files in their working directory by default** (appended to system prompt)


4. **Command Construction**: Fixed to use single `-p` flag with space-separated tools list (not comma-separated).

## Agent Configuration Format

```markdown
---
agent-name: Display Name
description: Brief description of agent's purpose
tools: Read, Write, Edit, MultiEdit, Bash, Grep, Search, Glob
model: opus  # or sonnet, haiku
cwd: .  # or absolute path, or path with ${HOME}
---

System-prompt:
Detailed instructions for the agent...
```

## Environment Variables

- `TASK_AGENTS_PATH`: Path to task-agents directory (optional - only needed for Claude Desktop to find agents)
- `CLAUDE_EXECUTABLE_PATH`: Full path to Claude executable (required for Claude Desktop, not needed for Claude Code CLI which finds it automatically)

## Adding New Agents

1. Create new `.md` file in task-agents directory
2. Add YAML frontmatter with all required fields
3. Write detailed system prompt after frontmatter
4. Restart server (agents are loaded on startup)

## Common Issues

1. **Claude CLI Integration**: For Claude Desktop, the server expects Claude Code CLI at the path specified in `CLAUDE_EXECUTABLE_PATH`. For Claude Code CLI usage, this environment variable is not needed as it finds the executable automatically.

2. **Tool List Format**: Tools must be specified as space-separated arguments in the CLI command, not comma-separated.

3. **Agent Loading**: Only `.md` files in the task-agents directory are loaded. Files must have valid YAML frontmatter with `agent-name` field or they're skipped.

4. **Agent Names**: Agent selection uses the `agent-name` field, not the filename. Ensure agent names are unique and descriptive.

## Testing Changes

When modifying agent behavior or server logic:
1. Run `python test_server.py` to validate configurations
2. Test actual execution requires Claude Code CLI to be installed
3. Check logs for command construction and execution details

## PyPI Package

The repository includes PyPI package structure for standard Python distribution:

### Files
- `pyproject.toml`: Package configuration with metadata and dependencies
- `src/task_agents_mcp/`: Python package with server and agent manager
- `src/task_agents_mcp/agents/`: Default agent configurations
- `MANIFEST.in`: Ensures agent markdown files are included

### Key Features
- Standard Python packaging following MCP ecosystem conventions
- Works with uvx for zero-installation usage
- Includes default agents in the package
- Compatible with all MCP clients (Claude Desktop, Claude Code CLI, etc.)

### Publishing
```bash
# Build the package
./build_pypi.sh

# Upload to PyPI
python -m twine upload dist/*
```