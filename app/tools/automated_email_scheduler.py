"""
Automated Email Scheduler for Educational Context.
This tool monitors student data and automatically sends contextual emails based on 
study patterns, schedules, exam dates, and compliance tracking.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from app.tools.base_tool import BaseTool
from app.tools.messaging_tool import MessagingTool
from app.tools.email_templates import email_templates
from app.tools.student_data_tool import StudentDataTool
from app.models.schemas import ToolResult


class AutomatedEmailScheduler(BaseTool):
    """Tool for automated educational email scheduling based on student data."""
    
    name: str = "automated_email_scheduler"
    description: str = "Automatically sends educational emails based on student schedules, study compliance, and upcoming events"
    
    def __init__(self):
        super().__init__()
        self.messaging_tool = MessagingTool()
        self.student_data_tool = StudentDataTool()
        self.email_log: List[Dict[str, Any]] = []  # Track sent emails
    
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
                                "check_daily_reminders",
                                "check_study_compliance",
                                "check_upcoming_exams",
                                "send_missed_study_followup",
                                "process_all_students",
                                "get_email_log",
                                "send_custom_notification"
                            ],
                            "description": "Action to perform"
                        },
                        "student_id": {
                            "type": "string",
                            "description": "Specific student ID to process (optional for individual operations)"
                        },
                        "date_filter": {
                            "type": "string",
                            "description": "Date filter (YYYY-MM-DD) for operations"
                        },
                        "notification_data": {
                            "type": "object",
                            "description": "Custom notification data"
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, simulate actions without sending emails",
                            "default": False
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the automated email scheduling operation."""
        try:
            action = parameters.get("action")
            dry_run = parameters.get("dry_run", False)
            
            if action == "check_daily_reminders":
                return await self._check_daily_reminders(
                    parameters.get("student_id"),
                    parameters.get("date_filter"),
                    dry_run
                )
            elif action == "check_study_compliance":
                return await self._check_study_compliance(
                    parameters.get("student_id"),
                    parameters.get("date_filter"),
                    dry_run
                )
            elif action == "check_upcoming_exams":
                return await self._check_upcoming_exams(
                    parameters.get("student_id"),
                    dry_run
                )
            elif action == "send_missed_study_followup":
                return await self._send_missed_study_followup(
                    parameters.get("student_id"),
                    dry_run
                )
            elif action == "process_all_students":
                return await self._process_all_students(dry_run)
            elif action == "get_email_log":
                return await self._get_email_log()
            elif action == "send_custom_notification":
                return await self._send_custom_notification(
                    parameters.get("notification_data", {}),
                    dry_run
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
                error=f"Error in automated email scheduler: {str(e)}"
            )
    
    async def _check_daily_reminders(self, student_id: Optional[str] = None, 
                                   date_filter: Optional[str] = None, 
                                   dry_run: bool = False) -> ToolResult:
        """Check and send daily study reminders for students."""
        target_date = date.today()
        if date_filter:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        
        students_to_check = []
        if student_id:
            students_to_check = [student_id]
        else:
            # Get all students
            students_to_check = list(self.student_data_tool.students.keys())
        
        sent_emails = []
        errors = []
        
        for sid in students_to_check:
            try:
                # Get today's sessions for the student
                sessions_result = await self.student_data_tool.execute({
                    "action": "get_today_sessions",
                    "student_id": sid,
                    "date_filter": target_date.isoformat()
                })
                
                if sessions_result.success and sessions_result.data["total_sessions"] > 0:
                    # Student has sessions today - send reminder
                    student_result = await self.student_data_tool.execute({
                        "action": "get_student", 
                        "student_id": sid
                    })
                    
                    if student_result.success:
                        email_sent = await self._send_daily_study_reminder(
                            student_result.data,
                            sessions_result.data,
                            target_date,
                            dry_run
                        )
                        if email_sent:
                            sent_emails.append({
                                "student_id": sid,
                                "email_type": "daily_reminder",
                                "sessions_count": sessions_result.data["total_sessions"]
                            })
                        
            except Exception as e:
                errors.append(f"Error processing student {sid}: {str(e)}")
        
        return ToolResult(
            success=True,
            data={
                "action": "daily_reminders",
                "date": target_date.isoformat(),
                "emails_sent": len(sent_emails),
                "students_processed": len(students_to_check),
                "sent_details": sent_emails,
                "errors": errors,
                "dry_run": dry_run
            }
        )
    
    async def _check_study_compliance(self, student_id: Optional[str] = None,
                                    date_filter: Optional[str] = None,
                                    dry_run: bool = False) -> ToolResult:
        """Check study compliance and send follow-up emails for non-compliant students."""
        check_date = date.today() - timedelta(days=1)  # Check yesterday by default
        if date_filter:
            check_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        
        students_to_check = []
        if student_id:
            students_to_check = [student_id]
        else:
            students_to_check = list(self.student_data_tool.students.keys())
        
        sent_emails = []
        errors = []
        
        for sid in students_to_check:
            try:
                # Check compliance for the date
                compliance_result = await self.student_data_tool.execute({
                    "action": "check_study_compliance",
                    "student_id": sid,
                    "date_filter": check_date.isoformat()
                })
                
                if (compliance_result.success and 
                    not compliance_result.data["is_compliant"] and
                    compliance_result.data["total_planned"] > 0):
                    
                    # Student is not compliant - send follow-up email
                    student_result = await self.student_data_tool.execute({
                        "action": "get_student",
                        "student_id": sid
                    })
                    
                    if student_result.success:
                        email_sent = await self._send_compliance_followup(
                            student_result.data,
                            compliance_result.data,
                            check_date,
                            dry_run
                        )
                        if email_sent:
                            sent_emails.append({
                                "student_id": sid,
                                "email_type": "compliance_followup",
                                "compliance_rate": compliance_result.data["compliance_rate"],
                                "missed_sessions": compliance_result.data["total_missed"]
                            })
                        
            except Exception as e:
                errors.append(f"Error processing student {sid}: {str(e)}")
        
        return ToolResult(
            success=True,
            data={
                "action": "compliance_check",
                "date": check_date.isoformat(),
                "emails_sent": len(sent_emails),
                "students_processed": len(students_to_check),
                "sent_details": sent_emails,
                "errors": errors,
                "dry_run": dry_run
            }
        )
    
    async def _check_upcoming_exams(self, student_id: Optional[str] = None,
                                  dry_run: bool = False) -> ToolResult:
        """Check for upcoming exams and send reminder emails."""
        students_to_check = []
        if student_id:
            students_to_check = [student_id]
        else:
            students_to_check = list(self.student_data_tool.students.keys())
        
        sent_emails = []
        errors = []
        
        # Check for exams in the next 14 days
        for sid in students_to_check:
            try:
                exams_result = await self.student_data_tool.execute({
                    "action": "get_upcoming_exams",
                    "student_id": sid,
                    "days_ahead": 14
                })
                
                if exams_result.success and exams_result.data["total_exams"] > 0:
                    student_result = await self.student_data_tool.execute({
                        "action": "get_student",
                        "student_id": sid
                    })
                    
                    if student_result.success:
                        # Send exam reminders for exams in specific timeframes
                        for exam_info in exams_result.data["upcoming_exams"]:
                            days_until = exam_info["days_until"]
                            
                            # Send reminders at 7 days, 3 days, and 1 day before exam
                            if days_until in [7, 3, 1]:
                                email_sent = await self._send_exam_reminder(
                                    student_result.data,
                                    exam_info,
                                    dry_run
                                )
                                if email_sent:
                                    sent_emails.append({
                                        "student_id": sid,
                                        "email_type": "exam_reminder",
                                        "exam_name": exam_info["exam"]["name"],
                                        "days_until": days_until
                                    })
                        
            except Exception as e:
                errors.append(f"Error processing student {sid}: {str(e)}")
        
        return ToolResult(
            success=True,
            data={
                "action": "exam_reminders",
                "emails_sent": len(sent_emails),
                "students_processed": len(students_to_check),
                "sent_details": sent_emails,
                "errors": errors,
                "dry_run": dry_run
            }
        )
    
    async def _send_daily_study_reminder(self, student_data: Dict[str, Any],
                                       sessions_data: Dict[str, Any],
                                       target_date: date,
                                       dry_run: bool = False) -> bool:
        """Send daily study reminder email."""
        try:
            profile = student_data["profile"]
            sessions = sessions_data["sessions"]
            
            # Prepare session details
            session_details = []
            for session_info in sessions:
                session = session_info["session"]
                course_name = session_info["course_name"]
                session_details.append(
                    f"• {session['planned_time']}: {session['topic']} ({course_name}) - {session['duration_minutes']} min"
                )
            
            # Get first course for the email (or create a combined message)
            first_session = sessions[0]["session"]
            first_course = sessions[0]["course_name"]
            
            template_vars = {
                'student_name': profile['name'],
                'course_name': first_course,
                'class_topic': first_session['topic'],
                'time_until': 'today',
                'class_date': target_date.strftime('%A, %B %d'),
                'class_time': first_session['planned_time'],
                'location': 'Your Study Space',
                'instructor_name': 'Your Study Plan',
                'materials': '\n'.join(first_session.get('materials', ['• Study materials', '• Notes'])),
                'preparation': f"Today's Study Sessions:\n" + '\n'.join(session_details),
                'sender_name': 'SMS Learning Assistant',
                'organization': profile['university']
            }
            
            if not dry_run:
                email_content = email_templates.render_template('course_reminder', **template_vars)
                
                if email_content:
                    result = await self.messaging_tool.execute({
                        "message_type": "email",
                        "recipient": profile['email'],
                        **email_content,
                        "sender_name": template_vars['sender_name']
                    })
                    
                    # Log the email
                    self.email_log.append({
                        "timestamp": datetime.now(),
                        "student_id": profile['student_id'],
                        "email_type": "daily_reminder",
                        "success": result.success,
                        "date": target_date.isoformat()
                    })
                    
                    return result.success
            else:
                # Dry run - just log what would be sent
                print(f"[DRY RUN] Would send daily reminder to {profile['name']} ({profile['email']})")
                print(f"          Sessions: {len(sessions)} planned for {target_date}")
                return True
                
        except Exception as e:
            print(f"Error sending daily reminder: {e}")
            return False
    
    async def _send_compliance_followup(self, student_data: Dict[str, Any],
                                      compliance_data: Dict[str, Any],
                                      check_date: date,
                                      dry_run: bool = False) -> bool:
        """Send study compliance follow-up email."""
        try:
            profile = student_data["profile"]
            
            # Prepare missed session details
            missed_sessions_text = []
            for session in compliance_data["missed_sessions"]:
                missed_sessions_text.append(
                    f"{session['planned_time']}: {session['topic']} ({session['duration_minutes']} min)"
                )
            
            # Create a catch-up plan
            total_missed_hours = sum(s['duration_minutes'] for s in compliance_data["missed_sessions"]) // 60
            catchup_plan = f"""Suggested Catch-up Plan:
• This weekend: Dedicate {max(1, total_missed_hours)} extra hours to missed topics
• Break down missed sessions into smaller 25-30 minute chunks
• Focus on the most important concepts first
• Schedule make-up sessions for next week"""
            
            # Get enrolled courses for context
            enrolled_courses = student_data.get("enrolled_courses", [])
            priority_topics = []
            for course in enrolled_courses[:2]:  # Top 2 courses
                priority_topics.append(f"• {course.get('name', 'Course')}: Review recent materials")
            
            template_vars = {
                'student_name': profile['name'],
                'course_name': enrolled_courses[0]['name'] if enrolled_courses else 'Your Studies',
                'missed_sessions': f"Date: {check_date.strftime('%A, %B %d')}\n" + '\n'.join(missed_sessions_text),
                'catchup_plan': catchup_plan,
                'priority_topics': '\n'.join(priority_topics) if priority_topics else '• Review most recent lessons\n• Focus on upcoming assignments',
                'help_resources': f'• Contact your academic advisor\n• Join study groups at {profile["university"]}\n• Use online resources and tutorials\n• Schedule one-on-one tutoring if needed',
                'sender_name': 'SMS Learning Assistant',
                'organization': profile['university']
            }
            
            if not dry_run:
                email_content = email_templates.render_template('missed_study', **template_vars)
                
                if email_content:
                    result = await self.messaging_tool.execute({
                        "message_type": "email",
                        "recipient": profile['email'],
                        **email_content,
                        "sender_name": template_vars['sender_name']
                    })
                    
                    # Log the email
                    self.email_log.append({
                        "timestamp": datetime.now(),
                        "student_id": profile['student_id'],
                        "email_type": "compliance_followup",
                        "success": result.success,
                        "compliance_rate": compliance_data["compliance_rate"]
                    })
                    
                    return result.success
            else:
                # Dry run
                print(f"[DRY RUN] Would send compliance follow-up to {profile['name']} ({profile['email']})")
                print(f"          Compliance rate: {compliance_data['compliance_rate']}%")
                print(f"          Missed sessions: {compliance_data['total_missed']}")
                return True
                
        except Exception as e:
            print(f"Error sending compliance follow-up: {e}")
            return False
    
    async def _send_exam_reminder(self, student_data: Dict[str, Any],
                                exam_info: Dict[str, Any],
                                dry_run: bool = False) -> bool:
        """Send exam reminder email."""
        try:
            profile = student_data["profile"]
            exam = exam_info["exam"]
            course_name = exam_info["course_name"]
            days_until = exam_info["days_until"]
            
            template_vars = {
                'student_name': profile['name'],
                'exam_name': exam['name'],
                'days_until': str(days_until),
                'exam_date': exam['date'],
                'exam_time': exam['time'],
                'exam_location': exam['location'],
                'exam_duration': f"{exam['duration_minutes'] // 60} hours {exam['duration_minutes'] % 60} minutes",
                'items_to_bring': '• Student ID\n• Pens/pencils\n• Calculator (if allowed)\n• Any permitted materials',
                'exam_topics': '\n'.join([f"• {topic}" for topic in exam.get('topics', ['Review all course materials'])]),
                'study_materials': '\n'.join([f"• {material}" for material in exam.get('study_materials', ['Course textbook', 'Lecture notes', 'Practice exercises'])]),
                'important_notes': exam.get('special_instructions', '• Arrive 15 minutes early\n• Bring water if needed\n• No electronic devices unless specified'),
                'sender_name': 'SMS Learning Assistant',
                'organization': profile['university']
            }
            
            if not dry_run:
                email_content = email_templates.render_template('exam_reminder', **template_vars)
                
                if email_content:
                    # Set high priority for exam reminders
                    result = await self.messaging_tool.execute({
                        "message_type": "email",
                        "recipient": profile['email'],
                        "priority": "high",
                        **email_content,
                        "sender_name": template_vars['sender_name']
                    })
                    
                    # Log the email
                    self.email_log.append({
                        "timestamp": datetime.now(),
                        "student_id": profile['student_id'],
                        "email_type": "exam_reminder",
                        "success": result.success,
                        "exam_id": exam['exam_id'],
                        "days_until": days_until
                    })
                    
                    return result.success
            else:
                # Dry run
                print(f"[DRY RUN] Would send exam reminder to {profile['name']} ({profile['email']})")
                print(f"          Exam: {exam['name']} in {days_until} days")
                return True
                
        except Exception as e:
            print(f"Error sending exam reminder: {e}")
            return False
    
    async def _process_all_students(self, dry_run: bool = False) -> ToolResult:
        """Process all students for daily reminders, compliance, and exam notifications."""
        results = {
            "daily_reminders": {},
            "compliance_checks": {},
            "exam_reminders": {},
            "total_emails": 0
        }
        
        # Daily reminders
        daily_result = await self._check_daily_reminders(dry_run=dry_run)
        if daily_result.success:
            results["daily_reminders"] = daily_result.data
            results["total_emails"] += daily_result.data["emails_sent"]
        
        # Compliance checks
        compliance_result = await self._check_study_compliance(dry_run=dry_run)
        if compliance_result.success:
            results["compliance_checks"] = compliance_result.data
            results["total_emails"] += compliance_result.data["emails_sent"]
        
        # Exam reminders
        exam_result = await self._check_upcoming_exams(dry_run=dry_run)
        if exam_result.success:
            results["exam_reminders"] = exam_result.data
            results["total_emails"] += exam_result.data["emails_sent"]
        
        return ToolResult(
            success=True,
            data={
                "action": "process_all_students",
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "dry_run": dry_run
            }
        )
    
    async def _get_email_log(self) -> ToolResult:
        """Get the email sending log."""
        return ToolResult(
            success=True,
            data={
                "email_log": self.email_log,
                "total_emails": len(self.email_log)
            }
        ) 