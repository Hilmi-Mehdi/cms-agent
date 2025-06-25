#!/usr/bin/env python3
"""
Demo: How to Use the AI Course Management Agent Programmatically
"""

import asyncio
from app.agent.core_agent import course_agent
from app.models.schemas import AIProvider

async def demo_basic_usage():
    """Demo 1: Basic agent usage for content analysis"""
    print("🎯 Demo 1: Basic Content Analysis")
    print("-" * 40)
    
    # Simple request
    response = await course_agent.process_request(
        user_request="Analyze this Python course outline and tell me what's missing",
        context={
            "course_content": """
            Python Programming Course:
            1. Variables and Data Types
            2. Control Structures  
            3. Functions
            4. Classes and Objects
            """,
            "target_audience": "beginners"
        }
    )
    
    print(f"✅ Response: {response.response[:200]}...")
    print(f"⏱️  Time: {response.processing_time:.2f}s")
    print(f"🛠️  Tools used: {[tool['name'] for tool in response.data.get('tools_executed', [])]}")
    
    return response

async def demo_multi_step_workflow():
    """Demo 2: Multi-step workflow - analyze then generate"""
    print("\n🔄 Demo 2: Multi-Step Workflow")
    print("-" * 40)
    
    response = await course_agent.process_request(
        user_request="First analyze this course content, then create a quiz based on the analysis",
        context={
            "course_material": """
            Machine Learning Basics:
            - Supervised Learning: Classification and Regression
            - Unsupervised Learning: Clustering, Dimensionality Reduction  
            - Model Evaluation: Cross-validation, Metrics
            - Overfitting and Regularization
            """,
            "quiz_difficulty": "intermediate",
            "num_questions": 5
        }
    )
    
    print(f"✅ Multi-step completed")
    print(f"📊 Steps executed: {len(response.data.get('execution_plan', []))}")
    print(f"🛠️  Tools used: {[tool['name'] for tool in response.data.get('tools_executed', [])]}")
    
    return response

async def demo_direct_tool_usage():
    """Demo 3: Using tools directly (without agent orchestration)"""
    print("\n🔧 Demo 3: Direct Tool Usage")
    print("-" * 40)
    
    # Get a specific tool
    analyzer = course_agent.tool_registry.get_tool("contentanalyzer")
    
    # Use it directly
    result = await analyzer.execute({
        "content": "Introduction to Data Structures: Arrays, Linked Lists, Stacks, Queues",
        "analysis_type": "concepts",
        "target_audience": "intermediate"
    })
    
    print(f"✅ Direct tool result: {result.success}")
    print(f"📝 Key concepts found: {len(result.data.get('key_concepts', []))}")
    
    return result

async def demo_different_providers():
    """Demo 4: Using different AI providers"""
    print("\n🤖 Demo 4: Different AI Providers")
    print("-" * 40)
    
    # Try with OpenAI
    response_openai = await course_agent.process_request(
        user_request="Summarize the key concepts in object-oriented programming",
        preferred_provider=AIProvider.OPENAI
    )
    
    # Try with Google AI
    response_google = await course_agent.process_request(
        user_request="Summarize the key concepts in object-oriented programming", 
        preferred_provider=AIProvider.GOOGLE
    )
    
    print(f"🟢 OpenAI response length: {len(response_openai.response)}")
    print(f"🔵 Google response length: {len(response_google.response)}")
    
    return response_openai, response_google

async def demo_with_files():
    """Demo 5: Processing files (simulated)"""
    print("\n📁 Demo 5: File Processing")
    print("-" * 40)
    
    # This would work with actual files
    response = await course_agent.process_request(
        user_request="Extract key concepts from this document and create a study guide",
        context={
            "file_content": """
            Chapter 1: Introduction to Algorithms
            
            An algorithm is a step-by-step procedure for solving a problem.
            Key characteristics:
            - Definiteness: Each step must be precisely defined
            - Input: Zero or more inputs
            - Output: One or more outputs  
            - Effectiveness: Steps must be basic enough to be carried out
            - Finiteness: Algorithm must terminate after finite steps
            
            Time Complexity: How runtime scales with input size
            Space Complexity: How memory usage scales with input size
            """,
            "file_type": "textbook_chapter"
        }
    )
    
    print(f"✅ File processed successfully")
    print(f"📄 Content length: {len(response.context.get('file_content', ''))}")
    
    return response

async def main():
    """Run all demos"""
    print("🚀 AI Course Management Agent - Usage Demos")
    print("=" * 60)
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Multi-Step Workflow", demo_multi_step_workflow),
        ("Direct Tool Usage", demo_direct_tool_usage),
        ("Different Providers", demo_different_providers),
        ("File Processing", demo_with_files)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
        except Exception as e:
            print(f"❌ {name} failed: {e}")
        
        print()  # Add spacing
    
    print("✨ All demos completed!")

if __name__ == "__main__":
    asyncio.run(main()) 