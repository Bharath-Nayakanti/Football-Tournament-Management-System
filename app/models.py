from . import db
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
from flask_login import UserMixin 

class Team(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', 'league_id', name='unique_team_name_per_league'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    coach = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id', ondelete='CASCADE'), nullable=False)
    
    league = db.relationship('League', back_populates='teams')
    home_fixtures = db.relationship('Fixture', 
                                  foreign_keys='Fixture.home_team_id', 
                                  back_populates='home_team',
                                  cascade='all, delete-orphan')
    away_fixtures = db.relationship('Fixture', 
                                   foreign_keys='Fixture.away_team_id', 
                                   back_populates='away_team',
                                   cascade='all, delete-orphan')
    players = db.relationship('Player', back_populates='team', cascade='all, delete-orphan')
    lineups = db.relationship('Lineup', back_populates='team', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Team {self.name}>'

class League(db.Model):
    __table_args__ = (
        db.UniqueConstraint('name', name='unique_league_name'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    teams = db.relationship('Team', back_populates='league', cascade='all, delete-orphan')
    fixtures = db.relationship('Fixture', back_populates='league', cascade='all, delete-orphan')

    def generate_fixtures(self, matches_per_day=2):
        """Generate fixtures for the league with specified matches per day"""
        teams = self.teams
        if len(teams) < 2:
            raise ValueError("Need at least 2 teams to generate fixtures")

        # Generate all possible unique match pairings (home and away)
        all_matches = []
        for home in teams:
            for away in teams:
                if home != away:
                    all_matches.append((home, away))
        
        # Shuffle for variety
        random.shuffle(all_matches)
        
        fixtures = []
        current_date = self.start_date
        matches_scheduled_today = 0
        
        for home, away in all_matches:
            # If we've hit the daily limit or passed end date
            if matches_scheduled_today >= matches_per_day or current_date > self.end_date:
                current_date += timedelta(days=1)
                matches_scheduled_today = 0
                if current_date > self.end_date:
                    current_date = self.end_date  # Squeeze remaining into last day
            
            fixtures.append(Fixture(
                league_id=self.id,
                home_team_id=home.id,
                away_team_id=away.id,
                date=current_date,
                stage='group',
                status='Pending'
            ))
            matches_scheduled_today += 1
        
        return fixtures

    def calculate_standings(self):
        teams = {team.id: {
            'team': team,
            'points': 0,
            'played': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0
        } for team in self.teams}

        for fixture in self.fixtures:
            if fixture.status != 'Completed':
                continue
                
            home_id = fixture.home_team_id
            away_id = fixture.away_team_id
            home_goals = fixture.home_score
            away_goals = fixture.away_score
            
            # Update matches played
            teams[home_id]['played'] += 1
            teams[away_id]['played'] += 1
            
            # Update goals
            teams[home_id]['goals_for'] += home_goals
            teams[home_id]['goals_against'] += away_goals
            teams[away_id]['goals_for'] += away_goals
            teams[away_id]['goals_against'] += home_goals
            
            # Update points and results
            if home_goals > away_goals:
                teams[home_id]['points'] += 3
                teams[home_id]['wins'] += 1
                teams[away_id]['losses'] += 1
            elif home_goals < away_goals:
                teams[away_id]['points'] += 3
                teams[away_id]['wins'] += 1
                teams[home_id]['losses'] += 1
            else:
                teams[home_id]['points'] += 1
                teams[away_id]['points'] += 1
                teams[home_id]['draws'] += 1
                teams[away_id]['draws'] += 1

        # Convert to sorted list
        standings = sorted(teams.values(), 
                         key=lambda x: (-x['points'], 
                                      -(x['goals_for'] - x['goals_against']),
                                      -x['goals_for']))
        
        return standings

    def __repr__(self):
        return f'<League {self.name}>'

class Fixture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id', ondelete='CASCADE'), nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    stage = db.Column(db.String(20), default='group')  # 'group' or 'knockout'
    status = db.Column(db.String(20), default='Pending')  # 'Pending' or 'Completed'

    # Relationships
    league = db.relationship('League', back_populates='fixtures')
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_fixtures')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_fixtures')
    lineups = db.relationship('Lineup', back_populates='fixture', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Fixture {self.id}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Removed: role = db.Column(db.String(20), default='user')
    
    # Required by Flask-Login
    def get_id(self):
        return str(self.id)  # Must return string
    
    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # For better debugging
    def __repr__(self):
        return f'<User {self.username}>'
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    jersey_number = db.Column(db.Integer)
    age = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)
    
    # Statistics fields
    matches_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    
    team = db.relationship('Team', back_populates='players')
    lineup_players = db.relationship('LineupPlayer', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Player {self.name}>'

class Lineup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, db.ForeignKey('fixture.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)
    formation = db.Column(db.String(20))
    
    # Relationships
    fixture = db.relationship('Fixture', back_populates='lineups')
    team = db.relationship('Team', back_populates='lineups')
    players = db.relationship('LineupPlayer', back_populates='lineup', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lineup {self.id}>'

class LineupPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lineup_id = db.Column(db.Integer, db.ForeignKey('lineup.id', ondelete='CASCADE'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id', ondelete='CASCADE'), nullable=False)
    is_starting = db.Column(db.Boolean, default=True)
    position = db.Column(db.String(50))
    
    # Relationships
    lineup = db.relationship('Lineup', back_populates='players')
    player = db.relationship('Player', back_populates='lineup_players')

    def __repr__(self):
        return f'<LineupPlayer {self.id}>'