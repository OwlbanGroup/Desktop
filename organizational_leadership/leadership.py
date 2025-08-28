"""
Organizational Leadership Module

This module provides classes and functions related to organizational leadership concepts,
including leadership styles, team management, and decision making.
"""

import logging
from enum import Enum
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LeadershipStyle(Enum):
    AUTOCRATIC = "Autocratic"
    DEMOCRATIC = "Democratic"
    TRANSFORMATIONAL = "Transformational"
    LAISSEZ_FAIRE = "Laissez-Faire"
    SERVANT = "Servant"


class Leader:
    """
    Represents a leader with a name and leadership style.
    """

    def __init__(self, name: str, style: LeadershipStyle):
        if not name:
            raise ValueError("Leader name must not be empty")
        if not isinstance(style, LeadershipStyle):
            raise ValueError("Invalid leadership style")
        self.name = name
        self.style = style
        self._revenue_tracker = None

    def set_revenue_tracker(self, revenue_tracker: RevenueTracker):
        self._revenue_tracker = revenue_tracker

    def lead_team(self):
        """
        Simulate leading a team based on the leadership style.
        """
        logger.info(f"{self.name} is leading the team with style {self.style.value}")

        # Log revenue update if tracker set
        if self._revenue_tracker:
            description = f"Team led by {self.name} ({self.style.value})"
            amount = 500.0  # Example fixed revenue impact
            self._revenue_tracker.add_record(description, amount)

        if self.style == LeadershipStyle.AUTOCRATIC:
            return f"{self.name} leads with a strict, top-down approach."
        elif self.style == LeadershipStyle.DEMOCRATIC:
            return f"{self.name} encourages team participation in decision making."
        elif self.style == LeadershipStyle.TRANSFORMATIONAL:
            return f"{self.name} inspires and motivates the team to innovate."
        elif self.style == LeadershipStyle.LAISSEZ_FAIRE:
            return f"{self.name} allows the team to self-manage and make decisions."
        elif self.style == LeadershipStyle.SERVANT:
            return f"{self.name} focuses on serving the needs of the team."
        else:
            return f"{self.name} has an undefined leadership style."


class TeamMember:
    """
    Represents a member of a team.
    """

    def __init__(self, name: str, role: Optional[str] = None):
        if not name:
            raise ValueError("Team member name must not be empty")
        self.name = name
        self.role = role

    def perform_task(self, task: str):
        """
        Simulate performing a task.
        """
        if not task:
            raise ValueError("Task must not be empty")
        logger.info(f"{self.name} is performing task: {task}")
        return f"{self.name} is performing task: {task}"


class Team:
    """
    Represents a team with a leader and members.
    """

    def __init__(self, leader: Leader, members: Optional[List[TeamMember]] = None):
        if not isinstance(leader, Leader):
            raise ValueError("Leader must be an instance of Leader class")
        self.leader = leader
        self.members = members if members is not None else []

    def add_member(self, member: TeamMember):
        """
        Add a member to the team.
        """
        if not isinstance(member, TeamMember):
            raise ValueError("Member must be an instance of TeamMember class")
        self.members.append(member)

    def team_status(self):
        """
        Return a summary of the team's status.
        """
        member_names = ", ".join(member.name for member in self.members)
        logger.info(f"Team led by {self.leader.name} with members: {member_names}")
        return f"Team led by {self.leader.name} with members: {member_names}"


# Import moved to avoid circular import
# from revenue_tracking import RevenueTracker

def make_decision(leader: Leader, decision: str, revenue_tracker=None):
    """
    Simulate a decision-making process based on the leader's style.
    """
    if not isinstance(leader, Leader):
        raise ValueError("Leader must be an instance of Leader class")
    if not decision:
        raise ValueError("Decision must not be empty")

    logger.info(f"{leader.name} is making a decision: {decision}")

    # Log revenue update if tracker provided
    if revenue_tracker:
        description = f"Decision made by {leader.name} ({leader.style.value}): {decision}"
        # Simulate revenue impact amount (example fixed value)
        amount = 1000.0
        revenue_tracker.add_record(description, amount)

    if leader.style == LeadershipStyle.AUTOCRATIC:
        return f"{leader.name} makes a quick, unilateral decision: {decision}"
    elif leader.style == LeadershipStyle.DEMOCRATIC:
        return f"{leader.name} consults the team before deciding: {decision}"
    elif leader.style == LeadershipStyle.TRANSFORMATIONAL:
        return f"{leader.name} inspires the team to embrace the decision: {decision}"
    elif leader.style == LeadershipStyle.LAISSEZ_FAIRE:
        return f"{leader.name} allows the team to decide on: {decision}"
    elif leader.style == LeadershipStyle.SERVANT:
        return f"{leader.name} supports the team in making the decision: {decision}"
    else:
        return f"{leader.name} makes an undefined decision regarding: {decision}"
