import asyncio
import aiosmtplib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
EMAIL_CONFIG = {
    'sender': "no-reply@example.com",  
    'password': "dummy_password",      
    'smtp_server': "smtp.example.com",
    'smtp_port': 587,
    'recipient': "admin@example.com"
}

class DigitalJournal:
    def __init__(self):
        self.students: Dict[int, Dict[str, Any]] = {}
        self.marks_by_date: Dict[datetime.date, List[Dict[str, Any]]] = defaultdict(list)
        self.running = True
        self._generate_sample_data()

    def _generate_sample_data(self):
        """Generate sample data for 100,000 students"""
        logger.info("Generating sample data for 100,000 students...")
        for i in range(1, 100001):
            self.students[i] = {
                'name': f'Student {i}',
                'marks': [],
                'created_at': datetime.now().isoformat()
            }
        logger.info("Sample data generation completed")

    async def add_mark(self, student_id: int, mark: int) -> bool:
        """Add a mark for a student with creation date"""
        if student_id not in self.students:
            logger.warning(f"Attempt to add mark for non-existent student ID: {student_id}")
            return False
        
        if not 1 <= mark <= 100:
            logger.warning(f"Attempt to add invalid mark: {mark}")
            return False

        creation_date = datetime.now()
        mark_data = {
            'value': mark,
            'creation_date': creation_date.isoformat(),
            'student_id': student_id
        }
        
        self.students[student_id]['marks'].append(mark_data)
        self.marks_by_date[creation_date.date()].append(mark_data)
        
        logger.debug(f"Added mark {mark} for student {student_id}")
        return True

    async def get_daily_average(self, date: datetime) -> Optional[float]:
        """Calculate average mark for a specific day"""
        daily_marks = self.marks_by_date.get(date.date(), [])
        
        if not daily_marks:
            logger.info(f"No marks found for date {date.date()}")
            return None
            
        total = sum(mark['value'] for mark in daily_marks)
        average = round(total / len(daily_marks), 2)
        
        logger.debug(f"Calculated average {average} for {date.date()} with {len(daily_marks)} marks")
        return average

    async def send_report(self, subject: str, body: str) -> bool:
        """Send email report with error handling"""
        message = aiosmtplib.email.message.EmailMessage()
        message["From"] = EMAIL_CONFIG['sender']
        message["To"] = EMAIL_CONFIG['recipient']
        message["Subject"] = subject
        
        try:
            message.set_content(body)
            await aiosmtplib.send(
                message,
                hostname=EMAIL_CONFIG['smtp_server'],
                port=EMAIL_CONFIG['smtp_port'],
                username=EMAIL_CONFIG['sender'],
                password=EMAIL_CONFIG['password'],
                use_tls=True
            )
            logger.info(f"Successfully sent report: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email report: {e}", exc_info=True)
            return False

    async def schedule_reports(self):
        """Schedule daily and monthly reports"""
        while self.running:
            try:
                now = datetime.now()

                # Daily report at 23:55
                daily_report_time = now.replace(hour=23, minute=55, second=0, microsecond=0)
                if now > daily_report_time:
                    daily_report_time += timedelta(days=1)
                
                daily_delay = (daily_report_time - now).total_seconds()
                await asyncio.sleep(daily_delay)
                
                avg = await self.get_daily_average(datetime.now())
                report_date = datetime.now().date()
                report_body = (
                    f"Date: {report_date}\n"
                    f"Average Mark: {avg if avg is not None else 'No marks today'}\n"
                    f"Total Marks Today: {len(self.marks_by_date.get(report_date, []))}"
                )
                await self.send_report(
                    "Daily Average Mark Report",
                    report_body
                )

                # Monthly report on 1st day at 00:05
                monthly_report_time = now.replace(day=1, hour=0, minute=5, second=0, microsecond=0)
                if now > monthly_report_time:
                    if now.month == 12:
                        monthly_report_time = monthly_report_time.replace(month=1, year=now.year + 1)
                    else:
                        monthly_report_time = monthly_report_time.replace(month=now.month + 1)
                
                monthly_delay = (monthly_report_time - now).total_seconds()
                await asyncio.sleep(monthly_delay)
                
                await self.send_report(
                    "Monthly Student Report",
                    f"Date: {datetime.now().date()}\n"
                    f"Total Students: {len(self.students)}\n"
                    f"Total Marks This Month: {sum(len(v) for d, v in self.marks_by_date.items() if d.month == now.month)}"
                )
            except asyncio.CancelledError:
                logger.info("Report scheduling cancelled")
                break
            except Exception as e:
                logger.error(f"Error in report scheduling: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retrying

    async def simulate_mark_addition(self):
        """Simulate adding marks in background"""
        while self.running:
            try:
                student_id = random.randint(1, 100000)
                mark = random.randint(1, 100)
                await self.add_mark(student_id, mark)
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                logger.info("Mark simulation cancelled")
                break
            except Exception as e:
                logger.error(f"Error in mark simulation: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def shutdown(self):
        """Clean shutdown of the application"""
        self.running = False
        logger.info("Shutting down Digital Journal")

async def async_input(prompt: str = "") -> str:
    """Non-blocking input using asyncio"""
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

async def main():
    """Main application entry point"""
    try:
        journal = DigitalJournal()
        report_task = asyncio.create_task(journal.schedule_reports())
        simulation_task = asyncio.create_task(journal.simulate_mark_addition())

        while True:
            cmd = (await async_input("\nCommand (addmark/list/quit): ")).strip().lower()

            if cmd == "quit":
                await journal.shutdown()
                report_task.cancel()
                simulation_task.cancel()
                logger.info("Application shutdown requested")
                break

            elif cmd == "addmark":
                try:
                    student_id = int(await async_input("Student ID (1-100000): "))
                    mark = int(await async_input("Mark (1-100): "))
                    
                    if not (1 <= student_id <= 100000):
                        print("Student ID must be between 1 and 100000")
                        continue
                        
                    if not (1 <= mark <= 100):
                        print("Mark must be between 1 and 100")
                        continue
                        
                    if await journal.add_mark(student_id, mark):
                        print("Mark added successfully")
                    else:
                        print("Failed to add mark")
                except ValueError:
                    print("Please enter valid numbers")

            elif cmd == "list":
                print(f"\nTotal students: {len(journal.students)}")
                print(f"Total marks in system: {sum(len(s['marks']) for s in journal.students.values())}")
                
                # Show first 10 students with marks
                students_with_marks = [
                    (sid, student) 
                    for sid, student in journal.students.items() 
                    if student['marks']
                ][:10]
                
                if not students_with_marks:
                    print("\nNo students with marks yet")
                else:
                    print("\nStudents with marks (showing first 10):")
                    for sid, student in students_with_marks:
                        print(f"\nStudent {sid}: {student['name']}")
                        print(f"Total marks: {len(student['marks'])}")
                        for mark in student['marks'][-3:]:  # Show last 3 marks
                            print(f"  - {mark['value']} on {mark['creation_date']}")
                
                # Show sample of students without marks if all shown have marks
                if len(students_with_marks) < 10:
                    students_without_marks = [
                        (sid, student) 
                        for sid, student in journal.students.items() 
                        if not student['marks']
                    ][:10 - len(students_with_marks)]
                    
                    if students_without_marks:
                        print("\nStudents without marks (sample):")
                        for sid, student in students_without_marks:
                            print(f"  {sid}: {student['name']}")

            else:
                print("Unknown command. Available: addmark, list, quit")

    except (KeyboardInterrupt, asyncio.CancelledError):
        await journal.shutdown()
        report_task.cancel()
        simulation_task.cancel()
        logger.info("Application terminated by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        print("\nAn unexpected error occurred. Check logs for details.")