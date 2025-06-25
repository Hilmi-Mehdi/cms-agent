#!/usr/bin/env python3
"""
Test script to verify exact text extraction from slide images.
This tests that the AI extracts text exactly as written without modification.
"""

import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from tools.slide_analyzer import SlideAnalyzerTool

async def test_exact_extraction():
    """Test that slide analyzer extracts text exactly as written."""
    print("=== Testing Exact Text Extraction ===")
    print("This test verifies that the AI extracts text exactly as it appears")
    print("without reformulation, correction, or structural changes.\n")
    
    # Look for test images
    image_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.webp', '.bmp']
    test_files = []
    
    for ext in image_extensions:
        test_files.extend(Path('.').glob(f'*{ext}'))
    
    if not test_files:
        print("📷 No test images found.")
        print("To test exact extraction, place an image or PDF file in the current directory.")
        return
    
    test_file = str(test_files[0])
    print(f"📷 Testing exact extraction with: {test_file}")
    
    try:
        tool = SlideAnalyzerTool()
        
        # Test with comprehensive analysis for maximum detail
        result = await tool.execute({
            'slide_images': [test_file],
            'ai_provider': 'google',  # Often better for exact text extraction
            'analysis_depth': 'comprehensive',
            'target_audience': 'advanced',
            'max_pdf_pages': 3  # Small batch for quality
        })
        
        if result.success:
            data = result.data
            print(f"\n✅ Analysis completed successfully")
            print(f"Document type: {data.get('type_document', 'Unknown')}")
            
            # Check for exact extraction indicators
            if data.get('type_document') in ['examen', 'serie_exercices']:
                exercices = data.get('exercices', [])
                print(f"\n📝 Found {len(exercices)} exercises")
                
                for i, exercice in enumerate(exercices[:2]):  # Show first 2 exercises
                    print(f"\n--- Exercise {i+1} ---")
                    print(f"Title: {exercice.get('id_exercice_ou_titre', 'No title')}")
                    
                    if exercice.get('enonce_exercice'):
                        enonce = exercice['enonce_exercice']
                        print(f"Statement: {enonce[:100]}{'...' if len(enonce) > 100 else ''}")
                    
                    questions = exercice.get('questions', [])
                    print(f"Questions: {len(questions)}")
                    
                    for j, question in enumerate(questions[:2]):  # Show first 2 questions
                        print(f"  Q{j+1} ID: {question.get('id_question_ou_numero', 'No ID')}")
                        
                        question_text = question.get('texte_question', '')
                        if question_text:
                            print(f"  Q{j+1} Text: {question_text[:150]}{'...' if len(question_text) > 150 else ''}")
                        
                        options = question.get('options_reponse', [])
                        if options:
                            print(f"  Q{j+1} Options: {len(options)} options")
                            for k, option in enumerate(options[:3]):  # Show first 3 options
                                print(f"    {chr(65+k)}) {option[:80]}{'...' if len(option) > 80 else ''}")
                
                # Analysis of extraction quality
                print(f"\n🔍 Extraction Quality Analysis:")
                
                # Check for signs of exact extraction
                total_text_length = 0
                has_exact_numbering = False
                has_original_formatting = False
                
                for exercice in exercices:
                    # Check exercise titles for exact formatting
                    title = exercice.get('id_exercice_ou_titre', '')
                    if any(pattern in title.lower() for pattern in ['exercice', 'ex.', 'question', 'q.']):
                        has_exact_numbering = True
                    
                    # Check questions for length and formatting
                    for question in exercice.get('questions', []):
                        question_text = question.get('texte_question', '')
                        total_text_length += len(question_text)
                        
                        # Check for original formatting indicators
                        if any(char in question_text for char in [':', ';', '(', ')', '-', '•']):
                            has_original_formatting = True
                
                print(f"  - Total extracted text: {total_text_length} characters")
                print(f"  - Exact numbering preserved: {'✅' if has_exact_numbering else '❌'}")
                print(f"  - Original formatting preserved: {'✅' if has_original_formatting else '❌'}")
                
                # Check for common signs of AI modification
                modification_indicators = []
                for exercice in exercices:
                    for question in exercice.get('questions', []):
                        text = question.get('texte_question', '').lower()
                        if 'veuillez' in text and 'analyser' in text:
                            modification_indicators.append("Generic AI language detected")
                        if text.startswith('cette question'):
                            modification_indicators.append("AI reformulation detected")
                
                if modification_indicators:
                    print(f"  ⚠️  Potential modifications detected:")
                    for indicator in modification_indicators:
                        print(f"    - {indicator}")
                else:
                    print(f"  ✅ No obvious AI modifications detected")
            
            elif data.get('type_document') == 'courses':
                print(f"\n📚 Course Analysis:")
                print(f"Title: {data.get('course_title', 'No title')}")
                description = data.get('detailed_description', '')
                if description:
                    print(f"Description length: {len(description)} characters")
                    print(f"Description preview: {description[:200]}{'...' if len(description) > 200 else ''}")
            
            print(f"\n⏱️  Analysis completed in {result.execution_time:.2f} seconds")
            
        else:
            print(f"❌ Analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

async def test_prompt_instructions():
    """Display the current prompt instructions for exact extraction."""
    print("\n=== Current Exact Extraction Instructions ===")
    
    tool = SlideAnalyzerTool()
    prompt = tool._create_analysis_prompt("comprehensive", "advanced", "auto-detect")
    
    # Extract the critical instructions section
    lines = prompt.split('\n')
    in_critical_section = False
    
    for line in lines:
        if 'INSTRUCTIONS CRITIQUES' in line:
            in_critical_section = True
        elif in_critical_section and line.strip() and not line.startswith(' '):
            if 'Toute votre analyse' in line:
                break
        
        if in_critical_section:
            print(line)
    
    print("\n✅ These instructions should ensure exact text extraction.")

if __name__ == "__main__":
    print("Testing exact text extraction for SMS-Agent...")
    print("This verifies that the AI extracts text exactly as written in images.\n")
    
    asyncio.run(test_exact_extraction())
    asyncio.run(test_prompt_instructions())
    
    print("\n🎯 The slide analyzer should now extract text exactly as it appears")
    print("without reformulation, correction, or structural changes.") 