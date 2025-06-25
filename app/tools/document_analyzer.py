"""Document analyzer tool for comprehensive analysis of Science Made Simple documents."""

import asyncio
from typing import Dict, Any, List, Optional

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult, AIProvider
from app.tools.base_tool import tool_registry


class DocumentAnalyzerTool(BaseTool):
    """Tool for comprehensive analysis of documents from Science Made Simple API."""
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="document_analyzer",
            description="Analyze documents from Science Made Simple API by fetching, extracting images, and performing slide analysis",
            parameters=[
                ToolParameter(
                    name="document_id",
                    type="string",
                    description="The document ID to fetch and analyze from the Science Made Simple API",
                    required=True
                ),
                ToolParameter(
                    name="ai_provider",
                    type="string",
                    description="AI provider for analysis",
                    required=False,
                    default="openai",
                    enum=["openai", "google"]
                ),
                ToolParameter(
                    name="analysis_depth",
                    type="string",
                    description="Depth of analysis to perform",
                    required=False,
                    default="comprehensive",
                    enum=["basic", "detailed", "comprehensive"]
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience for the analysis",
                    required=False,
                    default="general",
                    enum=["beginner", "intermediate", "advanced", "general"]
                ),
                ToolParameter(
                    name="subject_area",
                    type="string",
                    description="Subject area of the content (auto-detect if not specified)",
                    required=False
                ),
                ToolParameter(
                    name="max_images",
                    type="number",
                    description="Maximum number of images to analyze",
                    required=False,
                    default=25
                ),
                ToolParameter(
                    name="sms_api_key",
                    type="string",
                    description="Science Made Simple API key (uses default if not provided)",
                    required=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute comprehensive document analysis."""
        document_id = parameters["document_id"]
        ai_provider = parameters.get("ai_provider", "openai")
        analysis_depth = parameters.get("analysis_depth", "comprehensive")
        target_audience = parameters.get("target_audience", "general")
        subject_area = parameters.get("subject_area")
        max_images = parameters.get("max_images", 25)
        sms_api_key = parameters.get("sms_api_key", "4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5")  # Default API key
        
        try:
            # Get required tools
            document_fetcher = tool_registry.get_tool("documentfetcher")
            slide_analyzer = tool_registry.get_tool("slideanalyzer")
            content_generator = tool_registry.get_tool("contentgenerator")
            
            if not document_fetcher:
                return ToolResult(
                    success=False,
                    error="Document fetcher tool not available"
                )
            
            print(f"📄 Fetching document {document_id}...")
            
            # Use a custom version of document fetching that keeps files for analysis
            result_data = await self._fetch_and_analyze_document(
                document_id=document_id,
                sms_api_key=sms_api_key,
                max_images=max_images,
                ai_provider=ai_provider,
                analysis_depth=analysis_depth,
                target_audience=target_audience,
                subject_area=subject_area,
                slide_analyzer=slide_analyzer,
                content_generator=content_generator
            )
            
            if not result_data.get("success"):
                return ToolResult(
                    success=False,
                    error=result_data.get("error", "Unknown error occurred")
                )
            
            # Suggest next tools
            next_tools = []
            if "slide_analysis" in result_data:
                next_tools.extend(["content_generator", "content_analyzer"])
            
            return ToolResult(
                success=True,
                data=result_data,
                suggested_next_tools=next_tools,
                agent_notes=f"Analyzed document '{result_data.get('document_metadata', {}).get('Name', document_id)}' with {result_data.get('images_analyzed', 0)} images"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Document analysis failed: {str(e)}"
            )
    
    async def _fetch_and_analyze_document(
        self,
        document_id: str,
        sms_api_key: str,
        max_images: int,
        ai_provider: str,
        analysis_depth: str,
        target_audience: str,
        subject_area: Optional[str],
        slide_analyzer,
        content_generator
    ) -> Dict[str, Any]:
        """Fetch document and analyze slides while temp files exist."""
        import tempfile
        import httpx
        import tarfile
        import shutil
        from pathlib import Path
        
        try:
            # Step 1: Fetch document metadata
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://app.sciencemadesimple.io/api/_integration/get_document",
                    params={"id": document_id},
                    headers={"SMS-Access-Key": sms_api_key}
                )
                response.raise_for_status()
                document_metadata = response.json()
            
            print(f"✅ Document fetched: {document_metadata.get('Name', 'Unknown')}")
            
            result_data = {
                "success": True,
                "document_id": document_id,
                "document_metadata": document_metadata
            }
            
            # Step 2: Extract images and analyze immediately
            urls = document_metadata.get("URLs", {})
            image_archive_url = urls.get("ImageArchive100URL")
            
            if image_archive_url and image_archive_url != "url":
                print(f"📥 Downloading and extracting images...")
                
                # Create temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    tar_file_path = temp_path / "images.tar"
                    
                    # Download tar file
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        tar_response = await client.get(image_archive_url)
                        tar_response.raise_for_status()
                        
                        with open(tar_file_path, "wb") as f:
                            f.write(tar_response.content)
                    
                    # Extract tar file safely
                    with tarfile.open(tar_file_path, "r") as tar:
                        extracted_count = 0
                        image_paths = []
                        
                        for member in tar.getmembers():
                            if member.isfile():
                                # Convert absolute path to relative
                                safe_name = member.name.lstrip('/').replace('..', '_')
                                member.name = safe_name
                                
                                try:
                                    tar.extract(member, temp_path)
                                    
                                    # Check if it's an image file
                                    extracted_file = temp_path / safe_name
                                    if extracted_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}:
                                        if extracted_count < max_images:
                                            image_paths.append(str(extracted_file))
                                            extracted_count += 1
                                except Exception:
                                    continue
                    
                    print(f"🖼️  Extracted {len(image_paths)} images")
                    result_data["images_analyzed"] = len(image_paths)
                    
                    # Step 3: Analyze slides while files exist
                    if image_paths and slide_analyzer:
                        print(f"🔍 Analyzing {len(image_paths)} slides...")
                        
                        slide_params = {
                            "slide_images": image_paths,
                            "analysis_depth": analysis_depth,
                            "ai_provider": ai_provider,
                            "target_audience": target_audience
                        }
                        
                        if subject_area:
                            slide_params["subject_area"] = subject_area
                        
                        slide_result = await slide_analyzer.execute(slide_params)
                        
                        if slide_result.success:
                            print("✅ Slide analysis completed")
                            result_data["slide_analysis"] = slide_result.data
                            
                            # Extract key information for summary
                            slide_data = slide_result.data
                            result_data["analysis_summary"] = {
                                "course_title": slide_data.get("course_title", "N/A"),
                                "subject_area": slide_data.get("subject_area", "N/A"),
                                "difficulty_level": slide_data.get("difficulty_level", "N/A"),
                                "course_description": slide_data.get("course_description", "N/A"),
                                "images_analyzed": len(image_paths),
                                "provider_used": ai_provider,
                                "analysis_depth": analysis_depth
                            }
                            
                            # Step 4: Generate content summary
                            if content_generator and "detailed_description" in slide_data:
                                print("📝 Generating content summary...")
                                
                                gen_result = await content_generator.execute({
                                    "content_type": "summary",
                                    "source_content": slide_data["detailed_description"],
                                    "target_audience": target_audience,
                                    "length": "medium",
                                    "format": "markdown"
                                })
                                
                                if gen_result.success:
                                    result_data["generated_summary"] = gen_result.data
                                    print("✅ Content summary generated")
                        else:
                            print(f"❌ Slide analysis failed: {slide_result.error}")
                            result_data["slide_analysis"] = {
                                "status": "failed",
                                "error": slide_result.error
                            }
                    else:
                        print("⚠️ No slide analyzer available or no images to analyze")
                        result_data["slide_analysis"] = {
                            "status": "skipped",
                            "reason": "No slide analyzer or no images"
                        }
            else:
                print("⚠️ No image archive URL available")
                result_data["images_analyzed"] = 0
                result_data["slide_analysis"] = {
                    "status": "skipped",
                    "reason": "No image archive URL"
                }
            
            return result_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Document analysis failed: {str(e)}"
            } 