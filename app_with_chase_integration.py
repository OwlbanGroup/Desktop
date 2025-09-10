from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration_fixed import NvidiaIntegration
import argparse
from flask import Flask
import importlib.util
import sys
import os

# Add the OSCAR-BROOME-REVENUE directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE'))

# Import chase_mortgage using importlib
spec = importlib.util.spec_from_file_location("chase_mortgage", os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE', 'earnings_dashboard', 'chase_mortgage.py'))
chase_mortgage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chase_mortgage)

app = Flask(__name__)
app.register_blueprint(chase_mortgage.router, url_prefix='/chase-mortgage')

# Import chase_auto_finance using importlib
spec_auto = importlib.util.spec_from_file_location("chase_auto_finance", os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE', 'earnings_dashboard', 'chase_auto_finance.py'))
chase_auto_finance = importlib.util.module_from_spec(spec_auto)
spec_auto.loader.exec_module(chase_auto_finance)

app.register_blueprint(chase_auto_finance.router, url_prefix='/chase-auto-finance')

# Import chase_credit_cards using importlib
spec_credit = importlib.util.spec_from_file_location("chase_credit_cards", os.path.join(os.getcwd(), 'OSCAR-BROOME-REVENUE', 'earnings_dashboard', 'chase_credit_cards.py'))
chase_credit_cards = importlib.util.module_from_spec(spec_credit)
spec_credit.loader.exec_module(chase_credit_cards)

app.register_blueprint(chase_credit_cards.router, url_prefix='/chase-credit-cards')

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
    parser.add_argument(
        "--show-gpu-status",
        action="store_true",
        help="Show NVIDIA GPU status and settings",
    )

    args = parser.parse_args()

    style = leadership.LeadershipStyle[args.leadership_style.upper()]

    leader = leadership.Leader(args.leader_name, style)
    team = leadership.Team(leader)

    # Instantiate RevenueTracker
    revenue_tracker = RevenueTracker()
    # Set revenue tracker in leader
    leader.set_revenue_tracker(revenue_tracker)

    # Instantiate NvidiaIntegration singleton
    nvidia_integration = NvidiaIntegration()

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
    print(leadership.make_decision(leader, args.decision, revenue_tracker))

    if args.show_gpu_status:
        gpu_settings = nvidia_integration.get_gpu_settings()
        print("\nNVIDIA GPU Status and Settings:")
        for key, value in gpu_settings.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # No arguments provided, run Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # Arguments provided, run CLI
        main()
