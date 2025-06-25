#!/usr/bin/env python3
"""
Test script demonstrating PDF analysis via API
"""

import requests
import json
from pathlib import Path

def test_pdf_analysis_api():
    """Test PDF analysis through the API endpoint."""
    
    # API endpoint
    base_url = "http://localhost:8000/api/v1"
    endpoint = f"{base_url}/analyze-slides"
    
    # Check if test PDF exists
    test_pdf = Path("test.pdf")
    if not test_pdf.exists():
        print("❌ No test.pdf found. Please place a PDF file named 'test.pdf' in the current directory.")
        return False
    
    print(f"📄 Testing PDF analysis with {test_pdf}")
    
    try:
        # Prepare the file for upload
        with open(test_pdf, 'rb') as pdf_file:
            files = {
                'slides': (test_pdf.name, pdf_file, 'application/pdf')
            }
            
            # Prepare form data
            data = {
                'ai_provider': 'google',  # or 'openai'
                'analysis_depth': 'detailed',
                'target_audience': 'general',
                'subject_area': 'auto-detect',
                'max_pdf_pages': 10  # Limit to first 10 pages for testing
            }
            
            print("🚀 Sending PDF to API for analysis...")
            response = requests.post(endpoint, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF analysis successful!")
            print(f"📊 Analysis results:")
            print(f"   - Document type: {result['course_data'].get('type_document', 'Unknown')}")
            print(f"   - Execution time: {result.get('execution_time', 'Unknown')} seconds")
            print(f"   - Images analyzed: {result.get('images_analyzed', 'Unknown')}")
            
            if 'course_title' in result['course_data']:
                print(f"   - Course title: {result['course_data']['course_title']}")
            
            if 'tags' in result['course_data']:
                tags = result['course_data']['tags'][:5]  # Show first 5 tags
                print(f"   - Tags: {', '.join(tags)}")
            
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return False

def test_image_analysis_api():
    """Test image analysis through the API endpoint (for comparison)."""
    
    # Look for any image files in current directory
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path('.').glob(f'*{ext}'))
    
    if not image_files:
        print("📷 No image files found for comparison test.")
        return True
    
    test_image = image_files[0]
    print(f"📷 Testing image analysis with {test_image}")
    
    # API endpoint
    base_url = "http://localhost:8000/api/v1"
    endpoint = f"{base_url}/analyze-slides"
    
    try:
        # Prepare the file for upload
        with open(test_image, 'rb') as img_file:
            files = {
                'slides': (test_image.name, img_file, 'image/jpeg')
            }
            
            # Prepare form data
            data = {
                'ai_provider': 'google',
                'analysis_depth': 'detailed',
                'target_audience': 'general',
                'subject_area': 'auto-detect'
            }
            
            print("🚀 Sending image to API for analysis...")
            response = requests.post(endpoint, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image analysis successful!")
            print(f"📊 Analysis results:")
            print(f"   - Document type: {result['course_data'].get('type_document', 'Unknown')}")
            print(f"   - Execution time: {result.get('execution_time', 'Unknown')} seconds")
            return True
        else:
            print(f"❌ Image API request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during image API test: {e}")
        return False

if __name__ == "__main__":
    print("=== PDF API Test ===")
    print("This script tests the PDF analysis functionality via the API.")
    print("Make sure the server is running: python -m uvicorn app.main:app --reload")
    print()
    
    success = True
    success &= test_pdf_analysis_api()
    print()
    success &= test_image_analysis_api()
    
    if success:
        print("\n🎉 All API tests completed!")
    else:
        print("\n❌ Some API tests failed.") 