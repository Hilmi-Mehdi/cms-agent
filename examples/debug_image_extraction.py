#!/usr/bin/env python3
"""
Debug: Image Extraction from Science Made Simple API

This script investigates why no images were extracted from the tar file.
"""

import asyncio
import sys
import tempfile
import tarfile
import httpx
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.base_tool import tool_registry


async def debug_image_extraction():
    """Debug the image extraction process step by step."""
    
    print("🔍 Debug: Image Extraction Process")
    print("=" * 50)
    
    # Step 1: Get document metadata
    fetcher = tool_registry.get_tool("documentfetcher")
    result = await fetcher.execute({
        "document_id": "ct13hjqcchrs715kgjl0",
        "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},
        "extract_images": False  # Don't extract yet, just get metadata
    })
    
    if not result.success:
        print(f"❌ Failed to fetch document: {result.error}")
        return
    
    doc = result.data["document_metadata"]
    urls = doc.get("URLs", {})
    image_archive_url = urls.get("ImageArchive100URL")
    
    print(f"📄 Document: {doc.get('Name', 'Unknown')}")
    print(f"🔗 ImageArchive100URL: {image_archive_url}")
    
    if not image_archive_url or image_archive_url == "url":
        print("❌ No valid ImageArchive100URL found")
        return
    
    # Step 2: Download and inspect the tar file
    print("\n📥 Downloading tar file...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(image_archive_url)
            response.raise_for_status()
            
            print(f"✅ Downloaded {len(response.content)} bytes")
            
            # Save to temporary file and inspect
            with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Inspect tar file contents
            print("\n📋 Tar file contents:")
            with tarfile.open(temp_file_path, "r") as tar:
                members = tar.getmembers()
                print(f"   Total files: {len(members)}")
                
                for i, member in enumerate(members[:10]):  # Show first 10 files
                    file_type = "DIR" if member.isdir() else "FILE"
                    size = f"{member.size} bytes" if member.isfile() else ""
                    print(f"   {i+1}. [{file_type}] {member.name} {size}")
                
                if len(members) > 10:
                    print(f"   ... and {len(members) - 10} more files")
                
                # Check for image files specifically
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
                image_files = []
                
                for member in members:
                    if member.isfile():
                        file_path = Path(member.name)
                        if file_path.suffix.lower() in image_extensions:
                            image_files.append({
                                "name": member.name,
                                "size": member.size,
                                "extension": file_path.suffix.lower()
                            })
                
                print(f"\n🖼️  Image files found: {len(image_files)}")
                for img in image_files[:5]:  # Show first 5 images
                    print(f"   • {img['name']} ({img['extension']}, {img['size']} bytes)")
                
                if len(image_files) > 5:
                    print(f"   ... and {len(image_files) - 5} more images")
                
                # Try actual extraction
                if image_files:
                    print(f"\n📂 Extracting images...")
                    
                    with tempfile.TemporaryDirectory() as extract_dir:
                        tar.extractall(extract_dir)
                        extract_path = Path(extract_dir)
                        
                        extracted_images = []
                        for file_path in extract_path.rglob("*"):
                            if file_path.is_file():
                                file_extension = file_path.suffix.lower().lstrip(".")
                                if file_extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
                                    extracted_images.append({
                                        "path": str(file_path),
                                        "name": file_path.name,
                                        "size": file_path.stat().st_size,
                                        "extension": file_extension
                                    })
                        
                        print(f"✅ Successfully extracted: {len(extracted_images)} images")
                        for img in extracted_images[:3]:
                            print(f"   • {img['name']} ({img['extension']}, {img['size']} bytes)")
                else:
                    print("⚠️ No image files found in tar archive")
            
            # Clean up
            Path(temp_file_path).unlink()
            
    except Exception as e:
        print(f"❌ Error during download/extraction: {str(e)}")


async def test_with_different_formats():
    """Test extraction with different image format filters."""
    
    print(f"\n🎯 Testing different image format filters")
    print("=" * 50)
    
    fetcher = tool_registry.get_tool("documentfetcher")
    
    # Test with comprehensive format list
    formats_to_test = [
        ["jpg", "jpeg", "png"],
        ["jpg", "jpeg", "png", "gif", "bmp"],
        ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"],
        ["png", "jpg"],
        []  # Default (all formats)
    ]
    
    for i, formats in enumerate(formats_to_test):
        print(f"\nTest {i+1}: {formats if formats else 'All formats'}")
        
        result = await fetcher.execute({
            "document_id": "ct13hjqcchrs715kgjl0",
            "api_headers": {"SMS-Access-Key": "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5"},
            "extract_images": True,
            "max_images": 50,
            "image_format_filter": formats if formats else None
        })
        
        if result.success:
            images = result.data.get("extracted_images", {})
            if images.get("status") == "success":
                print(f"   ✅ Extracted: {images.get('image_count', 0)} images")
                print(f"   📁 Formats found: {images.get('formats_found', [])}")
            else:
                print(f"   ❌ Extraction failed: {images.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Tool failed: {result.error}")


if __name__ == "__main__":
    async def main():
        await debug_image_extraction()
        await test_with_different_formats()
        
        print("\n" + "=" * 50)
        print("🔍 Debug completed!")
        print("\n💡 If no images are found:")
        print("   1. The tar file might contain images in different formats")
        print("   2. The tar file might be empty")
        print("   3. Images might be in subdirectories with different extensions")
        print("   4. The tar file might be compressed differently")
    
    asyncio.run(main()) 