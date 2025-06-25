#!/usr/bin/env python3
"""
Test slide analyzer with PDF using PyMuPDF
"""

import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.append('app')

from tools.slide_analyzer import SlideAnalyzerTool

async def test_pdf_analysis():
    """Test slide analyzer with PDF file."""
    print("=== Testing Slide Analyzer with PDF ===")
    
    # Check if we have a PDF to test with
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No PDF files found for testing")
        return
    
    test_pdf = str(pdf_files[0])
    print(f"📄 Testing with: {test_pdf}")
    
    tool = SlideAnalyzerTool()
    
    try:
        result = await tool.execute({
            'slide_images': [test_pdf],
            'ai_provider': 'google',
            'analysis_depth': 'basic',
            'max_pdf_pages': 3
        })
        
        print(f"✅ Analysis completed successfully: {result.success}")
        
        if result.success:
            data = result.data
            print(f"📊 Results:")
            print(f"   - Document type: {data.get('type_document', 'Unknown')}")
            print(f"   - Execution time: {result.execution_time}s")
            
            metadata = data.get('analysis_metadata', {})
            print(f"   - Images analyzed: {metadata.get('images_analyzed', 0)}")
            print(f"   - Provider: {metadata.get('provider', 'Unknown')}")
            print(f"   - Model: {metadata.get('model', 'Unknown')}")
            
            # Show some content
            if data.get('type_document') == 'courses':
                print(f"   - Course title: {data.get('course_title', 'N/A')}")
            elif data.get('type_document') == 'autre':
                print(f"   - Content description: {data.get('description_contenu', 'N/A')[:100]}...")
        else:
            print(f"❌ Analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_pdf_analysis()) 