import json
import pandas as pd
import os
from collections import defaultdict

# Load existing match data
df = pd.read_csv("ipl_matches_supercharged.csv")

# Initialize enhanced features
new_features = [
    'team1_top3_batting_avg', 'team2_top3_batting_avg',
    'team1_top3_bowling_sr', 'team2_top3_bowling_sr',
    'team1_powerplay_avg', 'team2_powerplay_avg',
    'team1_powerplay_wickets', 'team2_powerplay_wickets'
]
df = df.assign(**{feat: 0.0 for feat in new_features})

def extract_stats(match_path):
    try:
        with open(match_path) as f:
            match = json.load(f)
        
        match_id = int(os.path.splitext(os.path.basename(match_path))[0])
        stats = {'match_id': match_id}
        
        for innings in match.get('innings', []):
            team = innings['team']
            try:
                is_team1 = team == df.loc[df['match_id'] == match_id, 'team1'].values[0]
            except IndexError:
                continue
                
            prefix = 'team1' if is_team1 else 'team2'
            pp_runs = 0
            pp_wickets = 0
            batsmen = defaultdict(int)
            bowlers = defaultdict(lambda: {'wickets': 0, 'balls': 0})
            valid_deliveries = 0
            
            # Wicket detection system
            current_pair = set()  # Tracks striker + non-striker
            last_bowler = None
            
            for over in innings['overs'][:6]:  # Powerplay overs
                for delivery in over['deliveries']:
                    batter = delivery.get('batter')
                    bowler = delivery.get('bowler')
                    non_striker = delivery.get('non_striker')
                    
                    if not all([batter, bowler, non_striker]):
                        continue
                    
                    # Initialize current batter pair
                    if not current_pair:
                        current_pair = {batter, non_striker}
                    
                    # Detect wickets (new batter not in current pair)
                    if batter not in current_pair:
                        pp_wickets += 1
                        if last_bowler:  # Credit wicket to previous bowler
                            bowlers[last_bowler]['wickets'] += 1
                        current_pair = {batter, non_striker}  # New pair
                    
                    # Handle striker rotation on odd runs
                    runs = delivery['runs'].get('batter', 0)
                    total_runs = delivery['runs']['total']
                    if total_runs % 2 != 0:  # Odd runs cause rotation
                        current_pair = {non_striker, batter}
                    
                    # Record stats
                    batsmen[batter] += runs
                    bowlers[bowler]['balls'] += 1
                    pp_runs += total_runs
                    valid_deliveries += 1
                    last_bowler = bowler
            
            # Calculate derived stats
            if valid_deliveries > 0:
                # Batting averages (runs per ball)
                if batsmen:
                    top3 = sorted(batsmen.values(), reverse=True)[:3]
                    stats[f"{prefix}_top3_batting_avg"] = sum(top3) / len(top3)
                
                # Bowling strike rates (wickets per 100 balls)
                if bowlers:
                    qualified_bowlers = {b: s for b, s in bowlers.items() if s['balls'] >= 6}  # Min 1 over
                    if qualified_bowlers:
                        top3_sr = sorted(
                            [(b, (s['wickets'] / s['balls']) * 100) 
                             for b, s in qualified_bowlers.items()],
                            key=lambda x: x[1], reverse=True
                        )[:3]
                        if top3_sr:
                            stats[f"{prefix}_top3_bowling_sr"] = sum(sr for _, sr in top3_sr) / len(top3_sr)
                
                stats[f"{prefix}_powerplay_avg"] = pp_runs / 6  # Runs per over
                stats[f"{prefix}_powerplay_wickets"] = pp_wickets
        
        return stats
    
    except json.JSONDecodeError:
        print(f"Invalid JSON: {os.path.basename(match_path)}")
    except Exception as e:
        print(f"Error processing {os.path.basename(match_path)}: {str(e)}")
    return None

# Process all JSON files
all_stats = []
processed_files = 0

for filename in os.listdir('ipl_data'):
    if filename.endswith('.json'):
        stats = extract_stats(os.path.join('ipl_data', filename))
        if stats:
            all_stats.append(stats)
            processed_files += 1
            if processed_files % 100 == 0:
                print(f"Processed {processed_files} files...")

# Merge results
if all_stats:
    stats_df = pd.DataFrame(all_stats)
    
    # Fill missing features with 0
    for feat in new_features:
        if feat not in stats_df.columns:
            stats_df[feat] = 0.0
    
    # Merge with original data
    for feat in new_features:
        df[feat] = df['match_id'].map(stats_df.set_index('match_id')[feat]).fillna(0)
    
    # Add these right before saving the CSV

# Calculate match outcomes based on powerplay performance
df['powerplay_dominance'] = df.apply(
    lambda x: x['team1_powerplay_avg'] - x['team2_powerplay_avg'], axis=1
)

# Win correlation with powerplay stats
df['win_correlation'] = df.apply(
    lambda x: 1 if (x['winner'] == x['team1'] and x['powerplay_dominance'] > 0) 
              or (x['winner'] == x['team2'] and x['powerplay_dominance'] < 0) 
              else 0, axis=1
)

# Save enhanced analysis
df.to_csv("ipl_matches_supercharged_enhanced.csv", index=False)

# Generate insights report
print("\nAdvanced Powerplay Insights:")
print(f"{df['win_correlation'].mean():.1%} of matches were won by team with better powerplay")
print("\nPowerplay Wickets vs Win Rate:")
print(df.groupby('team1_powerplay_wickets')['win_correlation'].mean())
