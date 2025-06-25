#!/usr/bin/env python3
"""
Automated Email System Demo for Educational Context.
This script demonstrates how to set up and use the automated email system
that monitors student data and sends contextual emails.
"""

import asyncio
from datetime import datetime, date, timedelta
from app.tools.student_data_tool import StudentDataTool
from app.tools.automated_email_scheduler import AutomatedEmailScheduler


async def setup_demo_data():
    """Set up demo student data for testing the automated system."""
    print("🏗️ Setting up demo data...")
    
    student_tool = StudentDataTool()
    
    # Add demo students
    students = [
        {
            "student_id": "STU001",
            "name": "Alice Johnson",
            "email": "alice.johnson@student.edu",
            "university": "DataScience University",
            "country": "USA",
            "language": "en"
        },
        {
            "student_id": "STU002", 
            "name": "Bob Wilson",
            "email": "bob.wilson@student.edu",
            "university": "DataScience University",
            "country": "USA", 
            "language": "en"
        },
        {
            "student_id": "STU003",
            "name": "Carol Brown",
            "email": "carol.brown@student.edu",
            "university": "Tech Institute",
            "country": "Canada",
            "language": "en"
        }
    ]
    
    for student_data in students:
        result = await student_tool.execute({
            "action": "add_student",
            "student_data": student_data
        })
        if result.success:
            print(f"   ✅ Added student: {student_data['name']}")
        else:
            print(f"   ❌ Failed to add student: {result.error}")
    
    # Add demo courses
    courses = [
        {
            "course_id": "CS101",
            "name": "Introduction to Data Science",
            "code": "CS 101",
            "instructor": "Dr. Sarah Johnson",
            "semester": "Fall 2024",
            "start_date": "2024-01-15",
            "end_date": "2024-05-15"
        },
        {
            "course_id": "CS201",
            "name": "Advanced Machine Learning",
            "code": "CS 201", 
            "instructor": "Prof. Michael Chen",
            "semester": "Fall 2024",
            "start_date": "2024-01-15",
            "end_date": "2024-05-15"
        },
        {
            "course_id": "MATH301",
            "name": "Statistics for Data Science",
            "code": "MATH 301",
            "instructor": "Dr. Emily Davis",
            "semester": "Fall 2024",
            "start_date": "2024-01-15",
            "end_date": "2024-05-15"
        }
    ]
    
    for course_data in courses:
        result = await student_tool.execute({
            "action": "add_course",
            "course_data": course_data
        })
        if result.success:
            print(f"   ✅ Added course: {course_data['name']}")
        else:
            print(f"   ❌ Failed to add course: {result.error}")
    
    # Enroll students in courses
    enrollments = [
        ("STU001", "CS101"),
        ("STU001", "MATH301"),
        ("STU002", "CS101"),
        ("STU002", "CS201"),
        ("STU003", "CS201"),
        ("STU003", "MATH301")
    ]
    
    for student_id, course_id in enrollments:
        result = await student_tool.execute({
            "action": "enroll_student",
            "student_id": student_id,
            "course_id": course_id
        })
        if result.success:
            print(f"   ✅ Enrolled {student_id} in {course_id}")
    
    # Add demo exams
    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)
    
    exams = [
        {
            "exam_id": "EXAM001",
            "course_id": "CS101",
            "name": "Data Science Fundamentals Midterm",
            "date": next_week.isoformat(),
            "time": "10:00 AM",
            "location": "Main Auditorium",
            "duration_minutes": 120,
            "topics": ["Data preprocessing", "Exploratory data analysis", "Basic statistics"],
            "study_materials": ["Textbook chapters 1-5", "Lecture slides 1-8", "Lab exercises 1-4"]
        },
        {
            "exam_id": "EXAM002",
            "course_id": "CS201",
            "name": "Machine Learning Algorithms Final",
            "date": (date.today() + timedelta(days=3)).isoformat(),
            "time": "2:00 PM",
            "location": "Computer Lab 2",
            "duration_minutes": 180,
            "topics": ["Supervised learning", "Unsupervised learning", "Neural networks"],
            "study_materials": ["ML textbook", "Research papers", "Coding assignments"]
        }
    ]
    
    for exam_data in exams:
        result = await student_tool.execute({
            "action": "add_exam",
            "exam_data": exam_data
        })
        if result.success:
            print(f"   ✅ Added exam: {exam_data['name']}")
    
    # Create study sessions for today (to test daily reminders)
    today = date.today()
    
    # Add some study sessions to the student data tool
    # Note: In a real implementation, this would be done through the study plan creation
    print(f"   📅 Demo data setup complete! Current date: {today}")
    
    return student_tool


async def demo_daily_reminders(student_tool):
    """Demo the daily reminder functionality."""
    print("\n📅 Testing Daily Reminders")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool  # Use shared instance
    
    # Check daily reminders for all students (dry run)
    result = await scheduler.execute({
        "action": "check_daily_reminders",
        "dry_run": True
    })
    
    if result.success:
        data = result.data
        print(f"✅ Daily reminders check completed")
        print(f"   Date: {data['date']}")
        print(f"   Students processed: {data['students_processed']}")
        print(f"   Emails that would be sent: {data['emails_sent']}")
        
        if data['sent_details']:
            print("   📧 Email details:")
            for email in data['sent_details']:
                print(f"      • {email['student_id']}: {email['sessions_count']} sessions")
        else:
            print("   📝 No students have study sessions scheduled for today")
    else:
        print(f"❌ Failed: {result.error}")


async def demo_compliance_checking(student_tool):
    """Demo the study compliance checking functionality."""
    print("\n📊 Testing Study Compliance Checking")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool  # Use shared instance
    
    # Check compliance for all students (dry run)
    result = await scheduler.execute({
        "action": "check_study_compliance",
        "dry_run": True
    })
    
    if result.success:
        data = result.data
        print(f"✅ Compliance check completed")
        print(f"   Date checked: {data['date']}")
        print(f"   Students processed: {data['students_processed']}")
        print(f"   Follow-up emails that would be sent: {data['emails_sent']}")
        
        if data['sent_details']:
            print("   📧 Follow-up email details:")
            for email in data['sent_details']:
                print(f"      • {email['student_id']}: {email['compliance_rate']}% compliance, {email['missed_sessions']} missed")
        else:
            print("   ✅ All students are compliant with their study plans!")
    else:
        print(f"❌ Failed: {result.error}")


async def demo_exam_reminders(student_tool):
    """Demo the exam reminder functionality."""
    print("\n🚨 Testing Exam Reminders")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool  # Use shared instance
    
    # Check exam reminders for all students (dry run)
    result = await scheduler.execute({
        "action": "check_upcoming_exams",
        "dry_run": True
    })
    
    if result.success:
        data = result.data
        print(f"✅ Exam reminders check completed")
        print(f"   Students processed: {data['students_processed']}")
        print(f"   Exam reminder emails that would be sent: {data['emails_sent']}")
        
        if data['sent_details']:
            print("   📧 Exam reminder details:")
            for email in data['sent_details']:
                print(f"      • {email['student_id']}: {email['exam_name']} in {email['days_until']} days")
        else:
            print("   📅 No exams requiring reminders at this time")
    else:
        print(f"❌ Failed: {result.error}")


async def demo_individual_student_processing(student_tool):
    """Demo processing a specific student."""
    print("\n👤 Testing Individual Student Processing")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool  # Use shared instance
    student_id = "STU001"
    
    print(f"Processing student: {student_id}")
    
    # Get student info first (using shared instance)
    student_result = await student_tool.execute({
        "action": "get_student",
        "student_id": student_id
    })
    
    if student_result.success:
        profile = student_result.data["profile"]
        print(f"   Student: {profile['name']} ({profile['email']})")
        print(f"   University: {profile['university']}")
        print(f"   Enrolled courses: {student_result.data['total_courses']}")
    
    # Check their upcoming exams
    exam_result = await student_tool.execute({
        "action": "get_upcoming_exams",
        "student_id": student_id,
        "days_ahead": 14
    })
    
    if exam_result.success:
        exams = exam_result.data["upcoming_exams"]
        print(f"   Upcoming exams: {len(exams)}")
        for exam_info in exams:
            exam = exam_info["exam"]
            print(f"      • {exam['name']} in {exam_info['days_until']} days")
    
    # Check daily reminders for this student
    daily_result = await scheduler.execute({
        "action": "check_daily_reminders",
        "student_id": student_id,
        "dry_run": True
    })
    
    if daily_result.success:
        print(f"   Daily reminders would send: {daily_result.data['emails_sent']} emails")


async def demo_full_automated_run(student_tool):
    """Demo a full automated run processing all students."""
    print("\n🤖 Testing Full Automated Processing")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    scheduler.student_data_tool = student_tool  # Use shared instance
    
    # Process all students for all types of notifications
    result = await scheduler.execute({
        "action": "process_all_students",
        "dry_run": True
    })
    
    if result.success:
        data = result.data
        print(f"✅ Full automated processing completed")
        print(f"   Timestamp: {data['timestamp']}")
        print(f"   Total emails that would be sent: {data['results']['total_emails']}")
        print()
        print("   📊 Breakdown by type:")
        
        daily = data['results']['daily_reminders']
        print(f"      Daily reminders: {daily['emails_sent']} emails to {daily['students_processed']} students")
        
        compliance = data['results']['compliance_checks']
        print(f"      Compliance follow-ups: {compliance['emails_sent']} emails to {compliance['students_processed']} students")
        
        exams = data['results']['exam_reminders']
        print(f"      Exam reminders: {exams['emails_sent']} emails to {exams['students_processed']} students")
        
        if data['results']['total_emails'] > 0:
            print("\n   🎯 This system would automatically:")
            print("      • Send daily study reminders")
            print("      • Follow up on missed study sessions")
            print("      • Alert students about upcoming exams")
            print("      • Personalize content based on student data")
    else:
        print(f"❌ Failed: {result.error}")


async def demo_email_log():
    """Demo the email logging functionality."""
    print("\n📝 Testing Email Log")
    print("=" * 50)
    
    scheduler = AutomatedEmailScheduler()
    
    # Get email log
    result = await scheduler.execute({
        "action": "get_email_log"
    })
    
    if result.success:
        log_data = result.data
        print(f"✅ Email log retrieved")
        print(f"   Total emails in log: {log_data['total_emails']}")
        
        if log_data['email_log']:
            print("   📧 Recent emails:")
            for email in log_data['email_log'][-5:]:  # Show last 5
                timestamp = email['timestamp']
                print(f"      • {timestamp}: {email['email_type']} to {email['student_id']} ({'✅' if email['success'] else '❌'})")
        else:
            print("   📭 No emails in log yet")
    else:
        print(f"❌ Failed: {result.error}")


async def main():
    """Run all demo functions."""
    print("🎓 Automated Email System Demo")
    print("=" * 60)
    
    try:
        # Setup demo data
        student_tool = await setup_demo_data()
        
        # Run all demos
        await demo_daily_reminders(student_tool)
        await demo_compliance_checking(student_tool)
        await demo_exam_reminders(student_tool)
        await demo_individual_student_processing(student_tool)
        await demo_full_automated_run(student_tool)
        await demo_email_log()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print()
        print("💡 Key Features Demonstrated:")
        print("   ✅ Automatic daily study reminders")
        print("   ✅ Study compliance monitoring")
        print("   ✅ Exam reminder scheduling")
        print("   ✅ Individual student processing")
        print("   ✅ Bulk processing capabilities")
        print("   ✅ Email logging and tracking")
        print()
        print("🚀 To use in production:")
        print("   1. Set up real student data")
        print("   2. Configure email credentials")
        print("   3. Remove 'dry_run=True' parameters")
        print("   4. Set up scheduled execution (cron jobs, etc.)")
        print("   5. Monitor email logs for delivery status")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 