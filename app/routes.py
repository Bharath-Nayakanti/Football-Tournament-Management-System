from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash, session, send_from_directory
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Team, User, League, Fixture, Player, Lineup , LineupPlayer
from datetime import timedelta
from datetime import date
from sqlalchemy import and_
from app.predictors.IPL.IPLWPredictor import IPLPredictor
from functools import wraps
from flask import abort
from werkzeug.utils import secure_filename
from .highlight_generator.process_highlights import generate_highlights
import os
import uuid

tasks = {}

bp = Blueprint('main', __name__)

# Authentication Routes (unchanged)
@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not registered', 'error')
        elif not user.check_password(password):
            flash('Incorrect password', 'error')
        else:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        
        return redirect(url_for('main.login'))
    
    return render_template('login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                flash('Username already exists', 'error')
            if existing_user.email == email:
                flash('Email already registered', 'error')
            return render_template('signup.html', 
                               username=username,
                               email=email)

        if not all([username, email, password]):
            flash('Please fill in all fields', 'error')
            return render_template('signup.html',
                               username=username,
                               email=email)

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
            return render_template('signup.html',
                               username=username,
                               email=email)

    return render_template('signup.html')

@bp.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('main.login'))

# League Management Routes
@bp.route('/league-management')
def league_management():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    return render_template('leagues.html')

@bp.route('/leagues', methods=['GET'])
def get_leagues():
    leagues = League.query.all()
    leagues_data = [{
        'id': league.id,
        'name': league.name,
        'description': league.description,
        'start_date': league.start_date.strftime('%Y-%m-%d'),
        'end_date': league.end_date.strftime('%Y-%m-%d')
    } for league in leagues]
    return jsonify(leagues_data), 200

@bp.route('/leagues', methods=['POST'])
def create_league():
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([name, start_date, end_date]):
        return jsonify({'error': 'Name, start date, and end date are required'}), 400

    if League.query.filter(db.func.lower(League.name) == name.lower()).first():
        return jsonify({'error': 'League name already exists'}), 400

    try:
        new_league = League(
            name=name,
            description=description,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date()
        )
        db.session.add(new_league)
        db.session.commit()
        return jsonify({'message': 'League created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@bp.route('/leagues/<int:league_id>', methods=['DELETE'])
def delete_league(league_id):
    try:
        league = League.query.get_or_404(league_id)
        Team.query.filter_by(league_id=league_id).delete()
        db.session.delete(league)
        db.session.commit()
        return jsonify({'message': 'League deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# New Separate Page Routes
@bp.route('/league/<int:league_id>')
def league_detail(league_id):  # Changed from league_hub to league_detail
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    return render_template('league_detail.html', league=league)

@bp.route('/league/<int:league_id>/teams')
def league_teams(league_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    teams = Team.query.filter_by(league_id=league.id).all()
    return render_template('league_teams.html', league=league, teams=teams)

@bp.route('/league/<int:league_id>/teams/add', methods=['POST'])
def add_team(league_id):
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    team_name = request.form['name'].strip()
    coach = request.form['coach'].strip()

    if not team_name or not coach:
        flash('All fields are required.', 'error')
        return redirect(url_for('main.team_management', league_id=league.id))

    existing_team = Team.query.filter(
        db.func.lower(Team.name) == team_name.lower(),
        Team.league_id == league_id
    ).first()

    if existing_team:
        flash(f'Team "{team_name}" already exists in this league.', 'error')
        return redirect(url_for('main.team_management', league_id=league.id))

    try:
        new_team = Team(name=team_name, coach=coach, league_id=league.id)
        db.session.add(new_team)
        db.session.commit()
        flash('Team added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to add team. Please try again.', 'error')

    return redirect(url_for('main.team_management', league_id=league.id))

@bp.route('/league/<int:league_id>/teams/<int:team_id>/delete', methods=['POST'])
def delete_team(league_id, team_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('main.team_management', league_id=league_id))

@bp.route('/league/<int:league_id>/fixtures')
def league_fixtures(league_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    fixtures = Fixture.query.filter_by(league_id=league.id).order_by(Fixture.date).all()
    return render_template('league_fixtures.html', league=league, fixtures=fixtures)

@bp.route('/league/<int:league_id>/fixtures/generate', methods=['POST'])
def generate_league_fixtures(league_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    league = League.query.get_or_404(league_id)
    data = request.get_json()
    matches_per_day = data.get('matches_per_day', 2)
    
    try:
        matches_per_day = int(matches_per_day)
        if matches_per_day < 1:
            raise ValueError("Matches per day must be at least 1")
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid matches_per_day value'}), 400
    
    try:
        Fixture.query.filter_by(league_id=league_id, stage='group').delete()
        fixtures = league.generate_fixtures(matches_per_day)
        db.session.add_all(fixtures)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(fixtures)} fixtures',
            'count': len(fixtures)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Endpoints (unchanged)
@bp.route('/leagues/<int:league_id>/teams', methods=['GET'])
def api_get_teams(league_id):
    teams = Team.query.filter_by(league_id=league_id).all()
    teams_data = [{
        'id': team.id,
        'name': team.name,
        'coach': team.coach
    } for team in teams]
    return jsonify(teams_data), 200

@bp.route('/leagues/<int:league_id>/fixtures', methods=['GET'])
def api_get_fixtures(league_id):
    fixtures = Fixture.query.filter_by(league_id=league_id).order_by(Fixture.date).all()
    fixtures_data = [{
        'id': f.id,
        'date': f.date.isoformat(),
        'home_team': f.home_team.name,
        'away_team': f.away_team.name,
        'home_score': f.home_score,
        'away_score': f.away_score,
        'status': f.status,
        'stage': f.stage
    } for f in fixtures]
    return jsonify(fixtures_data), 200
@bp.route('/league/<int:league_id>/fixtures/<int:fixture_id>/status', methods=['PATCH'])
def update_fixture_status(league_id, fixture_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Pending', 'Completed']:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        fixture = Fixture.query.filter_by(id=fixture_id, league_id=league_id).first_or_404()
        fixture.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/league/<int:league_id>/fixtures/<int:fixture_id>/score', methods=['PATCH'])
def update_fixture_score(league_id, fixture_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    home_score = data.get('home_score')
    away_score = data.get('away_score')
    
    try:
        fixture = Fixture.query.filter_by(id=fixture_id, league_id=league_id).first_or_404()
        fixture.home_score = home_score
        fixture.away_score = away_score
        fixture.status = 'Completed'  # Automatically mark as completed when score is saved
        db.session.commit()
        return jsonify({'success': True, 'message': 'Score updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
@bp.route('/league/<int:league_id>/leaderboard')
def league_leaderboard(league_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    standings = league.calculate_standings()
    return render_template('league_leaderboard.html', 
                         league=league,
                         standings=standings)
@bp.route('/league/<int:league_id>/team-management')
def team_management(league_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    league = League.query.get_or_404(league_id)
    teams = Team.query.filter_by(league_id=league.id).all()
    return render_template('team_management.html', league=league, teams=teams)

# Add these new routes to your existing routes.py

@bp.route('/sports-predictions')
def sports_predictions():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))
    return render_template('sports_predictions.html')

@bp.route('/ipl-prediction')
def ipl_prediction():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    predictor = IPLPredictor()
    teams = sorted(predictor.current_teams)
    venues = sorted(predictor.venues)

    return render_template('ipl_prediction.html', teams=teams, venues=venues)

@bp.route('/predict', methods=['POST'])
def predict():
    team1 = request.form['team1']
    team2 = request.form['team2']
    venue = request.form['venue']
    toss_winner = request.form['toss_winner']
    toss_decision = request.form['toss_decision']

    match_data = {
        'team1': team1,
        'team2': team2,
        'venue': venue,
        'toss_winner': toss_winner,
        'toss_decision': toss_decision
    }

    predictor = IPLPredictor()
    probabilities = predictor.predict_match(match_data)

    # Get favorite team in Python instead of Jinja2
    favorite = max(probabilities.items(), key=lambda x: x[1])[0]

    return render_template('result.html', match_data=match_data, probabilities=probabilities, favorite=favorite)

# Add these routes to your routes.py

# Edit League Route
@bp.route('/leagues/<int:league_id>', methods=['PUT'])
def update_league(league_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([name, start_date, end_date]):
        return jsonify({'error': 'Name, start date, and end date are required'}), 400

    try:
        league = League.query.get_or_404(league_id)
        
        # Check if name is being changed to an existing name
        if name.lower() != league.name.lower() and \
           League.query.filter(db.func.lower(League.name) == name.lower()).first():
            return jsonify({'error': 'League name already exists'}), 400

        league.name = name
        league.description = description
        league.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        league.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'message': 'League updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Edit Team Route

def update_team(league_id, team_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    name = data.get('name', '').strip()
    coach = data.get('coach', '').strip()

    if not all([name, coach]):
        return jsonify({'error': 'Name and coach are required'}), 400

    try:
        team = Team.query.filter_by(id=team_id, league_id=league_id).first_or_404()
        
        # Check if name is being changed to an existing name in the same league
        if name.lower() != team.name.lower() and \
           Team.query.filter(db.func.lower(Team.name) == name.lower(),
                           Team.league_id == league_id).first():
            return jsonify({'error': 'Team name already exists in this league'}), 400

        team.name = name
        team.coach = coach
        
        db.session.commit()
        return jsonify({'message': 'Team updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@bp.route('/team/<int:team_id>')
def team_detail(team_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))
    
    team = Team.query.get_or_404(team_id)
    league = League.query.get_or_404(team.league_id)
    today = date.today()
    
    # Get all fixtures involving this team
    all_fixtures = Fixture.query.filter(
        (Fixture.home_team_id == team_id) | (Fixture.away_team_id == team_id)
    ).order_by(Fixture.date.desc()).all()
    
    # Categorize fixtures
    upcoming_fixtures = []
    past_fixtures = []  # Changed from completed_fixtures to match template
    pending_fixtures = []
    
    for fixture in all_fixtures:
        if fixture.date > today:
            upcoming_fixtures.append(fixture)
        else:
            if fixture.status == 'Completed' or (fixture.home_score is not None and fixture.away_score is not None):
                past_fixtures.append(fixture)  # Using past_fixtures to match template
            else:
                pending_fixtures.append(fixture)
    
    # Sort fixtures appropriately
    upcoming_fixtures.sort(key=lambda x: x.date)  # Sort upcoming by date (ascending)
    pending_fixtures.sort(key=lambda x: x.date)   # Sort pending by date (ascending)
    
    # Initialize statistics
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    
    # Calculate statistics only from past matches
    for fixture in past_fixtures:
        if fixture.home_score is None or fixture.away_score is None:
            continue
            
        try:
            home_score = int(fixture.home_score)
            away_score = int(fixture.away_score)
        except (ValueError, TypeError):
            continue
            
        if fixture.home_team_id == team.id:
            goals_for += home_score
            goals_against += away_score
            if home_score > away_score:
                wins += 1
            elif home_score == away_score:
                draws += 1
            else:
                losses += 1
        else:
            goals_for += away_score
            goals_against += home_score
            if away_score > home_score:
                wins += 1
            elif away_score == home_score:
                draws += 1
            else:
                losses += 1
    
    # Get all players of the team ordered by jersey_number
    players = Player.query.filter_by(team_id=team_id).order_by(Player.jersey_number).all()

    return render_template(
        'team_detail.html',
        team=team,
        league=league,
        upcoming_fixtures=upcoming_fixtures,
        past_fixtures=past_fixtures,  # Changed to match template
        pending_fixtures=pending_fixtures,
        wins=wins,
        draws=draws,
        losses=losses,
        goals_for=goals_for,
        goals_against=goals_against,
        players=players,
        today=today
    )



@bp.route('/team/<int:team_id>/players/<int:player_id>/edit', methods=['POST'])
def edit_player(team_id, player_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    player = Player.query.filter_by(id=player_id, team_id=team_id).first_or_404()
    data = request.get_json()
    
    player.name = data.get('name', player.name)
    player.position = data.get('position', player.position)
    player.jersey_number = data.get('jersey_number', player.jersey_number)
    player.age = data.get('age', player.age)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Player updated successfully',
            'player': {
                'id': player.id,
                'name': player.name,
                'position': player.position,
                'jersey_number': player.jersey_number,
                'age': player.age
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/team/<int:team_id>/players/add', methods=['POST'])
def add_player(team_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data.get('name') or not data.get('position'):
        return jsonify({'error': 'Name and position are required'}), 400
    
    try:
        new_player = Player(
            name=data['name'],
            position=data['position'],
            jersey_number=data.get('jersey_number'),
            age=data.get('age'),
            team_id=team_id
        )
        db.session.add(new_player)
        db.session.commit()
        return jsonify({
            'message': 'Player added successfully',
            'player': {
                'id': new_player.id,
                'name': new_player.name,
                'position': new_player.position,
                'jersey_number': new_player.jersey_number,
                'age': new_player.age
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/team/<int:team_id>/players/<int:player_id>/delete', methods=['POST'])
def delete_player(team_id, player_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    player = Player.query.filter_by(id=player_id, team_id=team_id).first_or_404()
    
    try:
        db.session.delete(player)
        db.session.commit()
        return jsonify({'message': 'Player deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/fixture/<int:fixture_id>/lineup', methods=['GET', 'POST'])
def fixture_lineup(fixture_id):
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('main.login'))
    
    fixture = Fixture.query.get_or_404(fixture_id)
    home_team = Team.query.get_or_404(fixture.home_team_id)
    away_team = Team.query.get_or_404(fixture.away_team_id)
    
    if request.method == 'POST':
        try:
            # Validate starting XIs first
            home_starting_count = 0
            away_starting_count = 0
            
            for i in range(1, 12):
                if request.form.get(f'home_starting_{i}') and request.form.get(f'home_starting_{i}') != 'none':
                    home_starting_count += 1
                if request.form.get(f'away_starting_{i}') and request.form.get(f'away_starting_{i}') != 'none':
                    away_starting_count += 1
            
            if home_starting_count != 11:
                flash(f'Please select exactly 11 players for {home_team.name}\'s Starting XI', 'error')
                return redirect(url_for('main.fixture_lineup', fixture_id=fixture_id))
            
            if away_starting_count != 11:
                flash(f'Please select exactly 11 players for {away_team.name}\'s Starting XI', 'error')
                return redirect(url_for('main.fixture_lineup', fixture_id=fixture_id))
            
            # Clear existing lineups for this fixture
            Lineup.query.filter_by(fixture_id=fixture_id).delete()
            
            # Process home team lineup
            home_formation = request.form.get('home_formation', '4-4-2')
            home_lineup = Lineup(
                fixture_id=fixture_id,
                team_id=home_team.id,
                formation=home_formation
            )
            db.session.add(home_lineup)
            
            # Process home starting XI
            for i in range(1, 12):  # 11 starting players
                player_id = request.form.get(f'home_starting_{i}')
                if player_id and player_id != 'none':
                    position = request.form.get(f'home_position_{i}', '')
                    lineup_player = LineupPlayer(
                        lineup=home_lineup,
                        player_id=player_id,
                        is_starting=True,
                        position=position,
                        shirt_number=i
                    )
                    db.session.add(lineup_player)
            
            # Process home substitutes
            for i in range(1, 8):  # 7 substitutes
                player_id = request.form.get(f'home_sub_{i}')
                if player_id and player_id != 'none':
                    lineup_player = LineupPlayer(
                        lineup=home_lineup,
                        player_id=player_id,
                        is_starting=False,
                        shirt_number=11+i  # Subs start from number 12
                    )
                    db.session.add(lineup_player)
            
            # Process away team lineup
            away_formation = request.form.get('away_formation', '4-4-2')
            away_lineup = Lineup(
                fixture_id=fixture_id,
                team_id=away_team.id,
                formation=away_formation
            )
            db.session.add(away_lineup)
            
            # Process away starting XI
            for i in range(1, 12):  # 11 starting players
                player_id = request.form.get(f'away_starting_{i}')
                if player_id and player_id != 'none':
                    position = request.form.get(f'away_position_{i}', '')
                    lineup_player = LineupPlayer(
                        lineup=away_lineup,
                        player_id=player_id,
                        is_starting=True,
                        position=position,
                        shirt_number=i
                    )
                    db.session.add(lineup_player)
            
            # Process away substitutes
            for i in range(1, 8):  # 7 substitutes
                player_id = request.form.get(f'away_sub_{i}')
                if player_id and player_id != 'none':
                    lineup_player = LineupPlayer(
                        lineup=away_lineup,
                        player_id=player_id,
                        is_starting=False,
                        shirt_number=11+i  # Subs start from number 12
                    )
                    db.session.add(lineup_player)
            
            db.session.commit()
            flash('Lineups saved successfully!', 'success')
            return redirect(url_for('main.view_lineup', lineup_id=home_lineup.id))  # Redirect to view lineup
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving lineups: {str(e)}', 'error')
            app.logger.error(f"Error saving lineup: {str(e)}")
            return redirect(url_for('main.fixture_lineup', fixture_id=fixture_id))
    
    # GET request - show form
    home_players = Player.query.filter_by(team_id=home_team.id).order_by(Player.position, Player.name).all()
    away_players = Player.query.filter_by(team_id=away_team.id).order_by(Player.position, Player.name).all()
    
    # Get existing lineups if they exist
    home_lineup = Lineup.query.filter_by(fixture_id=fixture_id, team_id=home_team.id).first()
    away_lineup = Lineup.query.filter_by(fixture_id=fixture_id, team_id=away_team.id).first()
    
    return render_template('fixture_lineup.html',
                         fixture=fixture,
                         home_team=home_team,
                         away_team=away_team,
                         home_players=home_players,
                         away_players=away_players,
                         home_lineup=home_lineup,
                         away_lineup=away_lineup)

@bp.route('/lineup/<int:lineup_id>')
def view_lineup(lineup_id):
    lineup = Lineup.query.get_or_404(lineup_id)
    team = Team.query.get_or_404(lineup.team_id)
    fixture = Fixture.query.get_or_404(lineup.fixture_id)
    
    # Get players grouped by position
    starting_xi = db.session.query(LineupPlayer, Player)\
        .join(Player)\
        .filter(LineupPlayer.lineup_id == lineup_id, LineupPlayer.is_starting == True)\
        .order_by(LineupPlayer.shirt_number)\
        .all()
    
    substitutes = db.session.query(LineupPlayer, Player)\
        .join(Player)\
        .filter(LineupPlayer.lineup_id == lineup_id, LineupPlayer.is_starting == False)\
        .order_by(LineupPlayer.shirt_number)\
        .all()
    
    # Group starting players by position
    positions = {}
    for lp, player in starting_xi:
        if lp.position not in positions:
            positions[lp.position] = []
        positions[lp.position].append((lp, player))
    
    return render_template('view_lineup.html',
                         lineup=lineup,
                         team=team,
                         fixture=fixture,
                         positions=positions,
                         substitutes=substitutes)
@bp.route('/fixture/<int:fixture_id>/stats', methods=['GET', 'POST'])
def fixture_stats(fixture_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))
    
    fixture = Fixture.query.get_or_404(fixture_id)
    home_team = Team.query.get_or_404(fixture.home_team_id)
    away_team = Team.query.get_or_404(fixture.away_team_id)
    
    if request.method == 'POST':
        try:
            # Update match scores
            fixture.home_score = int(request.form.get('home_score', 0))
            fixture.away_score = int(request.form.get('away_score', 0))
            fixture.status = 'Completed'
            
            # Get all players from both teams
            all_players = home_team.players + away_team.players
            
            # Update player stats
            for player in all_players:
                player_id = str(player.id)
                
                # Update match-specific stats (could create a MatchStats model if you want to track per-match stats)
                player.goals += int(request.form.get(f'goals_{player_id}', 0))
                player.assists += int(request.form.get(f'assists_{player_id}', 0))
                
                # Handle cards (checkboxes)
                if request.form.get(f'yellow_{player_id}') == 'on':
                    player.yellow_cards += 1
                if request.form.get(f'red_{player_id}') == 'on':
                    player.red_cards += 1
                
                # Increment matches played if they were in the lineup
                lineup_player = LineupPlayer.query.filter_by(
                    player_id=player.id,
                    lineup_id=Lineup.query.filter_by(
                        fixture_id=fixture_id,
                        team_id=player.team_id
                    ).first().id
                ).first()
                
                if lineup_player:
                    player.matches_played += 1
            
            db.session.commit()
            flash('Match statistics updated successfully!', 'success')
            return redirect(url_for('main.fixture_stats', fixture_id=fixture_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating statistics: {str(e)}', 'error')
    
    # GET request - show form
    home_lineup = Lineup.query.filter_by(fixture_id=fixture_id, team_id=home_team.id).first()
    away_lineup = Lineup.query.filter_by(fixture_id=fixture_id, team_id=away_team.id).first()
    
    # Get players who were in the lineup
    home_players = []
    away_players = []
    
    if home_lineup:
        home_players = [lp.player for lp in home_lineup.players]
    if away_lineup:
        away_players = [lp.player for lp in away_lineup.players]
    
    return render_template('fixture_stats.html',
                         fixture=fixture,
                         home_team=home_team,
                         away_team=away_team,
                         home_players=home_players,
                         away_players=away_players)

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/generate-highlights', methods=['GET', 'POST'])
def generate_highlight_video():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        if 'video' not in request.files:
            return jsonify({'error': 'No video file part'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No selected video'}), 400

        if file and allowed_file(file.filename):
            # Create unique task ID
            task_id = str(uuid.uuid4())
            tasks[task_id] = {
                'status': 'PENDING',
                'filename': secure_filename(file.filename)
            }
            
            # Save file
            upload_dir = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            upload_path = os.path.join(upload_dir, tasks[task_id]['filename'])
            file.save(upload_path)
            
            # Start processing in background
            from threading import Thread
            thread = Thread(target=process_video_background, args=(task_id, upload_path))
            thread.start()
            
            return jsonify({'task_id': task_id})
    
    return render_template('generate_highlights.html')

def process_video_background(task_id, video_path):
    try:
        tasks[task_id]['status'] = 'PROCESSING'
        
        # Process the video
        final_path = generate_highlights(video_path)
        
        if final_path and os.path.exists(final_path):
            tasks[task_id].update({
                'status': 'COMPLETED',
                'output': final_path,
                'download_url': f"/download-highlight/{os.path.basename(final_path)}"
            })
        else:
            tasks[task_id].update({
                'status': 'FAILED',
                'error': 'Highlight generation failed'
            })
    except Exception as e:
        tasks[task_id].update({
            'status': 'FAILED',
            'error': str(e)
        })

@bp.route('/highlights/status/<task_id>')
def highlight_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Invalid task ID'}), 404
    
    return jsonify(task)

@bp.route('/download-highlight/<filename>')
def download_highlight(filename):
    highlights_dir = os.path.join('app', 'static', 'output', 'highlights')
    try:
        return send_from_directory(
            highlights_dir,
            filename,
            as_attachment=True,
            mimetype='video/mp4'
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404