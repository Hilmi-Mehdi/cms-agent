"""Content generator tool for creating educational materials."""

import asyncio
from typing import Dict, Any, List

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult
from app.utils.ai_client import ai_client


class ContentGeneratorTool(BaseTool):
    """Tool for generating educational content and materials."""
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="content_generator",
            description="Generate educational content such as summaries, exercises, quizzes, and explanations",
            parameters=[
                ToolParameter(
                    name="content_type",
                    type="string",
                    description="Type of content to generate",
                    required=True,
                    enum=["summary", "quiz", "exercises", "explanations", "study_guide", "flashcards", "outline"]
                ),
                ToolParameter(
                    name="source_content",
                    type="string",
                    description="Source content to base generation on",
                    required=True
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience level",
                    required=False,
                    default="intermediate",
                    enum=["beginner", "intermediate", "advanced", "expert"]
                ),
                ToolParameter(
                    name="length",
                    type="string",
                    description="Desired length of generated content",
                    required=False,
                    default="medium",
                    enum=["short", "medium", "long", "comprehensive"]
                ),
                ToolParameter(
                    name="focus_topics",
                    type="array",
                    description="Specific topics to focus on (optional)",
                    required=False
                ),
                ToolParameter(
                    name="format",
                    type="string",
                    description="Output format",
                    required=False,
                    default="markdown",
                    enum=["markdown", "html", "plain_text", "json"]
                ),
                ToolParameter(
                    name="include_examples",
                    type="boolean",
                    description="Whether to include practical examples",
                    required=False,
                    default=True
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute content generation."""
        content_type = parameters["content_type"]
        source_content = parameters["source_content"]
        target_audience = parameters.get("target_audience", "intermediate")
        length = parameters.get("length", "medium")
        focus_topics = parameters.get("focus_topics", [])
        format_type = parameters.get("format", "markdown")
        include_examples = parameters.get("include_examples", True)
        
        try:
            # Generate content based on type
            generated_content = await self._generate_content(
                content_type, source_content, target_audience, 
                length, focus_topics, format_type, include_examples
            )
            
            return ToolResult(
                success=True,
                data={
                    "content_type": content_type,
                    "generated_content": generated_content,
                    "metadata": {
                        "target_audience": target_audience,
                        "length": length,
                        "format": format_type,
                        "word_count": len(generated_content.get("text", "").split()),
                        "focus_topics": focus_topics
                    }
                },
                suggested_next_tools=self._suggest_next_tools(content_type),
                agent_notes=f"Generated {content_type} content for {target_audience} audience"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Content generation failed: {str(e)}"
            )
    
    async def _generate_content(
        self,
        content_type: str,
        source_content: str,
        target_audience: str,
        length: str,
        focus_topics: List[str],
        format_type: str,
        include_examples: bool
    ) -> Dict[str, Any]:
        """Generate content based on specified parameters."""
        
        # Create specialized prompts for different content types
        prompt_generators = {
            "summary": self._create_summary_prompt,
            "quiz": self._create_quiz_prompt,
            "exercises": self._create_exercises_prompt,
            "explanations": self._create_explanations_prompt,
            "study_guide": self._create_study_guide_prompt,
            "flashcards": self._create_flashcards_prompt,
            "outline": self._create_outline_prompt
        }
        
        prompt_generator = prompt_generators.get(content_type)
        if not prompt_generator:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Generate the prompt
        prompt = prompt_generator(
            source_content, target_audience, length, 
            focus_topics, format_type, include_examples
        )
        
        # Use AI to generate content
        messages = [
            {"role": "system", "content": "You are an expert educational content creator and instructional designer."},
            {"role": "user", "content": prompt}
        ]
        
        response = await ai_client.generate_response(
            messages=messages,
            temperature=0.7,  # Allow some creativity
            max_tokens=2000
        )
        
        # Parse and structure the generated content
        return self._parse_generated_content(response["content"], content_type, format_type)
    
    def _create_summary_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for summary generation."""
        focus_text = f"Focus particularly on: {', '.join(focus_topics)}" if focus_topics else ""
        examples_text = "Include practical examples and illustrations." if include_examples else ""
        
        length_guidance = {
            "short": "Keep it concise (2-3 paragraphs)",
            "medium": "Provide a moderate-length summary (4-6 paragraphs)",
            "long": "Create a detailed summary (7-10 paragraphs)",
            "comprehensive": "Provide a comprehensive summary covering all major points"
        }
        
        return f"""
Create a {length} summary of the following educational content for a {target_audience} audience.

{focus_text}
{examples_text}
{length_guidance.get(length, "")}

Format the output in {format_type}.

Source Content:
{source_content[:3000]}

Please provide a well-structured summary that captures the key concepts, main ideas, and important details.
"""
    
    def _create_quiz_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for quiz generation."""
        question_counts = {
            "short": "5-7 questions",
            "medium": "8-12 questions", 
            "long": "15-20 questions",
            "comprehensive": "25+ questions"
        }
        
        focus_text = f"Focus questions on: {', '.join(focus_topics)}" if focus_topics else ""
        
        return f"""
Create a quiz with {question_counts.get(length, "8-12 questions")} based on the following content for a {target_audience} audience.

{focus_text}

Include a variety of question types:
- Multiple choice (with 4 options)
- True/False
- Short answer
- Fill in the blank

For each question, provide:
1. The question
2. The correct answer
3. A brief explanation

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _create_exercises_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for exercises generation."""
        exercise_counts = {
            "short": "3-5 exercises",
            "medium": "6-8 exercises",
            "long": "9-12 exercises", 
            "comprehensive": "15+ exercises"
        }
        
        focus_text = f"Focus exercises on: {', '.join(focus_topics)}" if focus_topics else ""
        
        return f"""
Create {exercise_counts.get(length, "6-8 exercises")} based on the following content for a {target_audience} audience.

{focus_text}

Include different types of exercises:
- Practical applications
- Case studies
- Problem-solving scenarios
- Hands-on activities
- Critical thinking questions

For each exercise, provide:
1. Clear instructions
2. Expected outcomes
3. Sample solutions or approaches
4. Difficulty level

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _create_explanations_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for explanations generation."""
        focus_text = f"Focus explanations on: {', '.join(focus_topics)}" if focus_topics else ""
        examples_text = "Include concrete examples and analogies." if include_examples else ""
        
        return f"""
Create detailed explanations of the key concepts from the following content for a {target_audience} audience.

{focus_text}
{examples_text}

For each concept, provide:
1. Clear definition
2. Context and background
3. Step-by-step explanation
4. Real-world applications
5. Common misconceptions to avoid

Make the explanations accessible and engaging for the target audience.

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _create_study_guide_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for study guide generation."""
        focus_text = f"Emphasize: {', '.join(focus_topics)}" if focus_topics else ""
        
        return f"""
Create a comprehensive study guide based on the following content for a {target_audience} audience.

{focus_text}

Structure the study guide with:
1. Key concepts and definitions
2. Important formulas or principles
3. Summary of main points
4. Study tips and strategies
5. Self-assessment questions
6. Additional resources or readings

Make it practical and actionable for effective studying.

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _create_flashcards_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for flashcards generation."""
        card_counts = {
            "short": "10-15 flashcards",
            "medium": "20-30 flashcards",
            "long": "35-50 flashcards",
            "comprehensive": "50+ flashcards"
        }
        
        focus_text = f"Focus on: {', '.join(focus_topics)}" if focus_topics else ""
        
        return f"""
Create {card_counts.get(length, "20-30 flashcards")} based on the following content for a {target_audience} audience.

{focus_text}

For each flashcard, provide:
- Front: Question, term, or prompt
- Back: Answer, definition, or explanation

Include different types:
- Definitions and terminology
- Key concepts
- Facts and figures
- Relationships and connections
- Application scenarios

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _create_outline_prompt(
        self, source_content: str, target_audience: str, length: str, 
        focus_topics: List[str], format_type: str, include_examples: bool
    ) -> str:
        """Create prompt for outline generation."""
        focus_text = f"Emphasize: {', '.join(focus_topics)}" if focus_topics else ""
        
        return f"""
Create a detailed outline of the following content for a {target_audience} audience.

{focus_text}

Structure the outline with:
1. Main topics (Level 1 headers)
2. Subtopics (Level 2 headers)
3. Key points (Level 3 headers)
4. Supporting details and examples
5. Logical flow and connections

Make it hierarchical and easy to follow.

Format the output in {format_type}.

Source Content:
{source_content[:3000]}
"""
    
    def _parse_generated_content(
        self, ai_response: str, content_type: str, format_type: str
    ) -> Dict[str, Any]:
        """Parse and structure the generated content."""
        result = {
            "text": ai_response,
            "format": format_type,
            "content_type": content_type
        }
        
        # Add content-specific parsing
        if content_type == "quiz":
            result["questions"] = self._extract_quiz_questions(ai_response)
        elif content_type == "flashcards":
            result["cards"] = self._extract_flashcards(ai_response)
        elif content_type == "outline":
            result["structure"] = self._extract_outline_structure(ai_response)
        
        return result
    
    def _extract_quiz_questions(self, content: str) -> List[Dict[str, Any]]:
        """Extract quiz questions from generated content."""
        # Simplified extraction - in practice, you'd want more sophisticated parsing
        questions = []
        lines = content.split('\n')
        
        current_question = None
        for line in lines:
            line = line.strip()
            if line.startswith(('Q:', 'Question:', '**Q')):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": line, "options": [], "answer": "", "explanation": ""}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')) and current_question:
                current_question["options"].append(line)
            elif line.startswith(('Answer:', 'Correct:', '**Answer')) and current_question:
                current_question["answer"] = line
            elif line.startswith(('Explanation:', '**Explanation')) and current_question:
                current_question["explanation"] = line
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _extract_flashcards(self, content: str) -> List[Dict[str, str]]:
        """Extract flashcards from generated content."""
        cards = []
        lines = content.split('\n')
        
        current_card = None
        for line in lines:
            line = line.strip()
            if line.startswith(('Front:', '**Front', 'Q:')):
                if current_card:
                    cards.append(current_card)
                current_card = {"front": line, "back": ""}
            elif line.startswith(('Back:', '**Back', 'A:')) and current_card:
                current_card["back"] = line
        
        if current_card:
            cards.append(current_card)
        
        return cards
    
    def _extract_outline_structure(self, content: str) -> Dict[str, Any]:
        """Extract outline structure from generated content."""
        structure = {"levels": []}
        lines = content.split('\n')
        
        for line in lines:
            if line.strip():
                # Count leading spaces or detect markdown headers
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    text = line.lstrip('#').strip()
                    structure["levels"].append({"level": level, "text": text})
                elif line.startswith(('I.', '1.', 'A.', 'a.')):
                    # Roman numerals or numbered lists
                    structure["levels"].append({"level": 1, "text": line.strip()})
        
        return structure
    
    def _suggest_next_tools(self, content_type: str) -> List[str]:
        """Suggest next tools based on content type."""
        suggestions = {
            "summary": ["content_analyzer", "quality_assessor"],
            "quiz": ["exam_processor", "quality_assessor"],
            "exercises": ["exercise_matcher", "quality_assessor"],
            "explanations": ["content_analyzer"],
            "study_guide": ["learning_path_builder"],
            "flashcards": ["content_analyzer"],
            "outline": ["structure_extractor", "learning_path_builder"]
        }
        
        return suggestions.get(content_type, ["quality_assessor"]) 