"""
Performance Management System
Handles employee performance reviews, goal setting, and development planning
"""

import json
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class PerformanceRating(Enum):
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"
    MEETS_EXPECTATIONS = "meets_expectations"
    NEEDS_IMPROVEMENT = "needs_improvement"
    BELOW_EXPECTATIONS = "below_expectations"
    OUTSTANDING = "outstanding"

class GoalStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class ReviewStatus(Enum):
    DRAFT = "draft"
    EMPLOYEE_SELF_REVIEW = "employee_self_review"
    MANAGER_REVIEW = "manager_review"
    PEER_REVIEW = "peer_review"
    FINAL_REVIEW = "final_review"
    COMPLETED = "completed"

@dataclass
class PerformanceGoal:
    goal_id: str
    employee_id: str
    title: str
    description: str
    category: str  # e.g., "professional_development", "project_delivery", "skill_acquisition"
    target_date: date
    status: GoalStatus
    progress_percentage: float
    assigned_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

@dataclass
class PerformanceReview:
    review_id: str
    employee_id: str
    reviewer_id: str
    review_period_start: date
    review_period_end: date
    review_type: str  # e.g., "annual", "mid_year", "probation"
    status: ReviewStatus
    overall_rating: Optional[PerformanceRating]
    strengths: List[str]
    areas_for_improvement: List[str]
    goals_achieved: List[str]
    development_needs: List[str]
    reviewer_comments: str
    employee_comments: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

@dataclass
class DevelopmentPlan:
    plan_id: str
    employee_id: str
    review_id: str
    title: str
    objectives: List[str]
    activities: List[Dict[str, str]]  # List of {"activity": str, "timeline": str, "resources": str}
    success_metrics: List[str]
    mentor_id: Optional[str]
    target_completion_date: date
    status: str  # "active", "completed", "cancelled"
    progress_notes: List[Dict[str, Any]]  # List of {"date": str, "note": str, "progress": float}
    created_at: datetime
    updated_at: datetime

class PerformanceManager:
    def __init__(self, goals_file: str = "hr_system/performance_goals.json",
                 reviews_file: str = "hr_system/performance_reviews.json",
                 plans_file: str = "hr_system/development_plans.json"):
        self.goals_file = goals_file
        self.reviews_file = reviews_file
        self.plans_file = plans_file
        self.goals: Dict[str, PerformanceGoal] = {}
        self.reviews: Dict[str, PerformanceReview] = {}
        self.plans: Dict[str, DevelopmentPlan] = {}
        self._load_data()

    def _load_data(self):
        """Load performance data from files"""
        # Load goals
        try:
            with open(self.goals_file, 'r') as f:
                data = json.load(f)
                for goal_data in data.get('goals', []):
                    goal_data['target_date'] = date.fromisoformat(goal_data['target_date'])
                    goal_data['status'] = GoalStatus(goal_data['status'])
                    goal_data['created_at'] = datetime.fromisoformat(goal_data['created_at'])
                    goal_data['updated_at'] = datetime.fromisoformat(goal_data['updated_at'])
                    if goal_data.get('completed_at'):
                        goal_data['completed_at'] = datetime.fromisoformat(goal_data['completed_at'])
                    goal = PerformanceGoal(**goal_data)
                    self.goals[goal.goal_id] = goal
        except FileNotFoundError:
            self.goals = {}

        # Load reviews
        try:
            with open(self.reviews_file, 'r') as f:
                data = json.load(f)
                for review_data in data.get('reviews', []):
                    review_data['review_period_start'] = date.fromisoformat(review_data['review_period_start'])
                    review_data['review_period_end'] = date.fromisoformat(review_data['review_period_end'])
                    review_data['status'] = ReviewStatus(review_data['status'])
                    if review_data.get('overall_rating'):
                        review_data['overall_rating'] = PerformanceRating(review_data['overall_rating'])
                    review_data['created_at'] = datetime.fromisoformat(review_data['created_at'])
                    review_data['updated_at'] = datetime.fromisoformat(review_data['updated_at'])
                    if review_data.get('completed_at'):
                        review_data['completed_at'] = datetime.fromisoformat(review_data['completed_at'])
                    review = PerformanceReview(**review_data)
                    self.reviews[review.review_id] = review
        except FileNotFoundError:
            self.reviews = {}

        # Load development plans
        try:
            with open(self.plans_file, 'r') as f:
                data = json.load(f)
                for plan_data in data.get('plans', []):
                    plan_data['target_completion_date'] = date.fromisoformat(plan_data['target_completion_date'])
                    plan_data['created_at'] = datetime.fromisoformat(plan_data['created_at'])
                    plan_data['updated_at'] = datetime.fromisoformat(plan_data['updated_at'])
                    plan = DevelopmentPlan(**plan_data)
                    self.plans[plan.plan_id] = plan
        except FileNotFoundError:
            self.plans = {}

    def _save_goals(self):
        """Save performance goals to file"""
        data = {
            'goals': [asdict(goal) for goal in self.goals.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for goal_data in data['goals']:
            goal_data['target_date'] = goal_data['target_date'].isoformat()
            goal_data['status'] = goal_data['status'].value
            goal_data['created_at'] = goal_data['created_at'].isoformat()
            goal_data['updated_at'] = goal_data['updated_at'].isoformat()
            if goal_data.get('completed_at'):
                goal_data['completed_at'] = goal_data['completed_at'].isoformat()

        with open(self.goals_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_reviews(self):
        """Save performance reviews to file"""
        data = {
            'reviews': [asdict(review) for review in self.reviews.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for review_data in data['reviews']:
            review_data['review_period_start'] = review_data['review_period_start'].isoformat()
            review_data['review_period_end'] = review_data['review_period_end'].isoformat()
            review_data['status'] = review_data['status'].value
            if review_data.get('overall_rating'):
                review_data['overall_rating'] = review_data['overall_rating'].value
            review_data['created_at'] = review_data['created_at'].isoformat()
            review_data['updated_at'] = review_data['updated_at'].isoformat()
            if review_data.get('completed_at'):
                review_data['completed_at'] = review_data['completed_at'].isoformat()

        with open(self.reviews_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_plans(self):
        """Save development plans to file"""
        data = {
            'plans': [asdict(plan) for plan in self.plans.values()],
            'last_updated': datetime.now().isoformat()
        }
        # Convert for JSON serialization
        for plan_data in data['plans']:
            plan_data['target_completion_date'] = plan_data['target_completion_date'].isoformat()
            plan_data['created_at'] = plan_data['created_at'].isoformat()
            plan_data['updated_at'] = plan_data['updated_at'].isoformat()

        with open(self.plans_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_performance_goal(self, employee_id: str, title: str, description: str,
                              category: str, target_date: date, assigned_by: str) -> PerformanceGoal:
        """Create a new performance goal"""
        goal_id = str(uuid.uuid4())

        goal = PerformanceGoal(
            goal_id=goal_id,
            employee_id=employee_id,
            title=title,
            description=description,
            category=category,
            target_date=target_date,
            status=GoalStatus.NOT_STARTED,
            progress_percentage=0.0,
            assigned_by=assigned_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.goals[goal_id] = goal
        self._save_goals()
        return goal

    def update_goal_progress(self, goal_id: str, progress_percentage: float,
                           notes: Optional[str] = None) -> Optional[PerformanceGoal]:
        """Update goal progress"""
        if goal_id not in self.goals:
            return None

        goal = self.goals[goal_id]
        goal.progress_percentage = progress_percentage
        goal.notes = notes or goal.notes

        if progress_percentage >= 100:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now()
        elif progress_percentage > 0:
            goal.status = GoalStatus.IN_PROGRESS

        goal.updated_at = datetime.now()
        self._save_goals()
        return goal

    def get_employee_goals(self, employee_id: str, status: Optional[GoalStatus] = None) -> List[PerformanceGoal]:
        """Get goals for an employee"""
        goals = [goal for goal in self.goals.values() if goal.employee_id == employee_id]

        if status:
            goals = [goal for goal in goals if goal.status == status]

        return goals

    def create_performance_review(self, employee_id: str, reviewer_id: str,
                                review_period_start: date, review_period_end: date,
                                review_type: str) -> PerformanceReview:
        """Create a new performance review"""
        review_id = str(uuid.uuid4())

        review = PerformanceReview(
            review_id=review_id,
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            review_period_start=review_period_start,
            review_period_end=review_period_end,
            review_type=review_type,
            status=ReviewStatus.DRAFT,
            overall_rating=None,
            strengths=[],
            areas_for_improvement=[],
            goals_achieved=[],
            development_needs=[],
            reviewer_comments="",
            employee_comments=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.reviews[review_id] = review
        self._save_reviews()
        return review

    def update_review_content(self, review_id: str, updates: Dict[str, Any]) -> Optional[PerformanceReview]:
        """Update review content"""
        if review_id not in self.reviews:
            return None

        review = self.reviews[review_id]

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(review, key) and key not in ['review_id', 'created_at']:
                if key == 'overall_rating' and value:
                    value = PerformanceRating(value)
                elif key == 'status' and value:
                    value = ReviewStatus(value)
                elif key in ['review_period_start', 'review_period_end'] and value:
                    value = date.fromisoformat(value)

                setattr(review, key, value)

        review.updated_at = datetime.now()

        # Mark as completed if final review is done
        if review.status == ReviewStatus.FINAL_REVIEW and review.overall_rating:
            review.status = ReviewStatus.COMPLETED
            review.completed_at = datetime.now()

        self._save_reviews()
        return review

    def get_employee_reviews(self, employee_id: str, review_type: Optional[str] = None) -> List[PerformanceReview]:
        """Get reviews for an employee"""
        reviews = [review for review in self.reviews.values() if review.employee_id == employee_id]

        if review_type:
            reviews = [review for review in reviews if review.review_type == review_type]

        return reviews

    def get_pending_reviews(self, reviewer_id: str) -> List[PerformanceReview]:
        """Get pending reviews for a reviewer"""
        return [review for review in self.reviews.values()
                if review.reviewer_id == reviewer_id and review.status != ReviewStatus.COMPLETED]

    def create_development_plan(self, employee_id: str, review_id: str, title: str,
                              objectives: List[str], activities: List[Dict[str, str]],
                              success_metrics: List[str], target_completion_date: date,
                              mentor_id: Optional[str] = None) -> DevelopmentPlan:
        """Create a development plan"""
        plan_id = str(uuid.uuid4())

        plan = DevelopmentPlan(
            plan_id=plan_id,
            employee_id=employee_id,
            review_id=review_id,
            title=title,
            objectives=objectives,
            activities=activities,
            success_metrics=success_metrics,
            mentor_id=mentor_id,
            target_completion_date=target_completion_date,
            status="active",
            progress_notes=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.plans[plan_id] = plan
        self._save_plans()
        return plan

    def add_progress_note(self, plan_id: str, note: str, progress: float) -> bool:
        """Add progress note to development plan"""
        if plan_id not in self.plans:
            return False

        plan = self.plans[plan_id]
        progress_note = {
            'date': datetime.now().isoformat(),
            'note': note,
            'progress': progress
        }

        plan.progress_notes.append(progress_note)
        plan.updated_at = datetime.now()

        # Update status based on progress
        if progress >= 100:
            plan.status = "completed"
        elif progress > 0:
            plan.status = "active"

        self._save_plans()
        return True

    def get_employee_development_plans(self, employee_id: str, status: Optional[str] = None) -> List[DevelopmentPlan]:
        """Get development plans for an employee"""
        plans = [plan for plan in self.plans.values() if plan.employee_id == employee_id]

        if status:
            plans = [plan for plan in plans if plan.status == status]

        return plans

    def get_performance_summary(self, employee_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for an employee"""
        goals = self.get_employee_goals(employee_id)
        reviews = self.get_employee_reviews(employee_id)
        plans = self.get_employee_development_plans(employee_id)

        # Calculate goal completion rate
        completed_goals = len([g for g in goals if g.status == GoalStatus.COMPLETED])
        total_goals = len(goals)
        goal_completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0

        # Get latest review rating
        latest_review = None
        if reviews:
            latest_review = max(reviews, key=lambda r: r.created_at)

        # Active development plans
        active_plans = len([p for p in plans if p.status == "active"])

        return {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'goal_completion_rate': goal_completion_rate,
            'total_reviews': len(reviews),
            'latest_review_rating': latest_review.overall_rating.value if latest_review and latest_review.overall_rating else None,
            'active_development_plans': active_plans,
            'goals': [asdict(g) for g in goals],
            'reviews': [asdict(r) for r in reviews],
            'development_plans': [asdict(p) for p in plans]
        }

    def get_team_performance_summary(self, manager_id: str) -> Dict[str, Any]:
        """Get performance summary for all direct reports"""
        # This would need integration with employee management system to get direct reports
        # For now, return placeholder
        return {
            'total_direct_reports': 0,
            'average_goal_completion': 0.0,
            'reviews_due': 0,
            'development_plans_active': 0
        }

    def get_upcoming_reviews(self, days_ahead: int = 30) -> List[PerformanceReview]:
        """Get reviews that are due within specified days"""
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        return [review for review in self.reviews.values()
                if review.review_period_end <= future_date and review.status != ReviewStatus.COMPLETED]

    def get_overdue_goals(self) -> List[PerformanceGoal]:
        """Get goals that are past their target date"""
        today = date.today()

        return [goal for goal in self.goals.values()
                if goal.target_date < today and goal.status != GoalStatus.COMPLETED]
