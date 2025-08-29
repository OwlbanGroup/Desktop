import sys
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration


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

    # Initialize revenue tracker
    revenue_tracker = RevenueTracker()
    leader = leadership.Leader(leader_name, style)
    leader.set_revenue_tracker(revenue_tracker)
    team = leadership.Team(leader)

    # Initialize NVIDIA integration
    nvidia_integration = NvidiaIntegration()

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
    print(leader.lead_team())

    decision = input("Enter a decision for the leader to make: ").strip()
    if decision:
        print(leadership.make_decision(team.leader, decision, revenue_tracker))
    else:
        print("No decision entered.")
    
    # Show revenue report
    print("\nRevenue Report:")
    print(revenue_tracker.generate_report())

    # Show NVIDIA GPU status
    show_gpu = input("\nWould you like to see NVIDIA GPU status? (y/n): ").strip().lower()
    if show_gpu in ['y', 'yes']:
        gpu_settings = nvidia_integration.get_gpu_settings()
        print("\nNVIDIA GPU Status and Settings:")
        for key, value in gpu_settings.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    run_interface()
