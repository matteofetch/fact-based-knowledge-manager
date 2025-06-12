#!/usr/bin/env python3
"""Test script for task generation functionality."""

import os
import sys
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from task_generator import TaskGenerator


def main():
    """Test the task generation functionality."""
    logging.basicConfig(level=logging.INFO)
    
    print("=== Testing Task Generation ===\n")
    
    # Set environment variables for testing
    if not os.getenv('SUPABASE_URL'):
        print("Setting environment variables for testing...")
        os.environ['SUPABASE_URL'] = 'https://wsrfatvbhyirfaeflpym.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzcmZhdHZiaHlpcmZhZWZscHltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTgyMzAsImV4cCI6MjA2NTMzNDIzMH0.S3cQah8RDFnMnChShefIfAklgvl0JZ_Co6P1lvxjP30'
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set - this test will fail without it")
        print("Please set your OpenAI API key to test task generation")
        return
    
    task_generator = TaskGenerator()
    
    print("1. Generating tasks using ChatGPT...")
    result = task_generator.generate_tasks()
    
    print(f"\n2. Results:")
    print(f"   Success: {result['success']}")
    
    if result['success']:
        print(f"   Generated: {result['generated_count']} tasks")
        print(f"   Added to DB: {result['added_count']} tasks")
        print(f"\n3. Generated tasks:")
        for i, task in enumerate(result.get('tasks', []), 1):
            print(f"   {i}. {task['title']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n=== Test completed ===")


if __name__ == "__main__":
    main() 