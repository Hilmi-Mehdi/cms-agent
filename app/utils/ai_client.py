"""AI client for interacting with OpenAI and Google models."""

import json
import asyncio
import base64
import io
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from pathlib import Path

import openai
import google.generativeai as genai
from openai import AsyncOpenAI
from PIL import Image

from app.config import settings
from app.models.schemas import AIProvider


class BaseAIClient(ABC):
    """Abstract base class for AI clients."""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    async def generate_function_call(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict],
        function_call: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a function call response."""
        pass
    
    @abstractmethod
    async def analyze_images(
        self,
        images: List[Union[str, Path, bytes]],
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze multiple images with a prompt."""
        pass


class OpenAIClient(BaseAIClient):
    """Client for OpenAI models."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**params)
            
            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "provider": "openai"
            }
            
            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                result["tool_calls"] = []
                for tool_call in response.choices[0].message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def generate_function_call(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict],
        function_call: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate function call using OpenAI."""
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "tools": [{"type": "function", "function": func} for func in functions],
                "tool_choice": function_call if function_call else "auto",
                "temperature": 0.1  # Lower temperature for function calls
            }
            
            response = await self.client.chat.completions.create(**params)
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "provider": "openai"
            }
            
        except Exception as e:
            raise Exception(f"OpenAI function call error: {str(e)}")
    
    async def analyze_images(
        self,
        images: List[Union[str, Path, bytes]],
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze multiple images using OpenAI GPT-4 Vision."""
        try:
            # Convert images to base64 format
            image_contents = []
            for img in images:
                if isinstance(img, (str, Path)):
                    # Read image file
                    with open(img, "rb") as image_file:
                        image_data = image_file.read()
                elif isinstance(img, bytes):
                    image_data = img
                else:
                    raise ValueError(f"Unsupported image type: {type(img)}")
                
                # Convert to base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Determine image format
                try:
                    pil_image = Image.open(io.BytesIO(image_data))
                    image_format = pil_image.format.lower()
                except:
                    image_format = "jpeg"  # Default format
                
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_format};base64,{base64_image}",
                        "detail": "high"
                    }
                })
            
            # Create message with text prompt and images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ] + image_contents
                }
            ]
            
            params = {
                "model": "gpt-4.1-nano",  # Use current vision model
                "messages": messages,
                "temperature": temperature
                # Removed max_tokens to allow unlimited response length
            }
            
            response = await self.client.chat.completions.create(**params)
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "provider": "openai",
                "images_analyzed": len(images)
            }
            
        except Exception as e:
            raise Exception(f"OpenAI vision analysis error: {str(e)}")


class GoogleAIClient(BaseAIClient):
    """Client for Google AI models."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model_name = settings.google_model
        self.model = genai.GenerativeModel(self.model_name)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response using Google AI."""
        try:
            # Convert OpenAI-style messages to Google format
            prompt = self._convert_messages_to_prompt(messages)
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature
                # Removed max_output_tokens to allow unlimited response length
            )
            
            # For now, Google doesn't support tools in the same way as OpenAI
            # We'll implement a simplified version
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            )
            
            # Safely extract text content
            content = self._extract_response_text(response)
            
            return {
                "content": content,
                "role": "assistant",
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                },
                "model": self.model_name,
                "provider": "google"
            }
            
        except Exception as e:
            raise Exception(f"Google AI API error: {str(e)}")
    
    async def generate_function_call(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict],
        function_call: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate function call using Google AI."""
        # Google AI doesn't have the same function calling format as OpenAI
        # We'll simulate it by including function descriptions in the prompt
        try:
            prompt = self._convert_messages_to_prompt(messages)
            
            # Add function descriptions to the prompt
            function_descriptions = "\n\nAvailable functions:\n"
            for func in functions:
                function_descriptions += f"- {func['name']}: {func.get('description', '')}\n"
                if 'parameters' in func:
                    function_descriptions += f"  Parameters: {json.dumps(func['parameters'], indent=2)}\n"
            
            full_prompt = prompt + function_descriptions + "\n\nIf you need to call a function, respond with JSON in this format: {\"function_call\": {\"name\": \"function_name\", \"arguments\": {...}}}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            # Try to parse function call from response
            content = self._extract_response_text(response)
            tool_calls = None
            
            if "function_call" in content:
                try:
                    parsed = json.loads(content)
                    if "function_call" in parsed:
                        tool_calls = [{
                            "id": "google_call_1",
                            "type": "function",
                            "function": parsed["function_call"]
                        }]
                except json.JSONDecodeError:
                    pass
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                },
                "provider": "google"
            }
            
        except Exception as e:
            raise Exception(f"Google AI function call error: {str(e)}")
    
    async def analyze_images(
        self,
        images: List[Union[str, Path, bytes]],
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze multiple images using Google Gemini Vision."""
        try:
            # Use the configured model name for vision
            # TEMPORARY: Use stable model to test usage metadata
            vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Changed from self.model_name
            
            # Prepare content for Gemini
            content_parts = [prompt]
            
            for img in images:
                if isinstance(img, (str, Path)):
                    # Read image file
                    image_path = Path(img)
                    image_data = image_path.read_bytes()
                elif isinstance(img, bytes):
                    image_data = img
                else:
                    raise ValueError(f"Unsupported image type: {type(img)}")
                
                # Determine MIME type
                try:
                    pil_image = Image.open(io.BytesIO(image_data))
                    image_format = pil_image.format.lower()
                    if image_format == 'jpeg':
                        mime_type = 'image/jpeg'
                    elif image_format == 'png':
                        mime_type = 'image/png'
                    elif image_format == 'webp':
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/jpeg'  # Default
                except:
                    mime_type = 'image/jpeg'
                
                # Add image to content
                content_parts.append({
                    'mime_type': mime_type,
                    'data': image_data
                })
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature
            )
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: vision_model.generate_content(
                    content_parts,
                    generation_config=generation_config
                )
            )
            
            # Comprehensive debug printing for the response object
            print(f"DEBUG Google Response Object Type: {type(response)}")
            print(f"DEBUG Google Response dir(): {dir(response)}")
            
            # Try to get all attributes using vars() if available
            try:
                print(f"DEBUG Google Response vars(): {vars(response)}")
            except TypeError:
                print("DEBUG Google Response: vars() not available (object uses __slots__ or similar)")
            
            # Check specific attributes we care about
            response_attributes = {}
            for attr in ['text', 'parts', 'candidates', 'prompt_feedback', 'usage_metadata', 'usageMetadata']:
                if hasattr(response, attr):
                    response_attributes[attr] = getattr(response, attr)
            print(f"DEBUG Google Response Relevant Attributes: {response_attributes!r}")
            
            # Also check if there are any attributes with 'usage' or 'token' in the name
            usage_related_attrs = {}
            for attr in dir(response):
                if 'usage' in attr.lower() or 'token' in attr.lower():
                    try:
                        usage_related_attrs[attr] = getattr(response, attr)
                    except:
                        usage_related_attrs[attr] = "Error accessing attribute"
            print(f"DEBUG Google Response Usage/Token Related Attributes: {usage_related_attrs}")
            
            # Log additional potentially helpful attributes (keeping these for now)
            if hasattr(response, 'prompt_feedback'):
                print(f"DEBUG Google Response prompt_feedback: {response.prompt_feedback!r}")
            else:
                print("DEBUG Google Response has no prompt_feedback attribute")
            
            if hasattr(response, 'candidates') and response.candidates:
                print(f"DEBUG Google Response candidates: {response.candidates!r}")
                for i, candidate in enumerate(response.candidates):
                    if hasattr(candidate, 'finish_reason'):
                        print(f"DEBUG Google Response candidate[{i}].finish_reason: {candidate.finish_reason!r}")
                    if hasattr(candidate, 'safety_ratings'):
                        print(f"DEBUG Google Response candidate[{i}].safety_ratings: {candidate.safety_ratings!r}")
            else:
                print("DEBUG Google Response has no candidates or candidates list is empty")

            # UPDATED USAGE METADATA DEBUG PRINT
            if hasattr(response, 'usageMetadata'): # Check camelCase first
                print(f"DEBUG Google Response usageMetadata (camelCase): {response.usageMetadata!r}")
            elif hasattr(response, 'usage_metadata'): # Then snake_case
                print(f"DEBUG Google Response usage_metadata (snake_case): {response.usage_metadata!r}")
            else:
                print("DEBUG Google Response has no usage_metadata or usageMetadata attribute")

            # Safely extract text content
            content = self._extract_response_text(response)
            
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            if hasattr(response, 'usageMetadata'):
                # Try camelCase first as per user suggestion
                metadata_obj = response.usageMetadata
                if hasattr(metadata_obj, 'promptTokenCount'):
                    prompt_tokens = metadata_obj.promptTokenCount
                if hasattr(metadata_obj, 'candidatesTokenCount'): # Note: Google often calls this candidatesTokenCount or completionTokenCount
                    completion_tokens = metadata_obj.candidatesTokenCount
                elif hasattr(metadata_obj, 'completionTokenCount'): # Checking alternative for completion
                    completion_tokens = metadata_obj.completionTokenCount
                if hasattr(metadata_obj, 'totalTokenCount'):
                    total_tokens = metadata_obj.totalTokenCount
            elif hasattr(response, 'usage_metadata'):
                # Fallback to snake_case
                metadata_obj = response.usage_metadata
                if hasattr(metadata_obj, 'prompt_token_count'):
                    prompt_tokens = metadata_obj.prompt_token_count
                if hasattr(metadata_obj, 'candidates_token_count'):
                    completion_tokens = metadata_obj.candidates_token_count
                elif hasattr(metadata_obj, 'completion_token_count'): # Checking alternative for completion
                    completion_tokens = metadata_obj.completion_token_count
                if hasattr(metadata_obj, 'total_token_count'):
                    total_tokens = metadata_obj.total_token_count
            
            return {
                "content": content,
                "role": "assistant",
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                "model": self.model_name, # Use self.model_name here as well
                "provider": "google",
                "images_analyzed": len(images)
            }
            
        except Exception as e:
            raise Exception(f"Google AI vision analysis error: {str(e)}")
    
    def _extract_response_text(self, response) -> str:
        """Safely extract text from Google AI response."""
        try:
            # Try the simple accessor first
            return response.text
        except ValueError:
            # If that fails, use the parts accessor
            try:
                if hasattr(response, 'parts') and response.parts:
                    text_parts = [part.text for part in response.parts if hasattr(part, 'text') and part.text is not None]
                    return " ".join(text_parts) if text_parts else "No text content available in parts"
                elif response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                        text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text') and part.text is not None]
                        return " ".join(text_parts) if text_parts else "No text content available in candidate parts"
                return "No text content available"
            except Exception as e:
                # Log the error for debugging, but return a user-friendly message
                print(f"Detailed error extracting Google AI response text: {e!r}")
                return f"Error extracting response text. Details: {type(e).__name__}"
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt for Google AI."""
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)


class AIClientManager:
    """Manager for AI clients supporting multiple providers."""
    
    def __init__(self):
        self.clients = {
            AIProvider.OPENAI: OpenAIClient(),
            AIProvider.GOOGLE: GoogleAIClient()
        }
        self.default_provider = AIProvider.OPENAI
    
    def get_client(self, provider: Optional[AIProvider] = None) -> BaseAIClient:
        """Get AI client for specified provider."""
        provider = provider or self.default_provider
        return self.clients[provider]
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        provider: Optional[AIProvider] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified provider."""
        client = self.get_client(provider)
        return await client.generate_response(messages, tools, **kwargs)
    
    async def generate_function_call(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict],
        provider: Optional[AIProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate function call using specified provider."""
        client = self.get_client(provider)
        return await client.generate_function_call(messages, functions, **kwargs)
    
    async def analyze_images(
        self,
        images: List[Union[str, Path, bytes]],
        prompt: str,
        provider: Optional[AIProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze images using specified provider."""
        client = self.get_client(provider)
        return await client.analyze_images(images, prompt, **kwargs)
    
    async def test_connections(self) -> Dict[str, bool]:
        """Test connections to all AI providers."""
        results = {}
        
        test_messages = [
            {"role": "user", "content": "Hello, this is a connection test."}
        ]
        
        for provider, client in self.clients.items():
            try:
                response = await client.generate_response(test_messages, temperature=0.1, max_tokens=10)
                results[provider.value] = response is not None and "content" in response
            except Exception as e:
                print(f"Connection test failed for {provider.value}: {e}")
                results[provider.value] = False
        
        return results


# Global AI client manager instance
ai_client = AIClientManager() 