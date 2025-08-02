# Task-Agents MCP Server

Delegate specialized tasks to expert AI agents through any MCP-compatible client.

## Features

- 🤖 **Multiple Specialized Agents**: Code reviewer, debugger, test runner, documentation writer, and more
- 🔧 **Easy Configuration**: Simple markdown files define agent behavior
- 🚀 **Flexible Integration**: Works with Claude Desktop, Claude Code CLI, or any MCP client
- 📝 **Custom System Prompts**: Each agent has tailored instructions for specific tasks

## Installation

```bash
# Install with pip
pip install task-agents-mcp

# Or run directly with uvx (recommended)
uvx task-agents-mcp
```

## Quick Start

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-agents": {
      "command": "uvx",
      "args": ["task-agents-mcp"]
    }
  }
}
```

### Custom Agents

Create a `task-agents` folder in your project with `.md` files:

```markdown
---
agent-name: My Custom Agent
description: Specialized agent for specific tasks
tools: Read, Write, Edit, Bash
model: sonnet
cwd: .
---

System-prompt:
You are a specialized agent that...
```

Set `TASK_AGENTS_PATH` environment variable to use custom agents:

```json
{
  "mcpServers": {
    "task-agents": {
      "command": "uvx",
      "args": ["task-agents-mcp"],
      "env": {
        "TASK_AGENTS_PATH": "/path/to/your/agents"
      }
    }
  }
}
```

## Available Agents

- **Code Reviewer**: Comprehensive code analysis for quality and security
- **Debugger**: Bug fixing and troubleshooting specialist
- **Test Runner**: Test automation and coverage improvement
- **Documentation Writer**: Technical documentation creation
- **Performance Optimizer**: Performance analysis and optimization
- **Default Assistant**: General-purpose AI assistant

## Requirements

- Python 3.9+
- Claude Code CLI (for agent execution)

## License

MIT

## More Information

For detailed documentation and source code, visit: https://github.com/vredrick/task-agents