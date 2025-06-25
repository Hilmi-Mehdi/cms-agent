#!/usr/bin/env python3
"""
Test script for PDF processing functionality with PyMuPDF
"""

import sys
import json
import time
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from utils.pdf_processor import pdf_processor, PDF_SUPPORT_AVAILABLE

def test_pdf_support():
    """Test PDF processing capabilities with PyMuPDF."""
    print("=== PDF Support Test (PyMuPDF) ===")
    
    if not PDF_SUPPORT_AVAILABLE:
        print("❌ PDF support not available. Install with: pip install PyMuPDF")
        return False
    
    print("✅ PDF support is available (PyMuPDF)")
    print(f"PDF Processor: {pdf_processor}")
    
    # Test with a sample PDF if available
    test_pdf_path = Path("test.pdf")
    if test_pdf_path.exists():
        print(f"\n📄 Testing with {test_pdf_path}")
        
        try:
            # Validate PDF
            is_valid = pdf_processor.validate_pdf(test_pdf_path)
            print(f"PDF validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            if is_valid:
                # Get PDF info (replaces get_pdf_page_count)
                info = pdf_processor.get_pdf_info(test_pdf_path)
                print(f"PDF Info:")
                print(f"  - Pages: {info['page_count']}")
                print(f"  - Encrypted: {info['is_encrypted']}")
                print(f"  - Title: {info['metadata'].get('title', 'No title')}")
                
                # Test performance with different DPI settings
                page_count = info['page_count']
                max_pages = min(3, page_count)
                
                for dpi in [150, 200, 300]:
                    print(f"\n🔄 Converting {max_pages} pages at {dpi} DPI...")
                    start_time = time.time()
                    images = pdf_processor.pdf_to_images(test_pdf_path, dpi=dpi, max_pages=max_pages)
                    end_time = time.time()
                    
                    duration = end_time - start_time
                    print(f"✅ Converted {len(images)} pages in {duration:.2f}s")
                    
                    for i, img_bytes in enumerate(images):
                        size_kb = len(img_bytes) / 1024
                        print(f"  Page {i+1}: {size_kb:.1f} KB")
                
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return False
    else:
        print(f"\n📄 No test PDF found at {test_pdf_path}")
        print("To test with a real PDF, place a PDF file named 'test.pdf' in the current directory")
        
        # Try to create a sample PDF for testing
        try:
            print("\n📝 Creating sample PDF for testing...")
            import fitz
            
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 100), "Sample PDF for testing PyMuPDF performance", fontsize=16)
            page.insert_text((50, 150), "This PDF was created automatically for testing.", fontsize=12)
            doc.save("test_sample.pdf")
            doc.close()
            
            print("✅ Created test_sample.pdf")
            
            # Test with the created PDF
            info = pdf_processor.get_pdf_info("test_sample.pdf")
            images = pdf_processor.pdf_to_images("test_sample.pdf", dpi=200, max_pages=1)
            print(f"✅ Successfully processed sample PDF: {len(images)} images")
            
        except Exception as e:
            print(f"⚠️  Could not create sample PDF: {e}")
    
    return True

def test_slide_analyzer_with_pdf():
    """Test SlideAnalyzerTool with PDF support."""
    print("\n=== Slide Analyzer PDF Test ===")
    
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from app.tools.slide_analyzer import SlideAnalyzerTool
        
        tool = SlideAnalyzerTool()
        definition = tool.get_definition()
        
        print(f"Tool name: {definition.name}")
        print(f"Description: {definition.description}")
        
        # Check if PDF support is mentioned in description
        if "PDF" in definition.description:
            print("✅ PDF support is advertised in tool description")
        else:
            print("❌ PDF support not mentioned in tool description")
        
        # Check for max_pdf_pages parameter
        pdf_param = None
        for param in definition.parameters:
            if param.name == "max_pdf_pages":
                pdf_param = param
                break
        
        if pdf_param:
            print(f"✅ max_pdf_pages parameter found: {pdf_param.description}")
        else:
            print("❌ max_pdf_pages parameter not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SlideAnalyzerTool: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDF support for SMS-Agent...")
    
    success = True
    success &= test_pdf_support()
    success &= test_slide_analyzer_with_pdf()
    
    if success:
        print("\n🎉 All tests passed! PDF support is ready.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    sys.exit(0 if success else 1) 