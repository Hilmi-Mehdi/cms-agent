#!/usr/bin/env python3
"""
Maximum Quality Extraction Test - Get complete question data without truncation
"""

import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.append('app')

from tools.slide_analyzer import SlideAnalyzerTool
from utils.pdf_processor import pdf_processor

async def test_maximum_quality_extraction(pdf_path: str):
    """Test with maximum quality settings for complete question extraction."""
    print("🔍 Maximum Quality Extraction Test")
    print("=" * 50)
    print(f"📄 Processing: {pdf_path}")
    
    # Test with ultra-high quality settings
    tool = SlideAnalyzerTool()
    
    print("\n🚀 Using MAXIMUM quality settings:")
    print("   - DPI: 350 (ultra-high)")
    print("   - Analysis: comprehensive")
    print("   - Provider: Google AI")
    print("   - Audience: advanced")
    print("   - Small batches: 5 pages max")
    
    try:
        result = await tool.execute({
            'slide_images': [pdf_path],
            'ai_provider': 'google',           # Best for French text
            'analysis_depth': 'comprehensive', # Maximum analysis depth
            'target_audience': 'advanced',     # Most detailed analysis
            'max_pdf_pages': 5,               # Small batches for quality
        })
        
        if result.success:
            data = result.data
            print(f"\n✅ Analysis completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time}s")
            print(f"📋 Document type: {data.get('type_document', 'Unknown')}")
            
            # Detailed analysis of questions
            if data.get('type_document') in ['examen', 'serie_exercices']:
                exercises = data.get('exercices', [])
                tags = data.get('tags', [])
                learning_path = data.get('learning_path', [])
                
                print(f"\n📝 Complete Document Analysis:")
                print(f"   Total exercises found: {len(exercises)}")
                print(f"   Tags: {', '.join(tags) if tags else 'Aucun tag'}")
                print(f"   Learning modules: {len(learning_path)}")
                
                # Show learning path details
                if learning_path:
                    print(f"\n🎯 Learning Path / Prerequisites:")
                    for j, module in enumerate(learning_path):
                        print(f"   Module {j+1}: {module.get('module_name', 'N/A')}")
                        print(f"     Prerequisites: {', '.join(module.get('prerequisites', []))}")
                        print(f"     Topics: {', '.join(module.get('topics', []))}")
                        print(f"     Difficulty: {module.get('difficulty', 'N/A')}")
                
                for i, exercise in enumerate(exercises):
                    print(f"\n{'='*60}")
                    print(f"📚 EXERCISE {i+1}")
                    print(f"{'='*60}")
                    
                    # Exercise details
                    ex_id = exercise.get('id_exercice_ou_titre', 'N/A')
                    ex_statement = exercise.get('enonce_exercice', 'N/A')
                    
                    print(f"🏷️  ID/Title: {ex_id}")
                    print(f"📄 Statement: {ex_statement}")
                    
                    # Questions analysis
                    questions = exercise.get('questions', [])
                    print(f"\n❓ Questions: {len(questions)} found")
                    
                    for j, question in enumerate(questions):
                        print(f"\n   {'─'*40}")
                        print(f"   📝 QUESTION {j+1}")
                        print(f"   {'─'*40}")
                        
                        q_id = question.get('id_question_ou_numero', 'N/A')
                        q_text = question.get('texte_question', 'N/A')
                        q_options = question.get('options_reponse', [])
                        q_type = question.get('type_reponse_attendu', 'N/A')
                        
                        print(f"   🏷️  ID: {q_id}")
                        print(f"   📝 Text: {q_text}")
                        print(f"   📊 Type: {q_type}")
                        
                        if q_options:
                            print(f"   🔘 Options ({len(q_options)}):")
                            for k, option in enumerate(q_options):
                                print(f"      {chr(65+k)}. {option}")
                        
                        # Check for completeness
                        if len(q_text) < 50:
                            print(f"   ⚠️  WARNING: Question seems short ({len(q_text)} chars)")
                        elif "..." in q_text or q_text.endswith('.'):
                            print(f"   ⚠️  WARNING: Possible truncation detected")
                        else:
                            print(f"   ✅ Question appears complete ({len(q_text)} chars)")
                
                # Overall completeness check
                print(f"\n{'='*60}")
                print(f"📊 COMPLETENESS ANALYSIS")
                print(f"{'='*60}")
                
                total_questions = sum(len(ex.get('questions', [])) for ex in exercises)
                short_questions = 0
                truncated_questions = 0
                
                for exercise in exercises:
                    for question in exercise.get('questions', []):
                        q_text = question.get('texte_question', '')
                        if len(q_text) < 50:
                            short_questions += 1
                        if "..." in q_text:
                            truncated_questions += 1
                
                print(f"📈 Total questions: {total_questions}")
                print(f"⚠️  Short questions (<50 chars): {short_questions}")
                print(f"⚠️  Possibly truncated: {truncated_questions}")
                
                completeness_rate = ((total_questions - short_questions - truncated_questions) / total_questions * 100) if total_questions > 0 else 0
                print(f"✅ Completeness rate: {completeness_rate:.1f}%")
                
                if completeness_rate < 90:
                    print(f"\n💡 RECOMMENDATIONS FOR IMPROVEMENT:")
                    print(f"   1. Try even higher DPI (400-450)")
                    print(f"   2. Process fewer pages at once (2-3)")
                    print(f"   3. Check if PDF is scanned vs digital")
                    print(f"   4. Consider manual preprocessing")
                else:
                    print(f"\n🎉 Excellent extraction quality!")
            
        else:
            print(f"❌ Analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def test_ultra_high_dpi(pdf_path: str):
    """Test with ultra-high DPI for maximum text clarity."""
    print(f"\n🔬 Ultra-High DPI Test")
    print("=" * 30)
    
    try:
        # Convert with ultra-high DPI
        print("🚀 Converting with DPI 400 for maximum clarity...")
        images = pdf_processor.pdf_to_images(pdf_path, dpi=400, max_pages=3)
        
        print(f"✅ Converted {len(images)} pages")
        avg_size = sum(len(img) for img in images) / len(images) / 1024
        print(f"📏 Average image size: {avg_size:.1f} KB")
        
        # Save images temporarily and analyze
        import tempfile
        temp_images = []
        
        for i, img_bytes in enumerate(images):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_ultra_dpi_page_{i+1}.png')
            temp_file.write(img_bytes)
            temp_file.close()
            temp_images.append(temp_file.name)
        
        # Analyze with slide analyzer
        tool = SlideAnalyzerTool()
        result = await tool.execute({
            'slide_images': temp_images,
            'ai_provider': 'google',
            'analysis_depth': 'comprehensive',
            'target_audience': 'advanced',
        })
        
        # Clean up temp files
        for temp_file in temp_images:
            try:
                Path(temp_file).unlink()
            except:
                pass
        
        if result.success:
            data = result.data
            print(f"✅ Ultra-high DPI analysis completed")
            
            if data.get('type_document') in ['examen', 'serie_exercices']:
                exercises = data.get('exercices', [])
                total_questions = sum(len(ex.get('questions', [])) for ex in exercises)
                
                print(f"📊 Results with DPI 400:")
                print(f"   - Exercises: {len(exercises)}")
                print(f"   - Questions: {total_questions}")
                
                # Show first question in detail
                if exercises and exercises[0].get('questions'):
                    first_q = exercises[0]['questions'][0]
                    q_text = first_q.get('texte_question', '')
                    print(f"   - First question length: {len(q_text)} characters")
                    print(f"   - Sample: {q_text[:200]}{'...' if len(q_text) > 200 else ''}")
        else:
            print(f"❌ Ultra-high DPI analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Ultra-high DPI test failed: {e}")

async def main():
    """Run maximum quality extraction tests."""
    print("🎯 Maximum Quality Extraction for Complete Questions")
    print("=" * 60)
    
    # Find PDF files
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No PDF files found. Place your exam PDF in the current directory.")
        return
    
    test_pdf = str(pdf_files[0])
    
    # Run tests
    await test_maximum_quality_extraction(test_pdf)
    await test_ultra_high_dpi(test_pdf)
    
    print(f"\n💡 FOR COMPLETE QUESTION EXTRACTION:")
    print("1. Use 'comprehensive' analysis depth")
    print("2. Process 3-5 pages at a time maximum")
    print("3. Use Google AI provider")
    print("4. Set target_audience to 'advanced'")
    print("5. Consider DPI 350-400 for complex questions")

if __name__ == "__main__":
    asyncio.run(main()) 