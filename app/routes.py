from flask import Blueprint, request, jsonify
from .models import db, Team

# Define the blueprint for routes
bp = Blueprint('main', __name__)

# Home route
@bp.route('/')
def home():
    return "Football Tournament System Home"

# Route to create a team
@bp.route('/teams', methods=['POST'])
def create_team():
    # Get the data sent with the POST request
    data = request.get_json()

    # Extract name and founded date from the received JSON
    team_name = data.get('name')
    team_founded = data.get('founded')

    # Check if the required data exists
    if not team_name or not team_founded:
        return jsonify({'error': 'Missing data'}), 400

    # Create a new team object
    new_team = Team(name=team_name, founded=team_founded)

    # Add the new team to the database session and commit
    db.session.add(new_team)
    db.session.commit()

    # Return a success message and the created team info
    return jsonify({
        'message': 'Team created',
        'team': {
            'id': new_team.id,
            'name': new_team.name,
            'founded': new_team.founded
        }
    }), 201
# Route to fetch all teams
@bp.route('/teams', methods=['GET'])
def get_teams():
    # Query all teams from the database
    teams = Team.query.all()

    # Prepare a list of teams to send in the response
    teams_list = []
    for team in teams:
        teams_list.append({
            'id': team.id,
            'name': team.name,
            'founded': team.founded
        })

    # Return the teams as a JSON response
    return jsonify({'teams': teams_list})
