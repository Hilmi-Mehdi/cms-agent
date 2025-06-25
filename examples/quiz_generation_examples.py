#!/usr/bin/env python3
"""
Quiz Generation Examples for Science Made Simple Documents

This file demonstrates how to generate sophisticated quizzes from slide exercises
with realistic distractors using the new quiz generation functionality.
"""

import httpx
import asyncio
import json


async def test_document_analysis_with_quiz():
    """Test complete document analysis with quiz generation."""
    
    print("🧪 Document Analysis + Quiz Generation")
    print("=" * 50)
    
    url = "http://localhost:8001/api/v1/analyze-document"
    
    # Request with quiz generation enabled
    data = {
        "document_id": "ct13hjqcchrs715kgjl0",
        "ai_provider": "openai",
        "analysis_depth": "comprehensive",
        "target_audience": "intermediate",
        "subject_area": "physics",
        "generate_quiz": True,
        "max_quiz_questions": 3
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                analysis = result["analysis_result"]
                doc_name = analysis["document_metadata"]["Name"]
                images = analysis.get("images_analyzed", 0)
                
                print(f"✅ Document: {doc_name}")
                print(f"🖼️  Images analyzed: {images}")
                
                # Display quiz results if generated
                if "quiz_data" in result:
                    quiz_data = result["quiz_data"]
                    quiz_meta = quiz_data["quiz_metadata"]
                    questions = quiz_data["questions"]
                    
                    print(f"\n🧪 Quiz Generated!")
                    print(f"   📊 Total Questions: {quiz_meta['total_questions']}")
                    print(f"   🎯 Subject: {quiz_meta['subject_area']}")
                    print(f"   📈 Difficulty: {quiz_meta['difficulty_level']}")
                    print(f"   📄 Source Slides: {quiz_meta['source_slides']}")
                    
                    # Display each question
                    for q in questions[:2]:  # Show first 2 questions
                        print(f"\n📝 Question {q['question_id']}:")
                        print(f"   {q['question_text']}")
                        print(f"   Type: {q['question_type']} | Points: {q['points']}")
                        print(f"   Source: Slide {q['source_slide']} → Answer: Slide {q['answer_slide']}")
                        print(f"   Options:")
                        for option, text in q['options'].items():
                            marker = "✅" if option == q['correct_answer'] else "  "
                            print(f"     {marker} {option}) {text}")
                        print(f"   💡 {q['explanation']}")
                    
                    if len(questions) > 2:
                        print(f"\n   ... and {len(questions) - 2} more questions")
                    
                    return result
                elif "quiz_error" in result:
                    print(f"❌ Quiz generation failed: {result['quiz_error']}")
                else:
                    print("⚠️ No quiz data generated")
            else:
                print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
    
    return None


async def test_standalone_quiz_generation():
    """Test generating quiz from existing slide analysis data."""
    
    print("\n🔄 Standalone Quiz Generation")
    print("=" * 50)
    
    # First, get slide analysis
    doc_analysis_url = "http://localhost:8001/api/v1/analyze-document"
    analysis_data = {
        "document_id": "ct13hjqcchrs715kgjl0",
        "ai_provider": "openai",
        "analysis_depth": "detailed",
        "target_audience": "intermediate"
    }
    
    print("📄 Getting slide analysis...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        analysis_response = await client.post(doc_analysis_url, data=analysis_data)
        
        if analysis_response.status_code != 200:
            print(f"❌ Failed to get analysis: {analysis_response.status_code}")
            return
        
        analysis_result = analysis_response.json()
        if not analysis_result["success"] or "slide_analysis" not in analysis_result["analysis_result"]:
            print("❌ No slide analysis available")
            return
        
        slide_analysis = analysis_result["analysis_result"]["slide_analysis"]
        print("✅ Slide analysis obtained")
        
        # Now generate quiz from the analysis
        quiz_url = "http://localhost:8001/api/v1/generate-quiz"
        quiz_data = {
            "slide_analysis_data": json.dumps(slide_analysis),
            "ai_provider": "openai",
            "max_questions": 5,
            "difficulty_level": "advanced",
            "subject_area": "physics"
        }
        
        print("🧪 Generating quiz...")
        quiz_response = await client.post(quiz_url, data=quiz_data)
        
        if quiz_response.status_code == 200:
            quiz_result = quiz_response.json()
            if quiz_result["success"]:
                quiz_data = quiz_result["quiz_data"]
                stats = quiz_data["generation_stats"]
                
                print(f"✅ Quiz generation successful!")
                print(f"   🔍 Exercises found: {stats['exercises_found']}")
                print(f"   🔗 Pairs matched: {stats['pairs_matched']}")
                print(f"   📝 Questions generated: {stats['questions_generated']}")
                
                # Show question details
                questions = quiz_data["questions"]
                for i, q in enumerate(questions[:3]):
                    print(f"\n📋 Question {i+1}: {q['question_text'][:60]}...")
                    print(f"   📍 From slide {q['source_slide']} (answer on slide {q['answer_slide']})")
                    print(f"   🎯 Type: {q['question_type']} | Difficulty: {q['difficulty']}")
                
                return quiz_result
            else:
                print(f"❌ Quiz generation failed: {quiz_result['error']}")
        else:
            print(f"❌ HTTP Error: {quiz_response.status_code}")
            print(f"Response: {quiz_response.text}")


async def save_quiz_results(quiz_data, filename="generated_quiz.json"):
    """Save quiz results in a structured format."""
    
    if not quiz_data:
        print("❌ No quiz data to save")
        return
    
    try:
        # Create a clean quiz format for export
        clean_quiz = {
            "quiz_info": quiz_data["quiz_metadata"],
            "questions": []
        }
        
        for q in quiz_data["questions"]:
            clean_question = {
                "id": q["question_id"],
                "question": q["question_text"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"],
                "points": q["points"],
                "difficulty": q["difficulty"],
                "type": q["question_type"]
            }
            clean_quiz["questions"].append(clean_question)
        
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(clean_quiz, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Quiz saved to: {filename}")
        
        # Also create a text version for easy reading
        text_filename = filename.replace('.json', '.txt')
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(f"QUIZ: {clean_quiz['quiz_info']['subject_area']}\n")
            f.write(f"Difficulty: {clean_quiz['quiz_info']['difficulty_level']}\n")
            f.write(f"Total Questions: {clean_quiz['quiz_info']['total_questions']}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, q in enumerate(clean_quiz["questions"], 1):
                f.write(f"Question {i}: {q['question']}\n\n")
                for option, text in q["options"].items():
                    marker = "→" if option == q["correct_answer"] else " "
                    f.write(f"  {marker} {option}) {text}\n")
                f.write(f"\nExplanation: {q['explanation']}\n")
                f.write(f"Points: {q['points']} | Type: {q['type']}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"📄 Text version saved to: {text_filename}")
        
    except Exception as e:
        print(f"❌ Failed to save quiz: {str(e)}")


async def demonstrate_quiz_features():
    """Demonstrate different quiz generation features."""
    
    print("\n🎯 Quiz Feature Demonstration")
    print("=" * 50)
    
    # Test different difficulty levels
    difficulties = ["beginner", "intermediate", "advanced"]
    
    for difficulty in difficulties:
        print(f"\n🎚️ Testing {difficulty} difficulty...")
        
        url = "http://localhost:8001/api/v1/analyze-document"
        data = {
            "document_id": "ct13hjqcchrs715kgjl0",
            "ai_provider": "openai",
            "analysis_depth": "basic",
            "target_audience": difficulty,
            "generate_quiz": True,
            "max_quiz_questions": 2
        }
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result["success"] and "quiz_data" in result:
                        quiz = result["quiz_data"]
                        questions = quiz["questions"]
                        avg_points = sum(q["points"] for q in questions) / len(questions) if questions else 0
                        
                        print(f"   ✅ Generated {len(questions)} questions")
                        print(f"   📊 Average points: {avg_points:.1f}")
                        print(f"   🎯 Question types: {list(set(q['question_type'] for q in questions))}")
                    else:
                        print(f"   ❌ Failed: {result.get('quiz_error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")


if __name__ == "__main__":
    async def main():
        print("🚀 Quiz Generation Examples for Science Made Simple")
        print("=" * 70)
        
        # Run examples
        quiz_result = await test_document_analysis_with_quiz()
        
        await test_standalone_quiz_generation()
        
        await demonstrate_quiz_features()
        
        # Save results if we got any
        if quiz_result and "quiz_data" in quiz_result:
            await save_quiz_results(quiz_result["quiz_data"], "example_physics_quiz.json")
        
        print("\n" + "=" * 70)
        print("🎉 Quiz generation examples completed!")
        print("\n💡 Features demonstrated:")
        print("   • Extract exercises from slides automatically")
        print("   • Match questions with answers across different slides")
        print("   • Generate realistic wrong answers (distractors)")
        print("   • Create structured quiz with points and explanations")
        print("   • Support multiple difficulty levels")
        print("   • Handle different question types (calculation, conceptual, etc.)")
        print("\n🔧 API Endpoints:")
        print("   • POST /api/v1/analyze-document (with generate_quiz=True)")
        print("   • POST /api/v1/generate-quiz (standalone quiz generation)")
        print("\n📋 Quiz Features:")
        print("   • Questions from actual slide exercises")
        print("   • Correct answers from slide content") 
        print("   • AI-generated realistic distractors")
        print("   • Cross-slide question-answer matching")
        print("   • Structured output with metadata")
    
    asyncio.run(main()) 