"""
Benefits Administration System
Manages employee benefits including health insurance, retirement plans, and other perks
"""

import json
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class BenefitType(Enum):
    HEALTH_INSURANCE = "health_insurance"
    DENTAL_INSURANCE = "dental_insurance"
    VISION_INSURANCE = "vision_insurance"
    LIFE_INSURANCE = "life_insurance"
    RETIREMENT_401K = "retirement_401k"
    RETIREMENT_PENSION = "retirement_pension"
    HSA = "hsa"
    FSA = "fsa"
    DISABILITY_INSURANCE = "disability_insurance"
    PAID_TIME_OFF = "paid_time_off"
    SICK_LEAVE = "sick_leave"
    VACATION = "vacation"

class CoverageLevel(Enum):
    EMPLOYEE_ONLY = "employee_only"
    EMPLOYEE_SPOUSE = "employee_spouse"
    EMPLOYEE_CHILDREN = "employee_children"
    FAMILY = "family"

@dataclass
class BenefitPlan:
    plan_id: str
    name: str
    type: BenefitType
    provider: str
    description: str
    monthly_cost: float
    employee_contribution: float
    employer_contribution: float
    coverage_levels: List[CoverageLevel]
    effective_date: date
    created_at: datetime

@dataclass
class EmployeeBenefit:
    enrollment_id: str
    employee_id: str
    plan_id: str
    coverage_level: CoverageLevel
    enrollment_date: date
    effective_date: date
    status: str  # active, terminated, pending
    employee_monthly_cost: float
    employer_monthly_cost: float
    dependents: List[Dict[str, str]]  # List of dependent info
    created_at: datetime
    updated_at: datetime

class BenefitsManager:
    def __init__(self, plans_file: str = "hr_system/benefit_plans.json",
                 enrollments_file: str = "hr_system/benefit_enrollments.json"):
        self.plans_file = plans_file
        self.enrollments_file = enrollments_file
        self.plans: Dict[str, BenefitPlan] = {}
        self.enrollments: Dict[str, EmployeeBenefit] = {}
        self._load_data()

    def _load_data(self):
        """Load benefits data from files"""
        # Load plans
        try:
            with open(self.plans_file, 'r') as f:
                data = json.load(f)
                for plan_data in data.get('plans', []):
                    plan_data['type'] = BenefitType(plan_data['type'])
                    plan_data['effective_date'] = date.fromisoformat(plan_data['effective_date'])
                    plan_data['created_at'] = datetime.fromisoformat(plan_data['created_at'])
                    plan_data['coverage_levels'] = [CoverageLevel(level) for level in plan_data['coverage_levels']]
                    plan = BenefitPlan(**plan_data)
                    self.plans[plan.plan_id] = plan
        except FileNotFoundError:
            self.plans = {}

        # Load enrollments
        try:
            with open(self.enrollments_file, 'r') as f:
                data = json.load(f)
                for enroll_data in data.get('enrollments', []):
                    enroll_data['coverage_level'] = CoverageLevel(enroll_data['coverage_level'])
                    enroll_data['enrollment_date'] = date.fromisoformat(enroll_data['enrollment_date'])
                    enroll_data['effective_date'] = date.fromisoformat(enroll_data['effective_date'])
                    enroll_data['created_at'] = datetime.fromisoformat(enroll_data['created_at'])
                    enroll_data['updated_at'] = datetime.fromisoformat(enroll_data['updated_at'])
                    enrollment = EmployeeBenefit(**enroll_data)
                    self.enrollments[enrollment.enrollment_id] = enrollment
        except FileNotFoundError:
            self.enrollments = {}

    def _save_plans(self):
        """Save benefit plans to file"""
        data = {
            'plans': [asdict(plan) for plan in self.plans.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert enums and dates for JSON serialization
        for plan_data in data['plans']:
            plan_data['type'] = plan_data['type'].value
            plan_data['effective_date'] = plan_data['effective_date'].isoformat()
            plan_data['created_at'] = plan_data['created_at'].isoformat()
            plan_data['coverage_levels'] = [level.value for level in plan_data['coverage_levels']]

        with open(self.plans_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_enrollments(self):
        """Save benefit enrollments to file"""
        data = {
            'enrollments': [asdict(enrollment) for enrollment in self.enrollments.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert enums and dates for JSON serialization
        for enroll_data in data['enrollments']:
            enroll_data['coverage_level'] = enroll_data['coverage_level'].value
            enroll_data['enrollment_date'] = enroll_data['enrollment_date'].isoformat()
            enroll_data['effective_date'] = enroll_data['effective_date'].isoformat()
            enroll_data['created_at'] = enroll_data['created_at'].isoformat()
            enroll_data['updated_at'] = enroll_data['updated_at'].isoformat()

        with open(self.enrollments_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_benefit_plan(self, plan_data: Dict[str, Any]) -> BenefitPlan:
        """Create a new benefit plan"""
        plan_id = str(uuid.uuid4())

        plan = BenefitPlan(
            plan_id=plan_id,
            name=plan_data['name'],
            type=BenefitType(plan_data['type']),
            provider=plan_data['provider'],
            description=plan_data['description'],
            monthly_cost=plan_data['monthly_cost'],
            employee_contribution=plan_data['employee_contribution'],
            employer_contribution=plan_data['employer_contribution'],
            coverage_levels=[CoverageLevel(level) for level in plan_data['coverage_levels']],
            effective_date=date.fromisoformat(plan_data['effective_date']),
            created_at=datetime.now()
        )

        self.plans[plan_id] = plan
        self._save_plans()
        return plan

    def get_benefit_plan(self, plan_id: str) -> Optional[BenefitPlan]:
        """Get benefit plan by ID"""
        return self.plans.get(plan_id)

    def get_plans_by_type(self, benefit_type: BenefitType) -> List[BenefitPlan]:
        """Get all plans of a specific type"""
        return [plan for plan in self.plans.values() if plan.type == benefit_type]

    def enroll_employee(self, employee_id: str, plan_id: str,
                       coverage_level: CoverageLevel,
                       effective_date: date,
                       dependents: List[Dict[str, str]] = None) -> EmployeeBenefit:
        """Enroll an employee in a benefit plan"""
        if plan_id not in self.plans:
            raise ValueError(f"Benefit plan {plan_id} not found")

        plan = self.plans[plan_id]

        # Calculate costs based on coverage level
        if coverage_level == CoverageLevel.EMPLOYEE_ONLY:
            employee_cost = plan.employee_contribution
            employer_cost = plan.employer_contribution
        elif coverage_level == CoverageLevel.FAMILY:
            employee_cost = plan.employee_contribution * 2.5  # Family rate
            employer_cost = plan.employer_contribution * 2.5
        else:
            employee_cost = plan.employee_contribution * 1.8  # Spouse/Children rate
            employer_cost = plan.employer_contribution * 1.8

        enrollment = EmployeeBenefit(
            enrollment_id=str(uuid.uuid4()),
            employee_id=employee_id,
            plan_id=plan_id,
            coverage_level=coverage_level,
            enrollment_date=date.today(),
            effective_date=effective_date,
            status="active",
            employee_monthly_cost=employee_cost,
            employer_monthly_cost=employer_cost,
            dependents=dependents or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.enrollments[enrollment.enrollment_id] = enrollment
        self._save_enrollments()
        return enrollment

    def get_employee_benefits(self, employee_id: str) -> List[EmployeeBenefit]:
        """Get all benefits for an employee"""
        return [enrollment for enrollment in self.enrollments.values()
                if enrollment.employee_id == employee_id and enrollment.status == "active"]

    def terminate_benefit(self, enrollment_id: str, termination_date: date) -> bool:
        """Terminate a benefit enrollment"""
        if enrollment_id not in self.enrollments:
            return False

        enrollment = self.enrollments[enrollment_id]
        enrollment.status = "terminated"
        enrollment.updated_at = datetime.now()

        self._save_enrollments()
        return True

    def calculate_benefits_cost(self, employee_id: str) -> Dict[str, float]:
        """Calculate total benefits cost for an employee"""
        employee_benefits = self.get_employee_benefits(employee_id)

        total_employee_cost = sum(benefit.employee_monthly_cost for benefit in employee_benefits)
        total_employer_cost = sum(benefit.employer_monthly_cost for benefit in employee_benefits)

        return {
            'employee_monthly_total': total_employee_cost,
            'employer_monthly_total': total_employer_cost,
            'total_monthly_cost': total_employee_cost + total_employer_cost
        }

    def get_benefits_summary(self) -> Dict[str, Any]:
        """Get overall benefits summary"""
        active_enrollments = [e for e in self.enrollments.values() if e.status == "active"]

        total_employees_covered = len(set(e.employee_id for e in active_enrollments))
        total_monthly_cost = sum(e.employee_monthly_cost + e.employer_monthly_cost
                               for e in active_enrollments)

        # Breakdown by benefit type
        type_breakdown = {}
        for enrollment in active_enrollments:
            plan = self.plans.get(enrollment.plan_id)
            if plan:
                benefit_type = plan.type.value
                if benefit_type not in type_breakdown:
                    type_breakdown[benefit_type] = {'count': 0, 'cost': 0}
                type_breakdown[benefit_type]['count'] += 1
                type_breakdown[benefit_type]['cost'] += (enrollment.employee_monthly_cost +
                                                        enrollment.employer_monthly_cost)

        return {
            'total_employees_covered': total_employees_covered,
            'total_monthly_cost': total_monthly_cost,
            'active_enrollments': len(active_enrollments),
            'type_breakdown': type_breakdown
        }

    def get_open_enrollment_plans(self) -> List[BenefitPlan]:
        """Get plans available for open enrollment"""
        return list(self.plans.values())

    def update_benefit_plan(self, plan_id: str, updates: Dict[str, Any]) -> Optional[BenefitPlan]:
        """Update benefit plan information"""
        if plan_id not in self.plans:
            return None

        plan = self.plans[plan_id]

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(plan, key):
                if key == 'type' and value:
                    value = BenefitType(value)
                elif key == 'effective_date' and value:
                    value = date.fromisoformat(value)
                elif key == 'coverage_levels' and isinstance(value, list):
                    value = [CoverageLevel(level) for level in value]

                setattr(plan, key, value)

        self._save_plans()
        return plan
