# 🚀 PolyCLI - Multi-Model AI Agent Framework

**PolyCLI** is a powerful Python framework that enables stateful conversations with AI models, featuring seamless integration with Claude Code CLI and OpenRouter for multi-model support.

## ✨ Key Features

- **🔄 Stateful Conversations**: Maintain conversation history across sessions with automatic state management
- **🌐 Multi-Model Support**: Route to any LLM via OpenRouter (GPT-4, Claude, Llama, etc.) or use Claude Code CLI
- **💾 Persistent Memory**: Save and load conversation states with JSONL format
- **🎯 System Prompts**: Configure default or per-run system prompts for specialized behaviors
- **👻 Ephemeral Mode**: Run queries without saving to memory for one-off interactions
- **🧠 Smart Memory Management**: Automatic memory cutoff to prevent unbounded growth
- **🔧 Debug Mode**: Comprehensive logging for troubleshooting

## 🎯 Exciting Applications

### 1. 🤖 Parallel AI Orchestration
Run multiple AI agents in parallel for complex tasks:

```python
import polycli
from concurrent.futures import ThreadPoolExecutor

# Create a main agent to set up the project
setup_agent = polycli.Agent()
setup_agent.run("Create a new Python project structure")

# Run specialized agents in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    # Agent for documentation
    docs_agent = polycli.Agent(system_prompt="You are a technical writer")
    future1 = executor.submit(docs_agent.run, "Write comprehensive API documentation")
    
    # Agent for testing
    test_agent = polycli.Agent(system_prompt="You are a QA engineer") 
    future2 = executor.submit(test_agent.run, "Create unit tests for all modules")
    
    # Agent for optimization
    perf_agent = polycli.Agent(system_prompt="You are a performance expert")
    future3 = executor.submit(perf_agent.run, "Analyze and optimize code performance")
```

### 2. 🎭 Multi-Personality Assistant
Create agents with different personalities and expertise:

```python
import polycli

# Creative storyteller
storyteller = polycli.Agent(
    system_prompt="You are a creative storyteller who writes engaging children's stories",
    debug=True
)
story = storyteller.run("Write a story about the number 7")

# Technical expert  
tech_expert = polycli.Agent(
    system_prompt="You are a senior software architect",
    openrouter_api_key="your-api-key"
)
architecture = tech_expert.run(
    "Design a microservices architecture", 
    model="openai/gpt-4"
)

# Fun assistant with memory cutoff
fun_bot = polycli.Agent(system_prompt="You are a playful assistant who loves jokes")
fun_bot.run("Tell me a joke about cats")
fun_bot.run("Now one about dogs", memory_cutoff=5)  # Keep only last 5 messages
```

### 3. 🔄 Conversation State Management
Resume conversations seamlessly across sessions:

```python
import polycli
from pathlib import Path

state_file = Path("conversation_state.jsonl")

# Initialize agent
agent = polycli.Agent(debug=True)

# Load previous conversation if exists
if state_file.exists():
    agent.load_state(state_file)
    print("Resuming previous conversation...")

# Continue the conversation
response = agent.run("What were we discussing earlier?")
print(response['result'])

# Save state for next time
agent.save_state(state_file)
```

### 4. 🌐 Model Routing & Comparison
Compare responses from different models:

```python
import polycli

agent = polycli.Agent(openrouter_api_key="your-key")

prompt = "Explain quantum computing in simple terms"

# Get responses from different models
claude_response = agent.run(prompt)  # Uses Claude Code CLI
gpt4_response = agent.run(prompt, model="openai/gpt-4", ephemeral=True)
llama_response = agent.run(prompt, model="meta-llama/llama-3-70b", ephemeral=True)

# Compare responses without polluting conversation history
```

### 5. 🎯 Specialized Agents with Context
Create context-aware agents for specific tasks:

```python
import polycli

# Code reviewer agent
reviewer = polycli.Agent(
    system_prompt="""You are a senior code reviewer. Focus on:
    - Security vulnerabilities
    - Performance issues  
    - Code style and best practices
    - Potential bugs""",
    cwd="/path/to/project"  # Set working directory
)

# Review code with context
reviewer.run("Review the authentication module for security issues")
reviewer.run("Now check the database queries for SQL injection risks")

# The agent maintains context between reviews!
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/polycli.git
cd polycli

# Install dependencies
pip install instructor openai pydantic
```

### Basic Usage

```python
import polycli

# Create an agent
agent = polycli.Agent()

# Have a conversation
agent.run("Hello! I'm learning Python")
response = agent.run("What should I learn first?")
print(response['result'])
```

### Advanced Configuration

```python
agent = polycli.Agent(
    debug=True,                    # Enable debug logging
    openrouter_api_key="sk-...",   # OpenRouter API key
    system_prompt="You are helpful", # Default system prompt
    cwd="/path/to/project"         # Working directory for Claude Code
)
```

## 📋 Requirements

- Python 3.8+
- Claude CLI (for Claude Code integration)
- OpenRouter API key (optional, for multi-model support)
- Dependencies: `instructor`, `openai`, `pydantic`

## 🔑 API Key Setup

For OpenRouter support, set your API key:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Or pass it directly:

```python
agent = polycli.Agent(openrouter_api_key="your-api-key")
```

## 🎨 Real-World Example: Story Generation Pipeline

The included `test.py` demonstrates a practical multi-agent pipeline that generates children's stories:

```python
# Agent 1: Creates the project structure
agent1 = polycli.Agent()
agent1.run("create a folder called number_stories")

# Agents 2 & 3: Generate stories in parallel
with ThreadPoolExecutor(max_workers=2) as executor:
    # Agent 2 handles stories 1-10
    agent2 = polycli.Agent()
    future2 = executor.submit(
        agent2.run, 
        "Write educational stories for numbers 1-10"
    )
    
    # Agent 3 handles stories 11-20  
    agent3 = polycli.Agent()
    future3 = executor.submit(
        agent3.run,
        "Write educational stories for numbers 11-20"
    )
```

## 🔥 Why PolyCLI?

- **Flexibility**: Use Claude Code for complex tasks, route to GPT-4 for creative work, or Llama for open-source needs
- **Persistence**: Never lose conversation context with automatic state management
- **Scalability**: Run multiple agents in parallel for complex workflows
- **Simplicity**: Clean, intuitive API that gets out of your way
- **Power**: Full control over system prompts, memory management, and model selection

## 📄 License

MIT License - feel free to use in your projects!

---

Built with ❤️ for the AI engineering community. Happy coding! 🚀