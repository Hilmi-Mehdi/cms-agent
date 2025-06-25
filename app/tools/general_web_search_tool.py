import asyncio
from typing import Dict, Any, List, Optional
import json
import logging
import time
from duckduckgo_search import DDGS

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult
from app.config import settings
from openai import AsyncOpenAI

class GeneralWebSearchTool(BaseTool):
    """Tool to perform general web searches using OpenAI's GPT-4.1 web search capability."""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="general_web_search", # Will be registered as 'generalwebsearch'
            description="Performs a general web search using OpenAI's GPT-4.1 with web search capability and returns comprehensive search results including titles, URLs, and content snippets.",
            parameters=[
                ToolParameter(
                    name="search_query",
                    type="string",
                    description="The search query for the web search.",
                    required=True
                ),
                ToolParameter(
                    name="language",
                    type="string",
                    description="Language for the search results (e.g., 'en', 'fr', 'es'). Default is 'en'.",
                    required=False,
                    default="en"
                ),
                ToolParameter(
                    name="context",
                    type="string",
                    description="Optional context or domain to focus the search (e.g., 'academic', 'news', 'technical').",
                    required=False,
                    default=""
                )
            ]
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes the general web search tool using OpenAI's GPT-4.1 web search."""
        search_query = parameters.get("search_query")
        language = parameters.get("language", "en")
        context = parameters.get("context", "")

        if not search_query:
            return ToolResult(success=False, error="Search query cannot be empty.")

        if not settings.openai_api_key:
            return ToolResult(success=False, error="OpenAI API key not configured.")

        agent_notes = f"Performing smart web search for: '{search_query}'"
        
        try:
            # Use the robust, multi-step search process
            search_data = await self._execute_smart_search(search_query, language, context)
            
            if not search_data or not search_data.get("answer"):
                return ToolResult(
                    success=False, 
                    error="The web search could not find a definitive answer.",
                    agent_notes=agent_notes + ". No answer found."
                )

            return ToolResult(
                success=True,
                data=search_data,
                agent_notes=agent_notes + f". Found answer and {len(search_data.get('search_results', []))} sources."
            )

        except Exception as e:
            logging.error(f"An unexpected error occurred in GeneralWebSearchTool: {e}")
            return ToolResult(
                success=False, 
                error=f"An unexpected error occurred during the web search: {str(e)}",
                agent_notes=agent_notes + f". Error: {str(e)}"
            )

    async def _execute_smart_search(
        self, query: str, language: str, context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Orchestrates a robust 3-step process to answer a query.
        1. Generate search queries with an AI.
        2. Execute those queries with a real web search engine.
        3. Summarize the results and provide a direct answer with an AI.
        """
        # Step 1: Generate diverse search queries
        search_queries = await self._generate_search_queries(query, context)
        
        # Step 2: Execute web search
        search_results = await self._execute_web_search(search_queries)
        
        if not search_results:
            return {}
            
        # Step 3: Summarize results and generate a final answer
        final_answer = await self._summarize_results_with_ai(query, search_results)
        
        return final_answer

    async def _generate_search_queries(self, original_query: str, context: Optional[str]) -> List[str]:
        """Uses an AI to generate effective search queries."""
        prompt = (
            f"Generate 3 diverse and effective Google search queries to answer the question: '{original_query}'."
            f"\n- The first query should be a direct version of the question."
            f"\n- The second query should be a broader, related search."
            f"\n- The third query should include keywords that might find specific dates or official sources."
        )
        if context:
            prompt += f"\n- The search context is: {context}."
        prompt += "\nReturn a JSON object with a single key 'queries' containing a list of 3 strings."

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model=settings.pdf_finder_model, # Use the more powerful model
                messages=[
                    {"role": "system", "content": "You are a search query generation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            queries = data.get("queries", [original_query])
            logging.info(f"Generated search queries: {queries}")
            return queries
        except Exception as e:
            logging.error(f"Failed to generate search queries, using fallback: {e}")
            return [original_query]

    async def _execute_web_search(self, queries: List[str]) -> List[Dict[str, str]]:
        """Executes a web search using the DuckDuckGo Search library."""
        all_results = []
        with DDGS() as ddgs:
            for query in queries:
                try:
                    loop = asyncio.get_event_loop()
                    query_results = await loop.run_in_executor(
                        None, 
                        lambda: list(ddgs.text(query, max_results=5)) # 5 results per query
                    )
                    all_results.extend(query_results)
                    logging.info(f"Executed search for '{query}', found {len(query_results)} results.")
                    time.sleep(0.5)
                except Exception as e:
                    logging.error(f"DuckDuckGo search failed for query '{query}': {e}")
        
        return [{"title": r.get('title'), "url": r.get('href'), "snippet": r.get('body')} for r in all_results]

    async def _summarize_results_with_ai(
        self, original_query: str, results: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Uses an AI to analyze search results and synthesize a final answer."""
        context = ""
        for i, result in enumerate(results[:10]): # Limit context to top 10 results
            context += f"Source {i+1}:\nTitle: {result.get('title')}\nURL: {result.get('url')}\nSnippet: {result.get('snippet')}\n\n"

        if not context:
            return {}

        system_prompt = (
            "You are an expert AI assistant that synthesizes information from web search results to provide a direct, concise, and accurate answer to a user's question. "
            "You must cite the sources you use."
        )
        user_prompt = (
            f"Based on the following search results, provide a clear and direct answer to the question: '{original_query}'"
            f"\n\nSEARCH RESULTS:\n{context}"
            f"\n\nYour response MUST be a JSON object with two keys:"
            f"\n1. 'answer': A string containing the final, synthesized answer to the user's question."
            f"\n2. 'search_results': An array of objects for ONLY the sources you used to create the answer. Each object must have 'title', 'url', and 'snippet' keys."
        )

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            response = await client.chat.completions.create(
                model=settings.pdf_finder_model, # Use the more powerful model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            logging.info(f"AI summary generated: {data.get('answer')}")
            return {
                "answer": data.get("answer"),
                "search_results": data.get("search_results", []),
                "query": original_query
            }
        except Exception as e:
            logging.error(f"AI failed to summarize search results: {e}")
            return {} 