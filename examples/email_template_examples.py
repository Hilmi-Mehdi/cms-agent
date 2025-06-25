"""
Examples of using email templates for educational contexts.
This script demonstrates how to use the pre-built email templates with the messaging tool.
"""

import asyncio
from datetime import datetime, timedelta
from app.tools.messaging_tool import MessagingTool
from app.tools.email_templates import email_templates


async def send_course_reminder_example():
    """Example: Send a course reminder email."""
    print("📚 Sending Course Reminder...")
    
    messaging_tool = MessagingTool()
    
    # Prepare template variables
    template_vars = {
        'student_name': 'John Smith',
        'course_name': 'Introduction to Data Science',
        'class_topic': 'Machine Learning Basics',
        'time_until': '2 hours',
        'class_date': 'Monday, March 15th',
        'class_time': '2:00 PM',
        'location': 'Room 101, Science Building',
        'instructor_name': 'Dr. Sarah Johnson',
        'materials': '• Laptop with Python installed\n• Notebook and pen\n• Data Science textbook (Chapter 5)',
        'preparation': '• Review Chapter 4 homework\n• Install scikit-learn library\n• Complete the pre-class quiz',
        'sender_name': 'SMS Learning Assistant',
        'organization': 'DataScience University'
    }
    
    # Render the template
    email_content = email_templates.render_template('course_reminder', **template_vars)
    
    if email_content:
        # Send the email
        result = await messaging_tool.execute({
            "message_type": "email",
            "recipient": "john.smith@student.edu",
            **email_content,
            "sender_name": template_vars['sender_name']
        })
        
        print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
        if not result.success:
            print(f"   Error: {result.error}")
    else:
        print("   ❌ Failed to render template")


async def send_exam_reminder_example():
    """Example: Send an exam reminder email."""
    print("\n🚨 Sending Exam Reminder...")
    
    messaging_tool = MessagingTool()
    
    template_vars = {
        'student_name': 'Emma Davis',
        'exam_name': 'Midterm Exam - Advanced Algorithms',
        'days_until': '3',
        'exam_date': 'Friday, March 20th, 2024',
        'exam_time': '10:00 AM - 12:00 PM',
        'exam_location': 'Main Auditorium',
        'exam_duration': '2 hours',
        'items_to_bring': '• Student ID\n• Calculator (non-programmable)\n• Blue or black pen\n• Pencil for diagrams',
        'exam_topics': '• Graph algorithms (BFS, DFS, Dijkstra)\n• Dynamic programming\n• Greedy algorithms\n• Time complexity analysis',
        'study_materials': '• Textbook chapters 6-9\n• Lecture slides 8-12\n• Practice problems from homework 3-4\n• Sample exam on course website',
        'important_notes': '• Arrive 15 minutes early\n• No electronic devices allowed\n• Bring water bottle if needed\n• Late arrivals may not be admitted',
        'sender_name': 'SMS Learning Assistant',
        'organization': 'Computer Science Department'
    }
    
    email_content = email_templates.render_template('exam_reminder', **template_vars)
    
    if email_content:
        result = await messaging_tool.execute({
            "message_type": "email",
            "recipient": "emma.davis@student.edu",
            **email_content,
            "priority": "high",
            "sender_name": template_vars['sender_name']
        })
        
        print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
        if not result.success:
            print(f"   Error: {result.error}")


async def send_study_agenda_example():
    """Example: Send a weekly study agenda."""
    print("\n📅 Sending Study Agenda...")
    
    messaging_tool = MessagingTool()
    
    template_vars = {
        'student_name': 'Michael Chen',
        'week_number': '5',
        'agenda_title': 'Database Design and Normalization',
        'course_name': 'Database Systems (CS 340)',
        'learning_objectives': 'Understand 1NF, 2NF, 3NF, and BCNF. Design efficient database schemas.',
        'daily_schedule': '''Monday: Read Chapter 7 (1 hour) + Practice Problems
Tuesday: Watch video lectures on normalization (45 min)
Wednesday: Complete Lab 5 - Database Design (2 hours)
Thursday: Review concepts + Q&A session (1 hour)
Friday: Practice with sample exam questions (1.5 hours)
Weekend: Catch up on any missed topics''',
        'required_materials': '• Database textbook (Chapter 7-8)\n• Access to MySQL workbench\n• Lab 5 assignment sheet\n• Sample database files from course website',
        'assignments_due': '• Lab 5: Database Design Project (Due Friday)\n• Reading quiz on Chapter 7 (Due Wednesday)\n• Peer review of classmate\'s ER diagram (Due Sunday)',
        'sender_name': 'SMS Learning Assistant',
        'organization': 'Database Systems Course'
    }
    
    email_content = email_templates.render_template('study_agenda', **template_vars)
    
    if email_content:
        result = await messaging_tool.execute({
            "message_type": "email",
            "recipient": "michael.chen@student.edu",
            **email_content,
            "sender_name": template_vars['sender_name']
        })
        
        print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
        if not result.success:
            print(f"   Error: {result.error}")


async def send_missed_study_followup_example():
    """Example: Send a follow-up for missed study sessions."""
    print("\n📚 Sending Missed Study Follow-up...")
    
    messaging_tool = MessagingTool()
    
    template_vars = {
        'student_name': 'Sarah Rodriguez',
        'course_name': 'Organic Chemistry',
        'missed_sessions': '''Monday: Missed 1-hour review session
Wednesday: Skipped practice problems (planned 45 min)
Friday: Missed lab prep reading (30 min)

Total missed study time: 2 hours 15 minutes''',
        'catchup_plan': '''This Weekend Plan:
• Saturday morning: Catch up on missed practice problems (1 hour)
• Saturday afternoon: Complete lab prep reading (45 min)
• Sunday: Review Monday's concepts + do extra practice (1 hour)

Next Week: Get back on regular schedule''',
        'priority_topics': '• Organic reactions mechanisms\n• Stereochemistry basics\n• Lab safety procedures for next week\'s experiment',
        'help_resources': '• Office hours: Tuesdays 2-4 PM (Dr. Wilson)\n• Study group: Wednesdays 6 PM (Library room 203)\n• Online tutoring: Available 24/7 through course portal\n• Practice problem bank: Updated weekly on website',
        'sender_name': 'SMS Learning Assistant',
        'organization': 'Chemistry Department'
    }
    
    email_content = email_templates.render_template('missed_study', **template_vars)
    
    if email_content:
        result = await messaging_tool.execute({
            "message_type": "email",
            "recipient": "sarah.rodriguez@student.edu",
            **email_content,
            "sender_name": template_vars['sender_name']
        })
        
        print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
        if not result.success:
            print(f"   Error: {result.error}")


async def bulk_reminder_example():
    """Example: Send reminders to multiple students."""
    print("\n📧 Sending Bulk Course Reminders...")
    
    messaging_tool = MessagingTool()
    
    # List of students with their specific details
    students = [
        {
            'email': 'alice@student.edu',
            'name': 'Alice Johnson',
            'missed_topic': 'Linear Algebra Review'
        },
        {
            'email': 'bob@student.edu', 
            'name': 'Bob Wilson',
            'missed_topic': 'Calculus Integration'
        },
        {
            'email': 'carol@student.edu',
            'name': 'Carol Brown',
            'missed_topic': 'Probability Theory'
        }
    ]
    
    base_template_vars = {
        'course_name': 'Mathematics for Data Science',
        'class_topic': 'Final Review Session',
        'time_until': '1 day',
        'class_date': 'Tomorrow',
        'class_time': '3:00 PM',
        'location': 'Math Building, Room 150',
        'instructor_name': 'Prof. Anderson',
        'materials': '• Calculator\n• Previous homework assignments\n• Study notes',
        'sender_name': 'SMS Learning Assistant',
        'organization': 'Mathematics Department'
    }
    
    results = []
    
    for student in students:
        # Customize the template for each student
        template_vars = {
            **base_template_vars,
            'student_name': student['name'],
            'preparation': f'• Review {student["missed_topic"]} (especially important for you)\n• Complete practice problems 15-20\n• Bring questions about concepts you\'re unsure about'
        }
        
        email_content = email_templates.render_template('course_reminder', **template_vars)
        
        if email_content:
            result = await messaging_tool.execute({
                "message_type": "email",
                "recipient": student['email'],
                **email_content,
                "sender_name": template_vars['sender_name']
            })
            
            results.append((student['name'], result.success))
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
    
    # Print results
    print("   Bulk email results:")
    for name, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"     {name}: {status}")


async def custom_template_example():
    """Example: Create and use a custom template on the fly."""
    print("\n🎨 Using Custom Template...")
    
    from app.tools.email_templates import EmailTemplate
    
    # Create a custom template for assignment submissions
    subject = "Assignment Submitted: {{assignment_name}}"
    
    text = """Dear {{student_name}},

Thank you for submitting your assignment: {{assignment_name}}

📝 Submission Details:
• Submitted on: {{submission_date}}
• File name: {{file_name}}
• File size: {{file_size}}

⏱️ Next Steps:
• Your assignment will be graded within {{grading_time}}
• Feedback will be available on {{feedback_date}}
• If you have questions, please email {{instructor_email}}

✅ Tips while waiting:
• Start working on the next assignment
• Review your submission for any obvious errors
• Prepare questions for office hours

Best regards,
{{sender_name}}"""
    
    html = """<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0;">✅ Assignment Received!</h2>
    </div>
    
    <div style="padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
        <p>Dear <strong>{{student_name}}</strong>,</p>
        
        <p>Thank you for submitting your assignment: <strong>{{assignment_name}}</strong></p>
        
        <div style="background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
            <h4 style="color: #155724; margin-top: 0;">📝 Submission Details:</h4>
            <p><strong>Submitted on:</strong> {{submission_date}}</p>
            <p><strong>File name:</strong> {{file_name}}</p>
            <p><strong>File size:</strong> {{file_size}}</p>
        </div>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #0066cc; margin-top: 0;">⏱️ Next Steps:</h4>
            <ul>
                <li>Your assignment will be graded within {{grading_time}}</li>
                <li>Feedback will be available on {{feedback_date}}</li>
                <li>If you have questions, please email {{instructor_email}}</li>
            </ul>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #856404; margin-top: 0;">✅ Tips while waiting:</h4>
            <ul>
                <li>Start working on the next assignment</li>
                <li>Review your submission for any obvious errors</li>
                <li>Prepare questions for office hours</li>
            </ul>
        </div>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
            <p><strong>{{sender_name}}</strong></p>
        </div>
    </div>
</body>
</html>"""
    
    # Create the custom template
    custom_template = EmailTemplate(subject, text, html)
    
    # Use the custom template
    template_vars = {
        'student_name': 'Alex Turner',
        'assignment_name': 'Data Analysis Project #2',
        'submission_date': 'March 15, 2024 at 11:47 PM',
        'file_name': 'alex_turner_project2.pdf',
        'file_size': '2.3 MB',
        'grading_time': '5-7 business days',
        'feedback_date': 'March 22, 2024',
        'instructor_email': 'prof.smith@university.edu',
        'sender_name': 'SMS Learning Assistant'
    }
    
    email_content = custom_template.render(**template_vars)
    
    messaging_tool = MessagingTool()
    result = await messaging_tool.execute({
        "message_type": "email",
        "recipient": "alex.turner@student.edu",
        **email_content,
        "sender_name": template_vars['sender_name']
    })
    
    print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
    if not result.success:
        print(f"   Error: {result.error}")


async def main():
    """Run all email template examples."""
    print("📧 Email Template Examples for Educational Context")
    print("=" * 60)
    
    try:
        # Run individual examples
        await send_course_reminder_example()
        await send_exam_reminder_example() 
        await send_study_agenda_example()
        await send_missed_study_followup_example()
        
        # Run bulk example
        await bulk_reminder_example()
        
        # Run custom template example
        await custom_template_example()
        
        print("\n✅ All email template examples completed!")
        print("\n📋 Available Templates:")
        for template_name in email_templates.list_templates():
            print(f"   • {template_name}")
        
        print("\n💡 Tips for using templates:")
        print("   • Customize variables for each student")
        print("   • Use HTML templates for rich formatting")
        print("   • Set appropriate email priority for urgent messages")
        print("   • Test templates with sample data before bulk sending")
        print("   • Keep templates updated with current course information")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 