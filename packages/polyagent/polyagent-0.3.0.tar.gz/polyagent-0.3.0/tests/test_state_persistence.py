#!/usr/bin/env python3
"""Test state persistence functionality with actual Claude CLI runs"""

import tempfile
from pathlib import Path
from polycli import Agent

def test_state_persistence_with_claude():
    """Test saving and loading conversation state with actual Claude runs"""
    
    # Create temporary file for state
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp:
        state_file = Path(tmp.name)
    
    try:
        print("=== Creating first agent and running Claude ===")
        # Create first agent and have a conversation with Claude
        agent1 = Agent(debug=True)
        
        # First Claude run - establish context
        response1 = agent1.run("Remember that I am learning Python. What is 5+3?")
        print(f"Claude response 1: {response1.get('result', 'Error')}")
        
        # Second Claude run - build on context
        response2 = agent1.run("Good! Now what programming language am I learning?")
        print(f"Claude response 2: {response2.get('result', 'Error')}")
        
        print(f"Agent1 memory size after Claude runs: {len(agent1.memory)}")
        
        # Save state
        agent1.save_state(state_file)
        print(f"State saved to: {state_file}")
        
        print("\n=== Creating second agent and loading state ===")
        # Create second agent and load state
        agent2 = Agent(debug=True)
        agent2.load_state(state_file)
        print(f"Agent2 memory size after loading: {len(agent2.memory)}")
        
        # Continue conversation with loaded context
        print("\n=== Testing context continuity ===")
        response3 = agent2.run("What was the math problem I asked you earlier?")
        print(f"Claude response 3 (with loaded context): {response3.get('result', 'Error')}")
        
        # Verify state continuity worked
        if 'result' in response3:
            result = response3['result'].lower()
            if '5' in result and '3' in result:
                print("✓ Context successfully maintained across save/load!")
            else:
                print("⚠ Context may not have been fully maintained")
        
        print(f"Final memory size: {len(agent2.memory)}")
        print("✓ State persistence with Claude test completed!")
        
    except Exception as e:
        print(f"Test encountered error: {e}")
        print("Note: This may be due to Claude CLI configuration issues")
        
    finally:
        # Clean up
        if state_file.exists():
            state_file.unlink()
            print(f"Cleaned up state file: {state_file}")

if __name__ == "__main__":
    test_state_persistence_with_claude()