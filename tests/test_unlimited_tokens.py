#!/usr/bin/env python3
"""
Test script to verify unlimited token responses
"""

import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from utils.ai_client import ai_client
from models.schemas import AIProvider

async def test_unlimited_tokens():
    """Test that AI clients can return unlimited content."""
    print("=== Testing Unlimited Token Responses ===")
    
    # Create a prompt that should generate a long response
    long_prompt = """
    Please provide a very detailed, comprehensive explanation of machine learning, 
    including all major concepts, algorithms, applications, and examples. 
    Make it as thorough and detailed as possible, covering:
    
    1. Introduction to Machine Learning
    2. Types of Machine Learning (Supervised, Unsupervised, Reinforcement)
    3. Common Algorithms for each type
    4. Real-world applications
    5. Evaluation metrics
    6. Best practices
    7. Future trends
    
    Please be very detailed and comprehensive in your response.
    """
    
    messages = [{"role": "user", "content": long_prompt}]
    
    # Test OpenAI
    print("\n🤖 Testing OpenAI (unlimited tokens)...")
    try:
        openai_response = await ai_client.generate_response(
            messages=messages,
            provider=AIProvider.OPENAI,
            temperature=0.7
            # No max_tokens parameter - should allow unlimited response
        )
        
        content_length = len(openai_response["content"])
        token_count = openai_response.get("usage", {}).get("completion_tokens", 0)
        
        print(f"✅ OpenAI Response:")
        print(f"   - Content length: {content_length} characters")
        print(f"   - Completion tokens: {token_count}")
        print(f"   - First 200 chars: {openai_response['content'][:200]}...")
        
        if content_length > 1000:  # Expect a substantial response
            print("✅ OpenAI appears to be generating unlimited content")
        else:
            print("⚠️  OpenAI response seems short - may still have limits")
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
    
    # Test Google AI
    print("\n🤖 Testing Google AI (unlimited tokens)...")
    try:
        google_response = await ai_client.generate_response(
            messages=messages,
            provider=AIProvider.GOOGLE,
            temperature=0.7
            # No max_tokens parameter - should allow unlimited response
        )
        
        content_length = len(google_response["content"])
        token_count = google_response.get("usage", {}).get("completion_tokens", 0)
        
        print(f"✅ Google AI Response:")
        print(f"   - Content length: {content_length} characters")
        print(f"   - Completion tokens: {token_count}")
        print(f"   - First 200 chars: {google_response['content'][:200]}...")
        
        if content_length > 1000:  # Expect a substantial response
            print("✅ Google AI appears to be generating unlimited content")
        else:
            print("⚠️  Google AI response seems short - may still have limits")
            
    except Exception as e:
        print(f"❌ Google AI test failed: {e}")

async def test_slide_analyzer_unlimited():
    """Test that slide analyzer can return unlimited content."""
    print("\n=== Testing Slide Analyzer Unlimited Tokens ===")
    
    # Look for any image files to test with
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path('.').glob(f'*{ext}'))
    
    if not image_files:
        print("📷 No image files found for slide analyzer test.")
        return
    
    test_image = str(image_files[0])
    print(f"📷 Testing slide analyzer with {test_image}")
    
    try:
        from tools.slide_analyzer import SlideAnalyzerTool
        
        tool = SlideAnalyzerTool()
        result = await tool.execute({
            "slide_images": [test_image],
            "ai_provider": "google",
            "analysis_depth": "comprehensive",
            "target_audience": "general"
            # No max_pdf_pages or token limits - should allow unlimited response
        })
        
        if result.success:
            # Check the length of the analysis
            course_data = result.data
            if isinstance(course_data, dict):
                # Count total characters in all text fields
                total_chars = 0
                for key, value in course_data.items():
                    if isinstance(value, str):
                        total_chars += len(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                total_chars += len(item)
                            elif isinstance(item, dict):
                                for subkey, subvalue in item.items():
                                    if isinstance(subvalue, str):
                                        total_chars += len(subvalue)
                
                print(f"✅ Slide Analyzer Response:")
                print(f"   - Total text content: {total_chars} characters")
                print(f"   - Document type: {course_data.get('type_document', 'Unknown')}")
                print(f"   - Execution time: {result.execution_time} seconds")
                
                if total_chars > 500:
                    print("✅ Slide analyzer appears to be generating substantial content")
                else:
                    print("⚠️  Slide analyzer response seems short")
            else:
                print(f"⚠️  Unexpected response format: {type(course_data)}")
        else:
            print(f"❌ Slide analyzer failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Slide analyzer test failed: {e}")

if __name__ == "__main__":
    print("Testing unlimited token responses for SMS-Agent...")
    print("This verifies that max_tokens limits have been removed.")
    print()
    
    asyncio.run(test_unlimited_tokens())
    asyncio.run(test_slide_analyzer_unlimited())
    
    print("\n🎉 Unlimited token testing completed!")
    print("The AI should now be able to generate responses of any length.") 