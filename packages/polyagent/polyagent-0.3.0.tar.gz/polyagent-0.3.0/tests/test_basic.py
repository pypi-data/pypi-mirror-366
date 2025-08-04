#!/usr/bin/env python3
"""Minimal test - create agent and run a query"""

from polycli import Agent

# Create agent
agent = Agent(debug=True)

# Run a simple query
response = agent.run("What is 2+2?")

print("Response:", response)