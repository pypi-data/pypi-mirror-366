#!/usr/bin/env python3
"""Example: Using polyagent with multiple LLM providers"""

from pathlib import Path
from polycli import Agent

# Define where to save the conversation state
agent_state_file = Path.home() / ".polyagent-llm-routing.jsonl"

# Initialize the agent with a default system prompt
print(f"Initializing agent. State will be persisted to: {agent_state_file}")
my_agent = Agent(
    debug=True,
    system_prompt="You are a helpful coding assistant specializing in Python development."
)

# Load previous state if it exists
if agent_state_file.exists():
    print("Loading previous state...")
    my_agent.load_state(agent_state_file)

# Example: Regular (persistent) LLM call
print("\n>>> Regular GPT-4 call (will be saved)")
response = my_agent.run("What is recursion?", model="openai/gpt-4o")
if "result" in response:
    print(f"GPT-4 says: {response['result'][:100]}...")

# Example: Ephemeral LLM call (won't be saved)
print("\n>>> Ephemeral GPT-4 call (won't be saved)")
response = my_agent.run(
    "Tell me a joke about programming", 
    model="openai/gpt-4o",
    ephemeral=True
)
if "result" in response:
    print(f"GPT-4 says: {response['result']}")

# Check memory - the joke won't be there
print(f"\nMemory size before save: {len(my_agent.memory)}")

# Save state
my_agent.save_state(agent_state_file)
print(f"State saved to: {agent_state_file}")