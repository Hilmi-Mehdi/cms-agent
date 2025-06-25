"""Tools module for the AI agent system."""

from .base_tool import BaseTool, ToolDefinition, ToolParameter, tool_registry
from .content_analyzer import ContentAnalyzerTool
from .file_processor import FileProcessorTool
from .content_generator import ContentGeneratorTool
from .slide_analyzer import SlideAnalyzerTool
from .document_fetcher import DocumentFetcherTool
from .document_analyzer import DocumentAnalyzerTool
from .quiz_generator import QuizGeneratorTool
from .direct_quiz_generator import DirectQuizGeneratorTool
from .slide_digitalization import SlideDigitalizationTool
from .web_document_finder import WebDocumentFinderTool
from .general_web_search_tool import GeneralWebSearchTool
from .course_pdf_finder import CoursePdfFinderTool
from .messaging_tool import MessagingTool
from .student_data_tool import StudentDataTool
from .automated_email_scheduler import AutomatedEmailScheduler

# Auto-register tools when module is imported
def _register_tools():
    """Register all tools automatically."""
    try:
        tool_registry.register_tool(ContentAnalyzerTool())
        tool_registry.register_tool(FileProcessorTool())
        tool_registry.register_tool(ContentGeneratorTool())
        tool_registry.register_tool(SlideAnalyzerTool())
        tool_registry.register_tool(DocumentFetcherTool())
        tool_registry.register_tool(DocumentAnalyzerTool())
        tool_registry.register_tool(QuizGeneratorTool())
        tool_registry.register_tool(DirectQuizGeneratorTool())
        tool_registry.register_tool(SlideDigitalizationTool())
        tool_registry.register_tool(WebDocumentFinderTool())
        tool_registry.register_tool(GeneralWebSearchTool())
        tool_registry.register_tool(CoursePdfFinderTool())
        tool_registry.register_tool(MessagingTool())
        tool_registry.register_tool(StudentDataTool())
        tool_registry.register_tool(AutomatedEmailScheduler())
    except Exception as e:
        print(f"Warning: Failed to register some tools: {e}")

# Register tools automatically
_register_tools()

__all__ = [
    "BaseTool",
    "ToolDefinition", 
    "ToolParameter",
    "tool_registry",
    "ContentAnalyzerTool",
    "FileProcessorTool", 
    "ContentGeneratorTool",
    "SlideAnalyzerTool",
    "DocumentFetcherTool",
    "DocumentAnalyzerTool",
    "QuizGeneratorTool",
    "DirectQuizGeneratorTool",
    "SlideDigitalizationTool",
    "WebDocumentFinderTool",
    "GeneralWebSearchTool",
    "CoursePdfFinderTool",
    "MessagingTool",
    "StudentDataTool",
    "AutomatedEmailScheduler"
]
