# SMS-Agent (Science Made Simple Agent)

An intelligent AI agent system for course content analysis and educational material generation using OpenAI and Google AI models.

## 🚀 Features

- **Multi-Provider AI Support**: Works with both OpenAI GPT models and Google Gemini
- **Course Content Analysis**: Analyze course materials, extract key concepts, and assess difficulty
- **Content Generation**: Generate summaries, quizzes, exercises, study guides, and more
- **File Processing**: Extract content from PDF, PPTX, DOCX, TXT, and MD files
- **Intelligent Task Planning**: AI-powered multi-step task orchestration
- **Flexible Tool System**: Extensible architecture for adding new capabilities
- **RESTful API**: FastAPI-based web service with automatic documentation
- **Async Processing**: Concurrent task execution for optimal performance

## 🏗️ Architecture

The system follows a modular architecture with these key components:

```
├── app/
│   ├── agent/           # Core AI agent logic
│   ├── tools/           # Tool implementations
│   ├── models/          # Data models and schemas
│   ├── utils/           # Utilities (AI client, etc.)
│   ├── routers/         # FastAPI route handlers
│   └── config.py        # Configuration management
```

### Core Components

- **CourseManagementAgent**: Main orchestrator that analyzes intent, plans tasks, and coordinates execution
- **Tool Registry**: Manages available tools and their capabilities
- **AI Client Manager**: Handles communication with multiple AI providers
- **Content Analyzer**: Extracts insights from educational content
- **File Processor**: Handles multiple document formats
- **Content Generator**: Creates educational materials

## 📦 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (optional but recommended)
- Google AI API key (optional but recommended)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd sms_agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp config.env.example .env
```

Edit `.env` with your API keys:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-1106-preview

# Google AI Configuration  
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-pro

# Other settings (optional)
MAX_CONCURRENT_TOOLS=3
TOOL_EXECUTION_TIMEOUT=300
ENABLE_CONTENT_CACHING=true
```

## 🚀 Quick Start

### Running the API Server

```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Basic Usage Examples

#### 1. Analyze Course Content

```bash
curl -X POST "http://localhost:8000/api/v1/analyze-content" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content=Introduction to Machine Learning: This course covers supervised learning, unsupervised learning, and neural networks. Students will learn about regression, classification, clustering, and deep learning techniques.&analysis_type=comprehensive&target_audience=intermediate"
```

#### 2. Generate Educational Content

```bash
curl -X POST "http://localhost:8000/api/v1/generate-content" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content_type=quiz&source_content=Machine learning fundamentals including supervised and unsupervised learning&target_audience=beginner&length=medium"
```

#### 3. Process Files with AI Agent

```python
import requests

# Upload and process files
files = {'files': open('course_material.pdf', 'rb')}
data = {
    'user_query': 'Analyze this course material and create a summary',
    'target_audience': 'undergraduate students'
}

response = requests.post(
    'http://localhost:8000/api/v1/process-with-files',
    files=files,
    data=data
)
print(response.json())
```

## 🛠️ API Endpoints

### Core Agent Endpoints

- `POST /api/v1/process` - Process text-based requests
- `POST /api/v1/process-with-files` - Process requests with file uploads
- `GET /api/v1/tools` - List available tools
- `GET /api/v1/providers` - Get AI provider status

### Direct Tool Access

- `POST /api/v1/analyze-content` - Direct content analysis
- `POST /api/v1/generate-content` - Direct content generation

### System Health

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status

## 🧰 Available Tools

### 1. Content Analyzer
Analyzes educational content to extract:
- Key concepts and topics
- Learning objectives
- Difficulty assessment
- Content structure
- Prerequisites

**Usage**:
```python
{
    "content": "Your course content here",
    "analysis_type": "comprehensive|structure|concepts|objectives|difficulty",
    "target_audience": "beginner|intermediate|advanced",
    "subject_area": "computer science"
}
```

### 2. File Processor
Extracts content from various file formats:
- PDF documents
- PowerPoint presentations (PPTX)
- Word documents (DOCX)
- Text files (TXT)
- Markdown files (MD)

**Usage**:
```python
{
    "file_path": "path/to/file.pdf",
    "extraction_type": "text|structured|metadata|full",
    "include_images": false,
    "max_size_mb": 50
}
```

### 3. Content Generator
Generates educational materials:
- Summaries
- Quizzes and assessments
- Practice exercises
- Study guides
- Flashcards
- Course outlines

**Usage**:
```python
{
    "content_type": "summary|quiz|exercises|explanations|study_guide|flashcards|outline",
    "source_content": "Content to base generation on",
    "target_audience": "beginner|intermediate|advanced|expert",
    "length": "short|medium|long|comprehensive",
    "format": "markdown|html|plain_text|json"
}
```

## 🤖 AI Providers

The system supports multiple AI providers:

### OpenAI
- **Models**: GPT-4, GPT-3.5-turbo
- **Features**: Function calling, high-quality text generation
- **Best for**: Complex analysis, structured outputs

### Google AI (Gemini)
- **Models**: Gemini Pro
- **Features**: Large context windows, multimodal capabilities
- **Best for**: Long content analysis, diverse content types

## 📊 Example Workflows

### 1. Course Content Analysis Workflow

1. **Upload course materials** (PDF, PPTX, etc.)
2. **Agent analyzes intent** and plans execution
3. **File processor** extracts content
4. **Content analyzer** identifies key concepts
5. **Agent generates** comprehensive analysis report

### 2. Educational Content Creation Workflow

1. **Provide source content** and requirements
2. **Agent plans** content generation strategy
3. **Content generator** creates materials
4. **Quality assessment** ensures output meets standards
5. **Structured response** with generated content

### 3. Multi-step Analysis Workflow

1. **Intent classification** determines user goals
2. **Task planning** creates execution strategy
3. **Parallel tool execution** for efficiency
4. **Result synthesis** combines outputs
5. **Intelligent response** generation

## 🔧 Configuration

### Environment Variables

```bash
# AI Provider Settings
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-1106-preview
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL=gemini-pro

# Agent Configuration
MAX_CONCURRENT_TOOLS=3          # Max parallel tool execution
TOOL_EXECUTION_TIMEOUT=300      # Tool timeout in seconds
ENABLE_CONTENT_CACHING=true     # Enable result caching
SESSION_TTL_HOURS=24           # Session expiration time

# API Configuration
API_HOST=localhost
API_PORT=8000
API_PREFIX=/api/v1
LOG_LEVEL=INFO
```

### Supported File Types

- **PDF**: `.pdf`
- **PowerPoint**: `.pptx`
- **Word**: `.docx`
- **Text**: `.txt`
- **Markdown**: `.md`

Maximum file size: 50MB (configurable)

## 🚀 Advanced Usage

### Custom Tool Development

Create custom tools by extending the `BaseTool` class:

```python
from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult

class CustomTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="custom_tool",
            description="Description of what this tool does",
            parameters=[
                ToolParameter(
                    name="input_param",
                    type="string",
                    description="Input parameter description",
                    required=True
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        # Your tool logic here
        return ToolResult(
            success=True,
            data={"result": "Tool output"}
        )

# Register the tool
from app.tools.base_tool import tool_registry
tool_registry.register_tool(CustomTool())
```

### Batch Processing

Process multiple files or requests:

```python
import asyncio
import requests

async def process_multiple_files(file_paths, query):
    tasks = []
    for file_path in file_paths:
        files = {'files': open(file_path, 'rb')}
        data = {'user_query': query}
        
        task = requests.post(
            'http://localhost:8000/api/v1/process-with-files',
            files=files,
            data=data
        )
        tasks.append(task)
    
    return tasks
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health/detailed
```

### Test AI Providers
```bash
curl http://localhost:8000/api/v1/providers
```

### Test Tool Registry
```bash
curl http://localhost:8000/api/v1/tools
```

## 📈 Performance Optimization

- **Concurrent Processing**: Tools execute in parallel when possible
- **Content Caching**: Results cached to avoid reprocessing
- **Async Architecture**: Non-blocking I/O for scalability
- **Resource Limits**: Configurable timeouts and concurrency limits

## 🔒 Security Considerations

- **API Key Security**: Store keys in environment variables
- **File Upload Limits**: Configurable size and type restrictions
- **Input Validation**: All inputs validated before processing
- **Temporary File Cleanup**: Uploaded files automatically cleaned up

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the [API documentation](http://localhost:8000/docs)
2. Review the health check endpoint
3. Check logs for error details
4. Verify API key configuration

## 🔮 Future Enhancements

- **Database Integration**: Full DynamoDB implementation
- **Authentication**: User management and API authentication
- **Webhooks**: Real-time notifications
- **Batch Processing**: Queue-based job processing
- **Analytics**: Usage monitoring and performance metrics
- **Additional Tools**: More specialized educational tools 