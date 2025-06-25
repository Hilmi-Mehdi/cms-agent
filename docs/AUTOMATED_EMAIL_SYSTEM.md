# Automated Email System for Educational Context

This document describes the intelligent automated email system that monitors student data and sends contextual emails based on study patterns, schedules, exam dates, and compliance tracking.

## Overview

The automated email system consists of three main components:

1. **Student Data Tool** - Manages student profiles, courses, exams, and study schedules
2. **Automated Email Scheduler** - Monitors student data and triggers emails based on conditions
3. **Email Templates** - Professional, educational email templates for different scenarios

## Key Features

### 🎯 Intelligent Monitoring
- **Study Session Tracking** - Monitors planned vs. actual study sessions
- **Compliance Analysis** - Tracks adherence to study plans
- **Exam Scheduling** - Watches for upcoming exams and deadlines
- **Personalized Content** - Customizes emails based on individual student data

### 📧 Automated Email Types

1. **Daily Study Reminders**
   - Sent when students have study sessions planned for today
   - Includes session details, materials needed, and preparation

2. **Study Compliance Follow-ups**
   - Triggered when students miss scheduled study sessions
   - Provides catch-up plans and motivational content

3. **Exam Reminders**
   - Sent at 7 days, 3 days, and 1 day before exams
   - Includes exam details, study materials, and preparation tips

4. **Custom Notifications**
   - Flexible system for custom educational communications

### ⏰ Automated Scheduling
- **Morning Reminders** (8:00 AM) - Daily study session alerts
- **Evening Check-ins** (7:00 PM) - Compliance monitoring
- **Exam Alerts** (9:00 AM) - Upcoming exam notifications
- **Full Processing** (6:00 AM) - Complete system check

## Quick Start

### 1. Basic Setup

```python
from app.tools.student_data_tool import StudentDataTool
from app.tools.automated_email_scheduler import AutomatedEmailScheduler

# Initialize tools
student_tool = StudentDataTool()
scheduler = AutomatedEmailScheduler()
```

### 2. Add Student Data

```python
# Add a student
await student_tool.execute({
    "action": "add_student",
    "student_data": {
        "student_id": "STU001",
        "name": "Alice Johnson",
        "email": "alice@student.edu",
        "university": "DataScience University",
        "country": "USA",
        "language": "en"
    }
})

# Add a course
await student_tool.execute({
    "action": "add_course",
    "course_data": {
        "course_id": "CS101",
        "name": "Introduction to Data Science",
        "code": "CS 101",
        "instructor": "Dr. Sarah Johnson",
        "semester": "Fall 2024",
        "start_date": "2024-01-15",
        "end_date": "2024-05-15"
    }
})

# Enroll student in course
await student_tool.execute({
    "action": "enroll_student",
    "student_id": "STU001",
    "course_id": "CS101"
})
```

### 3. Run Automated Checks

```python
# Check for daily reminders
result = await scheduler.execute({
    "action": "check_daily_reminders",
    "dry_run": True  # Set to False for production
})

# Check study compliance
result = await scheduler.execute({
    "action": "check_study_compliance",
    "dry_run": True
})

# Check upcoming exams
result = await scheduler.execute({
    "action": "check_upcoming_exams", 
    "dry_run": True
})
```

## Student Data Management

### Student Profiles

Each student profile includes:
- Basic information (name, email, university, country, language)
- Timezone for scheduling
- Contact preferences
- Enrollment history

### Course Management

Course data includes:
- Course details (name, code, instructor)
- Semester and date information
- Prerequisites and credits
- Associated exams and assignments

### Study Plans and Sessions

Study sessions track:
- Planned study times and topics
- Actual completion status
- Materials and resources needed
- Progress tracking

### Exam Scheduling

Exam data includes:
- Date, time, and location
- Duration and format
- Topics covered
- Study materials and preparation guidance

## Automated Email Logic

### Daily Reminders Logic

```python
# Pseudocode for daily reminders
for each student:
    sessions = get_today_sessions(student_id)
    if sessions.count > 0:
        send_daily_reminder(student, sessions)
```

**Triggers:**
- Student has study sessions planned for today
- Sessions include specific times, topics, and materials

**Email Content:**
- List of today's study sessions
- Required materials and preparation
- Time management tips

### Compliance Monitoring Logic

```python
# Pseudocode for compliance checking
for each student:
    compliance = check_yesterday_compliance(student_id)
    if compliance.rate < 80%:  # Configurable threshold
        send_compliance_followup(student, compliance)
```

**Triggers:**
- Student compliance rate below 80% (configurable)
- Missed study sessions from previous day
- Pattern of non-compliance detected

**Email Content:**
- Summary of missed sessions
- Catch-up plan suggestions
- Motivational content and resources

### Exam Reminder Logic

```python
# Pseudocode for exam reminders
for each student:
    exams = get_upcoming_exams(student_id, days=14)
    for exam in exams:
        if exam.days_until in [7, 3, 1]:
            send_exam_reminder(student, exam)
```

**Triggers:**
- Exam is 7 days away (initial reminder)
- Exam is 3 days away (preparation reminder)
- Exam is 1 day away (final reminder)

**Email Content:**
- Exam details and logistics
- Study materials and topics
- Preparation strategies and tips

## Production Deployment

### Using the Scheduler Service

```bash
# Install dependencies
pip install schedule

# Run in dry-run mode for testing
python app/utils/email_scheduler_service.py --dry-run --test

# Run once (for testing)
python app/utils/email_scheduler_service.py --once --dry-run

# Run continuous scheduling (production)
python app/utils/email_scheduler_service.py
```

### Configuration Options

```python
# Email scheduling configuration
DAILY_REMINDER_TIME = "08:00"
COMPLIANCE_CHECK_TIME = "19:00"
EXAM_REMINDER_TIME = "09:00"
FULL_PROCESSING_TIME = "06:00"

# Compliance thresholds
COMPLIANCE_THRESHOLD = 80  # Percentage
MISSED_SESSION_LIMIT = 3   # Number of sessions

# Email settings
DRY_RUN = False
EMAIL_RETRY_ATTEMPTS = 3
EMAIL_TIMEOUT = 30
```

### Logging and Monitoring

The system provides comprehensive logging:

```python
# Log levels and messages
INFO: Daily operations and successful email sends
WARNING: Non-critical issues and retries
ERROR: Failed email sends and system errors
DEBUG: Detailed execution information
```

Log files:
- `automated_emails.log` - Main application log
- Email delivery status in database/memory
- Performance metrics and statistics

## Data Models

### StudentProfile
```python
{
    "student_id": "STU001",
    "name": "Alice Johnson", 
    "email": "alice@student.edu",
    "university": "DataScience University",
    "country": "USA",
    "language": "en",
    "timezone": "UTC"
}
```

### StudySession
```python
{
    "session_id": "SES001",
    "student_id": "STU001",
    "course_id": "CS101",
    "planned_date": "2024-03-15",
    "planned_time": "14:00",
    "duration_minutes": 60,
    "topic": "Data Preprocessing",
    "status": "planned|completed|missed|rescheduled"
}
```

### Exam
```python
{
    "exam_id": "EXAM001",
    "course_id": "CS101", 
    "name": "Midterm Exam",
    "date": "2024-03-20",
    "time": "10:00 AM",
    "location": "Main Auditorium",
    "topics": ["Data preprocessing", "EDA"],
    "study_materials": ["Textbook Ch. 1-5"]
}
```

## API Reference

### Student Data Tool Actions

- `add_student` - Add new student profile
- `get_student` - Retrieve student information
- `update_student` - Update student profile
- `add_course` - Add new course
- `enroll_student` - Enroll student in course
- `add_exam` - Add exam information
- `create_study_plan` - Create study schedule
- `log_study_session` - Record study session completion
- `get_today_sessions` - Get today's planned sessions
- `get_missed_sessions` - Get missed study sessions
- `get_upcoming_exams` - Get upcoming exams
- `check_study_compliance` - Check compliance rate

### Automated Email Scheduler Actions

- `check_daily_reminders` - Process daily study reminders
- `check_study_compliance` - Check and follow up on compliance
- `check_upcoming_exams` - Process exam reminders
- `process_all_students` - Run complete automation cycle
- `get_email_log` - Retrieve email sending history
- `send_custom_notification` - Send custom email

## Customization

### Adding New Email Types

1. Create new template in `email_templates.py`
2. Add trigger logic in `automated_email_scheduler.py`
3. Update scheduling in `email_scheduler_service.py`

### Custom Triggers

```python
# Example: Add assignment deadline reminders
async def check_assignment_deadlines(self):
    # Custom logic for assignment reminders
    pass
```

### Localization

```python
# Student language-based email customization
if student.language == "es":
    template_name = "course_reminder_es"
elif student.language == "fr":
    template_name = "course_reminder_fr"
else:
    template_name = "course_reminder"
```

## Best Practices

### Data Management
- Keep student data up to date
- Regular backup of study plans and progress
- Monitor data quality and completeness

### Email Delivery
- Test templates before deployment
- Monitor delivery rates and bounces
- Respect email frequency limits
- Provide unsubscribe options

### Performance
- Use database connections efficiently
- Implement email rate limiting
- Monitor system resource usage
- Set up appropriate logging levels

### Privacy and Security
- Encrypt sensitive student data
- Implement access controls
- Follow educational data privacy regulations
- Regular security audits

## Troubleshooting

### Common Issues

**Emails not sending:**
- Check email configuration in `.env`
- Verify SMTP server connectivity
- Check student email addresses
- Review error logs

**Missing student data:**
- Verify data import process
- Check database connections
- Validate data format

**Scheduling issues:**
- Check system timezone settings
- Verify cron job configuration
- Monitor service status

### Debug Commands

```bash
# Test email configuration
python -c "from app.tools.messaging_tool import MessagingTool; print('Email config OK')"

# Test student data
python examples/automated_email_system_demo.py

# Run scheduler in debug mode
python app/utils/email_scheduler_service.py --dry-run --test
```

## Integration Examples

### With Learning Management Systems

```python
# Import student data from LMS
async def import_from_lms():
    lms_data = fetch_lms_data()
    for student in lms_data:
        await student_tool.execute({
            "action": "add_student",
            "student_data": transform_lms_student(student)
        })
```

### With Calendar Systems

```python
# Sync with calendar for study sessions
async def sync_calendar_events():
    events = fetch_calendar_events()
    for event in events:
        if event.type == "study_session":
            await log_study_completion(event)
```

## Future Enhancements

- **AI-Powered Personalization** - Use ML to optimize email timing and content
- **Multi-language Support** - Expand template system for global use
- **Advanced Analytics** - Student engagement and success metrics
- **Mobile Integration** - SMS and push notification support
- **Adaptive Scheduling** - Dynamic scheduling based on student preferences

This automated email system provides a comprehensive solution for educational institutions to maintain engagement with students through intelligent, data-driven communications. 