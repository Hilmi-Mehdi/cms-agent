"""Content analyzer tool for extracting information from course materials."""

import asyncio
from typing import Dict, Any, List

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult, CourseAnalysis
from app.utils.ai_client import ai_client


class ContentAnalyzerTool(BaseTool):
    """Tool for analyzing course content and extracting key information."""
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="content_analyzer",
            description="Analyze course content to extract key concepts, learning objectives, and structure",
            parameters=[
                ToolParameter(
                    name="content",
                    type="string",
                    description="The course content to analyze (text, markdown, or extracted from files)",
                    required=True
                ),
                ToolParameter(
                    name="analysis_type",
                    type="string",
                    description="Type of analysis to perform",
                    required=False,
                    default="comprehensive",
                    enum=["comprehensive", "structure", "concepts", "objectives", "difficulty"]
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience for the course content",
                    required=False,
                    default="general"
                ),
                ToolParameter(
                    name="subject_area",
                    type="string",
                    description="Subject area or domain of the course",
                    required=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute content analysis."""
        content = parameters["content"]
        analysis_type = parameters.get("analysis_type", "comprehensive")
        target_audience = parameters.get("target_audience", "general")
        subject_area = parameters.get("subject_area", "")
        
        try:
            # Create analysis prompt based on type
            prompt = self._create_analysis_prompt(
                content, analysis_type, target_audience, subject_area
            )
            
            # Use AI to analyze content
            messages = [
                {"role": "system", "content": "You are an expert educational content analyst."},
                {"role": "user", "content": prompt}
            ]
            
            response = await ai_client.generate_response(
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the analysis result
            analysis_result = self._parse_analysis_result(response["content"], analysis_type)
            
            return ToolResult(
                success=True,
                data=analysis_result,
                suggested_next_tools=self._suggest_next_tools(analysis_type),
                agent_notes=f"Analyzed {len(content)} characters of {analysis_type} content"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Content analysis failed: {str(e)}"
            )
    
    def _create_analysis_prompt(
        self, 
        content: str, 
        analysis_type: str, 
        target_audience: str, 
        subject_area: str
    ) -> str:
        """Create analysis prompt based on type."""
        base_context = f"""
Analyze the following course content for a {target_audience} audience.
{f"Subject area: {subject_area}" if subject_area else ""}

Content to analyze:
{content[:4000]}  # Limit content length
"""
        
        if analysis_type == "comprehensive":
            return base_context + """
Provide a comprehensive analysis including:
1. Course title and description
2. Key concepts and topics covered
3. Learning objectives
4. Difficulty level (beginner/intermediate/advanced)
5. Estimated duration
6. Prerequisites
7. Content structure and organization
8. Assessment opportunities

Format your response as structured data that can be parsed.
"""
        
        elif analysis_type == "structure":
            return base_context + """
Analyze the structure and organization of this content:
1. Main sections and subsections
2. Logical flow and sequence
3. Content hierarchy
4. Module or chapter breakdown
5. Dependencies between sections

Provide a structured outline of the content organization.
"""
        
        elif analysis_type == "concepts":
            return base_context + """
Extract and analyze the key concepts:
1. Primary concepts and topics
2. Secondary supporting concepts
3. Relationships between concepts
4. Concept difficulty progression
5. Knowledge dependencies

List the concepts in order of introduction and complexity.
"""
        
        elif analysis_type == "objectives":
            return base_context + """
Identify and analyze learning objectives:
1. Explicit learning objectives mentioned
2. Implicit objectives based on content
3. Cognitive levels (knowledge, comprehension, application, etc.)
4. Measurable outcomes
5. Skills and competencies developed

Format as clear, actionable learning objectives.
"""
        
        elif analysis_type == "difficulty":
            return base_context + """
Assess the difficulty and complexity:
1. Overall difficulty level
2. Prerequisite knowledge required
3. Cognitive load assessment
4. Complexity progression
5. Challenging sections or concepts

Provide recommendations for different audience levels.
"""
        
        return base_context + "Provide a general analysis of this course content."
    
    def _parse_analysis_result(self, ai_response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse AI response into structured analysis result."""
        # This is a simplified parser - in practice, you might want more sophisticated parsing
        result = {
            "analysis_type": analysis_type,
            "raw_analysis": ai_response,
            "extracted_data": {}
        }
        
        # Try to extract structured information
        lines = ai_response.split('\n')
        current_section = None
        sections = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for section headers (numbered or with colons)
            if ':' in line and len(line) < 100:
                current_section = line.split(':')[0].strip()
                sections[current_section] = []
            elif current_section and line:
                sections[current_section].append(line)
        
        result["extracted_data"] = sections
        
        # Create CourseAnalysis object for comprehensive analysis
        if analysis_type == "comprehensive":
            try:
                course_analysis = self._create_course_analysis(sections, ai_response)
                result["course_analysis"] = course_analysis.dict()
            except Exception as e:
                result["parse_error"] = str(e)
        
        return result
    
    def _create_course_analysis(self, sections: Dict[str, List[str]], full_text: str) -> CourseAnalysis:
        """Create structured CourseAnalysis from parsed sections."""
        # Extract information from sections
        title = self._extract_title(sections, full_text)
        description = self._extract_description(sections, full_text)
        key_concepts = self._extract_list_items(sections, ["key concepts", "concepts", "topics"])
        learning_objectives = self._extract_list_items(sections, ["learning objectives", "objectives"])
        difficulty_level = self._extract_difficulty(sections, full_text)
        
        return CourseAnalysis(
            title=title,
            description=description,
            key_concepts=key_concepts,
            learning_objectives=learning_objectives,
            difficulty_level=difficulty_level,
            content_structure=sections
        )
    
    def _extract_title(self, sections: Dict[str, List[str]], full_text: str) -> str:
        """Extract course title from analysis."""
        for key in ["title", "course title", "name"]:
            if key in sections and sections[key]:
                return sections[key][0]
        return "Untitled Course"
    
    def _extract_description(self, sections: Dict[str, List[str]], full_text: str) -> str:
        """Extract course description."""
        for key in ["description", "course description", "overview"]:
            if key in sections and sections[key]:
                return ' '.join(sections[key])
        return ""
    
    def _extract_list_items(self, sections: Dict[str, List[str]], possible_keys: List[str]) -> List[str]:
        """Extract list items from sections."""
        items = []
        for key in possible_keys:
            for section_key in sections:
                if key.lower() in section_key.lower() and sections[section_key]:
                    items.extend(sections[section_key])
                    break
        return items[:10]  # Limit to top 10 items
    
    def _extract_difficulty(self, sections: Dict[str, List[str]], full_text: str) -> str:
        """Extract difficulty level."""
        difficulty_keywords = {
            "beginner": ["beginner", "basic", "introductory", "fundamental"],
            "intermediate": ["intermediate", "moderate", "standard"],
            "advanced": ["advanced", "expert", "complex", "sophisticated"]
        }
        
        text_lower = full_text.lower()
        for level, keywords in difficulty_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return "intermediate"  # Default
    
    def _suggest_next_tools(self, analysis_type: str) -> List[str]:
        """Suggest next tools based on analysis type."""
        suggestions = {
            "comprehensive": ["quality_assessor", "structure_extractor"],
            "structure": ["learning_path_builder"],
            "concepts": ["exercise_matcher"],
            "objectives": ["exam_processor"],
            "difficulty": ["content_optimizer"]
        }
        
        return suggestions.get(analysis_type, ["quality_assessor"]) 