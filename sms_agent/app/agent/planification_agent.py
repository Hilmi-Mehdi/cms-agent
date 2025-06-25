import uuid
from ..models.planification_models import StudentProfile, StudyPreferences, StudyPlan, Plan
from ..tools.student_profile_tool import StudentProfileTool
from ..tools.agenda_generator import AgendaGeneratorTool
from ..tools.general_web_search_tool import GeneralWebSearchTool
from typing import List, Dict, Any

class PlanificationAgent:
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.student_profile: StudentProfile | None = None
        self.exam_name: str | None = None
        self.exam_date: str | None = None
        self.study_preferences: StudyPreferences | None = None
        self.study_plan: StudyPlan | None = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.state = "initial"

    def _get_tools(self):
        return [
            StudentProfileTool(),
            AgendaGeneratorTool(),
            GeneralWebSearchTool(),
        ]

    def process_message(self, message: str) -> str:
        self.conversation_history.append({"role": "user", "content": message})
        
        response = ""
        if self.state == "initial":
            response = self._handle_initial_state()
        elif self.state == "gathering_exam_name":
            self.exam_name = message
            self.state = "gathering_exam_date"
            response = "Thanks! When is the exam? Please provide the date in YYYY-MM-DD format."
        elif self.state == "gathering_exam_date":
            self.exam_date = message # In a real scenario, we would validate this
            self.state = "gathering_preferences"
            response = "Great. Now, let's set up your study preferences. What are your preferred study times? (e.g., weekday evenings, weekend mornings)"
        elif self.state == "gathering_preferences":
            # This is a simplified gathering process
            self.study_preferences = StudyPreferences(
                preferred_study_times=[message],
                constraints=["None"],
                study_intensity="medium"
            )
            self.state = "generating_plan"
            response = self._generate_plan()
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _handle_initial_state(self) -> str:
        profile_tool = StudentProfileTool()
        profile_data = profile_tool.run()
        self.student_profile = StudentProfile(**profile_data)
        self.state = "gathering_exam_name"
        
        return f"Hello! I'm your personal study planner. I see you're studying {self.student_profile.program} at {self.student_profile.university}. Which exam are you preparing for?"

    def _generate_plan(self) -> str:
        if not all([self.student_profile, self.exam_name, self.exam_date, self.study_preferences]):
            self.state = "initial" # Reset state
            return "I seem to be missing some information. Let's start over."

        # At this point, type checkers know these are not None.
        agenda_tool = AgendaGeneratorTool(
            exam_name=self.exam_name,
            exam_date=self.exam_date,
            student_profile=self.student_profile.model_dump(),
            study_preferences=self.study_preferences.model_dump()
        )
        
        plan_data = agenda_tool.run()

        if "error" in plan_data:
            return f"There was an error generating your plan: {plan_data['error']}"

        self.study_plan = StudyPlan(**plan_data)
        self.state = "plan_generated"
        
        return f"I have generated a study plan for your {self.exam_name} exam. It includes {len(self.study_plan.sessions)} sessions. Would you like to view it?"

    def get_plan(self) -> Plan | None:
        if not all([self.study_plan, self.exam_name, self.exam_date, self.student_profile, self.study_preferences]):
            return None
        
        assert self.exam_date is not None

        from datetime import date
        exam_date_obj = date.fromisoformat(self.exam_date)

        return Plan(
            id=str(uuid.uuid4()),
            exam_name=self.exam_name,
            exam_date=exam_date_obj,
            study_plan=self.study_plan,
            student_profile=self.student_profile,
            study_preferences=self.study_preferences
        )