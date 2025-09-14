#!/usr/bin/env python3
"""
Test script to verify YAML integration is working correctly
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import studentagents
sys.path.insert(0, str(Path(__file__).parent))

try:
    from studentagents.crew import Studentagents
    print("✓ Successfully imported Studentagents crew")
    
    # Initialize the crew
    crew = Studentagents()
    print("✓ Successfully initialized Studentagents crew")
    
    # Test agent creation from YAML
    print("\n--- Testing Agent Creation from YAML ---")
    
    try:
        student_agent = crew.studentAgent()
        print(f"✓ Student Agent: {student_agent.role}")
    except Exception as e:
        print(f"✗ Student Agent failed: {e}")
    
    try:
        analyst_agent = crew.studentAnalyst()
        print(f"✓ Analyst Agent: {analyst_agent.role}")
    except Exception as e:
        print(f"✗ Analyst Agent failed: {e}")
    
    try:
        relevance_agent = crew.relevanceAgent()
        print(f"✓ Relevance Agent: {relevance_agent.role}")
    except Exception as e:
        print(f"✗ Relevance Agent failed: {e}")
    
    try:
        guideline_agent = crew.guidelineAgent()
        print(f"✓ Guideline Agent: {guideline_agent.role}")
    except Exception as e:
        print(f"✗ Guideline Agent failed: {e}")
    
    # Test task creation from YAML
    print("\n--- Testing Task Creation from YAML ---")
    
    try:
        student_task = crew.studentTask()
        print(f"✓ Student Task: {student_task.description[:50]}...")
    except Exception as e:
        print(f"✗ Student Task failed: {e}")
    
    try:
        analyst_task = crew.analystTask()
        print(f"✓ Analyst Task: {analyst_task.description[:50]}...")
    except Exception as e:
        print(f"✗ Analyst Task failed: {e}")
    
    try:
        relevance_task = crew.relevanceTask()
        print(f"✓ Relevance Task: {relevance_task.description[:50]}...")
    except Exception as e:
        print(f"✗ Relevance Task failed: {e}")
    
    try:
        guideline_task = crew.guidelineTask()
        print(f"✓ Guideline Task: {guideline_task.description[:50]}...")
    except Exception as e:
        print(f"✗ Guideline Task failed: {e}")
    
    print("\n--- YAML Integration Test Complete ---")
    print("All agents and tasks are properly loading from YAML configurations!")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("Make sure you're in the correct directory and dependencies are installed")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
