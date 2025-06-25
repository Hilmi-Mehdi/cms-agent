#!/usr/bin/env python3
"""
Performance comparison test for PDF processing:
PyMuPDF vs pdf2image
"""

import time
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

def test_pymupdf_performance():
    """Test PyMuPDF performance."""
    print("=== Testing PyMuPDF Performance ===")
    
    try:
        import fitz
        from utils.pdf_processor import pdf_processor
        
        # Look for PDF files to test
        pdf_files = list(Path('.').glob('*.pdf'))
        if not pdf_files:
            print("📄 No PDF files found for testing.")
            print("   Create a test PDF or place one in the current directory.")
            return
        
        test_pdf = pdf_files[0]
        print(f"📄 Testing with: {test_pdf}")
        
        # Get PDF info first
        info = pdf_processor.get_pdf_info(test_pdf)
        print(f"📊 PDF Info:")
        print(f"   - Pages: {info['page_count']}")
        print(f"   - Encrypted: {info['is_encrypted']}")
        
        # Test conversion with different page limits
        test_cases = [5, 10, 20] if info['page_count'] > 20 else [min(info['page_count'], 5)]
        
        for max_pages in test_cases:
            print(f"\n🚀 Converting {max_pages} pages with PyMuPDF...")
            
            start_time = time.time()
            images = pdf_processor.pdf_to_images(test_pdf, dpi=200, max_pages=max_pages)
            end_time = time.time()
            
            duration = end_time - start_time
            pages_per_second = max_pages / duration if duration > 0 else 0
            
            print(f"✅ PyMuPDF Results:")
            print(f"   - Time: {duration:.2f} seconds")
            print(f"   - Speed: {pages_per_second:.1f} pages/second")
            print(f"   - Images generated: {len(images)}")
            print(f"   - Average image size: {sum(len(img) for img in images) / len(images) / 1024:.1f} KB")
        
    except ImportError as e:
        print(f"❌ PyMuPDF not available: {e}")
    except Exception as e:
        print(f"❌ PyMuPDF test failed: {e}")

def test_pdf2image_performance():
    """Test pdf2image performance for comparison."""
    print("\n=== Testing pdf2image Performance (for comparison) ===")
    
    try:
        from pdf2image import convert_from_path
        import io
        
        # Look for PDF files to test
        pdf_files = list(Path('.').glob('*.pdf'))
        if not pdf_files:
            print("📄 No PDF files found for testing.")
            return
        
        test_pdf = pdf_files[0]
        print(f"📄 Testing with: {test_pdf}")
        
        # Test conversion with same parameters as PyMuPDF
        test_cases = [5, 10]  # Smaller test cases since pdf2image is slower
        
        for max_pages in test_cases:
            print(f"\n🐌 Converting {max_pages} pages with pdf2image...")
            
            start_time = time.time()
            pil_images = convert_from_path(test_pdf, dpi=200, last_page=max_pages)
            
            # Convert to bytes (same as PyMuPDF output)
            images = []
            for pil_img in pil_images:
                img_bytes = io.BytesIO()
                pil_img.save(img_bytes, format='PNG')
                images.append(img_bytes.getvalue())
            
            end_time = time.time()
            
            duration = end_time - start_time
            pages_per_second = max_pages / duration if duration > 0 else 0
            
            print(f"✅ pdf2image Results:")
            print(f"   - Time: {duration:.2f} seconds")
            print(f"   - Speed: {pages_per_second:.1f} pages/second")
            print(f"   - Images generated: {len(images)}")
            print(f"   - Average image size: {sum(len(img) for img in images) / len(images) / 1024:.1f} KB")
        
    except ImportError:
        print("📦 pdf2image not installed (expected with new setup)")
    except Exception as e:
        print(f"❌ pdf2image test failed: {e}")

def create_sample_pdf():
    """Create a sample PDF for testing if none exists."""
    try:
        import fitz
        
        print("📝 Creating sample PDF for testing...")
        
        # Create a new PDF
        doc = fitz.open()
        
        # Add 10 pages with some content
        for i in range(10):
            page = doc.new_page()
            text = f"""
            Sample PDF Page {i + 1}
            
            This is a test page for performance comparison.
            
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam, quis nostrud exercitation ullamco.
            
            Page created for PyMuPDF vs pdf2image performance testing.
            
            Current page: {i + 1} of 10
            """
            
            # Insert text
            page.insert_text((50, 100), text, fontsize=12)
            
            # Add some shapes for visual content
            page.draw_rect(fitz.Rect(50, 200, 200, 250), color=(0, 0, 1), fill=(0.8, 0.8, 1))
            page.draw_circle(fitz.Point(300, 300), 50, color=(1, 0, 0), fill=(1, 0.8, 0.8))
        
        # Save the PDF
        doc.save("sample_test.pdf")
        doc.close()
        
        print("✅ Created sample_test.pdf with 10 pages")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample PDF: {e}")
        return False

if __name__ == "__main__":
    print("🏁 PDF Processing Performance Comparison")
    print("=" * 50)
    
    # Check if we have PDFs to test with
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("📄 No PDF files found. Creating sample PDF...")
        if not create_sample_pdf():
            print("❌ Cannot create sample PDF. Please add a PDF file to test.")
            sys.exit(1)
    
    # Run performance tests
    test_pymupdf_performance()
    test_pdf2image_performance()
    
    print("\n🎯 Performance Summary:")
    print("PyMuPDF is typically 5-10x faster than pdf2image")
    print("- No external dependencies (poppler)")
    print("- Better memory management")
    print("- Direct C++ rendering")
    print("- Native Python bindings")
    
    print("\n💡 Recommendation: Use PyMuPDF for production PDF processing") 