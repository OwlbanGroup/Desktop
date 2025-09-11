"""
Employee Management System
Handles employee lifecycle, records, and organizational structure
"""

import json
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class EmploymentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"

class EmployeeRole(Enum):
    EXECUTIVE = "executive"
    MANAGER = "manager"
    SPECIALIST = "specialist"
    ANALYST = "analyst"
    ADMINISTRATOR = "administrator"
    INTERN = "intern"

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

@dataclass
class EmergencyContact:
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None

@dataclass
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    hire_date: date
    department: str
    position: str
    role: EmployeeRole
    manager_id: Optional[str]
    salary: float
    status: EmploymentStatus
    address: Address
    emergency_contact: EmergencyContact
    ssn: str  # Last 4 digits only for security
    date_of_birth: date
    created_at: datetime
    updated_at: datetime
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['hire_date'] = self.hire_date.isoformat()
        data['date_of_birth'] = self.date_of_birth.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.termination_date:
            data['termination_date'] = self.termination_date.isoformat()
        data['role'] = self.role.value
        data['status'] = self.status.value
        return data

class EmployeeManager:
    def __init__(self, data_file: str = "hr_system/employee_data.json"):
        self.data_file = data_file
        self.employees: Dict[str, Employee] = {}
        self._load_data()

    def _load_data(self):
        """Load employee data from file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for emp_data in data.get('employees', []):
                    emp_data['hire_date'] = date.fromisoformat(emp_data['hire_date'])
                    emp_data['date_of_birth'] = date.fromisoformat(emp_data['date_of_birth'])
                    emp_data['created_at'] = datetime.fromisoformat(emp_data['created_at'])
                    emp_data['updated_at'] = datetime.fromisoformat(emp_data['updated_at'])
                    if emp_data.get('termination_date'):
                        emp_data['termination_date'] = date.fromisoformat(emp_data['termination_date'])
                    emp_data['role'] = EmployeeRole(emp_data['role'])
                    emp_data['status'] = EmploymentStatus(emp_data['status'])
                    emp_data['address'] = Address(**emp_data['address'])
                    emp_data['emergency_contact'] = EmergencyContact(**emp_data['emergency_contact'])
                    employee = Employee(**emp_data)
                    self.employees[employee.employee_id] = employee
        except FileNotFoundError:
            self.employees = {}

    def _save_data(self):
        """Save employee data to file"""
        data = {
            'employees': [emp.to_dict() for emp in self.employees.values()],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Create a new employee record"""
        employee_id = str(uuid.uuid4())

        # Convert date strings to date objects
        hire_date = date.fromisoformat(employee_data['hire_date'])
        dob = date.fromisoformat(employee_data['date_of_birth'])

        employee = Employee(
            employee_id=employee_id,
            first_name=employee_data['first_name'],
            last_name=employee_data['last_name'],
            email=employee_data['email'],
            phone=employee_data['phone'],
            hire_date=hire_date,
            department=employee_data['department'],
            position=employee_data['position'],
            role=EmployeeRole(employee_data['role']),
            manager_id=employee_data.get('manager_id'),
            salary=employee_data['salary'],
            status=EmploymentStatus.ACTIVE,
            address=Address(**employee_data['address']),
            emergency_contact=EmergencyContact(**employee_data['emergency_contact']),
            ssn=employee_data['ssn'],  # Should be last 4 digits only
            date_of_birth=dob,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.employees[employee_id] = employee
        self._save_data()
        return employee

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.employees.get(employee_id)

    def update_employee(self, employee_id: str, updates: Dict[str, Any]) -> Optional[Employee]:
        """Update employee information"""
        if employee_id not in self.employees:
            return None

        employee = self.employees[employee_id]

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(employee, key) and key not in ['employee_id', 'created_at']:
                if key in ['hire_date', 'date_of_birth', 'termination_date'] and value:
                    value = date.fromisoformat(value)
                elif key == 'role' and value:
                    value = EmployeeRole(value)
                elif key == 'status' and value:
                    value = EmploymentStatus(value)
                elif key == 'address' and isinstance(value, dict):
                    value = Address(**value)
                elif key == 'emergency_contact' and isinstance(value, dict):
                    value = EmergencyContact(**value)

                setattr(employee, key, value)

        employee.updated_at = datetime.now()
        self._save_data()
        return employee

    def terminate_employee(self, employee_id: str, termination_date: date,
                          reason: str) -> bool:
        """Terminate an employee"""
        if employee_id not in self.employees:
            return False

        employee = self.employees[employee_id]
        employee.status = EmploymentStatus.TERMINATED
        employee.termination_date = termination_date
        employee.termination_reason = reason
        employee.updated_at = datetime.now()

        self._save_data()
        return True

    def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get all employees in a department"""
        return [emp for emp in self.employees.values()
                if emp.department == department and emp.status == EmploymentStatus.ACTIVE]

    def get_employees_by_manager(self, manager_id: str) -> List[Employee]:
        """Get all employees reporting to a manager"""
        return [emp for emp in self.employees.values()
                if emp.manager_id == manager_id and emp.status == EmploymentStatus.ACTIVE]

    def get_organizational_hierarchy(self) -> Dict[str, List[str]]:
        """Get organizational hierarchy as manager -> direct reports"""
        hierarchy = {}
        for emp in self.employees.values():
            if emp.status == EmploymentStatus.ACTIVE and emp.manager_id:
                if emp.manager_id not in hierarchy:
                    hierarchy[emp.manager_id] = []
                hierarchy[emp.manager_id].append(emp.employee_id)
        return hierarchy

    def get_employee_count_by_department(self) -> Dict[str, int]:
        """Get employee count by department"""
        counts = {}
        for emp in self.employees.values():
            if emp.status == EmploymentStatus.ACTIVE:
                counts[emp.department] = counts.get(emp.department, 0) + 1
        return counts

    def search_employees(self, query: str) -> List[Employee]:
        """Search employees by name, email, or position"""
        query = query.lower()
        results = []
        for emp in self.employees.values():
            if (query in emp.first_name.lower() or
                query in emp.last_name.lower() or
                query in emp.email.lower() or
                query in emp.position.lower() or
                query in emp.department.lower()):
                results.append(emp)
        return results
