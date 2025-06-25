"""
Student Data Management Tool for SMS Agent.
This tool handles student information, course enrollment, study schedules, and tracking.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import json
import asyncio
from app.tools.base_tool import BaseTool
from app.models.schemas import ToolResult


class StudentProfile(BaseModel):
    """Student profile data model."""
    student_id: str
    name: str
    email: str
    phone: Optional[str] = None
    university: str
    country: str
    language: str = "en"
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Course(BaseModel):
    """Course data model."""
    course_id: str
    name: str
    code: str
    instructor: str
    description: Optional[str] = None
    credits: int = 3
    semester: str
    start_date: date
    end_date: date


class Exam(BaseModel):
    """Exam data model."""
    exam_id: str
    course_id: str
    name: str
    date: date
    time: str
    location: str
    duration_minutes: int = 120
    topics: List[str] = []
    study_materials: List[str] = []
    special_instructions: Optional[str] = None


class StudySession(BaseModel):
    """Study session data model."""
    session_id: str
    student_id: str
    course_id: str
    planned_date: date
    planned_time: str
    duration_minutes: int
    topic: str
    materials: List[str] = []
    status: str = "planned"  # planned, completed, missed, rescheduled
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class StudyPlan(BaseModel):
    """Study plan data model."""
    plan_id: str
    student_id: str
    exam_id: str
    created_date: date
    sessions: List[StudySession] = []
    total_hours: int = 0
    completed_hours: int = 0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_hours == 0:
            return 0.0
        return (self.completed_hours / self.total_hours) * 100


class StudentDataTool(BaseTool):
    """Tool for managing student data and study tracking."""
    
    name: str = "student_data_tool"
    description: str = "Manages student profiles, courses, exams, and study schedules for automated educational communications"
    
    def __init__(self):
        super().__init__()
        # In a real implementation, this would connect to a database
        self.students: Dict[str, StudentProfile] = {}
        self.courses: Dict[str, Course] = {}
        self.exams: Dict[str, Exam] = {}
        self.study_plans: Dict[str, StudyPlan] = {}
        self.enrollments: Dict[str, List[str]] = {}  # student_id -> [course_ids]
        
    def get_definition(self) -> Dict[str, Any]:
        """Get tool definition for OpenAI function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "add_student",
                                "get_student",
                                "update_student",
                                "add_course",
                                "enroll_student",
                                "add_exam",
                                "create_study_plan",
                                "log_study_session",
                                "get_today_sessions",
                                "get_missed_sessions",
                                "get_upcoming_exams",
                                "get_student_progress",
                                "check_study_compliance"
                            ],
                            "description": "Action to perform"
                        },
                        "student_data": {
                            "type": "object",
                            "description": "Student profile data (for add_student, update_student)"
                        },
                        "course_data": {
                            "type": "object", 
                            "description": "Course data (for add_course)"
                        },
                        "exam_data": {
                            "type": "object",
                            "description": "Exam data (for add_exam)"
                        },
                        "study_plan_data": {
                            "type": "object",
                            "description": "Study plan data (for create_study_plan)"
                        },
                        "session_data": {
                            "type": "object",
                            "description": "Study session data (for log_study_session)"
                        },
                        "student_id": {
                            "type": "string",
                            "description": "Student ID for queries"
                        },
                        "course_id": {
                            "type": "string",
                            "description": "Course ID for operations"
                        },
                        "exam_id": {
                            "type": "string", 
                            "description": "Exam ID for operations"
                        },
                        "date_filter": {
                            "type": "string",
                            "description": "Date filter (YYYY-MM-DD) for queries"
                        },
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days to look ahead for upcoming items",
                            "default": 7
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the student data management operation."""
        try:
            action = parameters.get("action")
            
            if action == "add_student":
                return await self._add_student(parameters.get("student_data", {}))
            elif action == "get_student":
                return await self._get_student(parameters.get("student_id"))
            elif action == "update_student":
                return await self._update_student(
                    parameters.get("student_id"),
                    parameters.get("student_data", {})
                )
            elif action == "add_course":
                return await self._add_course(parameters.get("course_data", {}))
            elif action == "enroll_student":
                return await self._enroll_student(
                    parameters.get("student_id"),
                    parameters.get("course_id")
                )
            elif action == "add_exam":
                return await self._add_exam(parameters.get("exam_data", {}))
            elif action == "create_study_plan":
                return await self._create_study_plan(parameters.get("study_plan_data", {}))
            elif action == "log_study_session":
                return await self._log_study_session(parameters.get("session_data", {}))
            elif action == "get_today_sessions":
                return await self._get_today_sessions(
                    parameters.get("student_id"),
                    parameters.get("date_filter")
                )
            elif action == "get_missed_sessions":
                return await self._get_missed_sessions(
                    parameters.get("student_id"),
                    parameters.get("days_ahead", 7)
                )
            elif action == "get_upcoming_exams":
                return await self._get_upcoming_exams(
                    parameters.get("student_id"),
                    parameters.get("days_ahead", 14)
                )
            elif action == "get_student_progress":
                return await self._get_student_progress(parameters.get("student_id"))
            elif action == "check_study_compliance":
                return await self._check_study_compliance(
                    parameters.get("student_id"),
                    parameters.get("date_filter")
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Error in student data tool: {str(e)}"
            )
    
    async def _add_student(self, student_data: Dict[str, Any]) -> ToolResult:
        """Add a new student profile."""
        try:
            student = StudentProfile(**student_data)
            self.students[student.student_id] = student
            self.enrollments[student.student_id] = []
            
            return ToolResult(
                success=True,
                data={
                    "message": f"Student {student.name} added successfully",
                    "student_id": student.student_id
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to add student: {str(e)}"
            )
    
    async def _get_student(self, student_id: str) -> ToolResult:
        """Get student profile by ID."""
        if not student_id:
            return ToolResult(
                success=False,
                data=None,
                error="Student ID is required"
            )
        
        student = self.students.get(student_id)
        if not student:
            return ToolResult(
                success=False,
                data=None,
                error=f"Student {student_id} not found"
            )
        
        # Get enrolled courses
        enrolled_courses = []
        for course_id in self.enrollments.get(student_id, []):
            if course_id in self.courses:
                enrolled_courses.append(self.courses[course_id].dict())
        
        return ToolResult(
            success=True,
            data={
                "profile": student.dict(),
                "enrolled_courses": enrolled_courses,
                "total_courses": len(enrolled_courses)
            }
        )
    
    async def _add_course(self, course_data: Dict[str, Any]) -> ToolResult:
        """Add a new course."""
        try:
            # Convert date strings to date objects
            if "start_date" in course_data and isinstance(course_data["start_date"], str):
                course_data["start_date"] = datetime.strptime(course_data["start_date"], "%Y-%m-%d").date()
            if "end_date" in course_data and isinstance(course_data["end_date"], str):
                course_data["end_date"] = datetime.strptime(course_data["end_date"], "%Y-%m-%d").date()
            
            course = Course(**course_data)
            self.courses[course.course_id] = course
            
            return ToolResult(
                success=True,
                data={
                    "message": f"Course {course.name} added successfully",
                    "course_id": course.course_id
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to add course: {str(e)}"
            )
    
    async def _enroll_student(self, student_id: str, course_id: str) -> ToolResult:
        """Enroll a student in a course."""
        if student_id not in self.students:
            return ToolResult(
                success=False,
                data=None,
                error=f"Student {student_id} not found"
            )
        
        if course_id not in self.courses:
            return ToolResult(
                success=False,
                data=None,
                error=f"Course {course_id} not found"
            )
        
        if course_id not in self.enrollments[student_id]:
            self.enrollments[student_id].append(course_id)
        
        course = self.courses[course_id]
        return ToolResult(
            success=True,
            data={
                "message": f"Student enrolled in {course.name}",
                "student_id": student_id,
                "course_id": course_id
            }
        )
    
    async def _add_exam(self, exam_data: Dict[str, Any]) -> ToolResult:
        """Add an exam."""
        try:
            # Convert date string to date object
            if "date" in exam_data and isinstance(exam_data["date"], str):
                exam_data["date"] = datetime.strptime(exam_data["date"], "%Y-%m-%d").date()
            
            exam = Exam(**exam_data)
            self.exams[exam.exam_id] = exam
            
            return ToolResult(
                success=True,
                data={
                    "message": f"Exam {exam.name} added successfully",
                    "exam_id": exam.exam_id
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to add exam: {str(e)}"
            )
    
    async def _get_today_sessions(self, student_id: str, date_filter: Optional[str] = None) -> ToolResult:
        """Get today's study sessions for a student."""
        if not student_id:
            return ToolResult(
                success=False,
                data=None,
                error="Student ID is required"
            )
        
        target_date = date.today()
        if date_filter:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        
        today_sessions = []
        for plan in self.study_plans.values():
            if plan.student_id == student_id:
                for session in plan.sessions:
                    if session.planned_date == target_date:
                        course = self.courses.get(session.course_id)
                        today_sessions.append({
                            "session": session.dict(),
                            "course_name": course.name if course else "Unknown Course"
                        })
        
        return ToolResult(
            success=True,
            data={
                "date": target_date.isoformat(),
                "sessions": today_sessions,
                "total_sessions": len(today_sessions)
            }
        )
    
    async def _get_missed_sessions(self, student_id: str, days_back: int = 7) -> ToolResult:
        """Get missed study sessions for a student."""
        if not student_id:
            return ToolResult(
                success=False,
                data=None,
                error="Student ID is required"
            )
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        missed_sessions = []
        for plan in self.study_plans.values():
            if plan.student_id == student_id:
                for session in plan.sessions:
                    if (start_date <= session.planned_date <= end_date and 
                        session.status == "missed"):
                        course = self.courses.get(session.course_id)
                        missed_sessions.append({
                            "session": session.dict(),
                            "course_name": course.name if course else "Unknown Course"
                        })
        
        return ToolResult(
            success=True,
            data={
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "missed_sessions": missed_sessions,
                "total_missed": len(missed_sessions)
            }
        )
    
    async def _get_upcoming_exams(self, student_id: str, days_ahead: int = 14) -> ToolResult:
        """Get upcoming exams for a student."""
        if not student_id:
            return ToolResult(
                success=False,
                data=None,
                error="Student ID is required"
            )
        
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        upcoming_exams = []
        student_courses = self.enrollments.get(student_id, [])
        
        for exam in self.exams.values():
            if (exam.course_id in student_courses and 
                start_date <= exam.date <= end_date):
                course = self.courses.get(exam.course_id)
                days_until = (exam.date - start_date).days
                
                upcoming_exams.append({
                    "exam": exam.dict(),
                    "course_name": course.name if course else "Unknown Course",
                    "days_until": days_until
                })
        
        # Sort by date
        upcoming_exams.sort(key=lambda x: x["exam"]["date"])
        
        return ToolResult(
            success=True,
            data={
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "upcoming_exams": upcoming_exams,
                "total_exams": len(upcoming_exams)
            }
        )
    
    async def _check_study_compliance(self, student_id: str, date_filter: Optional[str] = None) -> ToolResult:
        """Check if student followed their study plan for a specific date."""
        if not student_id:
            return ToolResult(
                success=False,
                data=None,
                error="Student ID is required"
            )
        
        check_date = date.today() - timedelta(days=1)  # Yesterday by default
        if date_filter:
            check_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        
        planned_sessions = []
        completed_sessions = []
        missed_sessions = []
        
        for plan in self.study_plans.values():
            if plan.student_id == student_id:
                for session in plan.sessions:
                    if session.planned_date == check_date:
                        planned_sessions.append(session)
                        if session.status == "completed":
                            completed_sessions.append(session)
                        elif session.status == "missed":
                            missed_sessions.append(session)
        
        total_planned = len(planned_sessions)
        total_completed = len(completed_sessions)
        total_missed = len(missed_sessions)
        
        compliance_rate = (total_completed / total_planned * 100) if total_planned > 0 else 100
        
        return ToolResult(
            success=True,
            data={
                "date": check_date.isoformat(),
                "total_planned": total_planned,
                "total_completed": total_completed,
                "total_missed": total_missed,
                "compliance_rate": round(compliance_rate, 1),
                "is_compliant": compliance_rate >= 80,  # 80% threshold
                "missed_sessions": [s.dict() for s in missed_sessions]
            }
        ) 