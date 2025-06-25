from ..models.planification_models import StudentProfile, Course
from .base_tool import BaseTool
from pydantic import Field

class StudentProfileTool(BaseTool):
    name: str = "get_student_profile"
    description: str = "Fetches the student's profile, including university, program, academic level, and enrolled courses."
    
    def run(self, **kwargs) -> dict:
        """
        Returns a dummy student profile.
        In a real application, this would fetch data from an external API.
        """
        dummy_courses = [
            Course(name="Introduction to AI", study_hours_required=30),
            Course(name="Data Structures and Algorithms", study_hours_required=40),
            Course(name="Calculus II", study_hours_required=35),
            Course(name="Linear Algebra", study_hours_required=25),
        ]
        
        dummy_profile = StudentProfile(
            university="University of Example",
            program="Computer Science",
            academic_level="Bachelor's",
            enrolled_courses=dummy_courses,
        )
        
        return dummy_profile.model_dump()