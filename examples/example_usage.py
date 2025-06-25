#!/usr/bin/env python3
"""
Example usage script for the AI Course Management Agent.
This demonstrates various ways to use the agent programmatically.
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent
from app.agent.core_agent import course_agent
from app.models.schemas import AIProvider


async def example_content_analysis():
    """Example: Analyze course content."""
    print("📚 Example 1: Course Content Analysis")
    print("-" * 40)
    
    course_content = """
    Data Structures and Algorithms - CS301
    
    Course Overview:
    This comprehensive course introduces students to fundamental data structures 
    and algorithms essential for computer science. Students will learn to design, 
    implement, and analyze efficient algorithms and data structures.
    
    Learning Objectives:
    - Understand fundamental data structures (arrays, linked lists, stacks, queues)
    - Master tree and graph algorithms
    - Analyze time and space complexity using Big O notation
    - Implement sorting and searching algorithms
    - Apply dynamic programming techniques
    - Design efficient algorithms for real-world problems
    
    Prerequisites: 
    - Programming experience in Python or Java
    - Basic mathematics (discrete math recommended)
    
    Assessment Methods:
    - Programming assignments (40%)
    - Midterm exam (25%)
    - Final exam (35%)
    
    Target Audience: Computer Science majors, junior level
    Duration: 15 weeks
    """
    
    try:
        response = await course_agent.process_request(
            user_request="Analyze this course content and provide detailed insights about the structure, difficulty, and learning outcomes.",
            context={
                "target_audience": "computer science students",
                "analysis_focus": "comprehensive"
            }
        )
        
        print(f"✅ Analysis completed in {response.processing_time:.2f}s")
        print(f"📊 Session ID: {response.session_id}")
        print("\n📋 Analysis Results:")
        print(response.response)
        
        if response.data:
            print(f"\n📈 Structured data available: {len(response.data)} items")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_content_generation():
    """Example: Generate educational content."""
    print("\n" + "=" * 60)
    print("🎯 Example 2: Educational Content Generation")
    print("-" * 40)
    
    source_material = """
    Binary Search Trees (BST) are hierarchical data structures where each node 
    has at most two children. The left subtree contains nodes with values less 
    than the parent, and the right subtree contains nodes with values greater 
    than the parent. This property enables efficient searching, insertion, and 
    deletion operations with O(log n) average time complexity.
    """
    
    try:
        response = await course_agent.process_request(
            user_request="Generate a quiz with 5 questions about binary search trees based on this content.",
            context={
                "content_type": "quiz",
                "target_audience": "intermediate",
                "source_content": source_material
            }
        )
        
        print(f"✅ Content generated in {response.processing_time:.2f}s")
        print("\n📝 Generated Quiz:")
        print(response.response)
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def example_multi_step_analysis():
    """Example: Multi-step analysis workflow."""
    print("\n" + "=" * 60)
    print("🔄 Example 3: Multi-Step Analysis Workflow")
    print("-" * 40)
    
    try:
        # Step 1: Analyze course structure
        step1_response = await course_agent.process_request(
            user_request="Analyze the structure and organization of this machine learning course",
            context={
                "course_content": """
                Machine Learning Fundamentals
                
                Week 1-2: Introduction to ML
                - Types of learning (supervised, unsupervised, reinforcement)
                - Problem formulation and data preprocessing
                
                Week 3-5: Supervised Learning
                - Linear regression and logistic regression
                - Decision trees and random forests
                - Support vector machines
                
                Week 6-8: Unsupervised Learning
                - K-means clustering
                - Hierarchical clustering
                - Principal component analysis
                
                Week 9-10: Neural Networks
                - Perceptrons and multi-layer networks
                - Backpropagation algorithm
                
                Week 11-12: Advanced Topics
                - Ensemble methods
                - Model evaluation and validation
                """,
                "analysis_type": "structure"
            }
        )
        
        print(f"📊 Step 1 completed in {step1_response.processing_time:.2f}s")
        print("Structure analysis:", step1_response.response[:200] + "...")
        
        # Step 2: Generate study materials
        step2_response = await course_agent.process_request(
            user_request="Create a comprehensive study guide based on the course structure analysis",
            context={
                "previous_analysis": step1_response.response[:1000],
                "content_type": "study_guide",
                "target_audience": "undergraduate students"
            }
        )
        
        print(f"📚 Step 2 completed in {step2_response.processing_time:.2f}s")
        print("Study guide preview:", step2_response.response[:200] + "...")
        
        return step1_response, step2_response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


async def example_with_different_providers():
    """Example: Using different AI providers."""
    print("\n" + "=" * 60)
    print("🤖 Example 4: Testing Different AI Providers")
    print("-" * 40)
    
    test_content = "Explain the concept of recursion in programming with a simple example."
    
    providers = [AIProvider.OPENAI, AIProvider.GOOGLE]
    
    for provider in providers:
        try:
            print(f"\n🔄 Testing with {provider.value}...")
            
            response = await course_agent.process_request(
                user_request=f"Create a brief explanation of recursion suitable for beginners.",
                context={"target_audience": "beginners"},
                preferred_provider=provider
            )
            
            if response.success:
                print(f"✅ {provider.value} responded in {response.processing_time:.2f}s")
                print(f"Response preview: {response.response[:150]}...")
            else:
                print(f"❌ {provider.value} failed: {response.errors}")
                
        except Exception as e:
            print(f"❌ Error with {provider.value}: {e}")


async def example_error_handling():
    """Example: Error handling and edge cases."""
    print("\n" + "=" * 60)
    print("🛡️ Example 5: Error Handling")
    print("-" * 40)
    
    # Test with empty content
    try:
        print("Testing with empty content...")
        response = await course_agent.process_request(
            user_request="",
            context={}
        )
        print(f"Empty request result: {'Success' if response.success else 'Failed as expected'}")
    except Exception as e:
        print(f"Expected error for empty content: {type(e).__name__}")
    
    # Test with very long content
    try:
        print("\nTesting with very long content...")
        long_content = "This is a test. " * 1000  # Very long content
        response = await course_agent.process_request(
            user_request="Summarize this content",
            context={"content": long_content}
        )
        print(f"Long content result: {'Success' if response.success else 'Handled gracefully'}")
    except Exception as e:
        print(f"Long content handling: {type(e).__name__}")


def print_system_info():
    """Print system information."""
    print("🤖 AI Course Management Agent - Example Usage")
    print("=" * 60)
    
    from app.tools.base_tool import tool_registry
    from app.config import settings
    
    print(f"📋 Available tools: {len(tool_registry.available_tools)}")
    for tool_name in tool_registry.available_tools:
        tool = tool_registry.get_tool(tool_name)
        print(f"   • {tool_name}: {tool.definition.description}")
    
    print(f"\n⚙️  Configuration:")
    print(f"   • Max concurrent tools: {settings.max_concurrent_tools}")
    print(f"   • Tool timeout: {settings.tool_execution_timeout}s")
    print(f"   • Content caching: {settings.enable_content_caching}")
    print(f"   • Supported file types: {settings.supported_file_types}")


async def main():
    """Run all examples."""
    print_system_info()
    
    # Run examples
    examples = [
        ("Content Analysis", example_content_analysis),
        ("Content Generation", example_content_generation), 
        ("Multi-Step Workflow", example_multi_step_analysis),
        ("Different Providers", example_with_different_providers),
        ("Error Handling", example_error_handling)
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            print(f"\n🚀 Running {name}...")
            result = await example_func()
            results[name] = result
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Execution Summary")
    print("-" * 40)
    
    successful = sum(1 for r in results.values() if r is not None)
    total = len(results)
    
    print(f"✅ Successful examples: {successful}/{total}")
    
    for name, result in results.items():
        status = "✅ Success" if result is not None else "❌ Failed"
        print(f"   {name}: {status}")
    
    if successful == total:
        print("\n🎉 All examples completed successfully!")
    elif successful > 0:
        print(f"\n⚠️  {total - successful} examples failed. Check your configuration.")
    else:
        print("\n❌ All examples failed. Please check your setup and API keys.")
    
    print("\n💡 Tips:")
    print("   • Make sure your API keys are configured in .env")
    print("   • Check the logs for detailed error information")
    print("   • Run 'python test_agent.py' for basic system tests")


if __name__ == "__main__":
    asyncio.run(main()) 