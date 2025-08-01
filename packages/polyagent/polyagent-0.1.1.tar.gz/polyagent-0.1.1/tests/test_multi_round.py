#!/usr/bin/env python3
"""Test multi-round conversation continuity"""

from polycli import Agent

def test_multi_round_conversation():
    """Test that agent maintains context across multiple rounds"""
    
    agent = Agent(debug=True)
    
    # Round 1: Establish context
    print("=== Round 1: Setting context ===")
    response1 = agent.run("My name is Alice and I'm learning Python")
    print(f"Response 1: {response1.get('result', 'No result')}")
    
    # Round 2: Reference previous context
    print("\n=== Round 2: Using context ===")
    response2 = agent.run("What's my name and what am I learning?")
    print(f"Response 2: {response2.get('result', 'No result')}")
    
    # Round 3: Build on conversation
    print("\n=== Round 3: Building on context ===")
    response3 = agent.run("Can you recommend a Python project for beginners?")
    print(f"Response 3: {response3.get('result', 'No result')}")
    
    # Round 4: Continue conversation
    print("\n=== Round 4: Continuing conversation ===")
    response4 = agent.run("What were we just discussing about projects?")
    print(f"Response 4: {response4.get('result', 'No result')}")
    
    print(f"\nTotal memory items: {len(agent.memory)}")
    print("✓ Multi-round conversation test completed!")
    
    return agent

def test_message_appending():
    """Test that multiple add_fake_user calls append correctly"""
    
    print("\n=== Testing Message Appending ===")
    agent = Agent()
    
    # Add multiple user messages
    agent.add_user_message("First message")
    agent.add_user_message("Second message (should append)")
    agent.add_user_message("Third message (should also append)")
    
    # Should have only 1 memory item with all messages combined
    assert len(agent.memory) == 1, f"Expected 1 memory item, got {len(agent.memory)}"
    
    content = agent.memory[0]['message']['content'][0]['text']
    assert "First message" in content
    assert "Second message" in content  
    assert "Third message" in content
    
    print(f"Combined message content: {content[:100]}...")
    print("✓ Message appending test passed!")

if __name__ == "__main__":
    agent = test_multi_round_conversation()
    test_message_appending()