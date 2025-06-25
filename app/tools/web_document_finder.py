import asyncio
import httpx
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict, Any

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult

# DuckDuckGo search has been replaced with OpenAI web search
# This tool is kept for backward compatibility but will return an error
# Recommending users to use the new OpenAI web search functionality

class WebDocumentFinderTool(BaseTool):
    """Tool to search the web for specific file types and optionally download them."""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="web_document_finder",
            description="[DEPRECATED] This tool used DuckDuckGo search which has been replaced with OpenAI web search. Please use the general web search functionality instead.",
            parameters=[
                ToolParameter(
                    name="search_query",
                    type="string",
                    description="The main search query (e.g., 'electrostatics in belgium').",
                    required=True
                ),
                ToolParameter(
                    name="file_type",
                    type="string",
                    description="The desired file type extension (e.g., 'pdf', 'docx', 'pptx').",
                    required=False,
                    default="pdf"
                ),
                ToolParameter(
                    name="country_code",
                    type="string",
                    description="Optional two-letter country code to restrict search (e.g., 'be', 'fr', 'us'). This adds 'site:.XX' to the query.",
                    required=False,
                    default=None
                ),
                ToolParameter(
                    name="download_files",
                    type="boolean",
                    description="If true, download the found files. If false, return a list of links.",
                    required=False,
                    default=False
                ),
                ToolParameter(
                    name="download_location",
                    type="string",
                    description="Path to a directory where files should be downloaded. If not provided and download_files is true, a 'downloaded_web_files' directory will be created in the current working directory.",
                    required=False,
                    default=None
                ),
                ToolParameter(
                    name="max_search_results",
                    type="integer",
                    description="Maximum number of search results to fetch from the web search engine.",
                    required=False,
                    default=20
                )
            ]
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Returns an error message indicating this tool is deprecated."""
        return ToolResult(
            success=False, 
            error="WebDocumentFinderTool has been deprecated. DuckDuckGo search has been replaced with OpenAI web search. Please use the general web search endpoint (/api/v1/general-web-search) or the OpenAI web search streaming endpoint (/api/v1/search/openai-web-stream) instead.",
            agent_notes="This tool used DuckDuckGo search which has been replaced with superior OpenAI web search functionality."
        )

    async def _download_single_file(self, client: httpx.AsyncClient, link_url: str, file_type: str, download_dir: Path) -> str:
        """Helper to download a single file. Returns filepath on success, raises error on failure."""
        try:
            response = await client.get(link_url)
            response.raise_for_status()

            parsed_link_url = urlparse(link_url)
            fname_from_path = Path(unquote(parsed_link_url.path)).name
            
            content_disposition = response.headers.get("content-disposition")
            filename = fname_from_path
            if content_disposition:
                disp_filename_match = re.search(r'filename="?([^"]+)"?', content_disposition, re.IGNORECASE)
                if disp_filename_match:
                    filename = disp_filename_match.group(1)
            
            # Basic sanitization and ensure correct extension
            filename_stem = Path(filename).stem
            filename_ext = Path(filename).suffix.lower()

            # If original extension is missing or wrong, force it
            if not filename_ext.endswith(f".{file_type}"):
                # Check if the supposed stem actually contains the extension (e.g. file.pdf.pdf)
                if filename_stem.lower().endswith(f".{file_type}"):
                    filename = f"{filename_stem}.{file_type}"
                else:
                    filename = f"{filename_stem or f'download_{os.urandom(4).hex()}'}.{file_type}"
            else:
                 filename = f"{filename_stem}{filename_ext}" # Ensure consistent casing for extension if desired

            # More robust sanitization for filename
            filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
            filename = filename[:200] # Limit length
            if not filename or filename == f".{file_type}": # if sanitization made it empty or just extension
                filename = f"download_{os.urandom(8).hex()}.{file_type}"

            file_path = download_dir / filename
            counter = 1
            original_stem = file_path.stem
            original_suffix = file_path.suffix
            while file_path.exists():
                file_path = download_dir / f"{original_stem}_{counter}{original_suffix}"
                counter += 1
                if counter > 100: # Safety break for too many existing files
                    raise Exception(f"Could not find a unique filename for {link_url} after 100 attempts in {download_dir}")

            with open(file_path, 'wb') as f:
                f.write(response.content)
            return str(file_path.resolve())
        
        except httpx.RequestError as e:
            raise Exception(f"RequestError downloading {link_url}: {e}") from e
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTPStatusError {e.response.status_code} for {link_url}") from e
        except Exception as e:
            # Catch-all for other errors like file system issues, etc.
            raise Exception(f"Unexpected error downloading {link_url}: {type(e).__name__} - {e}") from e 