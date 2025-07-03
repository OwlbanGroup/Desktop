import unittest
from organizational_leadership import leadership


class TestLeadershipModule(unittest.TestCase):
    def setUp(self):
        self.leader = leadership.Leader("Test Leader", leadership.LeadershipStyle.DEMOCRATIC)
        self.team = leadership.Team(self.leader)
        self.member1 = leadership.TeamMember("Member1", "Developer")
        self.member2 = leadership.TeamMember("Member2", "Designer")
        self.team.add_member(self.member1)
        self.team.add_member(self.member2)

    def test_lead_team(self):
        result = self.leader.lead_team()
        self.assertIn("encourages team participation", result)

    def test_team_status(self):
        status = self.team.team_status()
        self.assertIn("Test Leader", status)
        self.assertIn("Member1", status)
        self.assertIn("Member2", status)

    def test_make_decision(self):
        decision = "Test decision"
        result = leadership.make_decision(self.leader, decision)
        self.assertIn(decision, result)

    def test_team_member_perform_task(self):
        task = "Complete unit tests"
        result = self.member1.perform_task(task)
        self.assertIn(task, result)


if __name__ == "__main__":
    unittest.main()
