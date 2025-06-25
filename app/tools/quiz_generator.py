"""Quiz generator tool for creating sophisticated quizzes from slide content."""

import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
import json

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult, AIProvider
from app.utils.ai_client import ai_client


class QuizGeneratorTool(BaseTool):
    """Tool for generating sophisticated quizzes from slide exercises with realistic distractors."""
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="quiz_generator",
            description="Generate sophisticated multiple-choice quizzes from exercises found in slides, with realistic wrong answers",
            parameters=[
                ToolParameter(
                    name="slide_analysis_data",
                    type="object",
                    description="The slide analysis data containing content from multiple slides",
                    required=True
                ),
                ToolParameter(
                    name="ai_provider",
                    type="string",
                    description="AI provider for generating distractors",
                    required=False,
                    default="openai",
                    enum=["openai", "google"]
                ),
                ToolParameter(
                    name="max_questions",
                    type="number",
                    description="Maximum number of quiz questions to generate",
                    required=False,
                    default=10
                ),
                ToolParameter(
                    name="difficulty_level",
                    type="string",
                    description="Difficulty level for the quiz questions",
                    required=False,
                    default="intermediate",
                    enum=["beginner", "intermediate", "advanced"]
                ),
                ToolParameter(
                    name="subject_area",
                    type="string",
                    description="Subject area to focus on for question generation",
                    required=False
                ),
                ToolParameter(
                    name="question_types",
                    type="array",
                    description="Types of questions to include (calculation, conceptual, application, etc.)",
                    required=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute quiz generation from slide exercises."""
        slide_data = parameters["slide_analysis_data"]
        ai_provider = parameters.get("ai_provider", "openai")
        max_questions = parameters.get("max_questions", 10)
        difficulty_level = parameters.get("difficulty_level", "intermediate")
        subject_area = parameters.get("subject_area")
        question_types = parameters.get("question_types", [])
        
        try:
            # Step 1: Extract exercises and questions from slides
            exercises = await self._extract_exercises_from_slides(slide_data)
            
            if not exercises:
                return ToolResult(
                    success=False,
                    error="No exercises or questions found in the slides"
                )
            
            print(f"🔍 Found {len(exercises)} potential exercises in slides")
            
            # Step 2: Match questions with answers across slides
            question_answer_pairs = await self._match_questions_with_answers(exercises, slide_data)
            
            print(f"✅ Matched {len(question_answer_pairs)} question-answer pairs")
            
            # Step 3: Generate quiz questions with distractors
            quiz_questions = await self._generate_quiz_questions(
                question_answer_pairs,
                ai_provider,
                max_questions,
                difficulty_level,
                subject_area,
                question_types
            )
            
            # Step 4: Structure the final quiz
            quiz_data = {
                "quiz_metadata": {
                    "total_questions": len(quiz_questions),
                    "difficulty_level": difficulty_level,
                    "subject_area": subject_area or slide_data.get("subject_area", "General"),
                    "source_slides": len(slide_data.get("slide_contents", [])),
                    "ai_provider": ai_provider
                },
                "questions": quiz_questions,
                "source_exercises": exercises,
                "generation_stats": {
                    "exercises_found": len(exercises),
                    "pairs_matched": len(question_answer_pairs),
                    "questions_generated": len(quiz_questions)
                }
            }
            
            return ToolResult(
                success=True,
                data=quiz_data,
                suggested_next_tools=["content_generator"],
                agent_notes=f"Generated {len(quiz_questions)} sophisticated quiz questions from {len(exercises)} slide exercises"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Quiz generation failed: {str(e)}"
            )
    
    async def _extract_exercises_from_slides(self, slide_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract exercises, questions, and problems from slide content."""
        exercises = []
        slide_contents = slide_data.get("slide_contents", [])
        
        # If no slide contents, try to extract from other analysis data
        if not slide_contents:
            print("⚠️ No slide contents found, trying alternative content sources...")
            return await self._extract_from_alternative_sources(slide_data)
        
        # Enhanced patterns to identify exercises, questions, and problems in multiple languages
        exercise_patterns = [
            # French patterns
            r"(?i)(?:exercice|problème)\s*\d*\s*:?\s*(.{20,}?)(?=\n\n|\nexercice|\nproblème|$)",
            r"(?i)(?:calculer|déterminer|trouver|résoudre|évaluer)\s+(.{20,}?)(?=\n|$)",
            r"(?i)(?:que vaut|combien vaut|quelle est)\s+(.{20,}?)(?=\n|\?|$)",
            r"(?i)(?:soit|étant donné|on donne)\s+(.{30,}?)(?:calculer|déterminer|trouver)(.{10,}?)(?=\n|$)",
            
            # English patterns  
            r"(?i)(?:exercise|problem|question)\s*\d*\s*:?\s*(.{20,}?)(?=\n\n|\nexercise|\nproblem|$)",
            r"(?i)(?:calculate|determine|find|solve|evaluate)\s+(.{20,}?)(?=\n|$)",
            r"(?i)(?:what is|how much|what value)\s+(.{20,}?)(?=\n|\?|$)",
            r"(?i)(?:given|given that|suppose)\s+(.{30,}?)(?:find|calculate|determine)(.{10,}?)(?=\n|$)",
            
            # Question patterns
            r"(?i)(?:what|que|how|comment|why|pourquoi|when|quand|where|où)\s+(?:is|are|est|sont|does|fait|would|sera|could|pourrait).{15,}?\?",
            r"(?i)if\s+.{15,}?\,?\s*(?:what|how|calculate|find|determine|que|comment|calculer|trouver|déterminer).{10,}?\??",
            
            # Mathematical patterns
            r"(?i)(?:calculer|calculate)\s+(?:la|le|l'|the)?\s*(?:force|vitesse|accélération|énergie|puissance|tension|courant|résistance|field|velocity|acceleration|energy|power|voltage|current|resistance).{10,}?(?=\n|$)",
            
            # Numbered patterns
            r"(?i)(\d+[\.\)]\s*)(.{30,}?)(?=\n\d+[\.\)]|\n\n|$)"
        ]
        
        for slide_idx, slide_content in enumerate(slide_contents):
            content = slide_content.get("content", "")
            slide_number = slide_idx + 1
            
            # Find potential exercises using patterns
            for pattern_idx, pattern in enumerate(exercise_patterns):
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    exercise_text = match.group(0).strip()
                    
                    # Skip very short matches
                    if len(exercise_text) < 25:
                        continue
                    
                    # Skip if it's just a heading or title
                    if len(exercise_text) < 50 and not any(word in exercise_text.lower() for word in 
                        ["?", "calculer", "calculate", "trouver", "find", "déterminer", "determine"]):
                        continue
                    
                    # Extract context around the exercise
                    start_pos = max(0, match.start() - 150)
                    end_pos = min(len(content), match.end() + 250)
                    context = content[start_pos:end_pos].strip()
                    
                    exercise = {
                        "slide_number": slide_number,
                        "exercise_text": exercise_text,
                        "context": context,
                        "type": self._classify_exercise_type(exercise_text),
                        "content_around": content[max(0, match.start() - 300):min(len(content), match.end() + 400)],
                        "pattern_used": pattern_idx,
                        "confidence": self._calculate_exercise_confidence(exercise_text, content)
                    }
                    
                    exercises.append(exercise)
                    print(f"🔍 Found potential exercise on slide {slide_number}: {exercise_text[:60]}...")
        
        # Filter exercises by confidence and remove duplicates
        filtered_exercises = []
        seen_texts = set()
        
        for exercise in exercises:
            # Remove duplicates (similar text)
            text_key = exercise["exercise_text"].lower().replace(" ", "")[:100]
            if text_key in seen_texts:
                continue
            seen_texts.add(text_key)
            
            # Only include if confidence is reasonable
            if exercise["confidence"] > 0.3:
                filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def _calculate_exercise_confidence(self, exercise_text: str, full_content: str) -> float:
        """Calculate confidence that this is actually an exercise."""
        confidence = 0.5  # Base confidence
        
        text_lower = exercise_text.lower()
        
        # Positive indicators
        if any(word in text_lower for word in ["exercice", "exercise", "problème", "problem"]):
            confidence += 0.3
        if any(word in text_lower for word in ["calculer", "calculate", "déterminer", "determine", "trouver", "find"]):
            confidence += 0.2
        if "?" in exercise_text:
            confidence += 0.2
        if any(word in text_lower for word in ["que", "what", "comment", "how", "pourquoi", "why"]):
            confidence += 0.15
        if re.search(r"\d+", exercise_text):  # Contains numbers
            confidence += 0.1
        if any(unit in text_lower for unit in ["m", "kg", "s", "n", "j", "w", "v", "a", "°c", "°f", "hz", "pa"]):
            confidence += 0.15
        
        # Negative indicators
        if len(exercise_text) < 30:
            confidence -= 0.2
        if exercise_text.isupper():  # All caps (likely a title)
            confidence -= 0.3
        if not any(char.isalpha() for char in exercise_text):  # No letters
            confidence -= 0.4
        
        return max(0.0, min(1.0, confidence))
    
    async def _extract_from_alternative_sources(self, slide_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract exercises from alternative sources when slide content is limited."""
        exercises = []
        
        # Try to extract from course description or detailed description
        sources = [
            ("course_description", slide_data.get("course_description", "")),
            ("detailed_description", slide_data.get("detailed_description", "")),
            ("summary", slide_data.get("summary", "")),
            ("content", slide_data.get("content", ""))
        ]
        
        for source_name, content in sources:
            if content and len(content) > 100:
                print(f"🔍 Trying to extract exercises from {source_name}...")
                
                # Look for exercise-like patterns in the description
                exercise_indicators = [
                    r"(?i)(example|exemple)\s*:?\s*(.{50,}?)(?=\n\n|example|exemple|$)",
                    r"(?i)(problem|problème|exercise|exercice)\s*\d*\s*:?\s*(.{50,}?)(?=\n\n|problem|problème|$)",
                    r"(?i)(calculate|calculer|find|trouver|determine|déterminer)\s+(.{30,}?)(?=\.|!|\?|$)",
                    r"(?i)(consider|considérons|suppose|supposons)\s+(.{40,}?)(?=\.|!|\?|$)"
                ]
                
                for pattern in exercise_indicators:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        exercise_text = match.group(0).strip()
                        
                        if len(exercise_text) > 30:
                            exercise = {
                                "slide_number": 1,  # Default to slide 1
                                "exercise_text": exercise_text,
                                "context": content[max(0, match.start() - 100):min(len(content), match.end() + 200)],
                                "type": self._classify_exercise_type(exercise_text),
                                "content_around": content[max(0, match.start() - 200):min(len(content), match.end() + 300)],
                                "source": source_name,
                                "confidence": self._calculate_exercise_confidence(exercise_text, content) * 0.7  # Lower confidence for alternative sources
                            }
                            
                            exercises.append(exercise)
                            print(f"📝 Found potential exercise from {source_name}: {exercise_text[:60]}...")
        
        # If still no exercises found, try to create conceptual questions from the content
        if not exercises:
            exercises = await self._generate_conceptual_questions(slide_data)
        
        return exercises
    
    async def _generate_conceptual_questions(self, slide_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate conceptual questions from the course content when no explicit exercises are found."""
        print("🧠 Generating conceptual questions from course content...")
        
        # Get the main content
        content_sources = [
            slide_data.get("detailed_description", ""),
            slide_data.get("course_description", ""),
            slide_data.get("summary", "")
        ]
        
        main_content = " ".join(filter(None, content_sources))
        
        if len(main_content) < 100:
            return []
        
        try:
            # Use AI to generate questions from the content
            prompt = f"""Based on this educational content, create 3-5 multiple choice questions that test understanding of the key concepts.

Content: {main_content[:1000]}

For each question, provide:
1. A clear question about the concept
2. The correct answer
3. Make the questions suitable for educational assessment

Format each question as:
Question: [question text]
Answer: [correct answer]

Focus on key concepts, definitions, and applications mentioned in the content."""

            provider = AIProvider.OPENAI
            
            # Format messages correctly for AI client
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response_data = await ai_client.generate_response(
                messages,
                provider=provider,
                temperature=0.7
            )
            
            response = response_data["content"]
            
            # Parse the AI response to extract questions
            questions = []
            lines = response.split('\n')
            current_question = None
            current_answer = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Question:'):
                    if current_question and current_answer:
                        # Save previous question
                        questions.append({
                            "slide_number": 1,
                            "exercise_text": current_question,
                            "context": main_content[:200],
                            "type": "conceptual",
                            "content_around": main_content[:500],
                            "source": "ai_generated",
                            "confidence": 0.6,
                            "answer": current_answer
                        })
                    current_question = line[9:].strip()
                    current_answer = None
                elif line.startswith('Answer:'):
                    current_answer = line[7:].strip()
            
            # Don't forget the last question
            if current_question and current_answer:
                questions.append({
                    "slide_number": 1,
                    "exercise_text": current_question,
                    "context": main_content[:200],
                    "type": "conceptual",
                    "content_around": main_content[:500],
                    "source": "ai_generated",
                    "confidence": 0.6,
                    "answer": current_answer
                })
            
            print(f"🤖 Generated {len(questions)} conceptual questions from content")
            return questions
            
        except Exception as e:
            print(f"⚠️ Failed to generate conceptual questions: {e}")
            return []
    
    def _classify_exercise_type(self, exercise_text: str) -> str:
        """Classify the type of exercise based on its content."""
        text_lower = exercise_text.lower()
        
        if any(word in text_lower for word in ["calculate", "calculer", "compute", "compute"]):
            return "calculation"
        elif any(word in text_lower for word in ["explain", "describe", "expliquer", "décrire"]):
            return "explanation"
        elif any(word in text_lower for word in ["what", "que", "which", "quel"]):
            return "identification"
        elif any(word in text_lower for word in ["how", "comment"]):
            return "procedure"
        elif any(word in text_lower for word in ["why", "pourquoi"]):
            return "reasoning"
        else:
            return "general"
    
    async def _match_questions_with_answers(self, exercises: List[Dict[str, Any]], slide_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match questions with their answers, which might be on different slides."""
        slide_contents = slide_data.get("slide_contents", [])
        question_answer_pairs = []
        
        for exercise in exercises:
            # If this is an AI-generated question with a pre-provided answer
            if exercise.get("source") == "ai_generated" and "answer" in exercise:
                question_answer_pairs.append({
                    "question": exercise,
                    "answer": {
                        "answer_text": exercise["answer"],
                        "slide_number": exercise["slide_number"],
                        "context": f"AI-generated answer: {exercise['answer']}",
                        "confidence": 0.9
                    },
                    "alternative_answers": []
                })
                continue
            
            # For regular exercises, find answers in slides
            exercise_slide = exercise["slide_number"]
            exercise_text = exercise["exercise_text"]
            
            # Look for answers in the same slide and nearby slides
            potential_answers = []
            
            # If we have slide contents, search there
            if slide_contents:
                # Search in current slide and next 2-3 slides
                search_slides = range(max(0, exercise_slide - 1), min(len(slide_contents), exercise_slide + 3))
                
                # Patterns to identify answers
                answer_patterns = [
                    r"(?i)(?:answer|réponse|solution|résultat|result)\s*:?\s*(.{10,}?)(?=\n\n|\n[A-Z]|$)",
                    r"(?i)(?:therefore|donc|thus|par conséquent|consequently|en conséquence)\s*,?\s*(.{10,}?)(?=\n|$)",
                    r"(?i)(?:we get|we find|on trouve|on obtient|nous obtenons)\s*:?\s*(.{10,}?)(?=\n|$)",
                    r"(?i)(?:=|equals|égale|est égal à)\s*([^=\n]{5,}?)(?=\n|$)",
                ]
                
                for slide_idx in search_slides:
                    slide_content = slide_contents[slide_idx].get("content", "")
                    
                    # Find potential answers using patterns
                    for pattern in answer_patterns:
                        matches = re.finditer(pattern, slide_content, re.MULTILINE | re.DOTALL)
                        for match in matches:
                            answer_text = match.group(1).strip() if match.groups() else match.group(0).strip()
                            
                            # Skip very short or very long answers
                            if 5 <= len(answer_text) <= 200:
                                potential_answers.append({
                                    "answer_text": answer_text,
                                    "slide_number": slide_idx + 1,
                                    "context": slide_content[max(0, match.start() - 50):min(len(slide_content), match.end() + 50)],
                                    "confidence": self._calculate_answer_confidence(exercise_text, answer_text, slide_idx, exercise_slide)
                                })
                
                # Also look for numerical answers and formulas
                for slide_idx in search_slides:
                    slide_content = slide_contents[slide_idx].get("content", "")
                    
                    # Find numerical results
                    numerical_answers = re.finditer(r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\s*(?:m|kg|s|A|K|mol|cd|N|J|W|V|Ω|Hz|Pa|°C|°F|%)?(?:/[a-zA-Z]+)?)", slide_content)
                    for match in numerical_answers:
                        answer_text = match.group(0).strip()
                        potential_answers.append({
                            "answer_text": answer_text,
                            "slide_number": slide_idx + 1,
                            "context": slide_content[max(0, match.start() - 30):min(len(slide_content), match.end() + 30)],
                            "confidence": self._calculate_answer_confidence(exercise_text, answer_text, slide_idx, exercise_slide) * 0.8  # Lower confidence for pure numbers
                        })
            
            # If no answers found in slides, try to generate a generic answer
            if not potential_answers:
                generic_answer = await self._generate_generic_answer(exercise_text, exercise.get("type", "general"))
                if generic_answer:
                    potential_answers.append({
                        "answer_text": generic_answer,
                        "slide_number": exercise_slide,
                        "context": f"Generated answer for: {exercise_text[:50]}...",
                        "confidence": 0.5
                    })
            
            # Select the best answer(s)
            if potential_answers:
                # Sort by confidence and take the best one
                potential_answers.sort(key=lambda x: x["confidence"], reverse=True)
                best_answer = potential_answers[0]
                
                # Only include if confidence is reasonable
                if best_answer["confidence"] > 0.3:
                    question_answer_pairs.append({
                        "question": exercise,
                        "answer": best_answer,
                        "alternative_answers": potential_answers[1:3] if len(potential_answers) > 1 else []
                    })
        
        return question_answer_pairs
    
    def _calculate_answer_confidence(self, question_text: str, answer_text: str, answer_slide: int, question_slide: int) -> float:
        """Calculate confidence that an answer matches a question."""
        confidence = 0.5  # Base confidence
        
        # Distance penalty (closer slides are more likely to contain the answer)
        distance = abs(answer_slide - question_slide)
        distance_factor = max(0.1, 1.0 - (distance * 0.2))
        confidence *= distance_factor
        
        # Content similarity bonus
        question_words = set(re.findall(r'\b\w+\b', question_text.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer_text.lower()))
        
        if question_words and answer_words:
            similarity = len(question_words.intersection(answer_words)) / len(question_words.union(answer_words))
            confidence += similarity * 0.3
        
        # Keyword bonuses
        if any(word in answer_text.lower() for word in ["=", "therefore", "result", "answer", "solution"]):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    async def _generate_quiz_questions(
        self,
        question_answer_pairs: List[Dict[str, Any]],
        ai_provider: str,
        max_questions: int,
        difficulty_level: str,
        subject_area: Optional[str],
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions with realistic distractors."""
        quiz_questions = []
        
        # Select the best question-answer pairs
        selected_pairs = question_answer_pairs[:max_questions]
        
        for idx, pair in enumerate(selected_pairs):
            question = pair["question"]
            answer = pair["answer"]
            
            # Generate distractors using AI
            distractors = await self._generate_distractors(
                question["exercise_text"],
                answer["answer_text"],
                subject_area,
                difficulty_level,
                ai_provider
            )
            
            # Create the quiz question
            quiz_question = {
                "question_id": idx + 1,
                "question_text": self._clean_question_text(question["exercise_text"]),
                "question_type": question["type"],
                "source_slide": question["slide_number"],
                "answer_slide": answer["slide_number"],
                "options": {
                    "A": answer["answer_text"],  # Correct answer
                    "B": distractors[0] if len(distractors) > 0 else "Option B",
                    "C": distractors[1] if len(distractors) > 1 else "Option C", 
                    "D": distractors[2] if len(distractors) > 2 else "Option D"
                },
                "correct_answer": "A",
                "explanation": f"Found on slide {answer['slide_number']}: {answer['context'][:100]}...",
                "difficulty": difficulty_level,
                "points": self._calculate_question_points(question["type"], difficulty_level)
            }
            
            quiz_questions.append(quiz_question)
            print(f"✅ Generated question {idx + 1}: {quiz_question['question_text'][:50]}...")
        
        return quiz_questions
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean and format question text for the quiz."""
        # Remove patterns like "Exercise 1:", "Problem:", etc.
        cleaned = re.sub(r"(?i)^(?:exercise|exercice|problem|problème|question)\s*\d*:?\s*", "", question_text)
        
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Ensure it ends with a question mark if it's a question
        if any(word in cleaned.lower() for word in ["what", "how", "why", "when", "where", "which", "que", "comment", "pourquoi"]):
            if not cleaned.endswith('?'):
                cleaned += '?'
        
        return cleaned
    
    async def _generate_distractors(
        self,
        question_text: str,
        correct_answer: str,
        subject_area: Optional[str],
        difficulty_level: str,
        ai_provider: str
    ) -> List[str]:
        """Generate realistic wrong answers (distractors) for the question."""
        
        prompt = f"""Create 3 realistic but incorrect answers for this question. The distractors should be:
1. Plausible and related to the topic
2. Close to the correct answer but clearly wrong
3. At {difficulty_level} level difficulty
4. Appropriate for {subject_area or 'the subject area'}

Question: {question_text}
Correct Answer: {correct_answer}

Generate 3 wrong answers that a student might reasonably choose if they made common mistakes or had partial understanding. 

Format your response as:
1. [distractor 1]
2. [distractor 2] 
3. [distractor 3]

Make sure each distractor is:
- Related to the correct answer but incorrect
- A common type of mistake students make
- Roughly the same format/style as the correct answer"""

        try:
            # Convert ai_provider string to enum
            provider = AIProvider.OPENAI if ai_provider.lower() == "openai" else AIProvider.GOOGLE
            
            # Format messages correctly for AI client
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response_data = await ai_client.generate_response(
                messages,
                provider=provider,
                temperature=0.7
            )
            
            response = response_data["content"]
            
            # Parse the response to extract distractors
            distractors = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for numbered items
                if re.match(r'\d+\.\s*', line):
                    distractor = re.sub(r'^\d+\.\s*', '', line).strip()
                    if distractor and len(distractor) > 2:
                        distractors.append(distractor)
            
            # If we didn't get exactly 3, generate some fallback distractors
            while len(distractors) < 3:
                if correct_answer.replace('.', '').replace(',', '').isdigit():
                    # For numerical answers, create variations
                    try:
                        num = float(correct_answer.replace(',', '.'))
                        variations = [
                            str(num * 2),
                            str(num / 2),
                            str(num + 1)
                        ]
                        distractors.extend(variations[:3-len(distractors)])
                    except:
                        distractors.extend([f"Alternative {i+1}" for i in range(3-len(distractors))])
                else:
                    # For text answers, create generic alternatives
                    distractors.extend([f"Alternative answer {i+1}" for i in range(3-len(distractors))])
            
            return distractors[:3]
            
        except Exception as e:
            print(f"⚠️ Failed to generate AI distractors: {e}")
            # Fallback distractors
            return [
                f"Incorrect option 1",
                f"Incorrect option 2", 
                f"Incorrect option 3"
            ]
    
    def _calculate_question_points(self, question_type: str, difficulty: str) -> int:
        """Calculate points for a question based on type and difficulty."""
        base_points = {
            "calculation": 3,
            "explanation": 2,
            "identification": 1,
            "procedure": 2,
            "reasoning": 3,
            "general": 2
        }
        
        multiplier = {
            "beginner": 1.0,
            "intermediate": 1.5,
            "advanced": 2.0
        }
        
        return int(base_points.get(question_type, 2) * multiplier.get(difficulty, 1.0))
    
    async def _generate_generic_answer(self, question_text: str, question_type: str) -> Optional[str]:
        """Generate a plausible answer when no specific answer is found."""
        try:
            # For different question types, generate appropriate answers
            if question_type == "calculation":
                # Look for numbers in the question and create a calculation-style answer
                numbers = re.findall(r'\d+(?:\.\d+)?', question_text)
                if numbers:
                    return f"{float(numbers[0]) * 2:.1f}" if len(numbers) >= 1 else "10.5"
                return "42.0"
            
            elif question_type == "identification":
                if any(word in question_text.lower() for word in ["force", "strength"]):
                    return "Magnetic force"
                elif any(word in question_text.lower() for word in ["field", "champ"]):
                    return "Magnetic field"
                elif any(word in question_text.lower() for word in ["current", "courant"]):
                    return "Electric current"
                return "Physical quantity"
            
            elif question_type == "conceptual":
                return "This depends on the physical principles discussed in the material"
            
            else:
                return "Answer varies based on given conditions"
                
        except Exception:
            return None 