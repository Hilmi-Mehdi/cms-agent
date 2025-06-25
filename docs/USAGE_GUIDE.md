# AI Course Management Agent - Complete Usage Guide

## 🚀 Quick Start

### 1. Basic Usage (Programmatic)

```python
import asyncio
from app.agent.core_agent import course_agent

async def basic_example():
    response = await course_agent.process_request(
        user_request="Analyze this content and create a quiz",
        context={
            "content": "Your course content here...",
            "target_audience": "beginner"
        }
    )
    print(response.response)

asyncio.run(basic_example())
```

### 2. Using via API (HTTP)

```bash
# Start the server
python3 -m uvicorn app.main:app --host localhost --port 8001

# Make requests
curl -X POST "http://localhost:8001/api/v1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Create a quiz from this content",
    "context": {"target_audience": "intermediate"}
  }'
```

### 3. Document Analysis from Science Made Simple API

```bash
# Analyze a document by ID
curl -X POST "http://localhost:8001/api/v1/analyze-document" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "document_id=ct13hjqcchrs715kgjl0&ai_provider=openai&analysis_depth=comprehensive&target_audience=intermediate"
```

### 4. Finding Web Documents (e.g., PDFs on a topic)

```bash
# Find PDF documents about 'electrostatics in Belgium' and get links
curl -X POST "http://localhost:8001/api/v1/find-web-documents" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "search_query=electrostatics study&file_type=pdf&country_code=be&download_files=false&max_search_results=10"

# Search for DOCX files on 'quantum computing algorithms' and download them
# (Files will be saved to a default 'downloaded_web_files' directory or a specified 'download_location')
curl -X POST "http://localhost:8001/api/v1/find-web-documents" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "search_query=quantum computing algorithms review&file_type=docx&download_files=true&max_search_results=5"
```

### 5. General Web Search (e.g., for information)

```bash
# Search for general information about 'exam dates for University of Brussels 2024'
curl -X POST "http://localhost:8001/api/v1/general-web-search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "search_query=exam dates for University of Brussels 2024&max_results=5&region=be-fr"
```

## 📋 Available Tools

### Core Analysis Tools
- **ContentAnalyzerTool**: Analyze text content for educational insights
- **SlideAnalyzerTool**: Analyze presentation slides and extract course information  
- **ContentGeneratorTool**: Generate educational content (quizzes, summaries, etc.)
- **FileProcessorTool**: Process uploaded files (PDFs, images, etc.)

### Science Made Simple Integration
- **DocumentFetcherTool**: Fetch documents and extract images from Science Made Simple API
- **DocumentAnalyzerTool**: Complete document analysis workflow (fetch → extract → analyze)

### Web Search Tools
- **WebDocumentFinderTool**: Searches the web for specific file types (e.g., PDF, DOCX) based on a query, an optional country filter (e.g. `site:.be`), and file type (e.g. `filetype:pdf`). Can return links or download files directly using `duckduckgo-search`. Handles entire search and download process in one call.
    - `search_query` (string, required): The main search query.
    - `file_type` (string, optional, default: "pdf"): Desired file extension.
    - `country_code` (string, optional): Two-letter country code to add `site:.XX` to the query.
    - `download_files` (boolean, optional, default: False): If true, download files.
    - `download_location` (string, optional): Directory to save downloaded files. Defaults to `./downloaded_web_files/`.
    - `max_search_results` (integer, optional, default: 20): Max results from search engine.

- **GeneralWebSearchTool**: Performs a general web search (not file-specific) using `duckduckgo-search` and returns a list of search results including titles, URLs, and snippets.
    - `search_query` (string, required): The search query.
    - `max_results` (integer, optional, default: 10): Maximum number of search results to return.
    - `region` (string, optional, default: "wt-wt"): Region for search (e.g., 'us-en', 'fr-fr').

## 🔄 Building Automation Workflows

### Pattern 1: Document Processing Pipeline

```python
async def document_processing_pipeline(document_id):
    """Complete document processing from API to analysis."""
    
    # Step 1: Fetch document data and images
    fetcher = tool_registry.get_tool("documentfetcher")
    fetch_result = await fetcher.execute({
        "document_id": document_id,
        "extract_images": True,
        "max_images": 30
    })
    
    if not fetch_result.success:
        return {"error": "Failed to fetch document"}
    
    results = {
        "document_metadata": fetch_result.data["document_metadata"],
        "fetch_time": fetch_result.execution_time
    }
    
    # Step 2: Analyze slides if images were extracted
    if fetch_result.data.get("extracted_images", {}).get("status") == "success":
        image_paths = fetch_result.data["extracted_images"]["image_paths"]
        
        analyzer = tool_registry.get_tool("slideanalyzer")
        slide_result = await analyzer.execute({
            "slide_images": image_paths,
            "analysis_depth": "comprehensive",
            "ai_provider": "openai"
        })
        
        if slide_result.success:
            results["slide_analysis"] = slide_result.data
            results["analysis_time"] = slide_result.execution_time
    
    # Step 3: Generate additional content based on analysis
    if "slide_analysis" in results:
        generator = tool_registry.get_tool("contentgenerator")
        gen_result = await generator.execute({
            "content_type": "summary",
            "source_content": results["slide_analysis"].get("detailed_description", ""),
            "target_audience": "intermediate",
            "length": "medium"
})

        if gen_result.success:
            results["generated_content"] = gen_result.data
    
    return results

# Usage
result = await document_processing_pipeline("ct13hjqcchrs715kgjl0")
```

### Pattern 2: Sequential Workflow

```python
class SequentialWorkflow:
    async def run_workflow(self, input_data):
        results = {}
        
        # Step 1: Analyze
        analyzer = tool_registry.get_tool("contentanalyzer")
        analysis = await analyzer.execute({"content": input_data})
        results["analysis"] = analysis.data
        
        # Step 2: Enhance based on analysis
        enhancer = tool_registry.get_tool("contentenhancer")
        enhancement = await enhancer.execute({
            "content": input_data,
            "enhancement_type": "examples"
        })
        results["enhanced"] = enhancement.data
        
        # Step 3: Generate quiz
        generator = tool_registry.get_tool("contentgenerator")
        quiz = await generator.execute({
            "content_type": "quiz",
            "source_content": enhancement.data["enhanced_content"]
        })
        results["quiz"] = quiz.data
        
        return results
```

### Pattern 3: Parallel Processing

```python
import asyncio

class ParallelWorkflow:
    async def run_parallel_analysis(self, content):
        # Run multiple analyses concurrently
        tasks = [
            self.analyze_structure(content),
            self.check_readability(content), 
            self.validate_code(content),
            self.assess_difficulty(content)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "structure": results[0],
            "readability": results[1],
            "code_validation": results[2],
            "difficulty": results[3]
        }
```

### Pattern 4: Conditional Workflow

```python
class ConditionalWorkflow:
    async def smart_processing(self, content, requirements):
        results = {}
        
        # Always analyze first
        analysis = await self.analyze_content(content)
        results["analysis"] = analysis
        
        # Conditional processing based on analysis
        if analysis.get("has_code", False):
            code_result = await self.validate_code(content)
            results["code_validation"] = code_result
        
        if analysis.get("difficulty_level") == "beginner":
            enhanced = await self.add_examples(content)
            results["enhancement"] = enhanced
        
        if requirements.get("generate_quiz", False):
            quiz = await self.create_quiz(content)
            results["quiz"] = quiz
        
        return results
```

## 🤖 Working with AI Providers

### Switching Providers

```python
from app.models.schemas import AIProvider

# Use OpenAI
response = await course_agent.process_request(
    user_request="Analyze this content",
    preferred_provider=AIProvider.OPENAI
)

# Use Google AI
response = await course_agent.process_request(
    user_request="Analyze this content", 
    preferred_provider=AIProvider.GOOGLE
)
```

### Testing Provider Connections

```python
from app.utils.ai_client import ai_client

# Test all providers
results = await ai_client.test_connections()
print(f"OpenAI: {'✅' if results['openai'] else '❌'}")
print(f"Google: {'✅' if results['google'] else '❌'}")
```

## 📊 Advanced Usage Patterns

### 1. Batch Processing

```python
async def process_multiple_courses(course_list):
    results = []
    
    for course in course_list:
        try:
            result = await course_agent.process_request(
                user_request="Analyze and enhance this course content",
                context={
                    "content": course["content"],
                    "target_audience": course.get("audience", "intermediate")
                }
            )
            results.append({
                "course_id": course["id"],
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "course_id": course["id"],
                "status": "failed", 
                "error": str(e)
            })
    
    return results
```

### 2. Custom Context Management

```python
class CourseProcessor:
    def __init__(self):
        self.session_context = {}
    
    async def process_with_context(self, request, course_id):
        # Load previous context for this course
        context = self.session_context.get(course_id, {})
        
        # Add new information
        context.update(request.get("context", {}))
        
        # Process with accumulated context
        response = await course_agent.process_request(
            user_request=request["user_request"],
            context=context
        )
        
        # Update session context
        self.session_context[course_id] = {
            **context,
            "last_response": response.response,
            "processing_history": context.get("processing_history", []) + [request["user_request"]]
        }
        
        return response
```

### 3. Result Caching and Optimization

```python
import hashlib
import json

class CachedProcessor:
    def __init__(self):
        self.cache = {}
    
    def _generate_cache_key(self, request, context):
        content = json.dumps({
            "request": request,
            "context": context
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def process_with_cache(self, request, context):
        cache_key = self._generate_cache_key(request, context)
        
        # Check cache first
        if cache_key in self.cache:
            print("📋 Using cached result")
            return self.cache[cache_key]
        
        # Process if not cached
        result = await course_agent.process_request(request, context)
        
        # Cache the result
        self.cache[cache_key] = result
        
        return result
```

## 🔧 Tool Development Best Practices

### 1. Error Handling

```python
class RobustTool(BaseTool):
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            # Validate inputs
            self._validate_inputs(parameters)
            
            # Process
            result = await self._process(parameters)
            
            return ToolResult(
                success=True,
                data=result,
                message="Processing completed"
            )
            
        except ValueError as e:
            return ToolResult(
                success=False,
                error=f"Invalid input: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Processing failed: {str(e)}"
            )
    
    def _validate_inputs(self, parameters):
        required = ["content"]
        for param in required:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
```

### 2. Progress Tracking

```python
class ProgressTrackingTool(BaseTool):
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        total_steps = 5
        progress_data = {"current_step": 0, "total_steps": total_steps}
        
        for step in range(total_steps):
            # Update progress
            progress_data["current_step"] = step + 1
            progress_data["step_name"] = f"Step {step + 1}"
            
            # Do processing
            await self._process_step(step, parameters)
            
            # Could emit progress events here
            print(f"Progress: {step + 1}/{total_steps}")
        
        return ToolResult(
            success=True,
            data={"result": "completed", "progress": progress_data}
        )
```

### 3. Resource Management

```python
class ResourceManagedTool(BaseTool):
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        resources = []
        
        try:
            # Acquire resources
            file_handle = await self._open_file(parameters["file_path"])
            resources.append(file_handle)
            
            api_client = await self._connect_to_api()
            resources.append(api_client)
            
            # Process
            result = await self._process_with_resources(file_handle, api_client)
            
            return ToolResult(success=True, data=result)
            
        finally:
            # Clean up resources
            for resource in resources:
                await self._cleanup_resource(resource)
```

## 📈 Performance Optimization

### 1. Concurrent Tool Execution

```python
# The agent automatically handles this, but you can control it:
async def optimized_processing():
    # Tools that can run in parallel
    concurrent_tasks = [
        tool_registry.get_tool("contentanalyzer").execute({"content": content}),
        tool_registry.get_tool("fileprocessor").execute({"file_path": path}),
        tool_registry.get_tool("coursestats").execute({"content": content})
    ]
    
    results = await asyncio.gather(*concurrent_tasks)
    return results
```

### 2. Streaming Results

```python
class StreamingTool(BaseTool):
    async def execute_streaming(self, parameters: Dict[str, Any]):
        """Execute with streaming results."""
        chunks = self._split_work(parameters)
        
        for chunk in chunks:
            result = await self._process_chunk(chunk)
            yield ToolResult(
                success=True,
                data=result,
                message=f"Chunk processed: {chunk['id']}"
            )
```

## 🎯 Common Use Cases

### 1. Content Quality Assurance

```python
async def quality_check_pipeline(content):
    # Multi-dimensional quality check
    checks = [
        ("structure", analyze_structure),
        ("readability", check_readability),
        ("accuracy", verify_accuracy),
        ("completeness", assess_completeness)
    ]
    
    results = {}
    overall_score = 0
    
    for check_name, check_func in checks:
        result = await check_func(content)
        results[check_name] = result
        overall_score += result.get("score", 0)
    
    return {
        "overall_score": overall_score / len(checks),
        "detailed_results": results,
        "passed": overall_score / len(checks) >= 75
    }
```

### 2. Automated Content Generation

```python
async def generate_complete_course(topic, audience, duration):
    # Generate comprehensive course materials
    workflow = [
        ("outline", create_course_outline),
        ("content", develop_content_sections),
        ("examples", add_practical_examples),
        ("exercises", create_practice_exercises),
        ("assessments", generate_quizzes),
        ("resources", compile_additional_resources)
    ]
    
    course_materials = {}
    
    for material_type, generator_func in workflow:
        material = await generator_func(
            topic=topic,
            audience=audience,
            duration=duration,
            previous_materials=course_materials
        )
        course_materials[material_type] = material
    
    return course_materials
```

### 3. Adaptive Learning Path

```python
async def create_adaptive_path(student_level, learning_goals, content_pool):
    # Analyze student needs
    needs_analysis = await course_agent.process_request(
        user_request="Analyze learning requirements and suggest optimal path",
        context={
            "student_level": student_level,
            "goals": learning_goals,
            "available_content": content_pool
        }
    )
    
    # Generate personalized sequence
    learning_path = await course_agent.process_request(
        user_request="Create step-by-step learning sequence",
        context={
            "analysis": needs_analysis.response,
            "content_pool": content_pool
        }
    )
    
    return {
        "analysis": needs_analysis,
        "learning_path": learning_path,
        "estimated_duration": calculate_duration(learning_path),
        "difficulty_progression": analyze_progression(learning_path)
    }
```

## 🚀 Getting Started Checklist

### ✅ Basic Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure API keys in `.env` file
- [ ] Test basic functionality: `python3 test_agent.py`
- [ ] Start the server: `python3 start.py`

### ✅ First Custom Tool
- [ ] Create tool class extending `BaseTool`
- [ ] Define `get_definition()` method
- [ ] Implement `execute()` method
- [ ] Register with `tool_registry.register_tool()`
- [ ] Test with direct execution

### ✅ First Automation Workflow
- [ ] Design your workflow steps
- [ ] Identify which tools you need
- [ ] Handle errors and edge cases
- [ ] Add progress tracking
- [ ] Test with sample data

### ✅ Production Deployment
- [ ] Set up proper environment configuration
- [ ] Implement logging and monitoring
- [ ] Add authentication if needed
- [ ] Set up health checks
- [ ] Configure rate limiting

## 💡 Tips and Tricks

1. **Tool Naming**: Tool names are automatically derived by removing "Tool" suffix and converting to lowercase. `MyAwesomeTool` becomes `myawesome`.

2. **Context Management**: Use the `context` parameter to pass additional information that helps the agent make better decisions.

3. **Error Recovery**: Implement graceful error handling in tools to prevent workflow failures.

4. **Performance**: Use async/await throughout for better concurrency. The agent can run multiple tools in parallel.

5. **Testing**: Always test tools individually before using them in workflows.

6. **Monitoring**: Use the built-in timing and logging features to monitor performance.

7. **Extensibility**: Design tools to be composable - small, focused tools work better than monolithic ones.

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Tool Not Found**: Check tool registration and name formatting
2. **Parameter Validation Errors**: Verify parameter types and required fields
3. **AI Provider Errors**: Check API keys and connection status
4. **Performance Issues**: Monitor concurrent tool execution limits
5. **Memory Issues**: Implement proper resource cleanup in tools

### Debugging Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check tool registry
print("Available tools:", tool_registry.available_tools)

# Test AI connections
results = await ai_client.test_connections()
print("AI Provider Status:", results)

# Validate tool definitions
for tool_name in tool_registry.available_tools:
    tool = tool_registry.get_tool(tool_name)
    print(f"Tool {tool_name}: {tool.definition}")
```

## 🧪 Sophisticated Quiz Generation

### Extract Exercises from Slides and Generate Realistic Quizzes

The system can now automatically extract exercises from slide content and generate sophisticated multiple-choice quizzes with AI-powered realistic distractors.

#### Key Features
- **Exercise Detection**: Automatically finds questions, problems, and exercises in slides
- **Cross-Slide Matching**: Matches questions with answers that may be on different slides  
- **Realistic Distractors**: Generates 3 plausible wrong answers using AI
- **Question Classification**: Categorizes questions by type (calculation, conceptual, etc.)
- **Difficulty Scaling**: Adjusts question difficulty and point values

#### API Usage

```bash
# Generate quiz during document analysis
curl -X POST "http://localhost:8001/api/v1/analyze-document" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "document_id=ct13hjqcchrs715kgjl0&generate_quiz=true&max_quiz_questions=5&difficulty_level=intermediate"

# Generate quiz from existing slide analysis  
curl -X POST "http://localhost:8001/api/v1/generate-quiz" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "slide_analysis_data={...}&max_questions=10&difficulty_level=advanced"
```

#### Programmatic Usage

```python
from app.tools import tool_registry

async def generate_quiz_from_slides(slide_analysis_data):
    """Generate sophisticated quiz from slide content."""
    
    quiz_generator = tool_registry.get_tool("quizgenerator")
    
    result = await quiz_generator.execute({
        "slide_analysis_data": slide_analysis_data,
        "ai_provider": "openai",
        "max_questions": 10,
        "difficulty_level": "intermediate",
        "subject_area": "physics"
    })
    
    if result.success:
        quiz_data = result.data
        
        # Access quiz metadata
        metadata = quiz_data["quiz_metadata"]
        print(f"Generated {metadata['total_questions']} questions")
        print(f"Subject: {metadata['subject_area']}")
        print(f"Difficulty: {metadata['difficulty_level']}")
        
        # Process questions
        for question in quiz_data["questions"]:
            print(f"Q{question['question_id']}: {question['question_text']}")
            print(f"Type: {question['question_type']} | Points: {question['points']}")
            print(f"Source: Slide {question['source_slide']} → Answer: Slide {question['answer_slide']}")
            
            # Options with correct answer marked
            for option, text in question["options"].items():
                marker = "✓" if option == question["correct_answer"] else " "
                print(f"  {marker} {option}) {text}")
            
            print(f"Explanation: {question['explanation']}\n")
        
        return quiz_data
    else:
        print(f"Quiz generation failed: {result.error}")
        return None
```

#### Complete Workflow Example

```python
async def complete_quiz_workflow(document_id):
    """Complete workflow: fetch document → analyze slides → generate quiz."""
    
    # Step 1: Analyze document with quiz generation
    document_analyzer = tool_registry.get_tool("documentanalyzer")
    
    analysis_result = await document_analyzer.execute({
        "document_id": document_id,
        "ai_provider": "openai",
        "analysis_depth": "comprehensive",
        "target_audience": "intermediate"
    })
    
    if not analysis_result.success:
        return {"error": "Document analysis failed"}
    
    # Step 2: Generate quiz from slide analysis
    if "slide_analysis" in analysis_result.data:
        quiz_generator = tool_registry.get_tool("quizgenerator")
        
        quiz_result = await quiz_generator.execute({
            "slide_analysis_data": analysis_result.data["slide_analysis"],
            "ai_provider": "openai",
            "max_questions": 8,
            "difficulty_level": "intermediate",
            "subject_area": "physics"
        })
        
        return {
            "document_analysis": analysis_result.data,
            "quiz": quiz_result.data if quiz_result.success else None,
            "quiz_error": quiz_result.error if not quiz_result.success else None
        }
    
    return {"error": "No slide analysis available for quiz generation"}
```

#### Exercise Detection Patterns

The system recognizes various exercise patterns in multiple languages:

```python
# Detected patterns include:
patterns = [
    "Exercise 1: Calculate the force...",
    "Problem: Find the velocity when...", 
    "Question: What is the acceleration?",
    "Calculate the magnetic field strength",
    "Determine the period of oscillation",
    "Given that F = 10N, find the displacement",
    "If the current is 2A, what is the voltage?"
]

# Also detects numbered questions:
numbered_patterns = [
    "1. Calculate the momentum of...",
    "2) What happens when the temperature increases?",
    "3. Determine the frequency of..."
]
```

#### Question Types and Point Values

The system classifies questions and assigns point values:

```python
question_types = {
    "calculation": 3,      # Mathematical computations
    "explanation": 2,      # Describe or explain concepts  
    "identification": 1,   # What/which questions
    "procedure": 2,        # How to do something
    "reasoning": 3,        # Why questions
    "general": 2          # Other types
}

difficulty_multipliers = {
    "beginner": 1.0,
    "intermediate": 1.5,
    "advanced": 2.0
}

# Final points = base_points × difficulty_multiplier
```

#### Distractor Generation

AI-powered distractor generation creates realistic wrong answers:

```python
# For numerical answers:
# - Common calculation errors (factor of 2, wrong sign, unit confusion)
# - Partial solutions (intermediate steps)
# - Formula misapplication

# For conceptual answers:
# - Related but incorrect concepts
# - Common misconceptions
# - Partially correct statements

# Example for F = ma calculation:
question = "If mass = 5kg and acceleration = 2m/s², what is the force?"
correct_answer = "10 N"
distractors = [
    "20 N",      # Common error: F = m × 2a
    "5 N",       # Confusion: using only mass
    "2.5 N"      # Division instead of multiplication
]
```

#### Quiz Output Format

```json
{
  "quiz_metadata": {
    "total_questions": 5,
    "difficulty_level": "intermediate", 
    "subject_area": "physics",
    "source_slides": 17,
    "ai_provider": "openai"
  },
  "questions": [
    {
      "question_id": 1,
      "question_text": "Calculate the magnetic force on a conductor with current 2A in a field of 0.5T",
      "question_type": "calculation",
      "source_slide": 3,
      "answer_slide": 4,
      "options": {
        "A": "1.0 N",          // Correct answer
        "B": "0.5 N",          // Distractor 1
        "C": "2.0 N",          // Distractor 2  
        "D": "4.0 N"           // Distractor 3
      },
      "correct_answer": "A",
      "explanation": "Found on slide 4: F = BIL, where B=0.5T, I=2A, L=1m",
      "difficulty": "intermediate",
      "points": 4
    }
  ],
  "generation_stats": {
    "exercises_found": 8,
    "pairs_matched": 6,
    "questions_generated": 5
  }
}
```

#### Integration with Document Analysis

```bash
# Enable quiz generation in document analysis
curl -X POST "http://localhost:8001/api/v1/analyze-document" \
  -d "document_id=your_doc_id" \
  -d "generate_quiz=true" \
  -d "max_quiz_questions=10" \
  -d "difficulty_level=advanced" \
  -d "subject_area=physics"
```

This will return both the full document analysis AND the generated quiz in a single response.

This guide should give you everything you need to effectively use and extend your AI Course Management Agent! 🚀 