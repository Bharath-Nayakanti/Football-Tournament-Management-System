# app/predictors/IPL/IPLWPredictor.py
import joblib
import pandas as pd
import numpy as np

class IPLPredictor:
    def __init__(self):
        self.model = joblib.load('app/predictors/IPL/ipl_predictor_model.pkl')
        self.preprocessor = joblib.load('app/predictors/IPL/preprocessor.pkl')
        self.label_encoder = joblib.load('app/predictors/IPL/label_encoder.pkl')

        self.current_teams = [
            'Chennai Super Kings', 'Delhi Capitals', 'Gujarat Titans',
            'Kolkata Knight Riders', 'Lucknow Super Giants', 'Mumbai Indians',
            'Punjab Kings', 'Rajasthan Royals', 'Royal Challengers Bengaluru',
            'Sunrisers Hyderabad'
        ]

        self.venues = [
            "Mumbai", "Kolkata", "Delhi", "Chennai", "Bangalore",
            "Hyderabad", "Ahmedabad", "Pune", "Jaipur", "Chandigarh",
            "Mohali", "Visakhapatnam", "Indore", "Dharamsala", "Nagpur",
            "Raipur", "Ranchi", "Cuttack", "Kochi", "Kanpur",
            "Rajkot", "Navi Mumbai", "Bengaluru", "Lucknow", "Guwahati",
            "Thiruvananthapuram", "Bhubaneswar", "Gwalior", "Vadodara", "Jamshedpur",
            "Cochin", "Goa", "Surat"
        ]

        self.default_values = {
            'h2h_win_pct': 0.52,
            'venue_team1_win_pct': 0.55,
            'team1_strength': 0.72,
            'team2_strength': 0.68,
            'team1_form': 0.65,
            'team2_form': 0.60,
            'toss_impact': 0.55,
            'is_day': 1,
            'is_playoff': 0,
            'team1_top3_batting_avg': 38.2,
            'team2_top3_batting_avg': 36.8,
            'team1_top3_bowling_sr': 24.5,
            'team2_top3_bowling_sr': 25.1,
            'team1_powerplay_avg': 47.3,
            'team2_powerplay_avg': 46.8,
            'team1_powerplay_wickets': 1.6,
            'team2_powerplay_wickets': 1.5,
            'powerplay_dominance': 0.52,
            'win_correlation': 0.58
        }

    def predict_match(self, match_data):
        input_data = {**self.default_values, **match_data}
        input_df = pd.DataFrame({k: [v] for k, v in input_data.items()})
        processed = self.preprocessor.transform(input_df)
        proba = self.model.predict_proba(processed)[0]

        team_indices = [
            np.where(self.label_encoder.classes_ == match_data['team1'])[0][0],
            np.where(self.label_encoder.classes_ == match_data['team2'])[0][0]
        ]
        team_probs = proba[team_indices]
        team_probs = team_probs / team_probs.sum()

        return {
            match_data['team1']: float(team_probs[0]),
            match_data['team2']: float(team_probs[1])
        }
