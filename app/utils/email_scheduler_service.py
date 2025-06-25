"""
Email Scheduler Service for SMS Agent.
This service runs the automated email system on a schedule and handles
production-level concerns like error handling, logging, and retry logic.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any
import schedule
import time as time_module
from app.tools.automated_email_scheduler import AutomatedEmailScheduler
from app.tools.student_data_tool import StudentDataTool


class EmailSchedulerService:
    """Service for running automated emails on a schedule."""
    
    def __init__(self, dry_run: bool = False):
        self.scheduler = AutomatedEmailScheduler()
        self.student_tool = StudentDataTool()
        self.dry_run = dry_run
        self.running = False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automated_emails.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_daily_reminders(self):
        """Run daily study reminders."""
        self.logger.info("🌅 Starting daily reminders check...")
        
        try:
            result = await self.scheduler.execute({
                "action": "check_daily_reminders",
                "dry_run": self.dry_run
            })
            
            if result.success:
                data = result.data
                self.logger.info(f"✅ Daily reminders completed: {data['emails_sent']} emails sent to {data['students_processed']} students")
                
                if data['errors']:
                    for error in data['errors']:
                        self.logger.error(f"Error in daily reminders: {error}")
            else:
                self.logger.error(f"❌ Daily reminders failed: {result.error}")
                
        except Exception as e:
            self.logger.error(f"💥 Exception in daily reminders: {str(e)}")
    
    async def run_compliance_check(self):
        """Run study compliance checks."""
        self.logger.info("📊 Starting compliance check...")
        
        try:
            result = await self.scheduler.execute({
                "action": "check_study_compliance",
                "dry_run": self.dry_run
            })
            
            if result.success:
                data = result.data
                self.logger.info(f"✅ Compliance check completed: {data['emails_sent']} follow-up emails sent")
                
                if data['errors']:
                    for error in data['errors']:
                        self.logger.error(f"Error in compliance check: {error}")
            else:
                self.logger.error(f"❌ Compliance check failed: {result.error}")
                
        except Exception as e:
            self.logger.error(f"💥 Exception in compliance check: {str(e)}")
    
    async def run_exam_reminders(self):
        """Run exam reminder checks."""
        self.logger.info("🚨 Starting exam reminders check...")
        
        try:
            result = await self.scheduler.execute({
                "action": "check_upcoming_exams",
                "dry_run": self.dry_run
            })
            
            if result.success:
                data = result.data
                self.logger.info(f"✅ Exam reminders completed: {data['emails_sent']} reminder emails sent")
                
                if data['errors']:
                    for error in data['errors']:
                        self.logger.error(f"Error in exam reminders: {error}")
            else:
                self.logger.error(f"❌ Exam reminders failed: {result.error}")
                
        except Exception as e:
            self.logger.error(f"💥 Exception in exam reminders: {str(e)}")
    
    async def run_full_processing(self):
        """Run full automated processing for all students."""
        self.logger.info("🤖 Starting full automated processing...")
        
        try:
            result = await self.scheduler.execute({
                "action": "process_all_students",
                "dry_run": self.dry_run
            })
            
            if result.success:
                data = result.data
                total_emails = data['results']['total_emails']
                self.logger.info(f"✅ Full processing completed: {total_emails} total emails processed")
                
                # Log breakdown
                daily = data['results']['daily_reminders']
                compliance = data['results']['compliance_checks'] 
                exams = data['results']['exam_reminders']
                
                self.logger.info(f"   📅 Daily reminders: {daily['emails_sent']} emails")
                self.logger.info(f"   📊 Compliance follow-ups: {compliance['emails_sent']} emails")
                self.logger.info(f"   🚨 Exam reminders: {exams['emails_sent']} emails")
            else:
                self.logger.error(f"❌ Full processing failed: {result.error}")
                
        except Exception as e:
            self.logger.error(f"💥 Exception in full processing: {str(e)}")
    
    def setup_schedule(self):
        """Set up the email sending schedule."""
        self.logger.info("⏰ Setting up email schedule...")
        
        # Daily reminders at 8:00 AM
        schedule.every().day.at("08:00").do(
            lambda: asyncio.create_task(self.run_daily_reminders())
        )
        
        # Compliance checks at 7:00 PM (check yesterday's compliance)
        schedule.every().day.at("19:00").do(
            lambda: asyncio.create_task(self.run_compliance_check())
        )
        
        # Exam reminders at 9:00 AM
        schedule.every().day.at("09:00").do(
            lambda: asyncio.create_task(self.run_exam_reminders())
        )
        
        # Full processing once per day at 6:00 AM
        schedule.every().day.at("06:00").do(
            lambda: asyncio.create_task(self.run_full_processing())
        )
        
        # Alternative: Run every few hours during the day
        # schedule.every(3).hours.do(
        #     lambda: asyncio.create_task(self.run_daily_reminders())
        # )
        
        self.logger.info("✅ Schedule configured:")
        self.logger.info("   📅 Daily reminders: 8:00 AM")
        self.logger.info("   📊 Compliance checks: 7:00 PM")  
        self.logger.info("   🚨 Exam reminders: 9:00 AM")
        self.logger.info("   🤖 Full processing: 6:00 AM")
    
    async def run_scheduled_jobs(self):
        """Run the scheduled jobs."""
        self.logger.info("🚀 Starting email scheduler service...")
        self.running = True
        
        while self.running:
            try:
                # Check for scheduled jobs
                schedule.run_pending()
                
                # Sleep for a minute before checking again
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ Received shutdown signal")
                self.running = False
            except Exception as e:
                self.logger.error(f"💥 Error in scheduler loop: {str(e)}")
                # Continue running even if there's an error
                await asyncio.sleep(60)
        
        self.logger.info("🛑 Email scheduler service stopped")
    
    def stop(self):
        """Stop the scheduler service."""
        self.running = False
    
    async def run_test_cycle(self):
        """Run a quick test cycle for demonstration."""
        self.logger.info("🧪 Running test cycle...")
        
        await self.run_daily_reminders()
        await asyncio.sleep(2)
        
        await self.run_compliance_check()
        await asyncio.sleep(2)
        
        await self.run_exam_reminders()
        await asyncio.sleep(2)
        
        self.logger.info("✅ Test cycle completed")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the scheduler service."""
        try:
            # Get email log
            log_result = await self.scheduler.execute({
                "action": "get_email_log"
            })
            
            # Get student count
            student_count = len(self.student_tool.students)
            
            status = {
                "running": self.running,
                "dry_run": self.dry_run,
                "student_count": student_count,
                "total_emails_sent": log_result.result["total_emails"] if log_result.success else 0,
                "last_check": datetime.now().isoformat(),
                "scheduled_jobs": len(schedule.jobs)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")
            return {"error": str(e)}


async def main():
    """Main function for running the email scheduler service."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Email Scheduler Service for SMS Agent")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual emails sent)")
    parser.add_argument("--test", action="store_true", help="Run a quick test cycle instead of continuous scheduling")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    service = EmailSchedulerService(dry_run=args.dry_run)
    
    if args.test:
        # Run test cycle
        await service.run_test_cycle()
    elif args.once:
        # Run full processing once
        await service.run_full_processing()
    else:
        # Run continuous scheduling
        service.setup_schedule()
        await service.run_scheduled_jobs()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Scheduler service stopped by user")
    except Exception as e:
        print(f"💥 Service failed: {e}")
        import traceback
        traceback.print_exc() 