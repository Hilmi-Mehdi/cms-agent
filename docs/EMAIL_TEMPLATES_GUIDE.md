# Email Templates for Educational Context

This guide explains how to use the pre-built email templates for educational purposes in your SMS agent project.

## Overview

The email template system provides ready-to-use, professionally designed email templates for common educational scenarios:

- **Course Reminders** - Notify students about upcoming classes
- **Exam Alerts** - Important exam information and preparation guidance  
- **Study Agendas** - Weekly study plans and schedules
- **Study Follow-ups** - Check-ins when students miss study sessions

## Quick Start

### 1. Import the Template System

```python
from app.tools.email_templates import email_templates
from app.tools.messaging_tool import MessagingTool
```

### 2. Use a Template

```python
# Render a course reminder template
email_content = email_templates.render_template('course_reminder', 
    student_name='John Smith',
    course_name='Introduction to Data Science',
    class_topic='Machine Learning Basics',
    class_date='Monday, March 15th',
    class_time='2:00 PM',
    location='Room 101, Science Building',
    instructor_name='Dr. Sarah Johnson',
    materials='• Laptop with Python installed\n• Notebook and pen',
    preparation='• Review Chapter 4 homework\n• Install scikit-learn library',
    sender_name='SMS Learning Assistant',
    organization='DataScience University'
)

# Send the email
messaging_tool = MessagingTool()
result = await messaging_tool.execute({
    "message_type": "email",
    "recipient": "john.smith@student.edu",
    **email_content
})
```

## Available Templates

### 1. Course Reminder (`course_reminder`)

**Purpose**: Remind students about upcoming classes

**Required Variables**:
- `student_name` - Student's name
- `course_name` - Name of the course
- `class_topic` - Topic for the specific class
- `class_date` - Date of the class
- `class_time` - Time of the class
- `location` - Where the class will be held
- `instructor_name` - Name of the instructor
- `materials` - Materials students should bring
- `preparation` - What students should prepare beforehand
- `sender_name` - Name of the sender
- `organization` - Your organization/institution name

**Example**:
```python
template_vars = {
    'student_name': 'Alice Johnson',
    'course_name': 'Web Development',
    'class_topic': 'React Hooks',
    'class_date': 'Wednesday, March 18th',
    'class_time': '10:00 AM',
    'location': 'Computer Lab 2',
    'instructor_name': 'Prof. Smith',
    'materials': '• Laptop\n• Code editor installed\n• Previous project files',
    'preparation': '• Complete homework 5\n• Review React basics',
    'sender_name': 'Learning Assistant',
    'organization': 'Tech University'
}
```

### 2. Exam Reminder (`exam_reminder`)

**Purpose**: Alert students about upcoming exams with detailed information

**Required Variables**:
- `student_name` - Student's name
- `exam_name` - Name/title of the exam
- `days_until` - Number of days until exam
- `exam_date` - Date of the exam
- `exam_time` - Time of the exam
- `exam_location` - Where the exam will be held
- `exam_duration` - How long the exam is
- `items_to_bring` - What students need to bring
- `exam_topics` - Topics that will be covered
- `study_materials` - Recommended study materials
- `important_notes` - Special instructions or notes
- `sender_name` - Name of the sender
- `organization` - Your organization/institution name

### 3. Study Agenda (`study_agenda`)

**Purpose**: Provide weekly study schedules and learning objectives

**Required Variables**:
- `student_name` - Student's name
- `week_number` - Which week of the course
- `agenda_title` - Title/theme for the week
- `course_name` - Name of the course
- `learning_objectives` - What students should learn
- `daily_schedule` - Day-by-day study schedule
- `required_materials` - Materials needed for the week
- `assignments_due` - Assignments due this week
- `sender_name` - Name of the sender
- `organization` - Your organization/institution name

### 4. Missed Study Follow-up (`missed_study`)

**Purpose**: Reach out to students who missed study sessions

**Required Variables**:
- `student_name` - Student's name
- `course_name` - Name of the course
- `missed_sessions` - Details about missed sessions
- `catchup_plan` - Plan to catch up on missed work
- `priority_topics` - Most important topics to focus on
- `help_resources` - Available help and resources
- `sender_name` - Name of the sender
- `organization` - Your organization/institution name

## Advanced Usage

### Creating Custom Templates

You can create your own templates using the `EmailTemplate` class:

```python
from app.tools.email_templates import EmailTemplate

# Define your template
subject = "New Assignment: {{assignment_name}}"
text_content = """Dear {{student_name}},
A new assignment has been posted: {{assignment_name}}
Due date: {{due_date}}
"""
html_content = """<html>...</html>"""

# Create the template
custom_template = EmailTemplate(subject, text_content, html_content)

# Use it
email_content = custom_template.render(
    student_name="John Doe",
    assignment_name="Project 1",
    due_date="March 25th"
)
```

### Bulk Email Sending

Send personalized emails to multiple students:

```python
students = [
    {'email': 'alice@student.edu', 'name': 'Alice', 'topic': 'JavaScript'},
    {'email': 'bob@student.edu', 'name': 'Bob', 'topic': 'Python'},
]

for student in students:
    email_content = email_templates.render_template('course_reminder',
        student_name=student['name'],
        course_name=f'Advanced {student["topic"]}',
        # ... other variables
    )
    
    await messaging_tool.execute({
        "message_type": "email",
        "recipient": student['email'],
        **email_content
    })
```

### Template Variables Tips

1. **Line Breaks**: Use `\n` for line breaks in lists:
   ```python
   materials = '• Textbook\n• Calculator\n• Notebook'
   ```

2. **Multi-line Content**: Use triple quotes for longer content:
   ```python
   daily_schedule = '''Monday: Chapter 1 (2 hours)
   Tuesday: Practice problems (1 hour)  
   Wednesday: Lab work (3 hours)'''
   ```

3. **HTML Formatting**: HTML templates support rich formatting automatically

## Email Features

The templates work with all messaging tool features:

- **Priority Levels**: Set `priority: "high"` for urgent emails
- **HTML/Text**: Templates include both HTML and plain text versions
- **Attachments**: Add files using the messaging tool's attachment feature
- **Delivery Confirmation**: Track if emails were sent successfully

## Best Practices

1. **Personalization**: Always include the student's name
2. **Clear Information**: Provide specific dates, times, and locations
3. **Action Items**: Make it clear what students need to do
4. **Contact Info**: Include how students can get help
5. **Consistent Branding**: Use consistent sender names and organization info
6. **Test First**: Test templates with sample data before bulk sending

## Integration with SMS Agent

These templates are designed to work seamlessly with your SMS agent's educational features:

- **Automated Reminders**: Set up scheduled reminders based on course calendars
- **Progress Tracking**: Send follow-ups based on student engagement data
- **Personalized Content**: Use student performance data to customize messages
- **Multi-channel**: Combine with WhatsApp messages for critical updates

## Examples

See `examples/email_template_examples.py` for complete working examples of:
- Individual template usage
- Bulk email sending
- Custom template creation
- Integration with the messaging tool

## Troubleshooting

**Template not rendering?**
- Check that all required variables are provided
- Verify variable names match exactly (case-sensitive)

**Email not sending?**
- Ensure your email configuration is set up correctly
- Check the messaging tool logs for error details

**HTML not displaying correctly?**
- Test with plain text first
- Verify HTML syntax in custom templates

## Need Help?

- Review the examples in `examples/email_template_examples.py`
- Check the messaging tool documentation
- Test individual components before combining them 