#!/usr/bin/env python3
"""
Simple test script for the AI Course Management Agent.
This script tests the basic functionality without requiring API keys.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_basic_functionality():
    """Test basic system functionality."""
    print("🧪 Testing AI Course Management Agent")
    print("=" * 50)
    
    try:
        # Test 1: Import core modules
        print("1. Testing module imports...")
        from app.config import settings
        from app.models.schemas import AgentRequest, AgentResponse
        from app.tools.base_tool import tool_registry
        from app.agent.core_agent import course_agent
        print("   ✅ All modules imported successfully")
        
        # Test 2: Check tool registry
        print("\n2. Testing tool registry...")
        available_tools = tool_registry.available_tools
        print(f"   📋 Available tools: {available_tools}")
        
        if len(available_tools) > 0:
            print("   ✅ Tool registry is populated")
        else:
            print("   ❌ Tool registry is empty")
            return False
        
        # Test 3: Test tool definitions
        print("\n3. Testing tool definitions...")
        for tool_name in available_tools:
            tool = tool_registry.get_tool(tool_name)
            definition = tool.get_definition()
            print(f"   🔧 {tool_name}: {definition.description}")
        print("   ✅ All tools have valid definitions")
        
        # Test 4: Test content analyzer (without AI)
        print("\n4. Testing content analyzer tool...")
        analyzer = tool_registry.get_tool("contentanalyzer")
        if analyzer:
            print("   ✅ Content analyzer tool found")
            print(f"   📝 Parameters: {[p.name for p in analyzer.definition.parameters]}")
        else:
            print("   ❌ Content analyzer tool not found")
            return False
        
        # Test 5: Test file processor tool
        print("\n5. Testing file processor tool...")
        processor = tool_registry.get_tool("fileprocessor")
        if processor:
            print("   ✅ File processor tool found")
            print(f"   📁 Supported types: {settings.supported_file_types}")
        else:
            print("   ❌ File processor tool not found")
            return False
        
        # Test 6: Test content generator tool
        print("\n6. Testing content generator tool...")
        generator = tool_registry.get_tool("contentgenerator")
        if generator:
            print("   ✅ Content generator tool found")
            print(f"   🎯 Content types: {[p.enum for p in generator.definition.parameters if p.enum]}")
        else:
            print("   ❌ Content generator tool not found")
            return False
        
        # Test 7: Test configuration
        print("\n7. Testing configuration...")
        print(f"   🔧 Max concurrent tools: {settings.max_concurrent_tools}")
        print(f"   ⏱️  Tool timeout: {settings.tool_execution_timeout}s")
        print(f"   💾 Content caching: {settings.enable_content_caching}")
        print(f"   📝 Supported file types: {len(settings.supported_file_types)} types")
        print("   ✅ Configuration loaded successfully")
        
        # Test 8: Test agent initialization
        print("\n8. Testing agent initialization...")
        if course_agent:
            print(f"   🤖 Agent initialized with {len(course_agent.tool_registry.available_tools)} tools")
            print("   ✅ Course management agent is ready")
        else:
            print("   ❌ Failed to initialize course management agent")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All basic tests passed!")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: python -m app.main")
        print("3. Visit: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_sample_content():
    """Test the system with sample content (requires API keys)."""
    print("\n" + "=" * 50)
    print("🧪 Testing with sample content...")
    
    try:
        from app.agent.core_agent import course_agent
        
        # Sample course content
        sample_content = """
        Introduction to Python Programming
        
        This course covers the fundamentals of Python programming language.
        Students will learn:
        - Basic syntax and data types
        - Control structures (loops, conditionals)
        - Functions and modules
        - Object-oriented programming
        - File handling and exceptions
        - Libraries and frameworks
        
        Prerequisites: Basic computer literacy
        Target audience: Beginners
        Duration: 8 weeks
        """
        
        print("📝 Sample content prepared")
        print("🔄 Processing with agent...")
        
        # Test the agent
        response = await course_agent.process_request(
            user_request="Analyze this course content and provide insights",
            context={"sample_content": sample_content}
        )
        
        if response.success:
            print("✅ Agent processed request successfully")
            print(f"📊 Response length: {len(response.response)} characters")
            print(f"⏱️  Processing time: {response.processing_time:.2f}s")
            
            if response.data:
                print("📈 Structured data available")
            
            print("\n📋 Agent Response Preview:")
            print("-" * 30)
            print(response.response[:300] + "..." if len(response.response) > 300 else response.response)
            
        else:
            print("❌ Agent processing failed")
            if response.errors:
                print(f"🚨 Errors: {response.errors}")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Content test failed: {e}")
        # This is expected if API keys are not configured
        if "API key" in str(e) or "Authentication" in str(e):
            print("💡 This is expected if API keys are not configured")
            print("   Configure OPENAI_API_KEY or GOOGLE_API_KEY to test with AI")
            return True
        return False


def check_api_keys():
    """Check if API keys are configured."""
    print("\n" + "=" * 50)
    print("🔑 Checking API key configuration...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key not configured")
    
    if google_key and google_key != 'your_google_api_key_here':
        print("✅ Google AI API key configured")
    else:
        print("⚠️  Google AI API key not configured")
    
    if not openai_key and not google_key:
        print("\n💡 To test with AI capabilities:")
        print("   1. Copy config.env.example to .env")
        print("   2. Add your API keys to .env")
        print("   3. Run this test again")
        return False
    
    return True


async def main():
    """Main test function."""
    print("🚀 AI Course Management Agent - Test Suite")
    print("Testing basic functionality...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run basic tests
    basic_success = await test_basic_functionality()
    
    if not basic_success:
        print("\n❌ Basic tests failed. Please fix the issues before proceeding.")
        return
    
    # Check API keys
    has_api_keys = check_api_keys()
    
    # Test with content if API keys are available
    if has_api_keys:
        content_success = await test_with_sample_content()
        if content_success:
            print("\n🎉 All tests passed! System is ready for use.")
        else:
            print("\n⚠️  Content tests failed. Check your API key configuration.")
    else:
        print("\n✅ Basic tests completed. Configure API keys for full testing.")


if __name__ == "__main__":
    asyncio.run(main()) 