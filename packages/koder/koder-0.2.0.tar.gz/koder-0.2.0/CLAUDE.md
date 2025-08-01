# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup

```bash
# Install dependencies
uv sync

# Run the CLI in interactive mode
koder

# Run with a single prompt
koder "Help me implement a new feature"

# Run with specific session
koder --session my-session "Your prompt"

# Enable streaming mode
koder --stream "Your prompt"

# MCP server management
koder mcp list
koder mcp add myserver command arg1 arg2
koder mcp remove myserver
```

### Development Commands

```bash
# Code formatting
black .

# Linting
ruff check .

# Type checking
mypy .
```

## Architecture

### Core Components

**Agent Scheduler (`koder_agent/core/scheduler.py`)**: Central orchestrator that manages agent execution, handles streaming, and coordinates context management. Uses semaphores for concurrency control.

**Context Manager (`koder_agent/core/context.py`)**: Manages conversation history with SQLite storage, implements token-aware compression (50k token limit), and handles session management. Database stored at `~/.koder/koder.db`.

**Tool Engine (`koder_agent/tools/engine.py`)**: Registers and executes tools with Pydantic validation. Filters sensitive information from outputs and enforces allowed tool lists.

### Agent System

The project uses the `openai-agents` library with:

- **Main Agent**: `create_dev_agent()` - Primary development agent with full tool access
- **Planner Agent**: `create_planner_agent()` - Returns numbered planning lists when needed
- **Model Selection**: Automatically chooses appropriate OpenAI model via `get_model_name()`

### Tool Categories

1. **File Operations**: `read_file`, `write_file`, `append_file`, `list_directory`
2. **Search Operations**: `glob_search`, `grep_search`
3. **Shell Operations**: `run_shell`, `git_command`
4. **Web Operations**: `web_search`, `web_fetch`
5. **Task Management**: `todo_read`, `todo_write`, `task_delegate`

### Key Features

- **Streaming Support**: Real-time output with Rich Live displays
- **Context Persistence**: Conversation history across sessions
- **Tool Validation**: Pydantic schemas with security checks
- **Interactive CLI**: Rich-formatted panels and prompts

### Configuration

The CLI looks for `KODER.md` in the working directory to load project-specific context. Set OpenAI API credentials via environment variables or the `openai-agents` configuration system.
