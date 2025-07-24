from organizational_leadership import leadership
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Organizational Leadership CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--leader-name",
        type=str,
        default="Alice",
        help="Name of the leader",
    )
    parser.add_argument(
        "--leadership-style",
        type=str,
        default="DEMOCRATIC",
        choices=[style.name for style in leadership.LeadershipStyle],
        help="Leadership style",
    )
    parser.add_argument(
        "--team-members",
        nargs="*",
        default=["Bob:Developer", "Charlie:Designer"],
        help="List of team members in 'Name:Role' format",
    )
    parser.add_argument(
        "--decision",
        type=str,
        default="Implement new project strategy",
        help="Decision to be made by the leader",
    )

    args = parser.parse_args()

    style = leadership.LeadershipStyle[args.leadership_style.upper()]

    leader = leadership.Leader(args.leader_name, style)
    team = leadership.Team(leader)

    for member_str in args.team_members:
        if ":" in member_str:
            name, role = member_str.split(":", 1)
        else:
            name, role = member_str, None
        try:
            member = leadership.TeamMember(name, role)
            team.add_member(member)
        except ValueError as e:
            print(f"Error adding team member: {e}")
            return

    print(leader.lead_team())
    print(team.team_status())
    print(leadership.make_decision(leader, args.decision))


if __name__ == "__main__":
    main()
