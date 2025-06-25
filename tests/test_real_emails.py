#!/usr/bin/env python3
"""
Test script for sending real emails with the automated system.
This will configure Mailtrap and send actual test emails.
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app.tools.student_data_tool import StudentDataTool, StudySession, StudyPlan
from app.tools.automated_email_scheduler import AutomatedEmailScheduler
from app.tools.messaging_tool import MessagingTool


async def setup_email_config():
    """Set up email configuration for testing."""
    print("📧 Setting up email configuration...")
    
    # Set environment variables for Mailtrap (from previous setup)
    os.environ['EMAIL_USER'] = '84d6fc1cf9741c'
    os.environ['EMAIL_PASSWORD'] = '86b7113a509df7'
    os.environ['SMTP_SERVER'] = 'sandbox.smtp.mailtrap.io'
    os.environ['SMTP_PORT'] = '2525'
    
    print("✅ Email configuration set with Mailtrap credentials")


async def test_basic_email():
    """Test basic email sending functionality."""
    print("\n🧪 Testing Basic Email Sending")
    print("-" * 40)
    
    messaging_tool = MessagingTool()
    
    # Test email sending
    result = await messaging_tool.execute({
        "message_type": "email",
        "recipient": "test@example.com",
        "subject": "Test Email from SMS Agent",
        "message": "This is a test email to verify the automated email system is working correctly.",
        "sender_name": "SMS Learning Assistant"
    })
    
    if result.success:
        print("✅ Basic email sent successfully!")
        print(f"   Result: {result.data}")
    else:
        print(f"❌ Email sending failed: {result.error}")
    
    return result.success


async def test_automated_emails():
    """Test the full automated email system with real sending."""
    print("\n🤖 Testing Automated Email System (REAL EMAILS)")
    print("-" * 50)
    
    # Create student tool and add test data
    student_tool = StudentDataTool()
    
    # Add a test student with a real email (use your email for testing)
    test_email = input("Enter your email address to receive test emails: ").strip()
    if not test_email:
        test_email = "test@example.com"
    
    await student_tool.execute({
        "action": "add_student",
        "student_data": {
            "student_id": "REAL001",
            "name": "Test Student",
            "email": test_email,
            "university": "Test University",
            "country": "USA",
            "language": "en"
        }
    })
    
    # Add a course
    await student_tool.execute({
        "action": "add_course",
        "course_data": {
            "course_id": "REAL101",
            "name": "Real Email Testing",
            "code": "REAL 101",
            "instructor": "Dr. Email",
            "semester": "Test 2024",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    })
    
    # Enroll student
    await student_tool.execute({
        "action": "enroll_student",
        "student_id": "REAL001",
        "course_id": "REAL101"
    })
    
    # Add an exam for today + 3 days (to trigger exam reminder)
    exam_date = date.today() + timedelta(days=3)
    await student_tool.execute({
        "action": "add_exam",
        "exam_data": {
            "exam_id": "REALEXAM001",
            "course_id": "REAL101",
            "name": "Real Email Test Exam",
            "date": exam_date.isoformat(),
            "time": "10:00 AM",
            "location": "Test Room 123",
            "duration_minutes": 120,
            "topics": ["Email testing", "Automation systems", "Student engagement"],
            "study_materials": ["Email templates guide", "System documentation", "Best practices"]
        }
    })
    
    # Create study sessions for today
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    today_sessions = [
        StudySession(
            session_id="REAL_SES001",
            student_id="REAL001",
            course_id="REAL101",
            planned_date=today,
            planned_time="09:00",
            duration_minutes=60,
            topic="Email System Testing",
            status="planned"
        ),
        StudySession(
            session_id="REAL_SES002",
            student_id="REAL001",
            course_id="REAL101",
            planned_date=today,
            planned_time="14:00",
            duration_minutes=90,
            topic="Advanced Email Automation",
            status="planned"
        )
    ]
    
    # Create missed sessions for yesterday
    yesterday_sessions = [
        StudySession(
            session_id="REAL_SES003",
            student_id="REAL001",
            course_id="REAL101",
            planned_date=yesterday,
            planned_time="10:00",
            duration_minutes=60,
            topic="Missed Study Session",
            status="missed"
        )
    ]
    
    # Create study plan
    study_plan = StudyPlan(
        plan_id="REAL_PLAN001",
        student_id="REAL001",
        exam_id="REALEXAM001",
        created_date=today,
        sessions=today_sessions + yesterday_sessions,
        total_hours=3,
        completed_hours=0
    )
    
    student_tool.study_plans["REAL_PLAN001"] = study_plan
    
    print(f"✅ Test data created for {test_email}")
    print(f"   Study sessions today: {len(today_sessions)}")
    print(f"   Missed sessions yesterday: {len(yesterday_sessions)}")
    print(f"   Exam in 3 days: {exam_date}")
    
    # Create scheduler with shared data
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool
    
    print(f"\n📧 Sending REAL emails to {test_email}...")
    print("(Check your email inbox - emails will arrive in a few seconds)")
    
    # Test 1: Daily reminder email
    print("\n1️⃣ Sending daily study reminder...")
    daily_result = await scheduler.execute({
        "action": "check_daily_reminders",
        "student_id": "REAL001",
        "dry_run": False  # REAL EMAILS!
    })
    
    if daily_result.success:
        print(f"✅ Daily reminder: {daily_result.data['emails_sent']} emails sent")
    else:
        print(f"❌ Daily reminder failed: {daily_result.error}")
    
    # Wait a moment between emails
    await asyncio.sleep(2)
    
    # Test 2: Compliance follow-up email
    print("\n2️⃣ Sending compliance follow-up...")
    compliance_result = await scheduler.execute({
        "action": "check_study_compliance",
        "student_id": "REAL001",
        "dry_run": False  # REAL EMAILS!
    })
    
    if compliance_result.success:
        print(f"✅ Compliance follow-up: {compliance_result.data['emails_sent']} emails sent")
    else:
        print(f"❌ Compliance follow-up failed: {compliance_result.error}")
    
    # Wait a moment between emails
    await asyncio.sleep(2)
    
    # Test 3: Exam reminder email
    print("\n3️⃣ Sending exam reminder...")
    exam_result = await scheduler.execute({
        "action": "check_upcoming_exams", 
        "student_id": "REAL001",
        "dry_run": False  # REAL EMAILS!
    })
    
    if exam_result.success:
        print(f"✅ Exam reminder: {exam_result.data['emails_sent']} emails sent")
    else:
        print(f"❌ Exam reminder failed: {exam_result.error}")
    
    print("\n" + "=" * 50)
    print("📬 CHECK YOUR EMAIL INBOX!")
    print("You should have received:")
    print("   📧 Daily study reminder email")
    print("   📧 Study compliance follow-up email") 
    print("   📧 Exam reminder email")
    print()
    print("💡 If emails don't appear in inbox, check:")
    print("   • Spam/junk folder")
    print("   • Mailtrap inbox (if using test email)")
    print("   • Email address spelling")


async def main():
    """Main function to test real email sending."""
    print("🚀 Real Email Testing for SMS Agent")
    print("=" * 60)
    
    try:
        # Setup email configuration
        await setup_email_config()
        
        # Test basic email sending first
        email_works = await test_basic_email()
        
        if not email_works:
            print("\n❌ Basic email test failed. Please check your email configuration.")
            print("Make sure Mailtrap credentials are correct and accessible.")
            return
        
        # Test automated emails
        await test_automated_emails()
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 