"""Document fetcher tool for retrieving course materials from external APIs."""

import asyncio
import tarfile
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx
import json

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult


class DocumentFetcherTool(BaseTool):
    """Tool for fetching document data from external APIs and processing associated files."""
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="document_fetcher",
            description="Fetch document data from Science Made Simple API and extract images from tar archives",
            parameters=[
                ToolParameter(
                    name="document_id",
                    type="string",
                    description="The document ID to fetch from the API",
                    required=True
                ),
                ToolParameter(
                    name="api_url",
                    type="string",
                    description="The API endpoint URL",
                    required=False,
                    default="https://app.sciencemadesimple.io/api/_integration/get_document"
                ),
                ToolParameter(
                    name="extract_images",
                    type="boolean",
                    description="Whether to extract images from the ImageArchive100URL tar file",
                    required=False,
                    default=True
                ),
                ToolParameter(
                    name="image_format_filter",
                    type="array",
                    description="List of image formats to extract (e.g., ['jpg', 'jpeg', 'png'])",
                    required=False
                ),
                ToolParameter(
                    name="max_images",
                    type="number",
                    description="Maximum number of images to extract",
                    required=False,
                    default=50
                ),
                ToolParameter(
                    name="api_headers",
                    type="object",
                    description="HTTP headers for API authentication (e.g., {'Authorization': 'Bearer token'})",
                    required=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute document fetching and processing."""
        document_id = parameters["document_id"]
        api_url = parameters.get("api_url", "https://app.sciencemadesimple.io/api/_integration/get_document")
        extract_images = parameters.get("extract_images", True)
        image_format_filter = parameters.get("image_format_filter", ["jpg", "jpeg", "png", "gif", "bmp"])
        max_images = parameters.get("max_images", 50)
        api_headers = parameters.get("api_headers", {})
        
        try:
            # Fetch document data from API
            document_data = await self._fetch_document_data(api_url, document_id, api_headers)
            
            if not document_data:
                return ToolResult(
                    success=False,
                    error="Failed to fetch document data from API"
                )
            
            result_data = {
                "document_metadata": document_data,
                "document_id": document_id,
                "api_url": api_url
            }
            
            # Extract images if requested and ImageArchive100URL is available
            if extract_images and "URLs" in document_data and "ImageArchive100URL" in document_data["URLs"]:
                image_archive_url = document_data["URLs"]["ImageArchive100URL"]
                
                if image_archive_url and image_archive_url != "url":  # Check if URL is not placeholder
                    images_data = await self._extract_images_from_tar(
                        image_archive_url, 
                        image_format_filter, 
                        max_images,
                        document_id
                    )
                    result_data["extracted_images"] = images_data
                else:
                    result_data["extracted_images"] = {
                        "status": "skipped",
                        "reason": "ImageArchive100URL is empty or placeholder"
                    }
            
            # Suggest next tools based on what was extracted
            next_tools = self._suggest_next_tools(result_data)
            
            return ToolResult(
                success=True,
                data=result_data,
                suggested_next_tools=next_tools,
                agent_notes=f"Fetched document '{document_data.get('Name', 'Unknown')}' with {result_data.get('extracted_images', {}).get('image_count', 0)} images"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Document fetching failed: {str(e)}"
            )
    
    async def _fetch_document_data(self, api_url: str, document_id: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Fetch document data from the external API."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare the request - you may need to adjust this based on the actual API specification
                params = {"id": document_id}  # or however the API expects the document ID
                
                # Add custom headers if provided (for authentication)
                request_headers = headers or {}
                
                response = await client.get(api_url, params=params, headers=request_headers)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"API request failed with status {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Network error while fetching document: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from API: {str(e)}")
    
    async def _extract_images_from_tar(
        self, 
        tar_url: str, 
        image_format_filter: List[str], 
        max_images: int,
        document_id: str
    ) -> Dict[str, Any]:
        """Download tar file and extract images."""
        try:
            # Create temporary directory for processing that persists
            temp_dir = tempfile.mkdtemp(prefix=f"sms_images_{document_id}_")
            temp_path = Path(temp_dir)
            tar_file_path = temp_path / "images.tar"
            
            try:
                # Download tar file
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(tar_url)
                    response.raise_for_status()
                    
                    with open(tar_file_path, "wb") as f:
                        f.write(response.content)
                
                # Extract tar file - let it extract to its preferred structure
                extract_success = False
                try:
                    # Try different tar modes
                    for mode in ['r', 'r:*', 'r:gz', 'r:bz2', 'r:xz']:
                        try:
                            with tarfile.open(tar_file_path, mode) as tar:
                                # Extract files safely, converting absolute paths to relative
                                extracted_count = 0
                                for member in tar.getmembers():
                                    if member.isfile():
                                        # Convert absolute path to relative and safe filename
                                        safe_name = member.name.lstrip('/')  # Remove leading slash
                                        safe_name = safe_name.replace('..', '_')  # Remove any .. path traversal
                                        
                                        # Create a new member with safe path
                                        member.name = safe_name
                                        
                                        try:
                                            tar.extract(member, temp_path)
                                            extracted_count += 1
                                        except Exception:
                                            continue  # Skip files that can't be extracted
                                
                                extract_success = True
                                break
                        except Exception:
                            continue
                    
                    if not extract_success:
                        return {
                            "status": "error",
                            "error": "Could not extract tar file with any supported mode",
                            "tar_url": tar_url
                        }
                        
                except Exception as e:
                    return {
                        "status": "error",
                        "error": f"Failed to extract tar file: {str(e)}",
                        "tar_url": tar_url
                    }
                
                # Find and process images anywhere in the temp directory
                image_files = []
                image_paths = []
                
                # Normalize format filters - convert to lowercase and add both jpg/jpeg variants
                normalized_filters = set()
                for fmt in image_format_filter:
                    fmt_lower = fmt.lower()
                    normalized_filters.add(fmt_lower)
                    # Add jpeg/jpg equivalents
                    if fmt_lower == "jpg":
                        normalized_filters.add("jpeg")
                    elif fmt_lower == "jpeg":
                        normalized_filters.add("jpg")
                
                # If no specific filters, use default image formats
                if not normalized_filters:
                    normalized_filters = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"}
                
                # Search the entire temp directory tree for image files
                file_count = 0
                image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
                
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                        file_count += 1
                        file_extension = file_path.suffix.lower().lstrip(".")
                        
                        if file_extension in normalized_filters:
                            if len(image_files) < max_images:
                                try:
                                    # Read image data
                                    with open(file_path, "rb") as img_file:
                                        image_data = img_file.read()
                                    
                                    if len(image_data) > 0:  # Ensure file has content
                                        image_info = {
                                            "filename": file_path.name,
                                            "size_bytes": len(image_data),
                                            "format": file_extension,
                                            "path_in_archive": str(file_path.relative_to(temp_path))
                                        }
                                        
                                        # Keep images in persistent temporary location
                                        image_files.append(image_info)
                                        image_paths.append(str(file_path))  # Use persistent path
                                    else:
                                        continue  # Skip empty files
                                        
                                except Exception as e:
                                    continue  # Skip files that can't be processed
                            else:
                                break  # Reached max images limit
                        else:
                            pass  # Skip files that don't match the filter
                
                return {
                    "status": "success",
                    "image_count": len(image_files),
                    "images": image_files,
                    "image_paths": image_paths,
                    "temp_dir": temp_dir,  # Include temp dir for cleanup later
                    "tar_url": tar_url,
                    "formats_found": list(set(img["format"] for img in image_files))
                }
                
            except Exception as e:
                # Clean up temp dir on error
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                raise e
                
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "error": f"Failed to download tar file: HTTP {e.response.status_code}",
                "tar_url": tar_url
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Image extraction failed: {str(e)}",
                "tar_url": tar_url
            }
    
    def _suggest_next_tools(self, result_data: Dict[str, Any]) -> List[str]:
        """Suggest next tools based on the fetched data."""
        next_tools = []
        
        # If we have extracted images, suggest slide analyzer
        if "extracted_images" in result_data:
            images_data = result_data["extracted_images"]
            if images_data.get("status") == "success" and images_data.get("image_count", 0) > 0:
                next_tools.append("slide_analyzer")
        
        # If we have document content, suggest content analyzer
        if "document_metadata" in result_data:
            next_tools.append("content_analyzer")
        
        # If we have document metadata with description, suggest content generator
        doc_meta = result_data.get("document_metadata", {})
        if doc_meta.get("Desc"):
            next_tools.append("content_generator")
        
        return next_tools 