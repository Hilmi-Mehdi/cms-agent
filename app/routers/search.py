from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
import json

from app.config import Settings, settings
from openai import AsyncOpenAI

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

class WebSearchRequest(BaseModel):
    query: str
    model: Optional[str] = Field("gpt-4.1", description="Model to use, e.g., 'gpt-4.1' or 'gpt-4o'.")

class SourceAnnotation(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    text_quote: Optional[str] = Field(None, description="The specific text snippet cited from the source.")

# Note: WebSearchResponse is not used as a response_model for the streaming endpoint,
# but it's a good reference for the structure of the data being streamed.
class WebSearchResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceAnnotation]] = None

@router.post("/openai-web-stream")
async def openai_web_search_stream(
    request: WebSearchRequest,
    settings: Settings = Depends(lambda: settings)
):
    """
    Performs a web search using OpenAI's Responses API with the web_search tool,
    focused on Belgian tax and finance, and streams the answer in French.
    
    The stream sends events:
    - `token`: The complete answer text (sent as a single event).
    - `source`: A structured source object with URL, title, and quote.
    - `done`: Signals the end of the stream.
    """
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured in settings.")

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_web_search_timeout
    )

    system_prompt = (
        "Vous êtes un assistant IA spécialisé en fiscalité et finance belge. "
        "Votre tâche principale est de trouver des informations pertinentes et à jour en ligne "
        "pour répondre à la question de l'utilisateur dans ce contexte spécifique. "
        "Répondez toujours en français. Fournissez une réponse complète et bien structurée "
        "basée sur vos résultats de recherche. Citez vos sources en listant les URL complètes."
    )

    async def generate_pseudo_stream():
        try:
            api_response = await client.responses.create(
                model=settings.openai_web_search_model,
                tools=[{"type": "web_search_preview"}],
                input=system_prompt + " " + request.query,
            )

            message_output = None
            if api_response.output:
                for output_item in api_response.output:
                    if getattr(output_item, 'type', None) == 'message':
                        message_output = output_item
                        break
            
            if not message_output or not message_output.content:
                raise Exception("OpenAI API did not return a parsable message in the output.")

            # Extract content from the message block
            main_content_block = message_output.content[0]
            if main_content_block.type != "output_text":
                raise Exception(f"Unexpected content block type: {main_content_block.type}")
            
            answer_text = main_content_block.text
            annotations = main_content_block.annotations

            # 1. Stream the entire answer text as a single "token" event
            yield f"data: {json.dumps({'type': 'token', 'data': answer_text})}\n\n"
            
            # 2. Process and stream each source individually
            if annotations:
                for ann in annotations:
                    if getattr(ann, 'type', None) == 'url_citation':
                        try:
                            url = HttpUrl(ann.url)
                            title = getattr(ann, 'title', None)
                            text_quote = None
                            if hasattr(ann, 'start_index') and hasattr(ann, 'end_index'):
                                start, end = ann.start_index, ann.end_index
                                if start is not None and end is not None and 0 <= start < end <= len(answer_text):
                                    text_quote = answer_text[start:end]
                            
                            source = SourceAnnotation(url=url, title=title, text_quote=text_quote)
                            yield f"data: {json.dumps({'type': 'source', 'data': source.dict()})}\n\n"
                        except Exception:
                            # Silently skip annotations that fail to parse
                            pass
            
            # 3. Signal the end of the stream
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            error_data = {"type": "error", "data": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(generate_pseudo_stream(), media_type="text/event-stream") 