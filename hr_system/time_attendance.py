"""
Time and Attendance System
Manages employee time tracking, leave requests, and attendance monitoring
"""

import json
import uuid
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class LeaveType(Enum):
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    PERSONAL_LEAVE = "personal_leave"
    MATERNITY_LEAVE = "maternity_leave"
    PATERNITY_LEAVE = "paternity_leave"
    BEREAVEMENT = "bereavement"
    JURY_DUTY = "jury_duty"
    MILITARY_LEAVE = "military_leave"

class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"

class AttendanceStatus(Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"

@dataclass
class TimeEntry:
    entry_id: str
    employee_id: str
    date: date
    clock_in: Optional[time]
    clock_out: Optional[time]
    break_start: Optional[time]
    break_end: Optional[time]
    total_hours: float
    overtime_hours: float
    status: AttendanceStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class LeaveRequest:
    request_id: str
    employee_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: LeaveStatus
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    comments: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class LeaveBalance:
    employee_id: str
    leave_type: LeaveType
    total_days: float
    used_days: float
    pending_days: float
    remaining_days: float
    year: int
    updated_at: datetime

class TimeAttendanceManager:
    def __init__(self, time_entries_file: str = "hr_system/time_entries.json",
                 leave_requests_file: str = "hr_system/leave_requests.json",
                 leave_balances_file: str = "hr_system/leave_balances.json"):
        self.time_entries_file = time_entries_file
        self.leave_requests_file = leave_requests_file
        self.leave_balances_file = leave_balances_file
        self.time_entries: Dict[str, TimeEntry] = {}
        self.leave_requests: Dict[str, LeaveRequest] = {}
        self.leave_balances: Dict[str, LeaveBalance] = {}
        self._load_data()

    def _load_data(self):
        """Load time and attendance data from files"""
        # Load time entries
        try:
            with open(self.time_entries_file, 'r') as f:
                data = json.load(f)
                for entry_data in data.get('entries', []):
                    entry_data['date'] = date.fromisoformat(entry_data['date'])
                    if entry_data.get('clock_in'):
                        entry_data['clock_in'] = time.fromisoformat(entry_data['clock_in'])
                    if entry_data.get('clock_out'):
                        entry_data['clock_out'] = time.fromisoformat(entry_data['clock_out'])
                    if entry_data.get('break_start'):
                        entry_data['break_start'] = time.fromisoformat(entry_data['break_start'])
                    if entry_data.get('break_end'):
                        entry_data['break_end'] = time.fromisoformat(entry_data['break_end'])
                    entry_data['status'] = AttendanceStatus(entry_data['status'])
                    entry_data['created_at'] = datetime.fromisoformat(entry_data['created_at'])
                    entry_data['updated_at'] = datetime.fromisoformat(entry_data['updated_at'])
                    entry = TimeEntry(**entry_data)
                    self.time_entries[entry.entry_id] = entry
        except FileNotFoundError:
            self.time_entries = {}

        # Load leave requests
        try:
            with open(self.leave_requests_file, 'r') as f:
                data = json.load(f)
                for request_data in data.get('requests', []):
                    request_data['leave_type'] = LeaveType(request_data['leave_type'])
                    request_data['start_date'] = date.fromisoformat(request_data['start_date'])
                    request_data['end_date'] = date.fromisoformat(request_data['end_date'])
                    request_data['status'] = LeaveStatus(request_data['status'])
                    request_data['created_at'] = datetime.fromisoformat(request_data['created_at'])
                    request_data['updated_at'] = datetime.fromisoformat(request_data['updated_at'])
                    if request_data.get('approved_at'):
                        request_data['approved_at'] = datetime.fromisoformat(request_data['approved_at'])
                    request = LeaveRequest(**request_data)
                    self.leave_requests[request.request_id] = request
        except FileNotFoundError:
            self.leave_requests = {}

        # Load leave balances
        try:
            with open(self.leave_balances_file, 'r') as f:
                data = json.load(f)
                for balance_data in data.get('balances', []):
                    balance_data['leave_type'] = LeaveType(balance_data['leave_type'])
                    balance_data['updated_at'] = datetime.fromisoformat(balance_data['updated_at'])
                    balance = LeaveBalance(**balance_data)
                    key = f"{balance.employee_id}_{balance.leave_type.value}_{balance.year}"
                    self.leave_balances[key] = balance
        except FileNotFoundError:
            self.leave_balances = {}

    def _save_time_entries(self):
        """Save time entries to file"""
        data = {
            'entries': [asdict(entry) for entry in self.time_entries.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for entry_data in data['entries']:
            entry_data['date'] = entry_data['date'].isoformat()
            entry_data['status'] = entry_data['status'].value
            entry_data['created_at'] = entry_data['created_at'].isoformat()
            entry_data['updated_at'] = entry_data['updated_at'].isoformat()
            if entry_data.get('clock_in'):
                entry_data['clock_in'] = entry_data['clock_in'].isoformat()
            if entry_data.get('clock_out'):
                entry_data['clock_out'] = entry_data['clock_out'].isoformat()
            if entry_data.get('break_start'):
                entry_data['break_start'] = entry_data['break_start'].isoformat()
            if entry_data.get('break_end'):
                entry_data['break_end'] = entry_data['break_end'].isoformat()

        with open(self.time_entries_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_leave_requests(self):
        """Save leave requests to file"""
        data = {
            'requests': [asdict(request) for request in self.leave_requests.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for request_data in data['requests']:
            request_data['leave_type'] = request_data['leave_type'].value
            request_data['start_date'] = request_data['start_date'].isoformat()
            request_data['end_date'] = request_data['end_date'].isoformat()
            request_data['status'] = request_data['status'].value
            request_data['created_at'] = request_data['created_at'].isoformat()
            request_data['updated_at'] = request_data['updated_at'].isoformat()
            if request_data.get('approved_at'):
                request_data['approved_at'] = request_data['approved_at'].isoformat()

        with open(self.leave_requests_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_leave_balances(self):
        """Save leave balances to file"""
        data = {
            'balances': [asdict(balance) for balance in self.leave_balances.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for balance_data in data['balances']:
            balance_data['leave_type'] = balance_data['leave_type'].value
            balance_data['updated_at'] = balance_data['updated_at'].isoformat()

        with open(self.leave_balances_file, 'w') as f:
            json.dump(data, f, indent=2)

    def clock_in(self, employee_id: str, clock_in_time: Optional[time] = None) -> TimeEntry:
        """Clock in an employee"""
        today = date.today()
        clock_in_time = clock_in_time or datetime.now().time()

        # Check if already clocked in today
        existing_entry = self.get_time_entry(employee_id, today)
        if existing_entry and existing_entry.clock_in:
            raise ValueError(f"Employee {employee_id} is already clocked in today")

        entry_id = str(uuid.uuid4())

        entry = TimeEntry(
            entry_id=entry_id,
            employee_id=employee_id,
            date=today,
            clock_in=clock_in_time,
            clock_out=None,
            break_start=None,
            break_end=None,
            total_hours=0.0,
            overtime_hours=0.0,
            status=AttendanceStatus.PRESENT,
            notes=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.time_entries[entry_id] = entry
        self._save_time_entries()
        return entry

    def clock_out(self, employee_id: str, clock_out_time: Optional[time] = None) -> Optional[TimeEntry]:
        """Clock out an employee"""
        today = date.today()
        clock_out_time = clock_out_time or datetime.now().time()

        entry = self.get_time_entry(employee_id, today)
        if not entry or not entry.clock_in:
            return None

        entry.clock_out = clock_out_time
        entry.updated_at = datetime.now()

        # Calculate total hours
        if entry.clock_out and entry.clock_in:
            start_datetime = datetime.combine(entry.date, entry.clock_in)
            end_datetime = datetime.combine(entry.date, entry.clock_out)

            # Subtract break time if applicable
            if entry.break_start and entry.break_end:
                break_duration = datetime.combine(entry.date, entry.break_end) - datetime.combine(entry.date, entry.break_start)
                total_duration = end_datetime - start_datetime - break_duration
            else:
                total_duration = end_datetime - start_datetime

            entry.total_hours = total_duration.total_seconds() / 3600

            # Calculate overtime (over 8 hours)
            if entry.total_hours > 8:
                entry.overtime_hours = entry.total_hours - 8
                entry.total_hours = 8

        self._save_time_entries()
        return entry

    def start_break(self, employee_id: str, break_start_time: Optional[time] = None) -> bool:
        """Start break for an employee"""
        today = date.today()
        break_start_time = break_start_time or datetime.now().time()

        entry = self.get_time_entry(employee_id, today)
        if not entry or not entry.clock_in or entry.clock_out:
            return False

        entry.break_start = break_start_time
        entry.updated_at = datetime.now()
        self._save_time_entries()
        return True

    def end_break(self, employee_id: str, break_end_time: Optional[time] = None) -> bool:
        """End break for an employee"""
        today = date.today()
        break_end_time = break_end_time or datetime.now().time()

        entry = self.get_time_entry(employee_id, today)
        if not entry or not entry.break_start:
            return False

        entry.break_end = break_end_time
        entry.updated_at = datetime.now()
        self._save_time_entries()
        return True

    def get_time_entry(self, employee_id: str, date: date) -> Optional[TimeEntry]:
        """Get time entry for a specific employee and date"""
        for entry in self.time_entries.values():
            if entry.employee_id == employee_id and entry.date == date:
                return entry
        return None

    def get_employee_time_entries(self, employee_id: str, start_date: date,
                                end_date: date) -> List[TimeEntry]:
        """Get time entries for an employee within a date range"""
        return [entry for entry in self.time_entries.values()
                if entry.employee_id == employee_id and start_date <= entry.date <= end_date]

    def submit_leave_request(self, employee_id: str, leave_type: LeaveType,
                           start_date: date, end_date: date, reason: str) -> LeaveRequest:
        """Submit a leave request"""
        # Calculate total days
        total_days = (end_date - start_date).days + 1

        # Adjust for weekends (optional - can be configured)
        weekdays = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                weekdays += 1
            current_date += timedelta(days=1)

        request = LeaveRequest(
            request_id=str(uuid.uuid4()),
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=weekdays,
            reason=reason,
            status=LeaveStatus.PENDING,
            approved_by=None,
            approved_at=None,
            comments=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.leave_requests[request.request_id] = request
        self._save_leave_requests()
        return request

    def approve_leave_request(self, request_id: str, approved_by: str,
                            comments: Optional[str] = None) -> bool:
        """Approve a leave request"""
        if request_id not in self.leave_requests:
            return False

        request = self.leave_requests[request_id]
        request.status = LeaveStatus.APPROVED
        request.approved_by = approved_by
        request.approved_at = datetime.now()
        request.comments = comments
        request.updated_at = datetime.now()

        # Update leave balance
        self._update_leave_balance(request.employee_id, request.leave_type,
                                 request.total_days, datetime.now().year)

        self._save_leave_requests()
        return True

    def deny_leave_request(self, request_id: str, approved_by: str,
                         comments: Optional[str] = None) -> bool:
        """Deny a leave request"""
        if request_id not in self.leave_requests:
            return False

        request = self.leave_requests[request_id]
        request.status = LeaveStatus.DENIED
        request.approved_by = approved_by
        request.approved_at = datetime.now()
        request.comments = comments
        request.updated_at = datetime.now()

        self._save_leave_requests()
        return True

    def get_leave_requests(self, employee_id: Optional[str] = None,
                          status: Optional[LeaveStatus] = None) -> List[LeaveRequest]:
        """Get leave requests with optional filtering"""
        requests = list(self.leave_requests.values())

        if employee_id:
            requests = [r for r in requests if r.employee_id == employee_id]

        if status:
            requests = [r for r in requests if r.status == status]

        return requests

    def initialize_leave_balance(self, employee_id: str, leave_type: LeaveType,
                               total_days: float, year: int) -> LeaveBalance:
        """Initialize leave balance for an employee"""
        key = f"{employee_id}_{leave_type.value}_{year}"

        balance = LeaveBalance(
            employee_id=employee_id,
            leave_type=leave_type,
            total_days=total_days,
            used_days=0.0,
            pending_days=0.0,
            remaining_days=total_days,
            year=year,
            updated_at=datetime.now()
        )

        self.leave_balances[key] = balance
        self._save_leave_balances()
        return balance

    def _update_leave_balance(self, employee_id: str, leave_type: LeaveType,
                            used_days: float, year: int):
        """Update leave balance after approval"""
        key = f"{employee_id}_{leave_type.value}_{year}"

        if key not in self.leave_balances:
            # Initialize with default values if not exists
            self.initialize_leave_balance(employee_id, leave_type, 0, year)

        balance = self.leave_balances[key]
        balance.used_days += used_days
        balance.remaining_days = balance.total_days - balance.used_days - balance.pending_days
        balance.updated_at = datetime.now()

        self._save_leave_balances()

    def get_leave_balance(self, employee_id: str, leave_type: LeaveType,
                         year: int) -> Optional[LeaveBalance]:
        """Get leave balance for an employee"""
        key = f"{employee_id}_{leave_type.value}_{year}"
        return self.leave_balances.get(key)

    def get_employee_leave_balances(self, employee_id: str, year: int) -> List[LeaveBalance]:
        """Get all leave balances for an employee in a year"""
        return [balance for balance in self.leave_balances.values()
                if balance.employee_id == employee_id and balance.year == year]

    def get_attendance_summary(self, employee_id: str, start_date: date,
                             end_date: date) -> Dict[str, Any]:
        """Get attendance summary for an employee"""
        entries = self.get_employee_time_entries(employee_id, start_date, end_date)

        total_hours = sum(entry.total_hours for entry in entries)
        overtime_hours = sum(entry.overtime_hours for entry in entries)
        present_days = len([e for e in entries if e.status == AttendanceStatus.PRESENT])
        absent_days = len([e for e in entries if e.status == AttendanceStatus.ABSENT])
        late_days = len([e for e in entries if e.status == AttendanceStatus.LATE])

        return {
            'total_hours': total_hours,
            'overtime_hours': overtime_hours,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'total_entries': len(entries)
        }

    def get_leave_summary(self, employee_id: Optional[str] = None,
                         year: Optional[int] = None) -> Dict[str, Any]:
        """Get leave summary"""
        year = year or datetime.now().year

        if employee_id:
            balances = self.get_employee_leave_balances(employee_id, year)
            requests = self.get_leave_requests(employee_id)
        else:
            balances = [b for b in self.leave_balances.values() if b.year == year]
            requests = list(self.leave_requests.values())

        total_pending = sum(r.total_days for r in requests
                          if r.status == LeaveStatus.PENDING)
        total_approved = sum(r.total_days for r in requests
                           if r.status == LeaveStatus.APPROVED)

        return {
            'total_pending_days': total_pending,
            'total_approved_days': total_approved,
            'leave_balances': [asdict(b) for b in balances]
        }
