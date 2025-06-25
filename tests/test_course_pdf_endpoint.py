#!/usr/bin/env python3
"""
Test script for the /find-course-pdfs endpoint
"""

import requests
import json

def test_course_pdf_endpoint():
    """Test the course PDF finder endpoint."""
    
    # Base URL (adjust if needed)
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Course PDF Finder Endpoint")
    print("=" * 50)
    
    # Test 1: Basic search without download
    print("\n🔍 Test 1: Finding course PDFs (no download)")
    print("-" * 40)
    
    data = {
        "course_topic": "machine learning",
        "course_level": "undergraduate",
        "institution_type": "university",
        "language": "en",
        "download_pdfs": False,
        "max_pdfs": 3
    }
    
    try:
        response = requests.post(f"{base_url}/find-course-pdfs", data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result.get('response', 'No response message')}")
            
            # Show found PDFs
            data_result = result.get('data', {})
            pdfs = data_result.get('pdfs', [])
            print(f"\n📚 Found {len(pdfs)} PDFs:")
            
            for i, pdf in enumerate(pdfs, 1):
                print(f"  {i}. {pdf.get('title', 'No title')}")
                print(f"     URL: {pdf.get('url', 'No URL')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Search with download
    print("\n📥 Test 2: Finding and downloading PDFs")
    print("-" * 40)
    
    data_download = {
        "course_topic": "calculus",
        "course_level": "undergraduate",
        "institution_type": "university",
        "language": "en",
        "download_pdfs": True,
        "download_location": "./test_downloads",
        "max_pdfs": 2
    }
    
    try:
        response = requests.post(f"{base_url}/find-course-pdfs", data=data_download)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result.get('response', 'No response message')}")
            
            # Show download results
            data_result = result.get('data', {})
            downloaded_files = data_result.get('downloaded_files', [])
            download_location = data_result.get('download_location', '')
            
            print(f"\n📁 Download location: {download_location}")
            print(f"📄 Downloaded {len(downloaded_files)} files:")
            
            for i, file_info in enumerate(downloaded_files, 1):
                print(f"  {i}. {file_info.get('title', 'No title')}")
                print(f"     Local: {file_info.get('local_path', 'No path')}")
                print(f"     Source: {file_info.get('url', 'No URL')}")
                print()
                
            # Show any errors
            errors = data_result.get('download_errors', [])
            if errors:
                print(f"⚠️  {len(errors)} download errors:")
                for error in errors:
                    print(f"  - {error.get('url', 'Unknown URL')}: {error.get('error', 'Unknown error')}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Course PDF Endpoint Test")
    test_course_pdf_endpoint()
    print("\n✅ Test completed!") 