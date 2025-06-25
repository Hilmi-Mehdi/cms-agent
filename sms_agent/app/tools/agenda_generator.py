from ..models.planification_models import StudyPlan, StudySession, BreakSession, RevisionSession, StudentProfile, StudyPreferences
from .base_tool import BaseTool
from pydantic import Field
from datetime import date, timedelta, datetime, time

class AgendaGeneratorTool(BaseTool):
    name: str = "generate_study_agenda"
    description: str = "Generates a personalized study agenda based on student's profile, exam date, and preferences."
    
    exam_name: str = Field(..., description="The name of the exam.")
    exam_date: str = Field(..., description="The date of the exam in 'YYYY-MM-DD' format.")
    student_profile: dict = Field(..., description="The student's profile.")
    study_preferences: dict = Field(..., description="The student's study preferences.")

    def run(self) -> dict:
        """
        Generates a study agenda.
        This is a simplified implementation. A real implementation would have more sophisticated logic.
        """
        profile = StudentProfile(**self.student_profile)
        preferences = StudyPreferences(**self.study_preferences)
        exam_date_obj = date.fromisoformat(self.exam_date)
        
        total_study_hours = sum(course.study_hours_required for course in profile.enrolled_courses)
        
        study_days = (exam_date_obj - date.today()).days
        if study_days <= 0:
            return {"error": "The exam date is in the past or today. Please provide a future date."}

        sessions = []
        current_date = date.today()
        
        # This is a very basic scheduler.
        # It just distributes hours evenly across the available days.
        hours_per_day = total_study_hours / study_days
        
        # A more advanced version would consider preferences, intensity, etc.
        
        for course in profile.enrolled_courses:
            hours_to_study = course.study_hours_required
            while hours_to_study > 0:
                study_start_time = time(9, 0) # Dummy start time
                study_end_time = time(12, 0) # Dummy end time
                
                sessions.append(StudySession(
                    date=current_date,
                    start_time=study_start_time,
                    end_time=study_end_time,
                    course=course.name
                ))
                
                hours_to_study -= 3 # Assuming 3 hour sessions
                current_date += timedelta(days=1)
                if current_date >= exam_date_obj:
                    break
            if current_date >= exam_date_obj:
                    break
        
        # Add a revision session
        if exam_date_obj > date.today():
             sessions.append(RevisionSession(
                date=exam_date_obj - timedelta(days=1),
                start_time=time(10, 0),
                end_time=time(13, 0),
                course=self.exam_name,
                activity="Final Revision"
            ))

        study_plan = StudyPlan(
            exam_name=self.exam_name,
            exam_date=exam_date_obj,
            sessions=sessions
        )
        
        return study_plan.model_dump()