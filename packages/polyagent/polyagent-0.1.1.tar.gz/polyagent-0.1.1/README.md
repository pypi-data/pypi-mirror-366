# PolyCLI

A unified interface for stateful conversations with CLI-based AI agents.

## Installation

```bash
pip install polyagent
```

## Usage

```python
from polycli import Agent

# Create agent
agent = Agent()

# Single query
response = agent.run("What is 2+2?")
print(response['result'])  # 4

# Multi-model support
response = agent.run("Explain recursion", model="openai/gpt-4o")

# Persistent conversations
agent.add_user_message("Remember this: my name is Alice")
agent.run("What's my name?")  # Remembers context

# State management
agent.save_state("conversation.jsonl")
agent.load_state("conversation.jsonl")
```

## Features

- **Unified API** - Single interface for any CLI-based AI agent (Claude Code, etc.)
- **Multi-agent Orchestration** - Coordinate multiple AI agents for complex workflows
- **Model Routing** - Switch between different LLM providers seamlessly
- **Memory Management** - Auto-appending messages and configurable memory limits

## Requirements

- Python 3.8+
- Claude CLI (for Claude models)
- OpenRouter API key (for other models)

## Configuration

Create a `.env` file:
```
OPENROUTER_API_KEY=your_key_here
```

---

*Simple. Stateful. Universal.*