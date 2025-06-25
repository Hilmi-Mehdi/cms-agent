"""
Direct Quiz Generator Tool: Generate quizzes directly from slide images
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult, AIProvider
from app.utils.ai_client import ai_client
from app.utils.pdf_processor import pdf_processor, PDF_SUPPORT_AVAILABLE


class DirectQuizGeneratorTool(BaseTool):
    """Tool that generates quizzes directly from slide images without complex preprocessing."""
    
    def get_definition(self) -> ToolDefinition:
        description = "Generate high-quality quizzes directly from slide images using AI vision"
        if PDF_SUPPORT_AVAILABLE:
            description += " (supports images and PDF files)"
        
        return ToolDefinition(
            name="direct_quiz_generator",
            description=description,
            parameters=[
                ToolParameter(
                    name="slide_images",
                    type="array",
                    description="List of slide image file paths, PDF file paths, or base64 encoded images",
                    required=True
                ),
                ToolParameter(
                    name="ai_provider",
                    type="string",
                    description="AI provider to use for quiz generation",
                    required=False,
                    default="openai",
                    enum=["openai", "google"]
                ),
                ToolParameter(
                    name="max_questions",
                    type="integer",
                    description="Maximum number of quiz questions to generate",
                    required=False,
                    default=10
                ),
                ToolParameter(
                    name="difficulty_level",
                    type="string",
                    description="Difficulty level of questions",
                    required=False,
                    default="intermediate",
                    enum=["beginner", "intermediate", "advanced"]
                ),
                ToolParameter(
                    name="subject_area",
                    type="string",
                    description="Subject area hint for better question generation",
                    required=False,
                    default="auto-detect"
                ),
                ToolParameter(
                    name="question_types",
                    type="array",
                    description="Types of questions to generate",
                    required=False,
                    default=["multiple_choice", "calculation", "conceptual"]
                ),
                ToolParameter(
                    name="language",
                    type="string",
                    description="Language for quiz questions",
                    required=False,
                    default="auto-detect",
                    enum=["english", "french", "auto-detect"]
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute direct quiz generation from slides."""
        start_time = time.monotonic()
        
        try:
            slide_images = parameters.get("slide_images", [])
            ai_provider = parameters.get("ai_provider", "openai")
            max_questions = parameters.get("max_questions", 10)
            difficulty_level = parameters.get("difficulty_level", "intermediate")
            subject_area = parameters.get("subject_area", "auto-detect")
            question_types = parameters.get("question_types", ["multiple_choice", "calculation", "conceptual"])
            language = parameters.get("language", "auto-detect")
            
            if not slide_images:
                return ToolResult(
                    success=False,
                    error="No slide images provided"
                )
            
            # Validate and prepare images
            validated_images = await self._validate_images(slide_images)
            if not validated_images:
                return ToolResult(
                    success=False,
                    error="No valid images found in the provided list"
                )
            
            # Determine AI provider
            provider = AIProvider.OPENAI if ai_provider.lower() == "openai" else AIProvider.GOOGLE
            
            # Generate quiz directly from images
            quiz_result = await self._generate_quiz_direct(
                validated_images,
                provider,
                max_questions,
                difficulty_level,
                subject_area,
                question_types,
                language
            )
            
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            
            return ToolResult(
                success=True,
                data=quiz_result,
                execution_time=execution_time,
                agent_notes=f"Generated {len(quiz_result.get('questions', []))} questions in {execution_time}s using {provider.value}"
            )
            
        except Exception as e:
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            return ToolResult(
                success=False,
                error=f"Direct quiz generation failed: {str(e)}",
                execution_time=execution_time
            )
    
    async def _validate_images(self, slide_images: List[Union[str, bytes]]) -> List[Union[str, bytes]]:
        """Validate and filter image inputs, including PDF conversion."""
        validated = []
        
        for img in slide_images:
            if isinstance(img, str):
                # Check if it's base64 encoded image data
                if img.startswith('data:image/') or (len(img) > 100 and not img.startswith('/')):
                    # Assume it's base64 encoded
                    validated.append(img)
                # Check if it's a file path
                elif Path(img).exists():
                    file_path = Path(img)
                    ext = file_path.suffix.lower()
                    
                    # Handle PDF files
                    if ext == '.pdf':
                        if not PDF_SUPPORT_AVAILABLE:
                            print(f"WARNING: PDF support not available. Skipping {img}")
                            continue
                        
                        try:
                            print(f"Converting PDF to images: {img}")
                            # Use high DPI for text clarity
                            pdf_images = pdf_processor.pdf_to_images(img, dpi=300, max_pages=20)
                            validated.extend(pdf_images)
                            print(f"Successfully converted {len(pdf_images)} pages from PDF")
                        except Exception as e:
                            print(f"ERROR: Failed to convert PDF {img}: {e}")
                            continue
                    
                    # Handle image files
                    elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                        validated.append(img)
                    
            elif isinstance(img, bytes):
                # Check if it's PDF bytes
                if PDF_SUPPORT_AVAILABLE and pdf_processor.validate_pdf(img):
                    try:
                        print("Converting PDF bytes to images")
                        pdf_images = pdf_processor.pdf_to_images(img, dpi=300, max_pages=20)
                        validated.extend(pdf_images)
                        print(f"Successfully converted {len(pdf_images)} pages from PDF bytes")
                    except Exception as e:
                        print(f"ERROR: Failed to convert PDF bytes: {e}")
                        continue
                else:
                    # Assume it's image bytes
                    validated.append(img)
        
        return validated
    
    async def _generate_quiz_direct(
        self,
        images: List[Union[str, bytes]],
        provider: AIProvider,
        max_questions: int,
        difficulty_level: str,
        subject_area: str,
        question_types: List[str],
        language: str
    ) -> Dict[str, Any]:
        """Generate quiz directly from images using AI vision."""
        
        # Create optimized quiz generation prompt
        prompt = self._create_quiz_prompt(
            max_questions, difficulty_level, subject_area, question_types, language
        )
        
        try:
            response = await ai_client.analyze_images(
                images=images,
                prompt=prompt,
                provider=provider,
                temperature=0.7  # Balanced creativity for good options
            )
            
            # Extract quiz data from response
            quiz_data = self._extract_quiz_from_response(response["content"])
            
            # Add metadata
            quiz_data["generation_metadata"] = {
                "provider": response["provider"],
                "model": response["model"],
                "images_analyzed": response.get("images_analyzed", len(images)),
                "usage_stats": response.get("usage", {}),
                "parameters": {
                    "max_questions": max_questions,
                    "difficulty_level": difficulty_level,
                    "subject_area": subject_area,
                    "question_types": question_types,
                    "language": language
                }
            }
            
            return quiz_data
            
        except Exception as e:
            raise Exception(f"Direct quiz generation failed: {str(e)}")
    
    def _create_quiz_prompt(
        self,
        max_questions: int,
        difficulty_level: str,
        subject_area: str,
        question_types: List[str],
        language: str
    ) -> str:
        """Create an optimized quiz generation prompt."""
        
        language_instruction = ""
        if language == "french":
            language_instruction = "Generate all questions and answers in FRENCH."
        elif language == "english":
            language_instruction = "Generate all questions and answers in ENGLISH."
        else:
            language_instruction = "Use the same language as the slides (French or English)."
        
        difficulty_guidance = {
            "beginner": "Focus on basic concepts, definitions, and simple calculations.",
            "intermediate": "Include moderate complexity problems requiring understanding of relationships and multi-step solutions.",
            "advanced": "Create challenging questions requiring deep analysis, complex calculations, and synthesis of multiple concepts."
        }
        
        types_instruction = ""
        if "multiple_choice" in question_types:
            types_instruction += "- Multiple choice questions with 4 realistic options (a, b, c, d)\n"
        if "calculation" in question_types:
            types_instruction += "- Calculation questions requiring specific numerical answers\n"
        if "conceptual" in question_types:
            types_instruction += "- Conceptual questions testing understanding of principles\n"
        
        prompt = f"""
EXPERT QUIZ GENERATOR - STRICT CONTENT VALIDATION

Analyze these slide images carefully and create a quiz ONLY based on content that is explicitly visible in the slides.

INSTRUCTIONS:
{language_instruction}

REQUIREMENTS:
- Generate UP TO {max_questions} questions (generate fewer if limited slide content)
- Difficulty level: {difficulty_level} - {difficulty_guidance.get(difficulty_level, '')}
- Subject area hint: {subject_area}

QUESTION TYPES TO INCLUDE:
{types_instruction}

CRITICAL CONTENT VALIDATION RULES:
1. ONLY create questions based on text, formulas, numbers, or diagrams EXPLICITLY VISIBLE in the slides
2. DO NOT invent or assume any values, formulas, or concepts not shown
3. DO NOT create questions based on general knowledge of the subject
4. If you can't see specific numerical values, formulas, or text clearly, DON'T make up questions
5. It's better to generate 1 accurate question than 5 inaccurate ones
6. For calculations: ONLY use exact numbers and formulas visible in the slides
7. For concepts: ONLY reference principles or laws explicitly mentioned or shown
8. Each question must reference the specific slide where the information is found

QUALITY STANDARDS:
1. Every question must be traceable to specific visible content in the slides
2. For multiple choice: Create 4 plausible options with only 1 correct answer
3. For calculations: Use ONLY exact values and formulas shown in slides
4. For concepts: Test ONLY principles, laws, or relationships explicitly shown
5. Include the specific slide reference where the content was found
6. Use simple text formatting - avoid LaTeX, complex symbols, or special characters
7. Use Greek letter names instead of symbols (e.g., "phi" instead of Φ)

VALIDATION PROCESS:
Before creating each question, ask yourself:
- Can I see this exact information in the slides?
- Is this formula/value/concept explicitly shown?
- Would someone looking at the slides find this exact content?

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure:
{{
  "quiz_title": "Descriptive title based on slide content",
  "instructions": "Brief instructions for taking the quiz",
  "questions": [
    {{
      "question_number": 1,
      "question_text": "Question text here (based ONLY on visible slide content)",
      "question_type": "multiple_choice|calculation|conceptual",
      "options": ["a) Option A", "b) Option B", "c) Option C", "d) Option D"],
      "correct_answer": "a",
      "explanation": "Brief explanation referencing the specific slide content",
      "difficulty": "beginner|intermediate|advanced",
      "topic": "Main topic/concept being tested",
      "slide_reference": "Specific slide number where this content is visible"
    }}
  ],
  "total_questions": number,
  "estimated_time": "Estimated completion time in minutes"
}}

FINAL REMINDER: 
- ONLY use content explicitly visible in the slides
- Better to generate fewer accurate questions than many inaccurate ones
- Each question must be verifiable by looking at the slides
- If you can't clearly see the information, don't create a question about it

Generate the quiz now, ensuring every question is based on clearly visible slide content:
"""
        
        return prompt
    
    def _extract_quiz_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract and validate quiz data from AI response."""
        
        try:
            # Try multiple approaches to extract JSON
            import re
            
            # Method 1: Try to parse the entire response as JSON
            try:
                # Clean the response first
                cleaned_response = response_text.strip()
                quiz_data = json.loads(cleaned_response)
                return self._validate_quiz_data(quiz_data)
            except json.JSONDecodeError:
                pass
            
            # Method 2: Find JSON objects using bracket matching with better error handling
            start_idx = response_text.find('{')
            if start_idx != -1:
                brace_count = 0
                in_string = False
                escape_next = False
                json_end = start_idx
                
                for i, char in enumerate(response_text[start_idx:], start_idx):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i
                                break
                
                if brace_count == 0:
                    json_str = response_text[start_idx:json_end + 1]
                    
                    try:
                        quiz_data = json.loads(json_str)
                        return self._validate_quiz_data(quiz_data)
                    except json.JSONDecodeError as e:
                        # Try to fix common issues
                        fixed_json = self._fix_json_issues(json_str)
                        try:
                            quiz_data = json.loads(fixed_json)
                            return self._validate_quiz_data(quiz_data)
                        except json.JSONDecodeError:
                            print(f"JSON parsing failed even after fixes: {e}")
            
            # Method 3: Try a more aggressive approach to find JSON
            # Look for quiz_title as a marker
            title_match = re.search(r'"quiz_title"\s*:\s*"([^"]*)"', response_text)
            if title_match:
                # Try to find the full JSON object around the quiz_title
                title_pos = title_match.start()
                
                # Find the opening brace before the title
                json_start = response_text.rfind('{', 0, title_pos)
                if json_start != -1:
                    # Find the matching closing brace
                    brace_count = 0
                    for i in range(json_start, len(response_text)):
                        if response_text[i] == '{':
                            brace_count += 1
                        elif response_text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_candidate = response_text[json_start:i+1]
                                try:
                                    quiz_data = json.loads(json_candidate)
                                    return self._validate_quiz_data(quiz_data)
                                except json.JSONDecodeError:
                                    continue
            
            # If all methods fail, create fallback structure
            print("Failed to extract valid JSON from AI response")
            return self._create_fallback_quiz(response_text)
                
        except Exception as e:
            print(f"Unexpected error in JSON extraction: {e}")
            return self._create_fallback_quiz(response_text)
    
    def _fix_json_issues(self, json_str: str) -> str:
        """Fix common JSON issues like unescaped characters and LaTeX notation."""
        import re
        
        # Start with the original string
        fixed = json_str
        
        # Fix common French character issues
        try:
            # Ensure proper UTF-8 encoding
            if isinstance(fixed, bytes):
                fixed = fixed.decode('utf-8', errors='replace')
            
            # Fix common escaping issues with French characters
            # Don't break existing proper escapes, but fix unescaped quotes in French text
            fixed = re.sub(r'(?<!\\)"([^"]*[àâäéèêëïîôöùûüÿç][^"]*)"(?=\s*[,}\]])', r'"\1"', fixed)
            
        except Exception:
            pass  # Continue with original if fixing fails
        
        # Fix LaTeX backslashes that aren't properly escaped
        try:
            fixed = re.sub(r'\\\\([a-zA-Z()])', r'\\\\\\\\\\1', fixed)
        except Exception:
            pass
        
        # Fix other common JSON issues
        try:
            # Fix unescaped backslashes (but preserve JSON escapes)
            fixed = re.sub(r'([^\\])\\([^"\\nrtbf/])', r'\1\\\\\\2', fixed)
            
            # Fix newlines not in strings
            fixed = re.sub(r'\\n(?!")', r'\\\\n', fixed)
            
            # Fix trailing commas in arrays and objects
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            
        except Exception:
            pass
        
        return fixed
    
    def _validate_quiz_data(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean quiz data structure."""
        
        # Ensure required fields
        quiz_data.setdefault("quiz_title", "Generated Quiz")
        quiz_data.setdefault("instructions", "Answer all questions based on the slide content.")
        quiz_data.setdefault("questions", [])
        quiz_data.setdefault("total_questions", len(quiz_data.get("questions", [])))
        quiz_data.setdefault("estimated_time", "15-20 minutes")
        
        # Validate questions
        validated_questions = []
        for i, q in enumerate(quiz_data.get("questions", [])):
            if isinstance(q, dict):
                # Ensure question has required fields
                validated_q = {
                    "question_number": q.get("question_number", i + 1),
                    "question_text": q.get("question_text", f"Question {i + 1}"),
                    "question_type": q.get("question_type", "multiple_choice"),
                    "options": q.get("options", []),
                    "correct_answer": q.get("correct_answer", "a"),
                    "explanation": q.get("explanation", ""),
                    "difficulty": q.get("difficulty", "intermediate"),
                    "topic": q.get("topic", "General"),
                    "slide_reference": q.get("slide_reference", "Multiple slides")
                }
                validated_questions.append(validated_q)
        
        quiz_data["questions"] = validated_questions
        quiz_data["total_questions"] = len(validated_questions)
        
        return quiz_data
    
    def _create_fallback_quiz(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback quiz structure if JSON extraction fails."""
        
        return {
            "quiz_title": "Generated Quiz",
            "instructions": "Answer the questions based on the slide content.",
            "questions": [],
            "total_questions": 0,
            "estimated_time": "N/A",
            "error": "Failed to parse quiz from AI response",
            "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
        } 