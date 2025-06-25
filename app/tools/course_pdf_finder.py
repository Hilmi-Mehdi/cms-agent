import asyncio
import httpx
import re
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Dict, Any, List, Optional
import logging
import json
from duckduckgo_search import DDGS
import time

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult
from app.config import settings
from openai import AsyncOpenAI

class CoursePdfFinderTool(BaseTool):
    """Tool to find and optionally download course PDFs using OpenAI web search."""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="course_pdf_finder",
            description="Finds course PDFs using OpenAI web search and optionally downloads them. Specifically designed for finding academic course materials.",
            parameters=[
                ToolParameter(
                    name="course_topic",
                    type="string",
                    description="The course topic or subject (e.g., 'machine learning', 'quantum physics', 'calculus').",
                    required=True
                ),
                ToolParameter(
                    name="course_level",
                    type="string", 
                    description="Course level to target (e.g., 'undergraduate', 'graduate', 'introductory', 'advanced').",
                    required=False,
                    default="undergraduate"
                ),
                ToolParameter(
                    name="institution_type",
                    type="string",
                    description="Type of institution to search (e.g., 'university', 'college', 'any'). Use 'university' to search .edu sites.",
                    required=False,
                    default="university"
                ),
                ToolParameter(
                    name="language",
                    type="string",
                    description="Language for the search (e.g., 'en', 'fr', 'es').",
                    required=False,
                    default="en"
                ),
                ToolParameter(
                    name="country",
                    type="string",
                    description="Full country name to focus search on a specific country (e.g., 'Belgium', 'France', 'United States').",
                    required=False,
                    default=None
                ),
                ToolParameter(
                    name="download_pdfs",
                    type="boolean",
                    description="Whether to download the found PDFs automatically.",
                    required=False,
                    default=False
                ),
                ToolParameter(
                    name="download_location",
                    type="string",
                    description="Directory to save downloaded PDFs. If not provided, creates a 'course_pdfs' directory.",
                    required=False,
                    default=None
                ),
                ToolParameter(
                    name="max_pdfs",
                    type="integer",
                    description="Maximum number of PDFs to find/download.",
                    required=False,
                    default=5
                )
            ]
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes the course PDF finder tool."""
        course_topic = parameters.get("course_topic")
        course_level = parameters.get("course_level")
        institution_type = parameters.get("institution_type")
        language = parameters.get("language", "en")
        country = parameters.get("country")
        download_pdfs = parameters.get("download_pdfs", False)
        download_location = parameters.get("download_location")
        max_pdfs = parameters.get("max_pdfs", 5)

        if not course_topic:
            return ToolResult(success=False, error="Course topic cannot be empty.")

        if not settings.openai_api_key:
            return ToolResult(success=False, error="OpenAI API key not configured.")

        agent_notes = f"Searching for '{course_topic}' course PDFs"
        if course_level:
            agent_notes += f" at {course_level} level"
        if country:
            agent_notes += f" in country '{country}'"

        try:
            # Use a robust, multi-step search process
            all_pdf_links = await self._find_pdfs_with_real_web_search(
                course_topic, course_level, institution_type, language, country, max_pdfs
            )
            
            # Remove duplicates
            seen_urls = set()
            unique_pdfs = []
            for pdf in all_pdf_links:
                if pdf['url'] not in seen_urls:
                    seen_urls.add(pdf['url'])
                    unique_pdfs.append(pdf)
            
            all_pdf_links = unique_pdfs[:max_pdfs]
            
            if not all_pdf_links:
                return ToolResult(
                    success=True,
                    data={"pdfs": [], "message": "No course PDFs found matching the criteria."},
                    agent_notes=agent_notes + ". No PDFs found."
                )

            agent_notes += f". Found {len(all_pdf_links)} potential PDF links."

            if not download_pdfs:
                return ToolResult(
                    success=True,
                    data={
                        "pdfs": all_pdf_links,
                        "found_count": len(all_pdf_links),
                        "download_ready": True
                    },
                    agent_notes=agent_notes
                )

            # Download PDFs
            downloaded_files = await self._download_pdfs(all_pdf_links, download_location, course_topic)
            
            final_notes = agent_notes + f" Downloaded {len(downloaded_files['successful'])} PDFs successfully."
            if downloaded_files['failed']:
                final_notes += f" {len(downloaded_files['failed'])} downloads failed."

            return ToolResult(
                success=True,
                data={
                    "pdfs": all_pdf_links,
                    "found_count": len(all_pdf_links),
                    "downloaded_files": downloaded_files['successful'],
                    "download_errors": downloaded_files['failed'],
                    "download_location": downloaded_files['location']
                },
                agent_notes=final_notes
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Course PDF finder failed: {type(e).__name__} - {str(e)}",
                agent_notes=agent_notes + f". Error: {str(e)}"
            )

    async def _find_pdfs_with_real_web_search(
        self, topic: str, level: Optional[str], institution_type: Optional[str], 
        language: str, country: Optional[str], max_results: int
    ) -> List[Dict[str, str]]:
        """
        Orchestrates a robust 3-step process to find real PDF links.
        1. Generate search queries with an AI.
        2. Execute those queries with a real web search engine.
        3. Extract and validate PDF links from the results with an AI.
        """
        # Step 1: Generate search queries
        search_queries = await self._generate_search_queries(topic, level, institution_type, country)
        
        # Step 2: Execute web search
        search_results = await self._execute_web_search(search_queries, max_results * 5) # Get more results to analyze
        
        if not search_results:
            return []
            
        # Step 3: Extract PDF links from results using an AI
        pdf_links = await self._extract_links_from_results(search_results, topic, max_results)
        
        return pdf_links

    async def _generate_search_queries(
        self, topic: str, level: Optional[str], institution_type: Optional[str], country: Optional[str]
    ) -> List[str]:
        """Uses an AI to generate effective search queries."""
        prompt = f"Generate 3 diverse and effective Google search queries to find course materials and PDFs for the topic '{topic}'."
        if level:
            prompt += f" The course level is '{level}'."
        if institution_type:
            prompt += f" The institution type is '{institution_type}'."
        if country:
            prompt += f" The search should be focused on the country '{country}'."
        prompt += "\nReturn a JSON object with a single key 'queries' containing a list of strings."

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model=settings.pdf_finder_model, # Use the powerful model for this
                messages=[
                    {"role": "system", "content": "You are a search query generation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            queries = data.get("queries", [])
            logging.info(f"Generated search queries: {queries}")
            return queries
        except Exception as e:
            logging.error(f"Failed to generate search queries: {e}")
            # Fallback to a basic query
            return [f'"{topic}" "{level or ""}" "{country or ""}" course material filetype:pdf']

    async def _execute_web_search(self, queries: List[str], max_results: int) -> List[Dict[str, str]]:
        """Executes a web search using the DuckDuckGo Search library."""
        all_results = []
        # Use a context manager for the search client
        with DDGS() as ddgs:
            for query in queries:
                try:
                    # DDGS search is synchronous, so we run it in a thread pool
                    # to avoid blocking the asyncio event loop.
                    loop = asyncio.get_event_loop()
                    query_results = await loop.run_in_executor(
                        None, 
                        lambda: list(ddgs.text(query, max_results=10))
                    )
                    all_results.extend(query_results)
                    logging.info(f"Executed search for '{query}', found {len(query_results)} results.")
                    # Sleep to be polite to the search engine API
                    time.sleep(0.5)
                except Exception as e:
                    logging.error(f"DuckDuckGo search failed for query '{query}': {e}")
                    continue
        
        # We only need the title, href, and body for analysis
        return [{"title": r.get('title'), "url": r.get('href'), "snippet": r.get('body')} for r in all_results[:max_results]]

    async def _extract_links_from_results(
        self, results: List[Dict[str, str]], topic: str, max_links: int
    ) -> List[Dict[str, str]]:
        """Uses an AI to analyze search result snippets and extract PDF links."""
        
        # Prepare context from search results for the AI
        context = ""
        for i, result in enumerate(results):
            context += f"Result {i+1}:\n"
            context += f"Title: {result.get('title')}\n"
            context += f"URL: {result.get('url')}\n"
            context += f"Snippet: {result.get('snippet')}\n\n"

        if not context:
            return []

        system_prompt = (
            "You are an expert at analyzing web search results to find course materials. "
            "Your task is to review the provided search result snippets and identify the most relevant links that are likely to be course syllabi, lecture notes, or textbooks, prioritizing direct PDF links."
            "\n- Analyze the title, URL, and snippet for each result."
            "\n- Only extract links that seem highly relevant to the user's topic."
            "\n- Return a JSON object with a 'results' key containing an array of objects. Each object must have 'url', 'title', and 'source' keys."
            "\n- If no relevant links are found, return an empty 'results' array."
        )
        user_prompt = (
            f"Please analyze the following web search results for the topic '{topic}' and extract up to {max_links} relevant course material links.\n\n"
            f"SEARCH RESULTS:\n{context}\n\n"
            "Extract the most relevant links and return them as a JSON object with a 'results' key."
        )

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model=settings.pdf_finder_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            validated_links = []
            for item in data.get("results", []):
                if isinstance(item, dict) and 'url' in item and 'title' in item:
                    validated_links.append({
                        'url': item['url'],
                        'title': item['title'],
                        'source': item.get('source', 'Web Search')
                    })
            logging.info(f"Extracted {len(validated_links)} links from search results.")
            return validated_links
        except Exception as e:
            logging.error(f"AI failed to extract links from search results: {e}")
            return []

    async def _download_pdfs(self, pdf_links: List[Dict[str, str]], download_location: Optional[str], course_topic: str) -> Dict[str, Any]:
        """Download the PDF files with better error handling."""
        if download_location:
            download_dir = Path(download_location)
        else:
            download_dir = Path("course_pdfs") / course_topic.replace(" ", "_")
        
        download_dir.mkdir(parents=True, exist_ok=True)
        
        successful_downloads = []
        failed_downloads = []
        
        # Better headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with httpx.AsyncClient(
            timeout=60.0, 
            follow_redirects=True, 
            headers=headers,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            tasks = []
            for pdf_info in pdf_links:
                tasks.append(self._download_single_pdf(client, pdf_info, download_dir))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_downloads.append({
                        "url": pdf_links[i]["url"],
                        "title": pdf_links[i]["title"],
                        "error": str(result)
                    })
                elif result:
                    successful_downloads.append({
                        "url": pdf_links[i]["url"],
                        "title": pdf_links[i]["title"],
                        "local_path": result
                    })
                else:
                    failed_downloads.append({
                        "url": pdf_links[i]["url"],
                        "title": pdf_links[i]["title"],
                        "error": "Download failed - no result returned"
                    })
        
        return {
            "successful": successful_downloads,
            "failed": failed_downloads,
            "location": str(download_dir.resolve())
        }

    async def _download_single_pdf(self, client: httpx.AsyncClient, pdf_info: Dict[str, str], download_dir: Path) -> Optional[str]:
        """Download a single PDF file with improved validation."""
        try:
            url = pdf_info["url"]
            logging.info(f"Attempting to download: {url}")
            
            # First, try a HEAD request to check if the URL exists
            try:
                head_response = await client.head(url, timeout=10.0)
                if head_response.status_code >= 400:
                    raise Exception(f"URL returned status {head_response.status_code}")
            except Exception as e:
                logging.warning(f"HEAD request failed for {url}, trying GET: {e}")
            
            # Download the content
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            # Check content type and content
            content_type = response.headers.get("content-type", "").lower()
            content = response.content
            
            if not content:
                raise Exception("Empty response content")
            
            # More flexible PDF detection
            is_pdf = (
                "pdf" in content_type or 
                url.lower().endswith('.pdf') or 
                content.startswith(b'%PDF') or
                b'%PDF' in content[:1024]  # Check first 1KB for PDF signature
            )
            
            if not is_pdf:
                # Check if it might be HTML pointing to a PDF
                if b'<html' in content[:1024].lower() or b'<!doctype' in content[:1024].lower():
                    raise Exception("URL points to HTML page, not a PDF file")
                else:
                    # If it doesn't look like HTML, assume it might be a valid file anyway
                    logging.warning(f"Content type '{content_type}' may not be PDF, but proceeding with download")
            
            # Generate filename
            filename = self._generate_filename(url, pdf_info["title"])
            file_path = download_dir / filename
            
            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_part = original_path.stem
                suffix_part = original_path.suffix
                file_path = download_dir / f"{name_part}_{counter}{suffix_part}"
                counter += 1
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            logging.info(f"Successfully downloaded: {file_path}")
            return str(file_path)
            
        except Exception as e:
            error_msg = f"Failed to download {pdf_info['url']}: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def _generate_filename(self, url: str, title: str) -> str:
        """Generate a clean filename for the PDF."""
        if title and title != url and len(title.strip()) > 0:
            # Use title as base
            filename = re.sub(r'[^a-zA-Z0-9\s\-_.]', '', title)
            filename = re.sub(r'\s+', '_', filename.strip())
            # Remove common course-related words that might make filename too long
            filename = re.sub(r'(lecture|notes|course|material|syllabus|pdf)_*', '', filename, flags=re.IGNORECASE)
        else:
            # Extract from URL
            parsed_url = urlparse(url)
            filename = Path(unquote(parsed_url.path)).name
            if not filename or filename == '/':
                # Generate from URL hash
                filename = f"course_material_{abs(hash(url)) % 100000}"
        
        # Clean up filename
        filename = filename.strip('_-. ')
        if not filename:
            filename = f"document_{abs(hash(url)) % 100000}"
        
        # Ensure .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Limit length but preserve extension
        if len(filename) > 100:
            name_part = filename[:-4]  # Remove .pdf
            filename = name_part[:90] + '.pdf'
        
        return filename