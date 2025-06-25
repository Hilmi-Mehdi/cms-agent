#!/usr/bin/env python3
"""
Complete Guide: How to Create Custom Tools for the AI Agent
"""

from typing import Dict, Any, List
from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult
import json
import re
import asyncio

# ==========================================
# Example 1: Simple Information Tool
# ==========================================

class CourseStatsTool(BaseTool):
    """Tool that analyzes course statistics and metrics."""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="course_stats",
            description="Analyze course content to extract statistics like reading time, complexity, prerequisites",
            parameters=[
                ToolParameter(
                    name="content",
                    type="string", 
                    description="Course content to analyze",
                    required=True
                ),
                ToolParameter(
                    name="analysis_depth",
                    type="string",
                    description="Level of analysis detail",
                    required=False,
                    default="basic",
                    enum=["basic", "detailed", "comprehensive"]
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the course stats analysis."""
        content = parameters.get("content", "")
        depth = parameters.get("analysis_depth", "basic")
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Basic stats
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # Assume 200 words per minute
        
        # Count different elements
        bullet_points = len(re.findall(r'^[-*•]\s+', content, re.MULTILINE))
        code_blocks = len(re.findall(r'```|`[^`]+`', content))
        urls = len(re.findall(r'https?://\S+', content))
        
        stats = {
            "word_count": word_count,
            "estimated_reading_time_minutes": reading_time,
            "bullet_points": bullet_points,
            "code_examples": code_blocks,
            "external_links": urls
        }
        
        if depth in ["detailed", "comprehensive"]:
            # More detailed analysis
            sentences = len(re.findall(r'[.!?]+', content))
            avg_sentence_length = word_count / max(1, sentences)
            complexity_score = min(10, avg_sentence_length / 2)  # Simple complexity metric
            
            stats.update({
                "sentence_count": sentences,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "complexity_score": round(complexity_score, 1),
                "difficulty_level": "beginner" if complexity_score < 3 else "intermediate" if complexity_score < 6 else "advanced"
            })
        
        if depth == "comprehensive":
            # Even more detailed analysis
            paragraphs = len([p for p in content.split('\n\n') if p.strip()])
            technical_terms = len(re.findall(r'\b[A-Z]{2,}|\b\w+(?:API|SDK|HTTP|JSON|XML|SQL)\b', content, re.IGNORECASE))
            
            stats.update({
                "paragraph_count": paragraphs,
                "technical_terms": technical_terms,
                "structure_quality": "good" if paragraphs > 2 and bullet_points > 0 else "basic"
            })
        
        return ToolResult(
            success=True,
            data=stats,
            message=f"Course statistics analyzed at {depth} level"
        )

# ==========================================
# Example 2: Tool with External API/Processing
# ==========================================

class CodeValidatorTool(BaseTool):
    """Tool that validates and checks code snippets in course content."""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="code_validator",
            description="Extract and validate code snippets from course content",
            parameters=[
                ToolParameter(
                    name="content",
                    type="string",
                    description="Course content containing code snippets",
                    required=True
                ),
                ToolParameter(
                    name="language",
                    type="string", 
                    description="Programming language to validate",
                    required=False,
                    default="python",
                    enum=["python", "javascript", "java", "cpp", "auto"]
                ),
                ToolParameter(
                    name="strict_mode",
                    type="boolean",
                    description="Whether to apply strict validation rules",
                    required=False,
                    default=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute code validation."""
        content = parameters.get("content", "")
        language = parameters.get("language", "python")
        strict_mode = parameters.get("strict_mode", False)
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        inline_code = re.findall(r'`([^`]+)`', content)
        
        validation_results = []
        
        for i, (lang_hint, code) in enumerate(code_blocks):
            # Determine language
            detected_lang = lang_hint or language
            if language == "auto":
                detected_lang = self._detect_language(code)
            
            # Validate code
            validation = await self._validate_code_snippet(code, detected_lang, strict_mode)
            validation_results.append({
                "block_number": i + 1,
                "language": detected_lang,
                "code_preview": code[:100] + "..." if len(code) > 100 else code,
                "is_valid": validation["valid"],
                "issues": validation["issues"],
                "suggestions": validation["suggestions"]
            })
        
        # Summary statistics
        total_blocks = len(code_blocks)
        valid_blocks = sum(1 for r in validation_results if r["is_valid"])
        total_issues = sum(len(r["issues"]) for r in validation_results)
        
        return ToolResult(
            success=True,
            data={
                "summary": {
                    "total_code_blocks": total_blocks,
                    "valid_blocks": valid_blocks,
                    "invalid_blocks": total_blocks - valid_blocks,
                    "total_issues": total_issues,
                    "inline_code_snippets": len(inline_code)
                },
                "validation_results": validation_results,
                "recommendations": self._generate_recommendations(validation_results)
            },
            message=f"Validated {total_blocks} code blocks with {total_issues} issues found"
        )
    
    def _detect_language(self, code: str) -> str:
        """Simple language detection based on syntax patterns."""
        if re.search(r'\bdef\b|\bimport\b|\bprint\(', code):
            return "python"
        elif re.search(r'\bfunction\b|\bconst\b|\blet\b|\bconsole\.log', code):
            return "javascript" 
        elif re.search(r'\bpublic class\b|\bSystem\.out\.print', code):
            return "java"
        elif re.search(r'#include|std::|cout', code):
            return "cpp"
        else:
            return "unknown"
    
    async def _validate_code_snippet(self, code: str, language: str, strict_mode: bool) -> Dict[str, Any]:
        """Validate a code snippet (simplified validation)."""
        await asyncio.sleep(0.05)  # Simulate processing
        
        issues = []
        suggestions = []
        
        # Basic syntax checks (simplified)
        if language == "python":
            if re.search(r'^[ \t]*[a-zA-Z]', code, re.MULTILINE) and not re.search(r'^def |^class |^import |^from ', code):
                # Check for basic Python structure
                pass
            
            # Check for common issues
            if 'print ' in code:  # Python 2 style print
                issues.append("Using Python 2 print statement (should be print() function)")
                suggestions.append("Replace 'print x' with 'print(x)'")
            
            if re.search(r'\btabs\t', code):
                issues.append("Mix of tabs and spaces detected")
                suggestions.append("Use consistent indentation (4 spaces recommended)")
        
        elif language == "javascript":
            if 'var ' in code and strict_mode:
                issues.append("Using 'var' instead of 'let' or 'const'")
                suggestions.append("Consider using 'let' or 'const' for better scoping")
        
        # Generic checks
        if len(code.strip()) == 0:
            issues.append("Empty code block")
        
        if len(code.split('\n')) > 50:
            suggestions.append("Consider breaking large code blocks into smaller examples")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _generate_recommendations(self, validation_results: List[Dict]) -> List[str]:
        """Generate overall recommendations based on validation results."""
        recommendations = []
        
        total_blocks = len(validation_results)
        invalid_blocks = sum(1 for r in validation_results if not r["is_valid"])
        
        if invalid_blocks > total_blocks * 0.3:
            recommendations.append("High number of code issues detected - consider reviewing all code examples")
        
        if any("Python 2" in str(r["issues"]) for r in validation_results):
            recommendations.append("Update Python 2 syntax to Python 3")
        
        if total_blocks > 10:
            recommendations.append("Consider creating a separate code repository for examples")
        
        return recommendations

# ==========================================
# Example 3: Tool that Uses AI for Processing
# ==========================================

class ContentEnhancerTool(BaseTool):
    """Tool that uses AI to enhance course content with examples, explanations, etc."""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="content_enhancer",
            description="Enhance course content by adding examples, clarifications, and practical applications",
            parameters=[
                ToolParameter(
                    name="content",
                    type="string",
                    description="Original course content to enhance",
                    required=True
                ),
                ToolParameter(
                    name="enhancement_type",
                    type="string",
                    description="Type of enhancement to apply",
                    required=True,
                    enum=["examples", "clarifications", "practical_applications", "analogies", "comprehensive"]
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience level",
                    required=False,
                    default="intermediate",
                    enum=["beginner", "intermediate", "advanced"]
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute content enhancement."""
        content = parameters.get("content", "")
        enhancement_type = parameters.get("enhancement_type", "examples")
        target_audience = parameters.get("target_audience", "intermediate")
        
        # Import AI client here to avoid circular imports
        from app.utils.ai_client import ai_client
        
        # Prepare enhancement prompt based on type
        enhancement_prompts = {
            "examples": f"Add practical examples to explain the concepts in this content for {target_audience} level students:",
            "clarifications": f"Add clarifying explanations and break down complex concepts for {target_audience} level:",
            "practical_applications": f"Add real-world applications and use cases for {target_audience} level:",
            "analogies": f"Add helpful analogies and metaphors to explain concepts for {target_audience} level:",
            "comprehensive": f"Comprehensively enhance this content with examples, clarifications, and applications for {target_audience} level:"
        }
        
        prompt = enhancement_prompts.get(enhancement_type, enhancement_prompts["examples"])
        
        messages = [
            {"role": "system", "content": "You are an expert educational content creator. Enhance the given content while maintaining its structure and accuracy."},
            {"role": "user", "content": f"{prompt}\n\n{content}"}
        ]
        
        try:
            # Use AI to enhance content
            ai_response = await ai_client.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            enhanced_content = ai_response.get("content", "")
            
            # Analyze what was added
            enhancement_analysis = self._analyze_enhancements(content, enhanced_content)
            
            return ToolResult(
                success=True,
                data={
                    "original_content": content,
                    "enhanced_content": enhanced_content,
                    "enhancement_type": enhancement_type,
                    "target_audience": target_audience,
                    "analysis": enhancement_analysis,
                    "usage_stats": ai_response.get("usage", {})
                },
                message=f"Content enhanced with {enhancement_type} for {target_audience} audience"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to enhance content: {str(e)}",
                data={"original_content": content}
            )
    
    def _analyze_enhancements(self, original: str, enhanced: str) -> Dict[str, Any]:
        """Analyze what enhancements were made."""
        return {
            "original_length": len(original),
            "enhanced_length": len(enhanced),
            "length_increase": len(enhanced) - len(original),
            "expansion_ratio": round(len(enhanced) / len(original), 2) if len(original) > 0 else 0,
            "new_examples_detected": enhanced.count("example") - original.count("example"),
            "new_sections_detected": enhanced.count("\n\n") - original.count("\n\n")
        }

# ==========================================
# How to Register and Use Custom Tools
# ==========================================

def register_custom_tools():
    """Register all custom tools with the agent."""
    from app.tools.base_tool import tool_registry
    
    # Register your custom tools
    tool_registry.register_tool(CourseStatsTool())
    tool_registry.register_tool(CodeValidatorTool()) 
    tool_registry.register_tool(ContentEnhancerTool())
    
    print("✅ Custom tools registered:")
    for tool_name in ["coursestats", "codevalidator", "contentenhancer"]:
        tool = tool_registry.get_tool(tool_name)
        if tool:
            print(f"   🔧 {tool_name}: {tool.definition.description}")

async def demo_custom_tools():
    """Demo how to use the custom tools."""
    from app.tools.base_tool import tool_registry
    
    print("🚀 Custom Tools Demo")
    print("=" * 50)
    
    # Demo 1: Course Stats Tool
    print("\n📊 Demo: Course Stats Tool")
    stats_tool = tool_registry.get_tool("coursestats")
    if stats_tool:
        result = await stats_tool.execute({
            "content": """
            # Python Functions
            
            Functions are reusable blocks of code that perform specific tasks.
            
            ## Basic Syntax
            ```python
            def function_name(parameters):
                return result
            ```
            
            - Functions improve code organization
            - They enable code reuse
            - Functions make debugging easier
            """,
            "analysis_depth": "comprehensive"
        })
        print(f"✅ Stats: {json.dumps(result.data, indent=2)}")
    
    # Demo 2: Code Validator Tool
    print("\n🔍 Demo: Code Validator Tool")
    validator_tool = tool_registry.get_tool("codevalidator")
    if validator_tool:
        result = await validator_tool.execute({
            "content": """
            Here's a Python example:
            ```python
            def greet(name):
                print "Hello, " + name
            ```
            
            And some inline code: `x = 5`
            """,
            "language": "python",
            "strict_mode": True
        })
        print(f"✅ Validation: {result.data['summary']}")
    
    # Demo 3: Content Enhancer Tool  
    print("\n✨ Demo: Content Enhancer Tool")
    enhancer_tool = tool_registry.get_tool("contentenhancer")
    if enhancer_tool:
        result = await enhancer_tool.execute({
            "content": "Variables store data in Python. Use descriptive names.",
            "enhancement_type": "examples",
            "target_audience": "beginner"
        })
        if result.success:
            print(f"✅ Enhanced content length: {result.data['analysis']['enhanced_length']} chars")
            print(f"📈 Expansion ratio: {result.data['analysis']['expansion_ratio']}x")

if __name__ == "__main__":
    # Register the tools
    register_custom_tools()
    
    # Demo them
    asyncio.run(demo_custom_tools()) 