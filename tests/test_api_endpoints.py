#!/usr/bin/env python3
"""
Test script for the slide analyzer API endpoints
"""

import asyncio
import json
from pathlib import Path
import aiohttp
import tempfile
from PIL import Image
import io

async def test_tools_endpoint():
    """Test the tools listing endpoint."""
    print("🔧 Testing Tools Endpoint")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/api/v1/tools") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Tools endpoint working")
                    print(f"📋 Available tools: {data.get('available_tools', [])}")
                    
                    # Check if slide analyzer is listed
                    if 'slideanalyzer' in data.get('available_tools', []):
                        print("✅ Slide analyzer tool is available!")
                        
                        # Show tool details
                        tool_details = data.get('tool_details', {}).get('slideanalyzer', {})
                        print(f"📖 Description: {tool_details.get('description', 'N/A')}")
                        print(f"🔧 Parameters: {len(tool_details.get('parameters', []))}")
                    else:
                        print("❌ Slide analyzer tool not found")
                else:
                    print(f"❌ Tools endpoint failed: {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Error testing tools endpoint: {str(e)}")


async def test_slide_analyzer_endpoint():
    """Test the slide analyzer endpoint with sample images."""
    print("\n📊 Testing Slide Analyzer Endpoint")
    print("=" * 40)
    
    # Create sample slide images for testing
    sample_slides = []
    temp_files = []
    
    try:
        # Create 3 sample slide images
        for i in range(3):
            # Create a simple test image
            img = Image.new('RGB', (800, 600), color=(100 + i*50, 150, 200))
            
            # Add some text-like rectangles to simulate slide content
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Title area
            draw.rectangle([50, 50, 750, 120], fill=(255, 255, 255))
            
            # Content areas
            draw.rectangle([50, 150, 750, 250], fill=(240, 240, 240))
            draw.rectangle([50, 280, 350, 450], fill=(250, 250, 250))
            draw.rectangle([400, 280, 750, 450], fill=(250, 250, 250))
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_slide_{i+1}.png')
            img.save(temp_file.name, 'PNG')
            temp_files.append(temp_file.name)
            sample_slides.append(temp_file.name)
        
        print(f"📁 Created {len(sample_slides)} sample slide images")
        
        # Test the endpoint
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            
            # Add form fields
            data.add_field('ai_provider', 'openai')
            data.add_field('analysis_depth', 'comprehensive')
            data.add_field('target_audience', 'intermediate')
            data.add_field('subject_area', 'programming')
            
            # Add slide files
            for slide_path in sample_slides:
                with open(slide_path, 'rb') as f:
                    data.add_field('slides', f.read(), 
                                 filename=Path(slide_path).name,
                                 content_type='image/png')
            
            try:
                async with session.post("http://localhost:8000/api/v1/analyze-slides", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Slide analysis successful!")
                        
                        course_data = result.get('course_data', {})
                        print(f"📊 Course Title: {course_data.get('course_title', 'N/A')}")
                        print(f"📝 Description: {course_data.get('short_description', 'N/A')}")
                        print(f"🏷️  Tags: {', '.join(course_data.get('tags', []))}")
                        print(f"📚 Learning Path: {len(course_data.get('learning_path', []))} modules")
                        print(f"⏱️  Execution Time: {result.get('execution_time', 'N/A')}s")
                        print(f"🖼️  Images Analyzed: {result.get('images_analyzed', 'N/A')}")
                        
                        # Show first module if available
                        learning_path = course_data.get('learning_path', [])
                        if learning_path:
                            first_module = learning_path[0]
                            print(f"\n📖 First Module: {first_module.get('module_name', 'N/A')}")
                            print(f"   🎯 Objectives: {len(first_module.get('objectives', []))}")
                            print(f"   📋 Topics: {len(first_module.get('topics', []))}")
                    else:
                        print(f"❌ Slide analysis failed: {response.status}")
                        text = await response.text()
                        print(f"Response: {text[:500]}...")
                        
            except Exception as e:
                print(f"❌ Error during slide analysis: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink()
            except:
                pass


async def test_tools_execute_endpoint():
    """Test the generic tools execute endpoint."""
    print("\n🛠️  Testing Tools Execute Endpoint")
    print("=" * 40)
    
    # Test with slide analyzer tool
    parameters = {
        "slide_images": [],  # Empty for testing validation
        "ai_provider": "openai",
        "analysis_depth": "basic"
    }
    
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('tool_name', 'slideanalyzer')
        data.add_field('parameters', json.dumps(parameters))
        
        try:
            async with session.post("http://localhost:8000/api/v1/tools/execute", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        print("✅ Tools execute endpoint working")
                        print(f"📊 Response: {result}")
                    else:
                        print("✅ Tools execute endpoint working (validation error expected)")
                        print(f"❌ Expected error: {result.get('error', 'N/A')}")
                else:
                    print(f"❌ Tools execute failed: {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Error testing tools execute: {str(e)}")


def print_endpoint_documentation():
    """Print documentation for the slide analyzer endpoints."""
    print("\n📚 Slide Analyzer API Endpoints")
    print("=" * 50)
    
    print("""
🔗 Available Endpoints:

1. 📋 List Tools:
   GET /api/v1/tools
   
   Returns list of available tools including the slide analyzer.

2. 📊 Analyze Slides:
   POST /api/v1/analyze-slides
   
   Upload slide images and get course structure analysis.
   
   Form Fields:
   - slides: Multiple image files (PNG, JPG, JPEG, WebP, BMP)
   - ai_provider: "openai" or "google" (optional, default: "openai")
   - analysis_depth: "basic", "detailed", or "comprehensive" (optional, default: "comprehensive")
   - target_audience: "beginner", "intermediate", "advanced", or "general" (optional, default: "general")
   - subject_area: Subject hint (optional, default: "auto-detect")

3. 🛠️  Execute Tool:
   POST /api/v1/tools/execute
   
   Execute any tool with JSON parameters.
   
   Form Fields:
   - tool_name: "slideanalyzer"
   - parameters: JSON string with tool parameters

📝 Example cURL Commands:

# List tools
curl -X GET http://localhost:8000/api/v1/tools

# Analyze slides
curl -X POST http://localhost:8000/api/v1/analyze-slides \\
  -F "slides=@slide1.png" \\
  -F "slides=@slide2.png" \\
  -F "ai_provider=openai" \\
  -F "analysis_depth=comprehensive" \\
  -F "target_audience=intermediate"

# Execute tool directly
curl -X POST http://localhost:8000/api/v1/tools/execute \\
  -F "tool_name=slideanalyzer" \\
  -F 'parameters={"slide_images":["slide1.png"],"ai_provider":"openai"}'

🎯 Response Format:
{
  "success": true,
  "course_data": {
    "course_title": "Generated Course Title",
    "detailed_description": "Comprehensive description",
    "short_description": "Brief overview",
    "tags": ["tag1", "tag2", "tag3"],
    "learning_path": [
      {
        "module_name": "Module Name",
        "objectives": ["objective1", "objective2"],
        "topics": ["topic1", "topic2"],
        "estimated_duration": "2 hours",
        "difficulty": "intermediate"
      }
    ],
    "target_audience": "intermediate",
    "prerequisites": ["prereq1"],
    "difficulty_level": "intermediate",
    "estimated_total_duration": "8 hours",
    "tools_required": ["tool1", "tool2"],
    "key_concepts": ["concept1", "concept2"],
    "practical_applications": ["app1", "app2"],
    "analysis_metadata": {
      "provider": "openai",
      "model": "gpt-4o",
      "images_analyzed": 3,
      "analysis_depth": "comprehensive"
    }
  },
  "execution_time": 15.42,
  "images_analyzed": 3,
  "suggested_next_tools": ["contentanalyzer", "contentgenerator"]
}
""")


async def main():
    """Run all API endpoint tests."""
    print("🚀 Slide Analyzer API Endpoint Tests")
    print("=" * 60)
    
    # Test individual endpoints
    await test_tools_endpoint()
    await test_slide_analyzer_endpoint()
    await test_tools_execute_endpoint()
    
    # Show documentation
    print_endpoint_documentation()
    
    print("\n🎉 API testing completed!")
    print("\n💡 To test with real slides:")
    print("   1. Save your slide images as PNG/JPG files")
    print("   2. Use the /api/v1/analyze-slides endpoint")
    print("   3. Check the response for structured course data")


if __name__ == "__main__":
    asyncio.run(main()) 