from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time

class Course(BaseModel):
    name: str = Field(..., description="Name of the course.")
    study_hours_required: int = Field(..., description="Estimated study hours required for the course.")

class StudentProfile(BaseModel):
    university: str = Field(..., description="Student's university.")
    program: str = Field(..., description="Student's academic program.")
    academic_level: str = Field(..., description="Student's academic level (e.g., Bachelor's, Master's).")
    enrolled_courses: List[Course] = Field(..., description="List of courses the student is enrolled in.")

class StudyPreferences(BaseModel):
    preferred_study_times: List[str] = Field(..., description="Preferred study days and times (e.g., 'Monday mornings', 'Wednesday afternoons').")
    constraints: List[str] = Field(..., description="Any constraints or unavailable times.")
    study_intensity: str = Field(..., description="Desired study intensity (light, medium, intensive).")

class StudySession(BaseModel):
    date: date
    start_time: time
    end_time: time
    course: str
    activity: str = "Study Session"

class BreakSession(BaseModel):
    date: date
    start_time: time
    end_time: time
    activity: str = "Break"

class RevisionSession(BaseModel):
    date: date
    start_time: time
    end_time: time
    course: str
    activity: str = "Revision Session"

class StudyPlan(BaseModel):
    exam_name: str
    exam_date: date
    sessions: List[StudySession | BreakSession | RevisionSession] = Field(..., description="List of all sessions in the study plan.")

class Plan(BaseModel):
    id: str
    exam_name: str
    exam_date: date
    study_plan: StudyPlan
    student_profile: StudentProfile
    study_preferences: StudyPreferences