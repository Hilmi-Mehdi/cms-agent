# __init__.py for tools module

from .base_tool import tool_registry, BaseTool
from .file_processor import FileProcessorTool
from .content_analyzer import ContentAnalyzerTool
from .content_generator import ContentGeneratorTool
from .course_pdf_finder import CoursePDFFinderTool
from .direct_quiz_generator import DirectQuizGeneratorTool
from .document_analyzer import DocumentAnalyzerTool
from .document_fetcher import DocumentFetcherTool
from .email_templates import EmailTemplatesTool
from .general_web_search_tool import GeneralWebSearchTool
from .messaging_tool import MessagingTool
from .quiz_generator import QuizGeneratorTool
from .slide_analyzer import SlideAnalyzerTool
from .slide_digitalization import SlideDigitalizationTool
from .student_data_tool import StudentDataTool
from .web_document_finder import WebDocumentFinderTool
from .automated_email_scheduler import AutomatedEmailSchedulerTool
from .agenda_generator import AgendaGeneratorTool
from .student_profile_tool import StudentProfileTool

# Populate the tool registry
tool_registry.register(FileProcessorTool())
tool_registry.register(ContentAnalyzerTool())
tool_registry.register(ContentGeneratorTool())
tool_registry.register(CoursePDFFinderTool())
tool_registry.register(DirectQuizGeneratorTool())
tool_registry.register(DocumentAnalyzerTool())
tool_registry.register(DocumentFetcherTool())
tool_registry.register(EmailTemplatesTool())
tool_registry.register(GeneralWebSearchTool())
tool_registry.register(MessagingTool())
tool_registry.register(QuizGeneratorTool())
tool_registry.register(SlideAnalyzerTool())
tool_registry.register(SlideDigitalizationTool())
tool_registry.register(StudentDataTool())
tool_registry.register(WebDocumentFinderTool())
tool_registry.register(AutomatedEmailSchedulerTool())
tool_registry.register(AgendaGeneratorTool())
tool_registry.register(StudentProfileTool())