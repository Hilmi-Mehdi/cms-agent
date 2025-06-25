#!/usr/bin/env python3
"""
Example Usage: Document Fetcher Tool

This example demonstrates how to use the DocumentFetcherTool to:
1. Fetch document data from Science Made Simple API
2. Extract images from tar archives
3. Analyze the images with SlideAnalyzerTool
4. Generate content based on the analysis

Requirements:
- Valid API credentials for Science Made Simple
- Document ID from their system
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.base_tool import tool_registry


async def example_basic_usage():
    """Basic usage example with Science Made Simple authentication."""
    
    print("📄 Document Fetcher Tool - Basic Usage")
    print("=" * 50)
    
    # Get the tool
    fetcher = tool_registry.get_tool("documentfetcher")
    
    # Science Made Simple API authentication header
    auth_headers = {
        "SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"  # Your API key
    }
    
    try:
        result = await fetcher.execute({
            "document_id": "ct13hjqcchrs715kgjl0",  # Replace with actual document ID
            "api_headers": auth_headers,  # Include SMS auth header
            "extract_images": True,
            "max_images": 20,
            "image_format_filter": ["jpg", "jpeg", "png"]
        })
        
        if result.success:
            print("✅ Document fetched successfully!")
            print(f"   Document: {result.data['document_metadata'].get('Name', 'Unknown')}")
            print(f"   Pages: {result.data['document_metadata'].get('PageCount', 'N/A')}")
            print(f"   Processing status: {result.data['document_metadata'].get('Processing', {}).get('Status', 'N/A')}")
            
            images = result.data.get("extracted_images", {})
            if images.get("status") == "success":
                print(f"   Images extracted: {images.get('image_count', 0)}")
                print(f"   Formats found: {images.get('formats_found', [])}")
                print(f"   Suggested next tools: {result.suggested_next_tools}")
            
            return result
        else:
            print(f"❌ Failed to fetch document: {result.error}")
            return None
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return None


async def example_complete_workflow():
    """Complete workflow: Fetch → Analyze → Generate content."""
    
    print("\n🔄 Complete Document Processing Workflow")
    print("=" * 50)
    
    # Step 1: Fetch document with proper authentication
    fetcher = tool_registry.get_tool("documentfetcher")
    fetch_result = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},  # SMS API auth
        "extract_images": True,
        "max_images": 15
    })
    
    if not fetch_result.success:
        print(f"❌ Step 1 failed: {fetch_result.error}")
        return
    
    print("✅ Step 1: Document fetched")
    
    # Step 2: Analyze slides if images were extracted
    images_data = fetch_result.data.get("extracted_images", {})
    if images_data.get("status") == "success" and images_data.get("image_count", 0) > 0:
        print("🔍 Step 2: Analyzing slides...")
        
        analyzer = tool_registry.get_tool("slideanalyzer")
        slide_result = await analyzer.execute({
            "slide_images": images_data["image_paths"],
            "analysis_depth": "comprehensive",
            "ai_provider": "openai",
            "target_audience": "intermediate"
        })
        
        if slide_result.success:
            print("✅ Step 2: Slides analyzed")
            print(f"   Course title: {slide_result.data.get('course_title', 'Unknown')}")
            print(f"   Description: {slide_result.data.get('course_description', 'N/A')[:100]}...")
            
            # Step 3: Generate additional content
            print("📝 Step 3: Generating content...")
            
            generator = tool_registry.get_tool("contentgenerator")
            gen_result = await generator.execute({
                "content_type": "summary",
                "source_content": slide_result.data.get("detailed_description", ""),
                "target_audience": "intermediate",
                "length": "medium",
                "format": "markdown"
            })
            
            if gen_result.success:
                print("✅ Step 3: Content generated")
                generated = gen_result.data.get("generated_content", {})
                print(f"   Word count: {generated.get('metadata', {}).get('word_count', 'N/A')}")
                
                # Display results
                print("\n📋 Final Results:")
                print("-" * 30)
                print(f"Document: {fetch_result.data['document_metadata'].get('Name', 'Unknown')}")
                print(f"Images processed: {images_data.get('image_count', 0)}")
                print(f"Course title: {slide_result.data.get('course_title', 'Unknown')}")
                print(f"Generated content type: {gen_result.data.get('content_type', 'N/A')}")
                
                return {
                    "document_data": fetch_result.data,
                    "slide_analysis": slide_result.data,
                    "generated_content": gen_result.data
                }
            else:
                print(f"❌ Step 3 failed: {gen_result.error}")
        else:
            print(f"❌ Step 2 failed: {slide_result.error}")
    else:
        print("⏭️ No images to analyze, proceeding with document metadata only")


async def example_error_handling():
    """Example showing proper error handling."""
    
    print("\n🛡️ Error Handling Example")
    print("=" * 50)
    
    fetcher = tool_registry.get_tool("documentfetcher")
    
    # Test with invalid document ID but valid auth
    result = await fetcher.execute({
        "document_id": "invalid_id_123",
        "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},
        "extract_images": False  # Skip image extraction for this test
    })
    
    if not result.success:
        print(f"Expected error caught: {result.error}")
        print("✅ Error handling works correctly")
    else:
        print("⚠️ Unexpected success - check API behavior")


async def example_configuration_options():
    """Example showing different configuration options."""
    
    print("\n⚙️ Configuration Options Example")
    print("=" * 50)
    
    fetcher = tool_registry.get_tool("documentfetcher")
    
    # Standard SMS auth header for all requests
    sms_headers = {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"}
    
    # Configuration 1: Images only
    print("Config 1: Extract only JPG images, max 5")
    result1 = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": sms_headers,
        "extract_images": True,
        "max_images": 5,
        "image_format_filter": ["jpg", "jpeg"]
    })
    
    # Configuration 2: No image extraction
    print("Config 2: Metadata only, no image extraction")
    result2 = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": sms_headers,
        "extract_images": False
    })
    
    # Configuration 3: All image formats, higher limit
    print("Config 3: All image formats, max 30 images")
    result3 = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": sms_headers,
        "extract_images": True,
        "max_images": 30,
        "image_format_filter": ["jpg", "jpeg", "png", "gif", "bmp"]
    })
    
    print(f"Results: {[r.success for r in [result1, result2, result3]]}")


async def test_real_api_connection():
    """Test the actual API connection with provided credentials."""
    
    print("\n🔗 Testing Real API Connection")
    print("=" * 50)
    
    fetcher = tool_registry.get_tool("documentfetcher")
    
    # Test with the provided credentials and document ID
    result = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},
        "extract_images": False  # Just test the API connection first
    })
    
    if result.success:
        print("✅ API connection successful!")
        doc_meta = result.data["document_metadata"]
        print(f"   Document Name: {doc_meta.get('Name', 'N/A')}")
        print(f"   Description: {doc_meta.get('Desc', 'N/A')[:100]}...")
        print(f"   Page Count: {doc_meta.get('PageCount', 'N/A')}")
        print(f"   Content Hash: {doc_meta.get('ContentHash', 'N/A')[:16]}...")
        
        # Check if we have image URLs
        urls = doc_meta.get('URLs', {})
        if urls.get('ImageArchive100URL'):
            print(f"   ✅ ImageArchive100URL available")
        else:
            print(f"   ⚠️ No ImageArchive100URL found")
            
        return result
    else:
        print(f"❌ API connection failed: {result.error}")
        return None


if __name__ == "__main__":
    async def main():
        # Test the real API connection first
        await test_real_api_connection()
        
        print("\n" + "=" * 70)
        
        # Run other examples
        await example_basic_usage()
        await example_complete_workflow()
        await example_error_handling()
        await example_configuration_options()
        
        print("\n🎉 All examples completed!")
        print("\n💡 Next steps:")
        print("   1. ✅ API credentials are configured (SMS-Access-Key)")
        print("   2. ✅ Document ID is set to your example")
        print("   3. 🔄 Try running with extract_images=True to get the full workflow")
        print("   4. 🎯 Use different document IDs from your Science Made Simple system")
    
    asyncio.run(main()) 