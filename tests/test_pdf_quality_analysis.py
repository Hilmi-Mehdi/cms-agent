#!/usr/bin/env python3
"""
PDF Quality Analysis Tool - Diagnose and optimize PDF processing for better exercise extraction
"""

import sys
import asyncio
import time
from pathlib import Path

# Add the app directory to the path
sys.path.append('app')

from utils.pdf_processor import pdf_processor
from tools.slide_analyzer import SlideAnalyzerTool

async def test_pdf_quality_settings(pdf_path: str):
    """Test different DPI settings to find optimal quality for exercise extraction."""
    print("=== PDF Quality Analysis for Exercise Extraction ===")
    print(f"📄 Testing PDF: {pdf_path}")
    
    # Test different DPI settings
    dpi_settings = [150, 200, 250, 300, 400]
    
    for dpi in dpi_settings:
        print(f"\n🔍 Testing DPI: {dpi}")
        print("-" * 40)
        
        try:
            # Convert PDF with specific DPI
            start_time = time.time()
            images = pdf_processor.pdf_to_images(pdf_path, dpi=dpi, max_pages=3)
            conversion_time = time.time() - start_time
            
            print(f"✅ Conversion completed in {conversion_time:.2f}s")
            print(f"📊 Generated {len(images)} images")
            
            # Calculate average image size
            avg_size_kb = sum(len(img) for img in images) / len(images) / 1024
            print(f"📏 Average image size: {avg_size_kb:.1f} KB")
            
            # Test with slide analyzer
            tool = SlideAnalyzerTool()
            
            # Use a temporary file approach to avoid modifying the original
            import tempfile
            temp_images = []
            
            for i, img_bytes in enumerate(images):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_page_{i+1}_dpi_{dpi}.png')
                temp_file.write(img_bytes)
                temp_file.close()
                temp_images.append(temp_file.name)
            
            # Analyze with slide analyzer
            analysis_start = time.time()
            result = await tool.execute({
                'slide_images': temp_images,
                'ai_provider': 'google',
                'analysis_depth': 'comprehensive',
                'max_pdf_pages': 3
            })
            analysis_time = time.time() - analysis_start
            
            # Clean up temp files
            for temp_file in temp_images:
                try:
                    Path(temp_file).unlink()
                except:
                    pass
            
            if result.success:
                data = result.data
                print(f"🎯 Analysis completed in {analysis_time:.2f}s")
                print(f"📋 Document type: {data.get('type_document', 'Unknown')}")
                
                # Count exercises and questions
                if data.get('type_document') == 'examen':
                    exercises = data.get('exercices', [])
                    total_questions = sum(len(ex.get('questions', [])) for ex in exercises)
                    print(f"📝 Exercises found: {len(exercises)}")
                    print(f"❓ Total questions: {total_questions}")
                    
                    # Show exercise details
                    for i, exercise in enumerate(exercises[:2]):  # Show first 2 exercises
                        print(f"   Exercise {i+1}: {exercise.get('id_exercice_ou_titre', 'N/A')}")
                        print(f"   Questions: {len(exercise.get('questions', []))}")
                        
                        # Show first question if available
                        questions = exercise.get('questions', [])
                        if questions:
                            first_q = questions[0]
                            question_text = first_q.get('texte_question', 'N/A')
                            print(f"   First Q: {question_text[:100]}{'...' if len(question_text) > 100 else ''}")
                
                elif data.get('type_document') == 'serie_exercices':
                    exercises = data.get('exercices', [])
                    total_questions = sum(len(ex.get('questions', [])) for ex in exercises)
                    print(f"📝 Exercises found: {len(exercises)}")
                    print(f"❓ Total questions: {total_questions}")
                
                # Check for completeness indicators
                analysis_text = result.data.get('analysis_metadata', {}).get('usage_stats', {})
                print(f"📊 Token usage: {analysis_text}")
                
            else:
                print(f"❌ Analysis failed: {result.error}")
                
        except Exception as e:
            print(f"❌ Error at DPI {dpi}: {e}")
    
    print(f"\n🎯 Recommendation:")
    print("- DPI 300+ for detailed text extraction")
    print("- DPI 200-250 for balanced speed/quality")
    print("- DPI 150 for quick previews only")

async def analyze_pdf_structure(pdf_path: str):
    """Analyze PDF structure to understand layout complexity."""
    print(f"\n=== PDF Structure Analysis ===")
    
    try:
        # Get PDF info
        info = pdf_processor.get_pdf_info(pdf_path)
        print(f"📊 PDF Information:")
        print(f"   - Total pages: {info['page_count']}")
        print(f"   - Encrypted: {info['is_encrypted']}")
        print(f"   - Title: {info['metadata'].get('title', 'No title')}")
        
        # Analyze page sizes
        page_sizes = info.get('page_sizes', [])
        if page_sizes:
            print(f"📏 Page dimensions:")
            for page_info in page_sizes:
                width = page_info['width']
                height = page_info['height']
                aspect_ratio = width / height if height > 0 else 0
                print(f"   Page {page_info['page']}: {width:.0f}x{height:.0f} (ratio: {aspect_ratio:.2f})")
        
        # Test with different page ranges
        print(f"\n🔍 Testing different page ranges:")
        
        page_ranges = [
            (1, 2),   # First 2 pages
            (3, 5),   # Middle pages
            (-2, -1)  # Last 2 pages (if enough pages)
        ]
        
        for start, end in page_ranges:
            if info['page_count'] >= abs(end):
                actual_start = start if start > 0 else info['page_count'] + start + 1
                actual_end = end if end > 0 else info['page_count'] + end + 1
                max_pages = actual_end - actual_start + 1
                
                print(f"   Pages {actual_start}-{actual_end}:")
                
                try:
                    images = pdf_processor.pdf_to_images(pdf_path, dpi=250, max_pages=max_pages)
                    avg_size = sum(len(img) for img in images) / len(images) / 1024
                    print(f"     ✅ {len(images)} images, avg {avg_size:.1f} KB")
                except Exception as e:
                    print(f"     ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Structure analysis failed: {e}")

async def test_comprehensive_extraction(pdf_path: str):
    """Test comprehensive extraction with optimal settings."""
    print(f"\n=== Comprehensive Extraction Test ===")
    
    try:
        # Use high DPI for maximum detail
        print("🔍 Using DPI 300 for maximum detail extraction...")
        
        tool = SlideAnalyzerTool()
        result = await tool.execute({
            'slide_images': [pdf_path],
            'ai_provider': 'google',
            'analysis_depth': 'comprehensive',  # Maximum depth
            'max_pdf_pages': 10,  # Process more pages
            'target_audience': 'advanced',  # More detailed analysis
        })
        
        if result.success:
            data = result.data
            print(f"✅ Comprehensive analysis completed")
            print(f"⏱️  Execution time: {result.execution_time}s")
            
            # Detailed exercise analysis
            if data.get('type_document') in ['examen', 'serie_exercices']:
                exercises = data.get('exercices', [])
                print(f"\n📝 Detailed Exercise Analysis:")
                print(f"   Total exercises: {len(exercises)}")
                
                for i, exercise in enumerate(exercises):
                    print(f"\n   Exercise {i+1}:")
                    print(f"     ID/Title: {exercise.get('id_exercice_ou_titre', 'N/A')}")
                    print(f"     Statement: {exercise.get('enonce_exercice', 'N/A')[:150]}...")
                    
                    questions = exercise.get('questions', [])
                    print(f"     Questions: {len(questions)}")
                    
                    for j, question in enumerate(questions[:3]):  # Show first 3 questions
                        q_text = question.get('texte_question', 'N/A')
                        print(f"       Q{j+1}: {q_text[:100]}{'...' if len(q_text) > 100 else ''}")
                        
                        options = question.get('options_reponse', [])
                        if options:
                            print(f"            Options: {len(options)} choices")
                
                # Check for incomplete extractions
                incomplete_exercises = []
                for i, exercise in enumerate(exercises):
                    questions = exercise.get('questions', [])
                    if not questions or any(not q.get('texte_question') for q in questions):
                        incomplete_exercises.append(i + 1)
                
                if incomplete_exercises:
                    print(f"\n⚠️  Potentially incomplete exercises: {incomplete_exercises}")
                    print("   This suggests image quality or layout complexity issues")
                else:
                    print(f"\n✅ All exercises appear complete")
            
        else:
            print(f"❌ Comprehensive analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")

async def main():
    """Run PDF quality analysis."""
    print("🔍 PDF Quality Analysis for Exercise Extraction")
    print("=" * 60)
    
    # Find PDF files
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No PDF files found. Place an exam PDF in the current directory.")
        return
    
    test_pdf = str(pdf_files[0])
    print(f"📄 Analyzing: {test_pdf}")
    
    # Run all tests
    await analyze_pdf_structure(test_pdf)
    await test_pdf_quality_settings(test_pdf)
    await test_comprehensive_extraction(test_pdf)
    
    print(f"\n💡 Recommendations for better exercise extraction:")
    print("1. Use DPI 300+ for exams with small text")
    print("2. Ensure PDF pages are not scanned at low resolution")
    print("3. Use 'comprehensive' analysis depth")
    print("4. Process fewer pages at a time for complex layouts")
    print("5. Check if PDF has text layers (not just images)")

if __name__ == "__main__":
    asyncio.run(main()) 