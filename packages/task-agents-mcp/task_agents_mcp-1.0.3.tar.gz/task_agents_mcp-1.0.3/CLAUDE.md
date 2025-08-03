# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Task-Agents is a Model Context Protocol (MCP) server that delegates tasks to specialized Claude Code CLI instances with custom configurations. It creates a team of AI agents (code reviewer, debugger, test runner, etc.) accessible through any MCP-compatible client.

## Commands

### Running the Server
```bash
# Development mode (with environment setup)
./scripts/run_server.sh

# Direct execution
python server.py

# As Python module (after pip install)
python -m task_agents_mcp
```

### Adding to Claude Code CLI (Project Scope)
```bash
# Using uvx (Recommended - includes default agents)
claude mcp add task-agents -s project -- uvx task-agents-mcp

# Using Python module
claude mcp add task-agents -s project -- python3.11 -m task_agents_mcp

# Using local source
claude mcp add task-agents -s project python3.11 /path/to/task-agents/server.py
```

### Testing
```bash
# Run all tests
python tests/test_server.py

# Test server startup
python server.py
# Should show: "Loaded X agents"
```

### Installation
```bash
# Install from PyPI
pip install task-agents-mcp

# Install from source for development
pip install -r requirements.txt
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
./scripts/build_pypi.sh

# Upload to PyPI
python -m twine upload dist/*
```

## Future Features

### Streaming Support (Option C: Direct HTTP/WebSocket Interface)

A future enhancement could add real-time streaming of agent output through a separate web interface:

**Architecture:**
- Keep MCP server for Claude Desktop/CLI integration (request/response)
- Add parallel HTTP server with SSE/WebSocket support
- Web app connects directly to streaming endpoint
- Agent manager streams progress updates in real-time

**Benefits:**
- True real-time streaming of agent actions
- Rich web UI for agent management
- Visual progress tracking
- Ability to create/edit agents through UI
- Live view of tool usage, thinking, and outputs

**Implementation Notes:**
- `agent_manager.py` already has progress callback infrastructure (Phase 2)
- Would need to add HTTP server (FastAPI/Starlette with SSE)
- Web app could use React/Vue for reactive UI
- WebSocket or SSE for bidirectional communication
- Could show multiple agents working in parallel

This approach bypasses MCP's request/response limitation while maintaining compatibility with Claude Desktop/CLI.