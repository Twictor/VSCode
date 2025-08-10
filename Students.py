import asyncio
import aiosmtplib
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import signal
import sys

# Configuration
STORAGE_FILE_NAME = "students.json"
EMAIL_CONFIG = {
    'sender': 'reports@digitaljournal.com',
    'password': 'your_email_password',
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'recipient': 'admin@digitaljournal.com'
}

class AsyncRepository:
    def __init__(self, filename: str = STORAGE_FILE_NAME):
        self.filename = filename
        self.students: Dict[int, Dict[str, Any]] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.running = True
        self._load_lock = asyncio.Lock()
        self._save_lock = asyncio.Lock()
        asyncio.create_task(self._initialize())

    async def _initialize(self):
        await self._ensure_file_exists()
        await self._load_students()
        asyncio.create_task(self._schedule_reports())

    async def _ensure_file_exists(self):
        if not await asyncio.get_event_loop().run_in_executor(
            self._executor, Path(self.filename).exists
        ):
            await self._save_students()

    async def _load_students(self):
        async with self._load_lock:
            try:
                def read_file():
                    with open(self.filename, 'r') as file:
                        return json.load(file)
                
                data = await asyncio.get_event_loop().run_in_executor(
                    self._executor, read_file
                )
                
                # Convert legacy format if needed
                for student_id, student in data.items():
                    if isinstance(student.get('marks'), list) and student['marks'] and isinstance(student['marks'][0], int):
                        student['marks'] = [{
                            'value': mark, 
                            'date': datetime.now().isoformat()
                        } for mark in student['marks']]
                
                self.students = {int(k): v for k, v in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                self.students = {}

    async def _save_students(self):
        async with self._save_lock:
            def write_file():
                with open(self.filename, 'w') as file:
                    json.dump(self.students, file, indent=2)
            
            await asyncio.get_event_loop().run_in_executor(
                self._executor, write_file
            )

    async def add_student(self, student: Dict[str, Any]) -> Optional[int]:
        if not student.get('name'):
            return None

        new_id = max(self.students.keys()) + 1 if self.students else 1
        self.students[new_id] = {
            'name': student['name'],
            'marks': student.get('marks', []),
            'info': student.get('info', '')
        }
        await self._save_students()
        return new_id

    async def add_mark(self, id_: int, mark: int) -> bool:
        if id_ not in self.students:
            return False

        mark_data = {
            'value': mark,
            'date': datetime.now().isoformat()
        }

        if 'marks' not in self.students[id_]:
            self.students[id_]['marks'] = []
        
        self.students[id_]['marks'].append(mark_data)
        await self._save_students()
        return True

    async def get_daily_average(self, date: datetime) -> float:
        total = 0
        count = 0
        
        for student in self.students.values():
            for mark in student.get('marks', []):
                try:
                    mark_date = datetime.fromisoformat(mark['date'])
                    if mark_date.date() == date.date():
                        total += mark['value']
                        count += 1
                except (ValueError, KeyError):
                    continue
        
        return round(total / count, 2) if count > 0 else 0.0

    async def _send_email(self, subject: str, body: str):
        message = aiosmtplib.email.message.EmailMessage()
        message["From"] = EMAIL_CONFIG['sender']
        message["To"] = EMAIL_CONFIG['recipient']
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=EMAIL_CONFIG['smtp_server'],
                port=EMAIL_CONFIG['smtp_port'],
                username=EMAIL_CONFIG['sender'],
                password=EMAIL_CONFIG['password'],
                use_tls=True
            )
            print(f"Email sent: {subject}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    async def _schedule_reports(self):
        while self.running:
            now = datetime.now()
            
            # Daily report at 23:55
            if now.hour == 23 and now.minute >= 55:
                avg = await self.get_daily_average(now)
                await self._send_email(
                    "Daily Average Mark Report",
                    f"Today's average mark: {avg}"
                )
                await asyncio.sleep(60)  # Prevent multiple sends
            
            # Monthly report on 1st day at 00:05
            elif now.day == 1 and now.hour == 0 and now.minute >= 5:
                await self._send_email(
                    "Monthly Student Report",
                    f"Total students: {len(self.students)}"
                )
                await asyncio.sleep(60)
            
            await asyncio.sleep(10)

    async def shutdown(self):
        self.running = False
        await self._save_students()
        self._executor.shutdown()

async def main():
    repo = AsyncRepository()
    
    # Signal handling
    def signal_handler():
        asyncio.create_task(repo.shutdown())
    
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    
    # Command loop
    while repo.running:
        command = input("\nEnter command: ").strip().lower()
        
        if command == "quit":
            await repo.shutdown()
            print("Goodbye!")
            break
        elif command == "addmark":
            try:
                student_id = int(input("Student ID: "))
                mark = int(input("Mark: "))
                if await repo.add_mark(student_id, mark):
                    print("Mark added")
                else:
                    print("Failed to add mark")
            except ValueError:
                print("Invalid input")
        # Add other command handlers...

if __name__ == "__main__":
    asyncio.run(main())