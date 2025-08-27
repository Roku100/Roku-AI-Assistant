#!/usr/bin/env python3
"""
Test script for Roku Jarvis tools
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import get_current_datetime, get_basic_knowledge, get_election_info

async def test_tools():
    """Test the new tools to ensure they work correctly"""
    
    print("Testing Roku Jarvis Tools...")
    print("=" * 50)
    
    # Test datetime tool
    print("\n1. Testing get_current_datetime:")
    try:
        result = await get_current_datetime(None)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test basic knowledge tool
    print("\n2. Testing get_basic_knowledge:")
    test_questions = [
        "What's your name?",
        "How are you?",
        "What can you do?",
        "Hello",
        "What day is it?"
    ]
    
    for question in test_questions:
        try:
            result = await get_basic_knowledge(None, question)
            print(f"Q: {question}")
            print(f"A: {result}")
            print()
        except Exception as e:
            print(f"Error with '{question}': {e}")
    
    # Test election info tool
    print("\n3. Testing get_election_info:")
    test_elections = [
        "2025 US elections",
        "2024 US elections",
        "Who won the presidential election"
    ]
    
    for election in test_elections:
        try:
            result = await get_election_info(None, election)
            print(f"Q: {election}")
            print(f"A: {result}")
            print()
        except Exception as e:
            print(f"Error with '{election}': {e}")
    
    print("=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_tools())
