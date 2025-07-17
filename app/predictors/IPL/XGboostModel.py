import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, log_loss
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib

# Load and prepare data
df = pd.read_csv("ipl_matches_supercharged_enhanced.csv")

# Team rebranding and cleanup
team_mapping = {
    'Gujarat Lions': 'Gujarat Titans',
    'Delhi Daredevils': 'Delhi Capitals', 
    'Kings XI Punjab': 'Punjab Kings'
}
for col in ['team1', 'team2', 'winner', 'toss_winner']:
    df[col] = df[col].replace(team_mapping)

defunct_teams = [
    'Deccan Chargers', 'Pune Warriors',
    'Kochi Tuskers Kerala', 'Rising Pune Supergiants'
]
df = df[~df['team1'].isin(defunct_teams) & 
        ~df['team2'].isin(defunct_teams) &
        ~df['winner'].isin(defunct_teams)]

# Feature engineering
features = [
    'venue', 'team1', 'team2', 'toss_winner', 'toss_decision',
    'h2h_win_pct', 'venue_team1_win_pct', 'team1_strength', 'team2_strength',
    'team1_form', 'team2_form', 'toss_impact', 'is_playoff',
    'team1_top3_batting_avg', 'team2_top3_batting_avg',
    'team1_top3_bowling_sr', 'team2_top3_bowling_sr',
    'team1_powerplay_avg', 'team2_powerplay_avg',
    'team1_powerplay_wickets', 'team2_powerplay_wickets',
    'powerplay_dominance', 'win_correlation'
]
target = 'winner'

X = df[features].copy()
y = df[target].copy()

# Encode target
y = y.astype(str).replace('nan', 'Unknown')
label_encoder_y = LabelEncoder()
y_encoded = label_encoder_y.fit_transform(y)

# Preprocessing
cat_cols = ['venue', 'team1', 'team2', 'toss_winner', 'toss_decision']
num_cols = [col for col in features if col not in cat_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', 'passthrough')
        ]), num_cols),
        ('cat', Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ]), cat_cols)
    ])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Preprocess data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Calculate sample weights
class_counts = np.bincount(y_train)
weights = len(y_train) / (len(np.unique(y_train)) * class_counts)
sample_weights = np.array([weights[cls] for cls in y_train])

# Optimized XGBoost model
model = XGBClassifier(
    n_estimators=500,
    max_depth=4,
    learning_rate=0.02,
    subsample=0.7,
    colsample_bytree=0.7,
    random_state=42,
    eval_metric='mlogloss',
    early_stopping_rounds=30,
    min_child_weight=2,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=0.5,
    tree_method='hist'
)

# Train model
model.fit(
    X_train_processed,
    y_train,
    sample_weight=sample_weights,
    eval_set=[(X_test_processed, y_test)],
    verbose=False
)

# Evaluation
y_pred = model.predict(X_test_processed)
y_proba = model.predict_proba(X_test_processed)

print("Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=label_encoder_y.classes_,
    zero_division=0
))
print(f"Log Loss: {log_loss(y_test, y_proba):.4f}")

# Confusion Matrix
plt.figure(figsize=(12, 10))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=label_encoder_y.classes_,
            yticklabels=label_encoder_y.classes_,
            cmap='Blues')
plt.title("Confusion Matrix", pad=20)
plt.xlabel("Predicted Team")
plt.ylabel("Actual Team")
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# Get feature importance only for numerical features
numerical_importance = pd.DataFrame({
    'Feature': num_cols,
    'Importance': model.feature_importances_[:len(num_cols)]
}).sort_values('Importance', ascending=False)


plt.figure(figsize=(12, 8))
top_numerical = numerical_importance.head(20)
plt.barh(top_numerical['Feature'], top_numerical['Importance'], color='teal')
plt.title("Top Numerical Features (Importance)")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.gca().invert_yaxis()
plt.show()

from sklearn.ensemble import RandomForestClassifier
from catboost import CatBoostClassifier

def evaluate_model(name, model, X_train, y_train, X_test, y_test, label_encoder):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    print(f"\n=== {name} ===")
    print("Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    print(f"Log Loss: {log_loss(y_test, y_proba):.4f}")
    return y_pred


# Save artifacts
joblib.dump(model, 'ipl_predictor_model.pkl')
joblib.dump(preprocessor, 'preprocessor.pkl')
joblib.dump(label_encoder_y, 'label_encoder.pkl')
print("Model saved successfully!")
