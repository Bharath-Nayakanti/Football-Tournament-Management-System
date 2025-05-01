from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Team, User

bp = Blueprint('main', __name__)

# Login page is now the root
@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Please fill in all fields')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid credentials')
            return redirect(url_for('main.login'))

        flash('Login successful!')
        return redirect(url_for('main.home'))

    return render_template('login.html')

# Signup page
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash('Please fill in all fields')
            return redirect(url_for('main.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use')
            return redirect(url_for('main.signup'))

        
        new_user = User(username=username, email=email)
        new_user.set_password(password) 

        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully! Please log in.')
        return redirect(url_for('main.login'))

    return render_template('signup.html')

# After login, show home
@bp.route('/home')
def home():
    return render_template('home.html')

# Create team
@bp.route('/teams', methods=['POST'])
def create_team():
    data = request.get_json()
    team_name = data.get('name')
    team_founded = data.get('founded')

    if not team_name or not team_founded:
        return jsonify({'error': 'Missing data'}), 400

    new_team = Team(name=team_name, founded=team_founded)
    db.session.add(new_team)
    db.session.commit()

    return jsonify({
        'message': 'Team created',
        'team': {
            'id': new_team.id,
            'name': new_team.name,
            'founded': new_team.founded
        }
    }), 201

# Get teams
@bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    teams_list = [{
        'id': team.id,
        'name': team.name,
        'founded': team.founded
    } for team in teams]

    return jsonify({'teams': teams_list})
