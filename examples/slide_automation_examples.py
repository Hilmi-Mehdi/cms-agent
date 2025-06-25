#!/usr/bin/env python3
"""
Automation examples using the integrated slide analyzer tool
"""

import asyncio
from typing import List, Dict, Any
from pathlib import Path

from app.tools import tool_registry
from app.agent.core_agent import course_agent


class SlideAnalysisAutomation:
    """Automated workflows using the slide analyzer tool."""
    
    async def workflow_1_basic_course_creation(self):
        """Workflow 1: Basic course creation from slide images."""
        print("🎯 Workflow 1: Basic Course Creation from Slides")
        print("=" * 60)
        
        # Simulate slide paths (replace with real paths in practice)
        slide_paths = [
            "course_slides/intro.png",
            "course_slides/module1.png", 
            "course_slides/module2.png",
            "course_slides/summary.png"
        ]
        
        print(f"📁 Processing {len(slide_paths)} slide images...")
        
        try:
            # Step 1: Analyze slides
            slide_analyzer = tool_registry.get_tool("slideanalyzer")
            
            result = await slide_analyzer.execute({
                "slide_images": slide_paths,
                "ai_provider": "openai",
                "analysis_depth": "comprehensive",
                "target_audience": "intermediate",
                "subject_area": "programming"
            })
            
            if result.success:
                print("✅ Slide analysis completed")
                course_data = result.data
                
                # Step 2: Use content analyzer for deeper analysis
                content_analyzer = tool_registry.get_tool("contentanalyzer")
                
                analysis_result = await content_analyzer.execute({
                    "content": course_data.get("detailed_description", ""),
                    "analysis_type": "comprehensive",
                    "target_audience": "intermediate"
                })
                
                if analysis_result.success:
                    print("✅ Content analysis completed")
                
                # Step 3: Generate additional materials
                content_generator = tool_registry.get_tool("contentgenerator")
                
                generation_result = await content_generator.execute({
                    "content_type": "course_outline",
                    "topic": course_data.get("course_title", "Course"),
                    "target_audience": "intermediate",
                    "requirements": {
                        "modules": len(course_data.get("learning_path", [])),
                        "difficulty": course_data.get("difficulty_level", "intermediate")
                    }
                })
                
                if generation_result.success:
                    print("✅ Content generation completed")
                
                print(f"\n📊 Course Title: {course_data.get('course_title')}")
                print(f"🏷️  Tags: {', '.join(course_data.get('tags', []))}")
                print(f"📚 Modules: {len(course_data.get('learning_path', []))}")
                
                return {
                    "slide_analysis": course_data,
                    "content_analysis": analysis_result.data if analysis_result.success else None,
                    "generated_content": generation_result.data if generation_result.success else None
                }
            else:
                print(f"❌ Slide analysis failed: {result.error}")
                return None
                
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return None
    
    async def workflow_2_agent_based_processing(self):
        """Workflow 2: Agent-based slide processing."""
        print("\n🤖 Workflow 2: Agent-Based Slide Processing")
        print("=" * 60)
        
        # Simulate request with slide images
        user_request = """
        I have a set of course slides about machine learning fundamentals. 
        Please analyze them and create a comprehensive course structure with:
        - Course title and description
        - Learning objectives for each module
        - Prerequisites and difficulty assessment
        - Suggested additional materials
        """
        
        context = {
            "slide_images": [
                "ml_slides/introduction.png",
                "ml_slides/supervised_learning.png", 
                "ml_slides/unsupervised_learning.png",
                "ml_slides/neural_networks.png",
                "ml_slides/conclusion.png"
            ],
            "subject_area": "machine_learning",
            "target_audience": "beginner",
            "analysis_depth": "comprehensive"
        }
        
        try:
            print("📤 Sending request to agent...")
            response = await course_agent.process_request(
                user_request=user_request,
                context=context
            )
            
            if response.success:
                print("✅ Agent processing completed")
                print(f"⏱️  Processing time: {response.processing_time:.2f}s")
                print(f"📝 Response length: {len(response.response)} characters")
                
                # Show tools that were executed
                tools_executed = response.data.get("tools_executed", [])
                print(f"🛠️  Tools used: {[tool.get('name', 'unknown') for tool in tools_executed]}")
                
                return response
            else:
                print(f"❌ Agent processing failed: {response.error}")
                return None
                
        except Exception as e:
            print(f"❌ Agent workflow failed: {str(e)}")
            return None
    
    async def workflow_3_batch_course_processing(self):
        """Workflow 3: Batch processing multiple course slide sets."""
        print("\n🔄 Workflow 3: Batch Course Processing")
        print("=" * 60)
        
        # Simulate multiple course slide sets
        course_sets = [
            {
                "name": "Python Programming Basics",
                "slides": ["python/intro.png", "python/syntax.png", "python/functions.png"],
                "config": {
                    "target_audience": "beginner",
                    "subject_area": "programming",
                    "analysis_depth": "detailed"
                }
            },
            {
                "name": "Data Science with Python", 
                "slides": ["datascience/pandas.png", "datascience/visualization.png", "datascience/ml.png"],
                "config": {
                    "target_audience": "intermediate",
                    "subject_area": "data_science", 
                    "analysis_depth": "comprehensive"
                }
            },
            {
                "name": "Web Development Fundamentals",
                "slides": ["web/html.png", "web/css.png", "web/javascript.png"],
                "config": {
                    "target_audience": "beginner",
                    "subject_area": "web_development",
                    "analysis_depth": "detailed"
                }
            }
        ]
        
        slide_analyzer = tool_registry.get_tool("slideanalyzer")
        batch_results = []
        
        for course in course_sets:
            print(f"\n📖 Processing: {course['name']}")
            print("-" * 40)
            
            try:
                # Analyze each course
                result = await slide_analyzer.execute({
                    "slide_images": course["slides"],
                    "ai_provider": "openai",
                    **course["config"]
                })
                
                if result.success:
                    course_data = result.data
                    batch_results.append({
                        "course_name": course["name"],
                        "status": "success",
                        "data": course_data,
                        "metrics": {
                            "modules": len(course_data.get("learning_path", [])),
                            "tags": len(course_data.get("tags", [])),
                            "difficulty": course_data.get("difficulty_level", "unknown")
                        }
                    })
                    
                    print(f"✅ {course['name']}: Analysis completed")
                    print(f"   📊 Title: {course_data.get('course_title', 'N/A')}")
                    print(f"   📚 Modules: {len(course_data.get('learning_path', []))}")
                    print(f"   🏷️  Tags: {len(course_data.get('tags', []))}")
                else:
                    batch_results.append({
                        "course_name": course["name"],
                        "status": "failed",
                        "error": result.error
                    })
                    print(f"❌ {course['name']}: {result.error}")
                    
            except Exception as e:
                batch_results.append({
                    "course_name": course["name"],
                    "status": "error", 
                    "error": str(e)
                })
                print(f"❌ {course['name']}: {str(e)}")
        
        # Summary
        successful = len([r for r in batch_results if r["status"] == "success"])
        print(f"\n📈 Batch Processing Summary:")
        print(f"   ✅ Successful: {successful}/{len(course_sets)}")
        print(f"   ❌ Failed: {len(course_sets) - successful}/{len(course_sets)}")
        
        return batch_results
    
    async def workflow_4_quality_assessment(self):
        """Workflow 4: Quality assessment and improvement suggestions."""
        print("\n📊 Workflow 4: Quality Assessment & Improvement")
        print("=" * 60)
        
        # Simulate analysis of existing course slides
        slides = ["quality_test/slide1.png", "quality_test/slide2.png"]
        
        try:
            # Step 1: Analyze slides
            slide_analyzer = tool_registry.get_tool("slideanalyzer")
            
            result = await slide_analyzer.execute({
                "slide_images": slides,
                "ai_provider": "openai",
                "analysis_depth": "comprehensive",
                "target_audience": "intermediate",
                "subject_area": "programming"
            })
            
            if result.success:
                print("✅ Slide analysis completed")
                course_data = result.data
                
                # Step 2: Use content analyzer for deeper analysis
                content_analyzer = tool_registry.get_tool("contentanalyzer")
                
                analysis_result = await content_analyzer.execute({
                    "content": course_data.get("detailed_description", ""),
                    "analysis_type": "comprehensive",
                    "target_audience": "intermediate"
                })
                
                if analysis_result.success:
                    print("✅ Content analysis completed")
                
                # Step 3: Generate additional materials
                content_generator = tool_registry.get_tool("contentgenerator")
                
                generation_result = await content_generator.execute({
                    "content_type": "course_outline",
                    "topic": course_data.get("course_title", "Course"),
                    "target_audience": "intermediate",
                    "requirements": {
                        "modules": len(course_data.get("learning_path", [])),
                        "difficulty": course_data.get("difficulty_level", "intermediate")
                    }
                })
                
                if generation_result.success:
                    print("✅ Content generation completed")
                
                print(f"\n📊 Course Title: {course_data.get('course_title')}")
                print(f"🏷️  Tags: {', '.join(course_data.get('tags', []))}")
                print(f"📚 Modules: {len(course_data.get('learning_path', []))}")
                
                return {
                    "slide_analysis": course_data,
                    "content_analysis": analysis_result.data if analysis_result.success else None,
                    "generated_content": generation_result.data if generation_result.success else None
                }
            else:
                print(f"❌ Slide analysis failed: {result.error}")
                return None
                
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return None 