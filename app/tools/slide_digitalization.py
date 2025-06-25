"""
Slide Digitalization Tool: Extract and digitize all content from slide images
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


class SlideDigitalizationTool(BaseTool):
    """Tool that digitizes slide content by extracting all text, formulas, and visual elements using AI vision."""
    
    def get_definition(self) -> ToolDefinition:
        description = "Digitize slide content by extracting all text, formulas, and visual elements into structured JSON"
        if PDF_SUPPORT_AVAILABLE:
            description += " (supports images and PDF files)"
        
        return ToolDefinition(
            name="slide_digitalization",
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
                    description="AI provider to use for content extraction",
                    required=False,
                    default="openai",
                    enum=["openai", "google"]
                ),
                ToolParameter(
                    name="language",
                    type="string",
                    description="Expected language of the slides",
                    required=False,
                    default="auto-detect",
                    enum=["english", "french", "auto-detect"]
                ),
                ToolParameter(
                    name="extract_formulas",
                    type="boolean",
                    description="Whether to extract and format mathematical formulas",
                    required=False,
                    default=True
                ),
                ToolParameter(
                    name="extract_diagrams",
                    type="boolean",
                    description="Whether to describe diagrams and visual elements",
                    required=False,
                    default=True
                ),
                ToolParameter(
                    name="preserve_structure",
                    type="boolean",
                    description="Whether to preserve original slide structure (bullets, sections, etc.)",
                    required=False,
                    default=True
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute slide digitalization."""
        start_time = time.monotonic()
        
        try:
            slide_images = parameters.get("slide_images", [])
            ai_provider = parameters.get("ai_provider", "openai")
            language = parameters.get("language", "auto-detect")
            extract_formulas = parameters.get("extract_formulas", True)
            extract_diagrams = parameters.get("extract_diagrams", True)
            preserve_structure = parameters.get("preserve_structure", True)
            
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
            
            # Digitize slides
            digitization_result = await self._digitize_slides(
                validated_images,
                provider,
                language,
                extract_formulas,
                extract_diagrams,
                preserve_structure
            )
            
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            
            return ToolResult(
                success=True,
                data=digitization_result,
                execution_time=execution_time,
                agent_notes=f"Digitized {len(digitization_result.get('slides', []))} slides in {execution_time}s using {provider.value}"
            )
            
        except Exception as e:
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            return ToolResult(
                success=False,
                error=f"Slide digitalization failed: {str(e)}",
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
                            # Use high DPI for text clarity in digitalization
                            pdf_images = pdf_processor.pdf_to_images(img, dpi=350, max_pages=50)
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
                        pdf_images = pdf_processor.pdf_to_images(img, dpi=350, max_pages=50)
                        validated.extend(pdf_images)
                        print(f"Successfully converted {len(pdf_images)} pages from PDF bytes")
                    except Exception as e:
                        print(f"ERROR: Failed to convert PDF bytes: {e}")
                        continue
                else:
                    # Assume it's image bytes
                    validated.append(img)
        
        return validated
    
    async def _digitize_slides(
        self,
        images: List[Union[str, bytes]],
        provider: AIProvider,
        language: str,
        extract_formulas: bool,
        extract_diagrams: bool,
        preserve_structure: bool
    ) -> Dict[str, Any]:
        """Digitize slides by extracting all content using AI vision."""
        
        # Create comprehensive digitalization prompt
        prompt = self._create_digitalization_prompt(
            language, extract_formulas, extract_diagrams, preserve_structure
        )
        
        try:
            response = await ai_client.analyze_images(
                images=images,
                prompt=prompt,
                provider=provider,
                temperature=0.1  # Low temperature for accurate extraction
            )
            
            # Extract and structure the digitized content
            digitized_data = self._extract_digitized_content(response["content"])
            
            # Add metadata
            digitized_data["digitalization_metadata"] = {
                "provider": response["provider"],
                "model": response["model"],
                "images_processed": response.get("images_analyzed", len(images)),
                "usage_stats": response.get("usage", {}),
                "extraction_parameters": {
                    "language": language,
                    "extract_formulas": extract_formulas,
                    "extract_diagrams": extract_diagrams,
                    "preserve_structure": preserve_structure
                }
            }
            
            return digitized_data
            
        except Exception as e:
            raise Exception(f"Slide digitalization failed: {str(e)}")
    
    def _create_digitalization_prompt(
        self,
        language: str,
        extract_formulas: bool,
        extract_diagrams: bool,
        preserve_structure: bool
    ) -> str:
        """Create a comprehensive digitalization prompt."""
        
        language_instruction = ""
        if language == "french":
            language_instruction = "Extract all content in FRENCH. Preserve original French text exactly."
        elif language == "english":
            language_instruction = "Extract all content in ENGLISH. Preserve original English text exactly."
        else:
            language_instruction = "Detect the language and preserve all text in its original language (French or English)."
        
        formula_instruction = ""
        if extract_formulas:
            formula_instruction = """
- Extract all mathematical formulas, equations, and scientific notation
- Convert complex formulas to clear text representation (e.g., E = mc² → E = m × c²)
- Preserve Greek letters as text (e.g., α → alpha, β → beta, Φ → phi)
- Include units and measurements exactly as shown"""
        
        diagram_instruction = ""
        if extract_diagrams:
            diagram_instruction = """
- Describe all diagrams, charts, graphs, and visual elements
- Include figure captions and labels
- Describe the layout and relationships shown in visuals
- Note any arrows, connections, or flow directions"""
        
        structure_instruction = ""
        if preserve_structure:
            structure_instruction = """
- Preserve bullet points, numbering, and indentation
- Maintain section headers and subheaders
- Keep the original organization and hierarchy
- Preserve table structures if present"""
        
        prompt = f"""
EXPERT SLIDE DIGITALIZATION SYSTEM

Analyze these slide images and extract ALL visible content with complete accuracy. Your goal is to create a perfect digital copy of the slide content.

CRITICAL: Process slides in the EXACT ORDER they are provided. Slide 1 = first image, Slide 2 = second image, etc.

INSTRUCTIONS:
{language_instruction}

CONTENT EXTRACTION REQUIREMENTS:
1. Extract EVERY piece of text visible on each slide
2. Include titles, headers, body text, footnotes, and annotations
3. Preserve exact wording, spelling, and punctuation
4. Do not summarize, rephrase, or interpret - extract exactly as written
5. MAINTAIN SLIDE ORDER: Process images sequentially (1st image = slide 1, 2nd image = slide 2, etc.)
{formula_instruction}
{diagram_instruction}
{structure_instruction}

QUALITY STANDARDS:
- Zero tolerance for missing content
- Exact text reproduction (character-perfect accuracy)
- Complete coverage of all visual elements
- Proper slide-by-slide organization
- Clear identification of content types (text, formula, diagram, etc.)

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure:
{{
  "document_title": "Overall title or subject based on content",
  "language_detected": "french|english|mixed",
  "total_slides": number,
  "slides": [
    {{
      "slide_number": 1,
      "slide_title": "Main title/header of the slide",
      "content_sections": [
        {{
          "section_type": "title|text|formula|diagram|bullet_list|table",
          "content": "Exact text or description",
          "formatting": {{
            "is_bold": true/false,
            "is_italic": true/false,
            "font_size": "large|medium|small",
            "alignment": "left|center|right"
          }},
          "position": "top|middle|bottom|left|right"
        }}
      ],
      "formulas": [
        {{
          "formula_text": "Complete formula in text format",
          "context": "Where this formula appears",
          "variables_defined": ["variable definitions if shown"]
        }}
      ],
      "diagrams": [
        {{
          "description": "Complete description of visual element",
          "type": "graph|chart|diagram|figure|table",
          "labels": ["all visible labels and captions"],
          "relationships": "connections and flows shown"
        }}
      ],
      "footnotes": ["any footnotes or small text"],
      "page_references": ["any page numbers or references shown"]
    }}
  ],
  "extraction_summary": {{
    "total_text_blocks": number,
    "total_formulas": number,
    "total_diagrams": number,
    "completeness_confidence": "high|medium|low"
  }}
}}

CRITICAL REMINDERS:
- Extract EVERYTHING visible - no content should be missed
- Maintain exact text accuracy - do not change wording
- Organize content logically by slide IN THE EXACT ORDER PROVIDED
- SLIDE NUMBERING: First image = slide_number: 1, Second image = slide_number: 2, etc.
- Include ALL visual elements and their descriptions
- Preserve the original language and formatting intent

Begin comprehensive digitalization now:
"""
        
        return prompt
    
    def _extract_digitized_content(self, response_text: str) -> Dict[str, Any]:
        """Extract and validate digitized content from AI response."""
        
        try:
            # Try multiple approaches to extract JSON (similar to quiz generator)
            import re
            
            # Method 1: Try to parse the entire response as JSON
            try:
                cleaned_response = response_text.strip()
                digitized_data = json.loads(cleaned_response)
                return self._validate_digitized_data(digitized_data)
            except json.JSONDecodeError:
                pass
            
            # Method 2: Find JSON using bracket matching
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
                        digitized_data = json.loads(json_str)
                        return self._validate_digitized_data(digitized_data)
                    except json.JSONDecodeError:
                        # Try fixing common issues
                        fixed_json = self._fix_json_issues(json_str)
                        try:
                            digitized_data = json.loads(fixed_json)
                            return self._validate_digitized_data(digitized_data)
                        except json.JSONDecodeError as e:
                            print(f"JSON parsing failed: {e}")
            
            # If JSON extraction fails, create fallback structure
            print("Failed to extract valid JSON from digitalization response")
            return self._create_fallback_digitization(response_text)
                
        except Exception as e:
            print(f"Unexpected error in digitalization extraction: {e}")
            return self._create_fallback_digitization(response_text)
    
    def _fix_json_issues(self, json_str: str) -> str:
        """Fix common JSON issues (reuse from quiz generator)."""
        import re
        
        # Start with the original string
        fixed = json_str
        
        # Fix common French character issues
        try:
            if isinstance(fixed, bytes):
                fixed = fixed.decode('utf-8', errors='replace')
            
            # Fix common escaping issues with French characters
            fixed = re.sub(r'(?<!\\)"([^"]*[àâäéèêëïîôöùûüÿç][^"]*)"(?=\s*[,}\]])', r'"\1"', fixed)
        except Exception:
            pass
        
        # Fix other common JSON issues
        try:
            fixed = re.sub(r'([^\\])\\([^"\\nrtbf/])', r'\1\\\\\\2', fixed)
            fixed = re.sub(r'\\n(?!")', r'\\\\n', fixed)
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        except Exception:
            pass
        
        return fixed
    
    def _validate_digitized_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean digitized data structure."""
        
        # Ensure required fields
        data.setdefault("document_title", "Digitized Slides")
        data.setdefault("language_detected", "auto-detected")
        data.setdefault("total_slides", len(data.get("slides", [])))
        data.setdefault("slides", [])
        
        # Validate slides
        validated_slides = []
        for i, slide in enumerate(data.get("slides", [])):
            if isinstance(slide, dict):
                validated_slide = {
                    "slide_number": slide.get("slide_number", i + 1),
                    "slide_title": slide.get("slide_title", f"Slide {i + 1}"),
                    "content_sections": slide.get("content_sections", []),
                    "formulas": slide.get("formulas", []),
                    "diagrams": slide.get("diagrams", []),
                    "footnotes": slide.get("footnotes", []),
                    "page_references": slide.get("page_references", [])
                }
                validated_slides.append(validated_slide)
        
        # Sort slides by slide number to ensure correct order
        validated_slides.sort(key=lambda x: x["slide_number"])
        
        data["slides"] = validated_slides
        data["total_slides"] = len(validated_slides)
        
        # Add extraction summary if missing
        if "extraction_summary" not in data:
            total_text_blocks = sum(len(slide.get("content_sections", [])) for slide in validated_slides)
            total_formulas = sum(len(slide.get("formulas", [])) for slide in validated_slides)
            total_diagrams = sum(len(slide.get("diagrams", [])) for slide in validated_slides)
            
            data["extraction_summary"] = {
                "total_text_blocks": total_text_blocks,
                "total_formulas": total_formulas,
                "total_diagrams": total_diagrams,
                "completeness_confidence": "high" if total_text_blocks > 0 else "low"
            }
        
        return data
    
    def _create_fallback_digitization(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback digitization structure if JSON extraction fails."""
        
        return {
            "document_title": "Digitization Failed",
            "language_detected": "unknown",
            "total_slides": 0,
            "slides": [],
            "extraction_summary": {
                "total_text_blocks": 0,
                "total_formulas": 0,
                "total_diagrams": 0,
                "completeness_confidence": "low"
            },
            "error": "Failed to parse digitization from AI response",
            "raw_response": response_text[:1000] + "..." if len(response_text) > 1000 else response_text
        } 