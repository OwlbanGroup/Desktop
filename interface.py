import sys
from organizational_leadership import leadership


def run_interface():
    print("Welcome to the Organizational Leadership CLI Interface")
    leader_name = input("Enter leader name: ").strip()
    print("Select leadership style:")
    for style in leadership.LeadershipStyle:
        print(f"- {style.name}")
    style_input = input("Enter leadership style: ").strip().upper()
    if style_input not in leadership.LeadershipStyle.__members__:
        print(f"Invalid leadership style: {style_input}")
        sys.exit(1)
    style = leadership.LeadershipStyle[style_input]

    team = leadership.Team(leadership.Leader(leader_name, style))

    while True:
        member_input = input("Add team member (format: Name:Role) or press Enter to finish: ").strip()
        if not member_input:
            break
        if ":" in member_input:
            name, role = member_input.split(":", 1)
        else:
            name, role = member_input, None
        try:
            member = leadership.TeamMember(name.strip(), role.strip() if role else None)
            team.add_member(member)
        except ValueError as e:
            print(f"Error adding team member: {e}")
            continue

    print("\nTeam Summary:")
    print(team.team_status())

    decision = input("Enter a decision for the leader to make: ").strip()
    if decision:
        print(leadership.make_decision(team.leader, decision))
    else:
        print("No decision entered.")


if __name__ == "__main__":
    run_interface()
