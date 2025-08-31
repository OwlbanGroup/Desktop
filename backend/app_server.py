from flask import Flask, send_from_directory, jsonify, request
from organizational_leadership import leadership
from revenue_tracking import RevenueTracker
from nvidia_integration import NvidiaIntegration
import os
import subprocess

app = Flask(__name__, static_folder='../frontend')

# Initialize components
revenue_tracker = RevenueTracker()
nvidia_integration = NvidiaIntegration()

@app.route('/api/leadership/lead_team', methods=['POST'])
def lead_team():
    data = request.json
    leader_name = data.get('leader_name', 'Alice')
    leadership_style = data.get('leadership_style', 'DEMOCRATIC').upper()
    team_members = data.get('team_members', ['Bob:Developer', 'Charlie:Designer'])

    style = leadership.LeadershipStyle[leadership_style]
    leader = leadership.Leader(leader_name, style)
    leader.set_revenue_tracker(revenue_tracker)
    team = leadership.Team(leader)

    for member_str in team_members:
        if ':' in member_str:
            name, role = member_str.split(':', 1)
        else:
            name, role = member_str, None
        member = leadership.TeamMember(name, role)
        team.add_member(member)

    lead_result = leader.lead_team()
    team_status = team.team_status()

    return jsonify({
        'lead_result': lead_result,
        'team_status': team_status
    })

@app.route('/api/leadership/make_decision', methods=['POST'])
def make_decision():
    data = request.json
    leader_name = data.get('leader_name', 'Alice')
    leadership_style = data.get('leadership_style', 'DEMOCRATIC').upper()
    decision = data.get('decision', 'Implement new project strategy')

    style = leadership.LeadershipStyle[leadership_style]
    leader = leadership.Leader(leader_name, style)
    leader.set_revenue_tracker(revenue_tracker)

    decision_result = leadership.make_decision(leader, decision, revenue_tracker)

    return jsonify({
        'decision_result': decision_result
    })

@app.route('/api/gpu/status', methods=['GET'])
def gpu_status():
    gpu_settings = nvidia_integration.get_gpu_settings()
    return jsonify(gpu_settings)

@app.route('/api/earnings', methods=['GET'])
def earnings_data():
    # Proxy or integrate with OSCAR-BROOME-REVENUE API here
    # For now, serve static files or implement backend logic
    return jsonify({"message": "Earnings data API placeholder"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
