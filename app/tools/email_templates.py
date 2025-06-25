"""
Email templates for educational contexts.
This module provides pre-built email templates for courses, exams, agendas, and study reminders.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re


class EmailTemplate:
    """Base class for email templates."""
    
    def __init__(self, subject_template: str, text_template: str, html_template: Optional[str] = None):
        self.subject_template = subject_template
        self.text_template = text_template
        self.html_template = html_template
    
    def render(self, **kwargs) -> Dict[str, str]:
        """Render the template with provided variables."""
        # Replace placeholders in templates
        subject = self._replace_vars(self.subject_template, **kwargs)
        text_content = self._replace_vars(self.text_template, **kwargs)
        
        result = {
            "subject": subject,
            "message": text_content,
            "message_format": "text"
        }
        
        if self.html_template:
            html_content = self._replace_vars(self.html_template, **kwargs)
            result.update({
                "message": html_content,
                "message_format": "html"
            })
        
        return result
    
    def _replace_vars(self, template: str, **kwargs) -> str:
        """Replace {{variable}} placeholders with actual values."""
        def replace_func(match):
            var_name = match.group(1).strip()
            return str(kwargs.get(var_name, f"{{{{ {var_name} }}}}"))
        
        return re.sub(r'\{\{\s*(\w+)\s*\}\}', replace_func, template)


class EducationalEmailTemplates:
    """Collection of educational email templates."""
    
    @staticmethod
    def course_reminder():
        """Template for course/class reminders."""
        subject = "Reminder: {{course_name}} - {{class_topic}} in {{time_until}}"
        
        text = """Dear {{student_name}},

This is a friendly reminder about your upcoming class:

📚 Course: {{course_name}}
📖 Topic: {{class_topic}}
🕐 Date & Time: {{class_date}} at {{class_time}}
📍 Location: {{location}}
👨‍🏫 Instructor: {{instructor_name}}

📋 Materials to bring:
{{materials}}

📝 Preparation required:
{{preparation}}

We look forward to seeing you in class!

Best regards,
{{sender_name}}
{{organization}}"""
        
        html = """<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0;">📚 Class Reminder</h2>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
        <p>Dear <strong>{{student_name}}</strong>,</p>
        
        <p>This is a friendly reminder about your upcoming class:</p>
        
        <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
            <p><strong>📚 Course:</strong> {{course_name}}</p>
            <p><strong>📖 Topic:</strong> {{class_topic}}</p>
            <p><strong>🕐 Date & Time:</strong> {{class_date}} at {{class_time}}</p>
            <p><strong>📍 Location:</strong> {{location}}</p>
            <p><strong>👨‍🏫 Instructor:</strong> {{instructor_name}}</p>
        </div>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0066cc; margin-top: 0;">📋 Materials to bring:</h4>
            <p>{{materials}}</p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #856404; margin-top: 0;">📝 Preparation required:</h4>
            <p>{{preparation}}</p>
        </div>
        
        <p style="margin-top: 20px;">We look forward to seeing you in class!</p>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
            <p><strong>{{sender_name}}</strong><br>{{organization}}</p>
        </div>
    </div>
</body>
</html>"""
        
        return EmailTemplate(subject, text, html)
    
    @staticmethod
    def exam_reminder():
        """Template for exam reminders."""
        subject = "Important: {{exam_name}} - {{days_until}} days remaining"
        
        text = """Dear {{student_name}},

🚨 EXAM REMINDER 🚨

Your {{exam_name}} is approaching:

📝 Exam: {{exam_name}}
📅 Date: {{exam_date}}
🕐 Time: {{exam_time}}
📍 Location: {{exam_location}}
⏱️ Duration: {{exam_duration}}

📋 What to bring:
{{items_to_bring}}

📚 Topics covered:
{{exam_topics}}

📖 Suggested study materials:
{{study_materials}}

⚠️ Important notes:
{{important_notes}}

🎯 Study Tips:
- Review all lecture notes and assignments
- Practice with sample questions
- Get plenty of rest the night before
- Arrive 15 minutes early

Good luck with your preparation!

Best regards,
{{sender_name}}
{{organization}}"""
        
        html = """<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0;">🚨 EXAM REMINDER</h2>
        <p style="margin: 5px 0 0 0; font-size: 18px;">{{days_until}} days remaining!</p>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
        <p>Dear <strong>{{student_name}}</strong>,</p>
        
        <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #ff6b6b;">
            <p><strong>📝 Exam:</strong> {{exam_name}}</p>
            <p><strong>📅 Date:</strong> {{exam_date}}</p>
            <p><strong>🕐 Time:</strong> {{exam_time}}</p>
            <p><strong>📍 Location:</strong> {{exam_location}}</p>
            <p><strong>⏱️ Duration:</strong> {{exam_duration}}</p>
        </div>
        
        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0c5460; margin-top: 0;">📋 What to bring:</h4>
            <p>{{items_to_bring}}</p>
        </div>
        
        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #155724; margin-top: 0;">📚 Topics covered:</h4>
            <p>{{exam_topics}}</p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #856404; margin-top: 0;">📖 Suggested study materials:</h4>
            <p>{{study_materials}}</p>
        </div>
        
        <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #721c24; margin-top: 0;">⚠️ Important notes:</h4>
            <p>{{important_notes}}</p>
        </div>
        
        <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #383d41; margin-top: 0;">🎯 Study Tips:</h4>
            <ul>
                <li>Review all lecture notes and assignments</li>
                <li>Practice with sample questions</li>
                <li>Get plenty of rest the night before</li>
                <li>Arrive 15 minutes early</li>
            </ul>
        </div>
        
        <p style="margin-top: 20px; font-weight: bold; color: #28a745;">Good luck with your preparation!</p>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
            <p><strong>{{sender_name}}</strong><br>{{organization}}</p>
        </div>
    </div>
</body>
</html>"""
        
        return EmailTemplate(subject, text, html)
    
    @staticmethod
    def study_agenda_reminder():
        """Template for study agenda reminders."""
        subject = "📅 Study Agenda: {{agenda_title}} - Week {{week_number}}"
        
        text = """Dear {{student_name}},

Here's your study agenda for this week:

📅 Week {{week_number}}: {{agenda_title}}
📚 Course: {{course_name}}
🎯 Learning Objectives: {{learning_objectives}}

📋 This Week's Schedule:
{{daily_schedule}}

📖 Required Materials:
{{required_materials}}

📝 Assignments Due:
{{assignments_due}}

🎯 Success Tips:
- Set aside dedicated study time each day
- Take notes on key concepts
- Ask questions if you need clarification
- Review previous material regularly

💪 You've got this! Stay consistent and reach out if you need help.

Best regards,
{{sender_name}}
{{organization}}"""
        
        html = """<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0;">📅 Study Agenda</h2>
        <p style="margin: 5px 0 0 0; font-size: 18px;">Week {{week_number}}: {{agenda_title}}</p>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
        <p>Dear <strong>{{student_name}}</strong>,</p>
        
        <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #74b9ff;">
            <p><strong>📚 Course:</strong> {{course_name}}</p>
            <p><strong>🎯 Learning Objectives:</strong> {{learning_objectives}}</p>
        </div>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0066cc; margin-top: 0;">📋 This Week's Schedule:</h4>
            <div style="white-space: pre-line;">{{daily_schedule}}</div>
        </div>
        
        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #155724; margin-top: 0;">📖 Required Materials:</h4>
            <p>{{required_materials}}</p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #856404; margin-top: 0;">📝 Assignments Due:</h4>
            <p>{{assignments_due}}</p>
        </div>
        
        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0c5460; margin-top: 0;">🎯 Success Tips:</h4>
            <ul>
                <li>Set aside dedicated study time each day</li>
                <li>Take notes on key concepts</li>
                <li>Ask questions if you need clarification</li>
                <li>Review previous material regularly</li>
            </ul>
        </div>
        
        <p style="margin-top: 20px; font-weight: bold; color: #28a745;">💪 You've got this! Stay consistent and reach out if you need help.</p>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
            <p><strong>{{sender_name}}</strong><br>{{organization}}</p>
        </div>
    </div>
</body>
</html>"""
        
        return EmailTemplate(subject, text, html)
    
    @staticmethod
    def missed_study_followup():
        """Template for when a student didn't follow their study agenda."""
        subject = "📚 Study Check-in: We noticed you missed some study time"
        
        text = """Dear {{student_name}},

We hope you're doing well! 

📊 Study Progress Check:
We noticed that you may have missed some of your scheduled study time for {{course_name}} this week.

📅 Missed Sessions:
{{missed_sessions}}

Don't worry - it happens to everyone! Here's how to get back on track:

🎯 Catch-Up Plan:
{{catchup_plan}}

📚 Priority Topics:
{{priority_topics}}

💡 Study Tips to Stay on Track:
- Set phone reminders for study sessions
- Find a consistent study space
- Break large topics into smaller chunks
- Reward yourself for completing sessions

🤝 Need Help?
{{help_resources}}

Remember: Consistency is more important than perfection. Even 15-20 minutes of focused study is better than none!

You're capable of great things. Let's get back on track together! 💪

Best regards,
{{sender_name}}
{{organization}}

P.S. Reply to this email if you'd like to discuss adjusting your study schedule."""
        
        html = """<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0;">📚 Study Check-in</h2>
        <p style="margin: 5px 0 0 0; font-size: 16px;">Let's get back on track together!</p>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
        <p>Dear <strong>{{student_name}}</strong>,</p>
        
        <p>We hope you're doing well! 😊</p>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <h4 style="color: #856404; margin-top: 0;">📊 Study Progress Check:</h4>
            <p>We noticed that you may have missed some of your scheduled study time for <strong>{{course_name}}</strong> this week.</p>
        </div>
        
        <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #721c24; margin-top: 0;">📅 Missed Sessions:</h4>
            <div style="white-space: pre-line;">{{missed_sessions}}</div>
        </div>
        
        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <p style="color: #0c5460; margin: 0;"><strong>Don't worry - it happens to everyone!</strong> Here's how to get back on track:</p>
        </div>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0066cc; margin-top: 0;">🎯 Catch-Up Plan:</h4>
            <div style="white-space: pre-line;">{{catchup_plan}}</div>
        </div>
        
        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #155724; margin-top: 0;">📚 Priority Topics:</h4>
            <p>{{priority_topics}}</p>
        </div>
        
        <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #383d41; margin-top: 0;">💡 Study Tips to Stay on Track:</h4>
            <ul>
                <li>Set phone reminders for study sessions</li>
                <li>Find a consistent study space</li>
                <li>Break large topics into smaller chunks</li>
                <li>Reward yourself for completing sessions</li>
            </ul>
        </div>
        
        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0c5460; margin-top: 0;">🤝 Need Help?</h4>
            <p>{{help_resources}}</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center;">
            <p style="margin: 0; font-weight: bold;">Remember: Consistency is more important than perfection.</p>
            <p style="margin: 5px 0 0 0;">Even 15-20 minutes of focused study is better than none!</p>
        </div>
        
        <p style="margin-top: 20px; font-weight: bold; color: #28a745; text-align: center;">You're capable of great things. Let's get back on track together! 💪</p>
        
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 15px; font-style: italic; border-left: 3px solid #6c757d;">
            <p style="margin: 0; font-size: 14px;">P.S. Reply to this email if you'd like to discuss adjusting your study schedule.</p>
        </div>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
            <p><strong>{{sender_name}}</strong><br>{{organization}}</p>
        </div>
    </div>
</body>
</html>"""
        
        return EmailTemplate(subject, text, html)


class EmailTemplateManager:
    """Manager class for handling email templates."""
    
    def __init__(self):
        self.templates = {
            'course_reminder': EducationalEmailTemplates.course_reminder(),
            'exam_reminder': EducationalEmailTemplates.exam_reminder(),
            'study_agenda': EducationalEmailTemplates.study_agenda_reminder(),
            'missed_study': EducationalEmailTemplates.missed_study_followup()
        }
    
    def get_template(self, template_name: str) -> Optional[EmailTemplate]:
        """Get a template by name."""
        return self.templates.get(template_name)
    
    def render_template(self, template_name: str, **kwargs) -> Optional[Dict[str, str]]:
        """Render a template with provided variables."""
        template = self.get_template(template_name)
        if template:
            return template.render(**kwargs)
        return None
    
    def list_templates(self) -> list:
        """List available template names."""
        return list(self.templates.keys())


# Global instance
email_templates = EmailTemplateManager() 