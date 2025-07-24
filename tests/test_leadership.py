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

    def test_invalid_leader_name(self):
        with self.assertRaises(ValueError):
            leadership.Leader("", leadership.LeadershipStyle.DEMOCRATIC)

    def test_invalid_leadership_style(self):
        with self.assertRaises(ValueError):
            leadership.Leader("Leader", "InvalidStyle")  # type: ignore

    def test_invalid_team_member_name(self):
        with self.assertRaises(ValueError):
            leadership.TeamMember("")

    def test_add_invalid_member(self):
        with self.assertRaises(ValueError):
            self.team.add_member("NotATeamMember")  # type: ignore

    def test_make_decision_empty(self):
        with self.assertRaises(ValueError):
            leadership.make_decision(self.leader, "")

    def test_all_leadership_styles(self):
        for style in leadership.LeadershipStyle:
            leader = leadership.Leader("Leader", style)
            lead_result = leader.lead_team()
            self.assertIn(style.value, lead_result)
            decision_result = leadership.make_decision(leader, "Decision")
            self.assertIn("Decision", decision_result)


if __name__ == "__main__":
    unittest.main()
