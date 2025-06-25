"""
Example usage of the messaging tool for sending emails and WhatsApp messages.
"""

import asyncio
import os
from app.tools.messaging_tool import MessagingTool


async def send_email_example():
    """Example of sending an email."""
    messaging_tool = MessagingTool()
    
    # Simple text email
    result = await messaging_tool.execute({
        "message_type": "email",
        "recipient": "recipient@example.com",
        "subject": "Test Email from SMS Agent",
        "message": "Hello! This is a test email sent from the SMS Agent messaging tool.",
        "sender_name": "SMS Agent"
    })
    
    print("Email Result:", result.dict())
    return result


async def send_html_email_with_attachments():
    """Example of sending an HTML email with attachments."""
    messaging_tool = MessagingTool()
    
    html_message = """
    <html>
        <body>
            <h2>Course Materials</h2>
            <p>Dear Student,</p>
            <p>Please find the course materials attached to this email.</p>
            <ul>
                <li>Lecture slides</li>
                <li>Assignment instructions</li>
                <li>Reading materials</li>
            </ul>
            <p>Best regards,<br>SMS Agent</p>
        </body>
    </html>
    """
    
    result = await messaging_tool.execute({
        "message_type": "email",
        "recipient": "student@university.edu",
        "subject": "Course Materials - Week 1",
        "message": html_message,
        "message_format": "html",
        "attachments": [
            # Add paths to actual files here
            # "/path/to/lecture_slides.pdf",
            # "/path/to/assignment.docx"
        ],
        "priority": "high",
        "sender_name": "Course Instructor"
    })
    
    print("HTML Email with Attachments Result:", result.dict())
    return result


async def send_whatsapp_example():
    """Example of sending a WhatsApp message."""
    messaging_tool = MessagingTool()
    
    result = await messaging_tool.execute({
        "message_type": "whatsapp",
        "recipient": "+1234567890",  # Replace with actual phone number
        "message": "Hello! This is a test message from SMS Agent. How can I help you today?"
    })
    
    print("WhatsApp Result:", result.dict())
    return result


async def send_course_reminder_email():
    """Example of sending a course reminder email."""
    messaging_tool = MessagingTool()
    
    result = await messaging_tool.execute({
        "message_type": "email",
        "recipient": "student@university.edu",
        "subject": "Reminder: Exam Tomorrow at 2 PM",
        "message": """
        Dear Student,
        
        This is a friendly reminder that you have an exam scheduled for tomorrow:
        
        Course: Introduction to Data Science
        Date: Tomorrow
        Time: 2:00 PM - 4:00 PM
        Location: Room 101, Science Building
        
        Please make sure to bring:
        - Student ID
        - Calculator
        - Blue or black pen
        
        Good luck with your exam!
        
        Best regards,
        SMS Agent
        """,
        "priority": "high",
        "sender_name": "SMS Agent - Course Reminders"
    })
    
    print("Course Reminder Result:", result.dict())
    return result


async def send_assignment_notification():
    """Example of sending assignment notification via WhatsApp."""
    messaging_tool = MessagingTool()
    
    result = await messaging_tool.execute({
        "message_type": "whatsapp",
        "recipient": "+1234567890",  # Replace with actual phone number
        "message": """
        📚 Assignment Reminder
        
        Hi! Your assignment "Data Analysis Project" is due in 2 days.
        
        Due Date: Friday, 5:00 PM
        
        Don't forget to submit it through the course portal.
        
        Need help? Reply to this message!
        """
    })
    
    print("Assignment Notification Result:", result.dict())
    return result


async def bulk_messaging_example():
    """Example of sending messages to multiple recipients."""
    messaging_tool = MessagingTool()
    
    recipients = [
        {"email": "student1@university.edu", "phone": "+1234567890"},
        {"email": "student2@university.edu", "phone": "+1234567891"},
        {"email": "student3@university.edu", "phone": "+1234567892"},
    ]
    
    message_content = "Important: Class has been moved to Room 205 for today's session."
    
    results = []
    
    # Send emails to all recipients
    for recipient in recipients:
        email_result = await messaging_tool.execute({
            "message_type": "email",
            "recipient": recipient["email"],
            "subject": "Class Location Change",
            "message": message_content,
            "sender_name": "SMS Agent"
        })
        results.append(("email", recipient["email"], email_result.success))
        
        # Optional: Also send WhatsApp message
        whatsapp_result = await messaging_tool.execute({
            "message_type": "whatsapp",
            "recipient": recipient["phone"],
            "message": f"🏫 {message_content}"
        })
        results.append(("whatsapp", recipient["phone"], whatsapp_result.success))
        
        # Add a small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    print("Bulk Messaging Results:")
    for msg_type, recipient, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {msg_type.title()} to {recipient}: {status}")
    
    return results


async def main():
    """Run all messaging examples."""
    print("=== Messaging Tool Examples ===\n")
    
    # Check if environment variables are set
    email_configured = bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD"))
    whatsapp_configured = bool(
        (os.getenv("WHATSAPP_API_URL") and os.getenv("WHATSAPP_TOKEN")) or
        (os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"))
    )
    
    print(f"Email configured: {'✅' if email_configured else '❌'}")
    print(f"WhatsApp configured: {'✅' if whatsapp_configured else '❌'}")
    print()
    
    if not email_configured and not whatsapp_configured:
        print("⚠️  No messaging services configured.")
        print("Please check the MESSAGING_TOOL_SETUP.md file for configuration instructions.")
        return
    
    try:
        if email_configured:
            print("1. Sending simple email...")
            await send_email_example()
            print()
            
            print("2. Sending HTML email with attachments...")
            await send_html_email_with_attachments()
            print()
            
            print("3. Sending course reminder email...")
            await send_course_reminder_email()
            print()
        
        if whatsapp_configured:
            print("4. Sending WhatsApp message...")
            await send_whatsapp_example()
            print()
            
            print("5. Sending assignment notification via WhatsApp...")
            await send_assignment_notification()
            print()
        
        if email_configured and whatsapp_configured:
            print("6. Bulk messaging example...")
            await bulk_messaging_example()
            print()
        
        print("✅ All examples completed!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 