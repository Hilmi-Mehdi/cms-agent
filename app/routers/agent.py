"""Agent interaction endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import tempfile
import os
import json
import shutil
import uuid

from app.models.schemas import AgentRequest, AgentResponse, AIProvider
from app.agent.core_agent import course_agent
from app.tools.base_tool import tool_registry

router = APIRouter()


@router.post("/process", response_model=AgentResponse)
async def process_request(request: AgentRequest):
    """Process a user request through the AI agent."""
    try:
        response = await course_agent.process_request(
            user_request=request.user_query,
            context=request.context,
            user_id="api_user",  # In production, get from authentication
            preferred_provider=request.preferred_provider
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-with-files", response_model=AgentResponse)
async def process_request_with_files(
    user_query: str = Form(...),
    files: List[UploadFile] = File(...),
    target_audience: Optional[str] = Form("general"),
    preferred_provider: Optional[str] = Form(None)
):
    """Process a request with uploaded files."""
    try:
        # Save uploaded files temporarily
        file_paths = []
        temp_files = []
        
        for file in files:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}")
            temp_files.append(temp_file.name)
            
            # Write file content
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            file_paths.append(temp_file.name)
        
        # Create context with file paths
        context = {
            "files": file_paths,
            "target_audience": target_audience,
            "uploaded_filenames": [file.filename for file in files]
        }
        
        # Convert provider string to enum if provided
        provider = None
        if preferred_provider:
            try:
                provider = AIProvider(preferred_provider.lower())
            except ValueError:
                pass
        
        # Process request
        response = await course_agent.process_request(
            user_request=user_query,
            context=context,
            user_id="api_user",
            preferred_provider=provider
        )
        
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        return response
        
    except Exception as e:
        # Clean up temporary files on error
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_available_tools():
    """Get list of available tools and their definitions."""
    tools = tool_registry.get_all_tools()
    
    tool_info = {}
    for name, tool in tools.items():
        tool_info[name] = {
            "name": tool.name,
            "description": tool.definition.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "enum": param.enum
                }
                for param in tool.definition.parameters
            ]
        }
    
    return {
        "available_tools": list(tools.keys()),
        "tool_details": tool_info
    }


@router.post("/analyze-content")
async def analyze_content(
    content: str = Form(...),
    analysis_type: str = Form("comprehensive"),
    target_audience: str = Form("general"),
    subject_area: Optional[str] = Form(None)
):
    """Direct content analysis endpoint."""
    try:
        # Get the content analyzer tool
        analyzer = tool_registry.get_tool("content_analyzer")
        if not analyzer:
            raise HTTPException(status_code=500, detail="Content analyzer tool not available")
        
        # Prepare parameters
        parameters = {
            "content": content,
            "analysis_type": analysis_type,
            "target_audience": target_audience
        }
        
        if subject_area:
            parameters["subject_area"] = subject_area
        
        # Execute analysis
        result = await analyzer.execute(parameters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "analysis_result": result.data,
            "execution_time": result.execution_time,
            "suggested_next_tools": result.suggested_next_tools
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-content")
async def generate_content(
    content_type: str = Form(...),
    source_content: str = Form(...),
    target_audience: str = Form("intermediate"),
    length: str = Form("medium"),
    format_type: str = Form("markdown"),
    include_examples: bool = Form(True)
):
    """Direct content generation endpoint."""
    try:
        # Get the content generator tool
        generator = tool_registry.get_tool("content_generator")
        if not generator:
            raise HTTPException(status_code=500, detail="Content generator tool not available")
        
        # Prepare parameters
        parameters = {
            "content_type": content_type,
            "source_content": source_content,
            "target_audience": target_audience,
            "length": length,
            "format": format_type,
            "include_examples": include_examples
        }
        
        # Execute generation
        result = await generator.execute(parameters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "generated_content": result.data,
            "execution_time": result.execution_time,
            "suggested_next_tools": result.suggested_next_tools
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/execute")
async def execute_tool(
    tool_name: str = Form(...),
    parameters: str = Form(...),  # JSON string of parameters
):
    """Execute a specific tool with given parameters."""
    try:
        # Get the tool
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # Parse parameters
        try:
            params = json.loads(parameters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in parameters")
        
        # Execute the tool
        result = await tool.execute(params)
        
        return {
            "success": result.success,
            "data": result.data if result.success else None,
            "error": result.error if not result.success else None,
            "execution_time": getattr(result, 'execution_time', None),
            "tool_name": tool_name,
            "suggested_next_tools": getattr(result, 'suggested_next_tools', []),
            "agent_notes": getattr(result, 'agent_notes', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-slides")
async def analyze_slides(
    slides: List[UploadFile] = File(...),
    ai_provider: str = Form("openai"),
    analysis_depth: str = Form("comprehensive"),
    target_audience: str = Form("general"),
    subject_area: str = Form("auto-detect"),
    max_pdf_pages: int = Form(50)
):
    """Analyze uploaded slide images or PDF files to extract course information."""
    try:
        # Get the slide analyzer tool
        slide_analyzer = tool_registry.get_tool("slideanalyzer")
        if not slide_analyzer:
            raise HTTPException(status_code=500, detail="Slide analyzer tool not available")
        
        # Save uploaded slide images/PDFs temporarily
        slide_paths = []
        temp_files = []
        
        for slide in slides:
            # Validate file type - now includes PDF
            file_ext = slide.filename.lower()
            if not (file_ext.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')) or file_ext.endswith('.pdf')):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {slide.filename}. Supported: PNG, JPG, JPEG, WebP, BMP, PDF"
                )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{slide.filename}")
            temp_files.append(temp_file.name)
            
            # Write slide content
            content = await slide.read()
            temp_file.write(content)
            temp_file.close()
            
            slide_paths.append(temp_file.name)
        
        # Prepare parameters for slide analyzer
        parameters = {
            "slide_images": slide_paths,
            "ai_provider": ai_provider,
            "analysis_depth": analysis_depth,
            "target_audience": target_audience,
            "subject_area": subject_area,
            "max_pdf_pages": max_pdf_pages
        }
        
        # Execute slide analysis
        result = await slide_analyzer.execute(parameters)
        
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "course_data": result.data,
            "execution_time": getattr(result, 'execution_time', None),
            "images_analyzed": len(slide_paths),
            "suggested_next_tools": getattr(result, 'suggested_next_tools', []),
            "agent_notes": getattr(result, 'agent_notes', None)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up temporary files on error
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_ai_providers():
    """Get available AI providers and their status."""
    try:
        status = await course_agent.ai_client.test_connections()
        return {
            "available_providers": [provider.value for provider in AIProvider],
            "provider_status": status,
            "default_provider": course_agent.ai_client.default_provider.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-quiz")
async def generate_quiz(
    slide_analysis_data: str = Form(...),  # JSON string of slide analysis
    ai_provider: str = Form("openai"),
    max_questions: int = Form(10),
    difficulty_level: str = Form("intermediate"),
    subject_area: Optional[str] = Form(None)
):
    """Generate a sophisticated quiz from slide analysis data."""
    try:
        # Get the quiz generator tool
        quiz_generator = tool_registry.get_tool("quizgenerator")
        if not quiz_generator:
            raise HTTPException(status_code=500, detail="Quiz generator tool not available")
        
        # Parse slide analysis data
        try:
            analysis_data = json.loads(slide_analysis_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in slide_analysis_data")
        
        # Prepare parameters
        parameters = {
            "slide_analysis_data": analysis_data,
            "ai_provider": ai_provider,
            "max_questions": max_questions,
            "difficulty_level": difficulty_level
        }
        
        if subject_area:
            parameters["subject_area"] = subject_area
        
        # Execute quiz generation
        result = await quiz_generator.execute(parameters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "quiz_data": result.data,
            "execution_time": result.execution_time,
            "suggested_next_tools": result.suggested_next_tools
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-document")
async def analyze_document(
    document_id: str = Form(...),
    ai_provider: str = Form("openai"),
    analysis_depth: str = Form("comprehensive"),
    target_audience: str = Form("general"),
    subject_area: Optional[str] = Form(None),
    generate_quiz: bool = Form(False),
    max_quiz_questions: int = Form(5)
):
    """Analyze a document from Science Made Simple API using document ID."""
    try:
        # Get the document analyzer tool
        document_analyzer = tool_registry.get_tool("documentanalyzer")
        if not document_analyzer:
            raise HTTPException(status_code=500, detail="Document analyzer tool not available")
        
        # Prepare parameters
        parameters = {
            "document_id": document_id,
            "ai_provider": ai_provider,
            "analysis_depth": analysis_depth,
            "target_audience": target_audience
        }
        
        if subject_area:
            parameters["subject_area"] = subject_area
        
        # Execute analysis
        result = await document_analyzer.execute(parameters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        response_data = {
            "success": True,
            "analysis_result": result.data,
            "execution_time": result.execution_time,
            "suggested_next_tools": result.suggested_next_tools
        }
        
        # Generate quiz if requested and we have slide analysis
        if generate_quiz and "slide_analysis" in result.data:
            quiz_generator = tool_registry.get_tool("quizgenerator")
            if quiz_generator:
                print("🧪 Generating quiz from slide analysis...")
                
                quiz_result = await quiz_generator.execute({
                    "slide_analysis_data": result.data["slide_analysis"],
                    "ai_provider": ai_provider,
                    "max_questions": max_quiz_questions,
                    "difficulty_level": target_audience,
                    "subject_area": subject_area
                })
                
                if quiz_result.success:
                    response_data["quiz_data"] = quiz_result.data
                    print(f"✅ Generated {quiz_result.data['quiz_metadata']['total_questions']} quiz questions")
                else:
                    response_data["quiz_error"] = quiz_result.error
                    print(f"❌ Quiz generation failed: {quiz_result.error}")
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-quiz-from-document")
async def generate_quiz_from_document(
    document_id: str = Form(...),
    ai_provider: str = Form("openai"),
    max_questions: int = Form(10),
    difficulty_level: str = Form("intermediate"),
    subject_area: Optional[str] = Form("auto-detect"),
    question_types: str = Form("multiple_choice,calculation,conceptual"),
    language: str = Form("auto-detect")
):
    """Generate quiz directly from document ID - fast and high-quality approach."""
    temp_dir_to_cleanup = None
    
    try:
        from app.config import settings
        
        # Step 1: Fetch document images using configured API key
        document_fetcher = tool_registry.get_tool("documentfetcher")
        if not document_fetcher:
            raise HTTPException(status_code=500, detail="Document fetcher tool not available")
        
        print(f"📥 Fetching document {document_id}...")
        fetch_result = await document_fetcher.execute({
            "document_id": document_id,
            "api_headers": {"SMS-Access-Key": settings.sms_api_key},
            "extract_images": True,
            "max_images": 20  # Allow more images for comprehensive quiz
        })
        
        if not fetch_result.success:
            raise HTTPException(status_code=500, detail=f"Failed to fetch document: {fetch_result.error}")
        
        images_data = fetch_result.data.get("extracted_images", {})
        if images_data.get("status") != "success":
            raise HTTPException(status_code=500, detail=f"Image extraction failed: {images_data}")
        
        image_paths = images_data.get("image_paths", [])
        if not image_paths:
            raise HTTPException(status_code=500, detail="No images found in document")
        
        # Store temp dir for cleanup
        temp_dir_to_cleanup = images_data.get("temp_dir")
        
        print(f"✅ Extracted {len(image_paths)} images from document")
        
        # Step 2: Generate quiz directly from images
        direct_quiz_generator = tool_registry.get_tool("directquizgenerator")
        if not direct_quiz_generator:
            raise HTTPException(status_code=500, detail="Direct quiz generator tool not available")
        
        # Parse question types
        question_types_list = [t.strip() for t in question_types.split(",")]
        
        print(f"🧪 Generating quiz using {ai_provider}...")
        quiz_result = await direct_quiz_generator.execute({
            "slide_images": image_paths,
            "ai_provider": ai_provider,
            "max_questions": max_questions,
            "difficulty_level": difficulty_level,
            "subject_area": subject_area,
            "question_types": question_types_list,
            "language": language
        })
        
        if not quiz_result.success:
            raise HTTPException(status_code=500, detail=f"Quiz generation failed: {quiz_result.error}")
        
        # Add document information to response
        quiz_data = quiz_result.data
        
        # Get execution times safely
        fetch_time = getattr(fetch_result, 'execution_time', 0) or 0
        quiz_time = getattr(quiz_result, 'execution_time', 0) or 0
        
        quiz_data["document_info"] = {
            "document_id": document_id,
            "document_name": fetch_result.data.get("document_metadata", {}).get("Name", "Unknown"),
            "images_analyzed": len(image_paths),
            "fetch_time": fetch_time,
            "quiz_generation_time": quiz_time,
            "total_time": fetch_time + quiz_time
        }
        
        print(f"✅ Quiz generated successfully in {quiz_time}s")
        
        # Clean up temporary directory
        if temp_dir_to_cleanup:
            try:
                shutil.rmtree(temp_dir_to_cleanup, ignore_errors=True)
                print(f"🧹 Cleaned up temporary directory: {temp_dir_to_cleanup}")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temp directory: {e}")
        
        return {
            "success": True,
            "quiz": quiz_data,
            "execution_time": fetch_time + quiz_time,
            "agent_notes": f"Generated {len(quiz_data.get('questions', []))} questions from document {document_id} in {fetch_time + quiz_time:.1f}s"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions but clean up first
        if temp_dir_to_cleanup:
            try:
                shutil.rmtree(temp_dir_to_cleanup, ignore_errors=True)
            except:
                pass
        raise
    except Exception as e:
        # Clean up temp directory on any error
        if temp_dir_to_cleanup:
            try:
                shutil.rmtree(temp_dir_to_cleanup, ignore_errors=True)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-quiz-direct")
async def generate_quiz_direct(
    slides: List[UploadFile] = File(...),
    ai_provider: str = Form("openai"),
    max_questions: int = Form(10),
    difficulty_level: str = Form("intermediate"),
    subject_area: Optional[str] = Form("auto-detect"),
    question_types: str = Form("multiple_choice,calculation,conceptual"),  # Comma-separated
    language: str = Form("auto-detect")
):
    """Direct quiz generation from slide images - fast and high-quality."""
    try:
        # Save uploaded files temporarily
        temp_files = []
        slide_paths = []
        
        for slide in slides:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{slide.filename}")
            temp_files.append(temp_file.name)
            
            # Write file content
            content = await slide.read()
            temp_file.write(content)
            temp_file.close()
            
            slide_paths.append(temp_file.name)
        
        # Parse question types
        question_types_list = [t.strip() for t in question_types.split(",")]
        
        # Get the direct quiz generator tool
        quiz_generator = tool_registry.get_tool("directquizgenerator")
        if not quiz_generator:
            raise HTTPException(status_code=500, detail="Direct quiz generator tool not available")
        
        # Execute quiz generation
        result = await quiz_generator.execute({
            "slide_images": slide_paths,
            "ai_provider": ai_provider,
            "max_questions": max_questions,
            "difficulty_level": difficulty_level,
            "subject_area": subject_area,
            "question_types": question_types_list,
            "language": language
        })
        
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "quiz": result.data,
            "execution_time": result.execution_time,
            "agent_notes": result.agent_notes
        }
        
    except Exception as e:
        # Clean up temporary files on error
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/digitalize-slides")
async def digitalize_slides(
    slides: List[UploadFile] = File(...),
    ai_provider: str = Form("openai"),
    language: str = Form("auto-detect"),
    extract_formulas: bool = Form(True),
    extract_diagrams: bool = Form(True),
    preserve_structure: bool = Form(True)
):
    """Digitalize slide content by extracting all text, formulas, and visual elements."""
    try:
        # Save uploaded files temporarily
        temp_files = []
        slide_paths = []
        
        for slide in slides:
            # Validate file type
            file_ext = slide.filename.lower()
            if not (file_ext.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')) or file_ext.endswith('.pdf')):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {slide.filename}. Supported: PNG, JPG, JPEG, WebP, BMP, PDF"
                )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{slide.filename}")
            temp_files.append(temp_file.name)
            
            # Write slide content
            content = await slide.read()
            temp_file.write(content)
            temp_file.close()
            
            slide_paths.append(temp_file.name)
        
        # Get the slide digitalization tool
        digitalization_tool = tool_registry.get_tool("slidedigitalization")
        if not digitalization_tool:
            raise HTTPException(status_code=500, detail="Slide digitalization tool not available")
        
        # Execute digitalization
        result = await digitalization_tool.execute({
            "slide_images": slide_paths,
            "ai_provider": ai_provider,
            "language": language,
            "extract_formulas": extract_formulas,
            "extract_diagrams": extract_diagrams,
            "preserve_structure": preserve_structure
        })
        
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "success": True,
            "digitized_content": result.data,
            "execution_time": result.execution_time,
            "slides_processed": len(slide_paths),
            "agent_notes": result.agent_notes
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up temporary files on error
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/digitalize-document")
async def digitalize_document(
    document_id: str = Form(...),
    ai_provider: str = Form("openai"),
    language: str = Form("auto-detect"),
    extract_formulas: bool = Form(True),
    extract_diagrams: bool = Form(True),
    preserve_structure: bool = Form(True)
):
    """Digitalize a document from Science Made Simple API, extracting all content from slides."""
    try:
        digitalization_tool = tool_registry.get_tool("slide_digitalization") # This seems to be the intent, or a new one
        document_fetcher_tool = tool_registry.get_tool("document_fetcher")
        
        if not document_fetcher_tool or not digitalization_tool:
            raise HTTPException(status_code=500, detail="Required tools (DocumentFetcherTool or SlideDigitalizationTool) not available.")

        # Step 1: Fetch document images using DocumentFetcherTool
        # For this endpoint, we assume document_id gives us image paths/data to pass to slide_digitalization
        # This part might need the DocumentAnalyzerTool's orchestration logic if it's complex,
        # or simplify if DocumentFetcherTool can provide image data directly for digitalization.
        
        # Let's assume DocumentFetcherTool can give us image paths or base64 data suitable for SlideDigitalizationTool
        fetch_params = {"document_id": document_id, "extract_images": True, "api_headers": None} # Assuming default/no auth for now or it's handled internally by fetcher
        fetch_result = await document_fetcher_tool.execute(fetch_params)

        if not fetch_result.success or not fetch_result.data.get("extracted_images", {}).get("image_paths"):
            error_detail = fetch_result.error or "Failed to fetch document images or no images found."
            if fetch_result.data and fetch_result.data.get("extracted_images", {}).get("status") == "no_images_found":
                error_detail = "No images found in the document to digitalize."
            raise HTTPException(status_code=404, detail=error_detail)

        image_paths_or_data = fetch_result.data["extracted_images"]["image_paths"]
        if not image_paths_or_data:
             raise HTTPException(status_code=404, detail="No image paths extracted from document.")

        # Step 2: Digitalize the fetched images
        digitalize_params = {
            "slide_images": image_paths_or_data,
            "ai_provider": ai_provider,
            "language": language,
            "extract_formulas": extract_formulas,
            "extract_diagrams": extract_diagrams,
            "preserve_structure": preserve_structure
        }
        
        digitalization_result = await digitalization_tool.execute(digitalize_params)
        
        if not digitalization_result.success:
            raise HTTPException(status_code=500, detail=digitalization_result.error or "Slide digitalization failed")
            
        return {
            "success": True,
            "document_id": document_id,
            "digitalized_content": digitalization_result.data,
            "fetch_time": fetch_result.execution_time,
            "digitalization_time": digitalization_result.execution_time,
            "agent_notes": {
                "fetch_notes": fetch_result.agent_notes,
                "digitalization_notes": digitalization_result.agent_notes
            }
        }
        
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in /digitalize-document endpoint: {type(e).__name__} - {e}")
        # Potentially log traceback for more detail: import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during document digitalization: {str(e)}")


@router.post("/find-web-documents", response_model=AgentResponse)
async def find_web_documents_endpoint(
    search_query: str = Form(...),
    file_type: Optional[str] = Form("pdf"),
    country_code: Optional[str] = Form(None),
    download_files: bool = Form(False),
    download_location: Optional[str] = Form(None),
    max_search_results: int = Form(20)
):
    """Searches the web for specific file types and optionally downloads them."""
    try:
        finder_tool = tool_registry.get_tool("webdocumentfinder")
        if not finder_tool:
            raise HTTPException(status_code=500, detail="WebDocumentFinderTool not available.")

        params = {
            "search_query": search_query,
            "file_type": file_type,
            "country_code": country_code,
            "download_files": download_files,
            "download_location": download_location,
            "max_search_results": max_search_results
        }

        result = await finder_tool.execute(params)

        if result.success and result.data:
            # Determine the primary list of files (either downloaded or links)
            files_list = result.data.get('downloaded_files') if download_files else result.data.get('files')
            if files_list is None: files_list = [] # Ensure it's a list
            
            # Construct a meaningful response string
            response_message = f"Found {result.data.get('files_found_count', 0)} potential links. "
            if download_files:
                response_message += f"Successfully downloaded {len(result.data.get('downloaded_files', []))} files. "
                if result.data.get('download_errors'):
                    response_message += f"{len(result.data.get('download_errors', []))} download errors encountered."
            else:
                response_message += f"Returning {len(files_list)} links."

            return AgentResponse(
                session_id=uuid.uuid4().hex,
                response=response_message.strip(),
                data=result.data,
                success=True,
                error_message=None, # Explicitly set for clarity
                errors=[],          # Explicitly set for clarity
                execution_summary=result.agent_notes, # Or a more structured summary if available
                processing_time=getattr(result, 'execution_time', None)
                # suggested_follow_ups and agent_reasoning can be added if applicable
            )
        elif result.success: # Success but no data (e.g. no files found)
            return AgentResponse(
                session_id=uuid.uuid4().hex,
                response=result.data.get("message", "Search completed, but no files found matching criteria.") if result.data else "Search completed, no specific data returned.",
                data=result.data if result.data else {},
                success=True,
                error_message=None,
                errors=[],
                execution_summary=result.agent_notes,
                processing_time=getattr(result, 'execution_time', None)
            )
        else: # Tool execution failed
            # For a 500 error from the tool itself, we might want to return a structured AgentResponse
            # or stick to HTTPException. For consistency with other direct tool errors, HTTPException is fine.
            # However, the original error was Pydantic validation on AgentResponse, so let's ensure failure also can be structured if not raising HTTPException.
            # If we want the endpoint to always return AgentResponse (even for tool failures not caught as HTTPExceptions earlier):
            # return AgentResponse(
            #     session_id=uuid.uuid4().hex,
            #     response="Failed to process the request due to a tool error.",
            #     data=None,
            #     success=False,
            #     error_message=result.error or "Unknown tool execution error.",
            #     errors=[result.error or "Unknown tool execution error."],
            #     execution_summary=result.agent_notes,
            #     processing_time=getattr(result, 'execution_time', None)
            # )
            # Sticking to HTTPException for tool failures for now as per previous structure for other direct tool calls.
            raise HTTPException(status_code=500, detail=result.error or "Failed to find web documents due to an internal tool error.")

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        # Log the full error for debugging
        error_id = uuid.uuid4().hex
        print(f"Error ID {error_id} in /find-web-documents endpoint: {type(e).__name__} - {e}")
        # import traceback; traceback.print_exc() # for more detailed server-side logs
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred. Please try again or contact support with error ID: {error_id}")


@router.post("/general-web-search", response_model=AgentResponse)
async def general_web_search_endpoint(
    search_query: str = Form(...),
    max_results: int = Form(10),
    region: str = Form("wt-wt") # Default to worldwide, user can specify e.g. 'us-en'
):
    """Performs a general web search and returns titles, URLs, and snippets."""
    try:
        search_tool = tool_registry.get_tool("generalwebsearch") # Name is auto-lowercased
        if not search_tool:
            raise HTTPException(status_code=500, detail="GeneralWebSearchTool not available.")

        params = {
            "search_query": search_query,
            "max_results": max_results,
            "region": region
        }

        result = await search_tool.execute(params)

        if result.success and result.data:
            search_results = result.data.get("search_results", [])
            response_message = f"Found {len(search_results)} results for your query."
            
            return AgentResponse(
                session_id=uuid.uuid4().hex,
                response=response_message,
                data=result.data, # Contains {"search_results": [...]}
                success=True,
                error_message=None,
                errors=[],
                execution_summary=result.agent_notes,
                processing_time=getattr(result, 'execution_time', None)
            )
        elif result.success: # Success but no data/results
             return AgentResponse(
                session_id=uuid.uuid4().hex,
                response="Search completed, but no results were found.",
                data=result.data if result.data else {},
                success=True,
                error_message=None,
                errors=[],
                execution_summary=result.agent_notes,
                processing_time=getattr(result, 'execution_time', None)
            )
        else: # Tool execution failed
            raise HTTPException(status_code=500, detail=result.error or "General web search failed due to an internal tool error.")

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        error_id = uuid.uuid4().hex
        print(f"Error ID {error_id} in /general-web-search endpoint: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred. Error ID: {error_id}") 


@router.post("/find-course-pdfs", response_model=AgentResponse)
async def find_course_pdfs_endpoint(
    course_topic: str = Form(...),
    course_level: Optional[str] = Form(None),
    institution_type: Optional[str] = Form(None),
    language: str = Form("en"),
    country: Optional[str] = Form(None),
    download_pdfs: bool = Form(False),
    download_location: Optional[str] = Form(None),
    max_pdfs: int = Form(5)
):
    """Find and optionally download course PDFs using OpenAI web search."""
    try:
        pdf_finder = tool_registry.get_tool("coursepdffinder") # Name is auto-transformed from CoursePdfFinderTool
        if not pdf_finder:
            raise HTTPException(status_code=500, detail="CoursePdfFinderTool not available.")

        params = {
            "course_topic": course_topic,
            "course_level": course_level,
            "institution_type": institution_type,
            "language": language,
            "country": country,
            "download_pdfs": download_pdfs,
            "download_location": download_location,
            "max_pdfs": max_pdfs
        }

        result = await pdf_finder.execute(params)

        if result.success and result.data:
            pdfs_found = result.data.get("found_count", 0)
            downloaded_count = len(result.data.get("downloaded_files", []))
            
            if download_pdfs:
                response_message = f"Found {pdfs_found} course PDFs for '{course_topic}'. Downloaded {downloaded_count} successfully."
            else:
                response_message = f"Found {pdfs_found} course PDFs for '{course_topic}'. Ready for download."
            
            return AgentResponse(
                session_id=uuid.uuid4().hex,
                response=response_message,
                data=result.data,
                success=True,
                error_message=None,
                errors=[],
                execution_summary=result.agent_notes,
                processing_time=getattr(result, 'execution_time', None)
            )
        elif result.success: # Success but no PDFs found
            return AgentResponse(
                session_id=uuid.uuid4().hex,
                response=f"No course PDFs found for '{course_topic}' matching the specified criteria.",
                data=result.data if result.data else {},
                success=True,
                error_message=None,
                errors=[],
                execution_summary=result.agent_notes,
                processing_time=getattr(result, 'execution_time', None)
            )
        else: # Tool execution failed
            raise HTTPException(status_code=500, detail=result.error or "Course PDF finder failed due to an internal tool error.")

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        error_id = uuid.uuid4().hex
        print(f"Error ID {error_id} in /find-course-pdfs endpoint: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred. Error ID: {error_id}")