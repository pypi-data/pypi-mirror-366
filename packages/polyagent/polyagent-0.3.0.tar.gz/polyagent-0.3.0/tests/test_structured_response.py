#!/usr/bin/env python3
"""Test unified response format"""

from polycli import Agent
from pydantic import BaseModel, Field


class MathResult(BaseModel):
    answer: int = Field(description="The answer")
    explanation: str = Field(description="Brief explanation")


def test_response_formats():
    """Test that both Claude and OpenRouter return same format"""
    
    agent = Agent(debug=True)
    
    # Test Claude Code
    print("=== Claude Code ===")
    claude_resp = agent.run("What is 3+4?")
    print(f"Keys: {list(claude_resp.keys())}")
    print(f"Result: {claude_resp['result']}")
    
    # Test OpenRouter (if available)
    print("\n=== OpenRouter ===")
    try:
        openrouter_resp = agent.run("What is 5+6?", model="openai/gpt-4o")
        print(f"Keys: {list(openrouter_resp.keys())}")
        print(f"Result: {openrouter_resp['result']}")
    except Exception as e:
        print(f"Skipped: {e}")
    
    # Test structured response (if available)
    print("\n=== Structured Response ===")
    try:
        struct_resp = agent.run("What is 7+8?", model="openai/gpt-4o", schema_cls=MathResult)
        print(f"Keys: {list(struct_resp.keys())}")
        print(f"Result: {struct_resp['result']}")
    except Exception as e:
        print(f"Skipped: {e}")


if __name__ == "__main__":
    test_response_formats()