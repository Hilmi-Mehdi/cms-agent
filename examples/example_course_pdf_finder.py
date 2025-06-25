#!/usr/bin/env python3
"""
Example script showing how to find and download course PDFs using the new OpenAI-powered endpoint.
"""

import requests
import json

# Base URL for your API (adjust as needed)
BASE_URL = "http://localhost:8000/api/v1"

def find_course_pdfs_example():
    """Example of finding course PDFs without downloading."""
    print("🔍 Example 1: Finding Course PDFs (No Download)")
    print("=" * 60)
    
    # Example 1: Find machine learning course PDFs
    data = {
        "course_topic": "machine learning",
        "course_level": "undergraduate", 
        "institution_type": "university",
        "language": "en",
        "download_pdfs": False,  # Just find, don't download
        "max_pdfs": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/find-course-pdfs", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['response']}")
            
            pdfs = result.get('data', {}).get('pdfs', [])
            print(f"\n📚 Found {len(pdfs)} PDFs:")
            
            for i, pdf in enumerate(pdfs, 1):
                print(f"  {i}. {pdf['title']}")
                print(f"     URL: {pdf['url']}")
                print()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def download_course_pdfs_example():
    """Example of finding and downloading course PDFs."""
    print("\n📥 Example 2: Finding & Downloading Course PDFs")
    print("=" * 60)
    
    # Example 2: Find and download quantum physics PDFs
    data = {
        "course_topic": "quantum physics",
        "course_level": "graduate",
        "institution_type": "university", 
        "language": "en",
        "download_pdfs": True,  # Download the PDFs
        "download_location": "./downloaded_courses",  # Custom download location
        "max_pdfs": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/find-course-pdfs", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['response']}")
            
            data_result = result.get('data', {})
            downloaded_files = data_result.get('downloaded_files', [])
            download_location = data_result.get('download_location', '')
            
            print(f"\n📁 Download location: {download_location}")
            print(f"📄 Downloaded {len(downloaded_files)} files:")
            
            for i, file in enumerate(downloaded_files, 1):
                print(f"  {i}. {file['title']}")
                print(f"     Local: {file['local_path']}")
                print(f"     Source: {file['url']}")
                print()
                
            # Show any download errors
            errors = data_result.get('download_errors', [])
            if errors:
                print(f"⚠️  {len(errors)} download errors:")
                for error in errors:
                    print(f"  - {error['url']}: {error['error']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def general_web_search_example():
    """Example using the general web search for broader course material search."""
    print("\n🌐 Example 3: General Web Search for Course Materials")
    print("=" * 60)
    
    data = {
        "search_query": "artificial intelligence course materials syllabus filetype:pdf",
        "language": "en",
        "context": "academic"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/general-web-search", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['response']}")
            
            data_result = result.get('data', {})
            search_results = data_result.get('search_results', [])
            answer = data_result.get('answer', '')
            
            print(f"\n🤖 AI Summary:")
            print(answer[:300] + "..." if len(answer) > 300 else answer)
            
            print(f"\n🔗 Found {len(search_results)} sources:")
            for i, source in enumerate(search_results[:3], 1):  # Show top 3
                print(f"  {i}. {source['title']}")
                print(f"     URL: {source['url']}")
                print(f"     Snippet: {source['snippet'][:100]}...")
                print()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("📚 Course PDF Finder Examples")
    print("Using OpenAI-powered web search to find course materials")
    print("=" * 70)
    
    # Run examples
    find_course_pdfs_example()
    download_course_pdfs_example()  
    general_web_search_example()
    
    print("\n" + "=" * 70)
    print("🎯 Summary of Available Endpoints:")
    print()
    print("1. 📚 /api/v1/find-course-pdfs")
    print("   - Specifically designed for finding course PDFs")
    print("   - Can download files automatically")
    print("   - Filters for academic sources (.edu, universities)")
    print()
    print("2. 🔍 /api/v1/general-web-search")
    print("   - General web search with AI-powered answers")
    print("   - Good for broad course material searches")
    print("   - Returns both search results and comprehensive answers")
    print()
    print("3. 🌊 /api/v1/search/openai-web-stream")
    print("   - Streaming search results")
    print("   - Real-time responses")
    print("   - Specialized for Belgian tax/finance (configurable)")
    print()
    print("💡 Tips:")
    print("- Use specific course topics for better results")
    print("- Try different course levels (undergraduate, graduate, advanced)")
    print("- Set download_pdfs=true to automatically download files")
    print("- Use custom download_location to organize files")