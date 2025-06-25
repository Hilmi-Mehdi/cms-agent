#!/usr/bin/env python3
"""
Quick Reference: Science Made Simple API Integration

This is a minimal example showing exactly how to use the DocumentFetcherTool
with your Science Made Simple API credentials.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.base_tool import tool_registry


async def fetch_and_analyze_document():
    """Simple workflow: Fetch document → Extract images → Analyze slides."""
    
    print("🚀 Science Made Simple API - Quick Example")
    print("=" * 60)
    
    # Your credentials and settings
    SMS_API_KEY = "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"
    DOCUMENT_ID = "ct13hjqcchrs715kgjl0"
    
    # Step 1: Fetch document and extract images
    print("📄 Step 1: Fetching document and extracting images...")
    
    fetcher = tool_registry.get_tool("documentfetcher")
    result = await fetcher.execute({
        "document_id": DOCUMENT_ID,
        "api_headers": {"SMS-Access-Key": SMS_API_KEY},
        "extract_images": True,
        "max_images": 25,
        "image_format_filter": ["jpg", "jpeg", "png"]
    })
    
    if not result.success:
        print(f"❌ Failed to fetch document: {result.error}")
        return None
    
    # Display document info
    doc = result.data["document_metadata"]
    print(f"✅ Document fetched: {doc.get('Name', 'Unknown')}")
    print(f"   📄 Pages: {doc.get('PageCount', 'N/A')}")
    print(f"   📝 Description: {doc.get('Desc', 'N/A')[:80]}...")
    
    # Check image extraction
    images = result.data.get("extracted_images", {})
    if images.get("status") == "success":
        image_count = images.get("image_count", 0)
        print(f"   🖼️  Images extracted: {image_count}")
        print(f"   📁 Formats found: {images.get('formats_found', [])}")
        
        if image_count > 0:
            # Step 2: Analyze the images as slides
            print("\n🔍 Step 2: Analyzing slides...")
            
            analyzer = tool_registry.get_tool("slideanalyzer")
            slide_result = await analyzer.execute({
                "slide_images": images["image_paths"],
                "analysis_depth": "comprehensive",
                "ai_provider": "openai",
                "target_audience": "intermediate"
            })
            
            if slide_result.success:
                print("✅ Slide analysis completed!")
                print(f"   📚 Course title: {slide_result.data.get('course_title', 'N/A')}")
                print(f"   🎯 Subject: {slide_result.data.get('subject_area', 'N/A')}")
                print(f"   📊 Difficulty: {slide_result.data.get('difficulty_level', 'N/A')}")
                
                # Return complete results
                return {
                    "document": result.data,
                    "analysis": slide_result.data,
                    "success": True
                }
            else:
                print(f"❌ Slide analysis failed: {slide_result.error}")
        else:
            print("⚠️ No images found to analyze")
    else:
        error_msg = images.get("error", "Unknown error")
        print(f"❌ Image extraction failed: {error_msg}")
    
    return {"document": result.data, "success": result.success}


async def simple_metadata_fetch():
    """Just fetch document metadata without image processing."""
    
    print("\n📋 Simple metadata fetch (no images)")
    print("-" * 40)
    
    fetcher = tool_registry.get_tool("documentfetcher")
    result = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},
        "extract_images": False  # Skip image processing
    })
    
    if result.success:
        doc = result.data["document_metadata"]
        print(f"✅ Document: {doc.get('Name', 'Unknown')}")
        print(f"   Status: {doc.get('Processing', {}).get('Status', 'N/A')}")
        print(f"   Hash: {doc.get('ContentHash', 'N/A')[:16]}...")
        
        # Show available URLs
        urls = doc.get('URLs', {})
        print(f"   Available URLs:")
        for url_type, url in urls.items():
            if url and url != "url":
                print(f"     • {url_type}: ✅")
            else:
                print(f"     • {url_type}: ❌")
        
        return doc
    else:
        print(f"❌ Failed: {result.error}")
        return None


if __name__ == "__main__":
    async def main():
        try:
            # Run full workflow
            full_result = await fetch_and_analyze_document()
            
            # Run simple metadata fetch
            metadata = await simple_metadata_fetch()
            
            print("\n" + "=" * 60)
            print("🎉 Example completed!")
            
            if full_result and full_result.get("success"):
                print("\n📋 Summary:")
                if "analysis" in full_result:
                    print(f"   ✅ Document processed and analyzed")
                    print(f"   ✅ Course title extracted")
                    print(f"   ✅ Content structure identified")
                else:
                    print(f"   ✅ Document fetched successfully")
                    print(f"   ⚠️ No images to analyze")
            else:
                print("\n⚠️ Check your credentials and document ID")
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("💡 Make sure the SMS agent system is properly set up")
    
    asyncio.run(main()) 