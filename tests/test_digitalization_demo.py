#!/usr/bin/env python3
"""
Test script to demonstrate the slide digitalization tool
"""

import requests
import json

def test_digitalization():
    """Test the digitalization endpoint and display results."""
    
    print("🔬 Testing Slide Digitalization Tool")
    print("=" * 50)
    
    # Test the digitalization endpoint
    url = "http://localhost:8000/api/v1/digitalize-document"
    
    data = {
        "document_id": "cvsk40cubc2s712jggj0",
        "ai_provider": "openai",
        "language": "french",
        "extract_formulas": "true",
        "extract_diagrams": "true",
        "preserve_structure": "true"
    }
    
    print(f"📥 Fetching and digitalizing document: {data['document_id']}")
    print(f"🤖 Using AI provider: {data['ai_provider']}")
    print(f"🌍 Language: {data['language']}")
    print()
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("success"):
            digitized = result["digitized_content"]
            
            print("✅ Digitalization Success!")
            print(f"📄 Document: {digitized['document_title']}")
            print(f"🌍 Language detected: {digitized['language_detected']}")
            print(f"📊 Total slides: {digitized['total_slides']}")
            print(f"⏱️  Execution time: {result['execution_time']:.1f}s")
            print()
            
            # Show extraction summary
            summary = digitized.get("extraction_summary", {})
            print("📈 Extraction Summary:")
            print(f"   📝 Text blocks: {summary.get('total_text_blocks', 0)}")
            print(f"   🧮 Formulas: {summary.get('total_formulas', 0)}")
            print(f"   📊 Diagrams: {summary.get('total_diagrams', 0)}")
            print(f"   🎯 Confidence: {summary.get('completeness_confidence', 'unknown')}")
            print()
            
            # Show first few slides
            print("📝 Sample Slide Content (First 5 slides):")
            for i, slide in enumerate(digitized["slides"][:5]):
                print(f"\n   Slide {slide['slide_number']}: {slide['slide_title']}")
                
                # Show content sections
                for section in slide.get("content_sections", [])[:2]:
                    content = section["content"]
                    if len(content) > 80:
                        content = content[:80] + "..."
                    print(f"      - {section['section_type']}: {content}")
                
                # Show formulas
                for formula in slide.get("formulas", [])[:1]:
                    print(f"      - Formula: {formula['formula_text']}")
                
                # Show diagrams
                for diagram in slide.get("diagrams", [])[:1]:
                    desc = diagram["description"]
                    if len(desc) > 60:
                        desc = desc[:60] + "..."
                    print(f"      - Diagram: {desc}")
            
            # Verify slide ordering
            print(f"\n🔢 Slide Order Verification:")
            slide_numbers = [slide["slide_number"] for slide in digitized["slides"]]
            expected_order = list(range(1, len(slide_numbers) + 1))
            if slide_numbers == expected_order:
                print(f"   ✅ Slides are in correct order: {slide_numbers}")
            else:
                print(f"   ❌ Slide order issue - Expected: {expected_order}, Got: {slide_numbers}")
            
            print("\n🎉 Digitalization completed successfully!")
            print(f"💾 Full structured content available in JSON format")
            
        else:
            print(f"❌ Digitalization failed: {result.get('error', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_digitalization() 