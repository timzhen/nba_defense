from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai


import pandas as pd
import os

app = FastAPI() # creates web application

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://nba-defense.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEAM_NAMES = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'LA Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks', 'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'
}


df = pd.read_csv('data/season_2025-26.csv')

@app.get("/")
def root():
    return {"message": "NBA Defense Rater API is running", "endpoints": ["/players", "/players/{name}"]}

def _safe_round(value, digits):
    if pd.isna(value):
        return None
    return round(float(value), digits)

def _safe_label(value):
    if pd.isna(value):
        return None
    return value

def clean_player(row):
    return {
        "player_name": row['PLAYER_NAME'],
        "team": TEAM_NAMES.get(row['TEAM_ABBREVIATION'], row['TEAM_ABBREVIATION']),
        "age": None if pd.isna(row['AGE']) else row['AGE'],
        "rim_protection_score": _safe_round(row['rim_protection_score'], 1),
        "rim_protection_percentile": _safe_round(row['rim_protection_percentile'], 0),
        "rim_protection_label": _safe_label(row['rim_protection_label']),
        "shot_contesting_score": _safe_round(row['shot_contesting_score'], 1),
        "shot_contesting_percentile": _safe_round(row['shot_contesting_percentile'], 0),
        "shot_contesting_label": _safe_label(row['shot_contesting_label']),
        "ball_disruption_score": _safe_round(row['ball_disruption_score'], 1),
        "ball_disruption_percentile": _safe_round(row['ball_disruption_percentile'], 0),
        "ball_disruption_label": _safe_label(row['ball_disruption_label']),
        "on_ball_matchup_def_score": _safe_round(row['on_ball_matchup_def_score'], 1),
        "on_ball_matchup_def_percentile": _safe_round(row['on_ball_matchup_def_percentile'], 0),
        "on_ball_matchup_def_label": _safe_label(row['on_ball_matchup_def_label']),
        "def_reb_score": _safe_round(row['def_reb_score'], 1),
        "def_reb_percentile": _safe_round(row['def_reb_percentile'], 0),
        "def_reb_label": _safe_label(row['def_reb_label']),
        "player_id": None if pd.isna(row['PLAYER_ID']) else int(row['PLAYER_ID']),
    }

@app.get("/players") # this is a decorator. it tags function below this line. "/players" (GET requests) → get_all_players function
def get_all_players():
    return [clean_player(row) for _, row in df.iterrows()]

@app.get("/players/{name}")
def get_player(name: str):
    player = df[df['PLAYER_NAME'].str.lower() == name.lower()]
    if player.empty:
        return {"error": "Player not found"}
    
    row = player.iloc[0]
    return clean_player(row)


@app.get("/players/{name}/explain")
def explain_player(name: str, question: str = "Why is this player ranked this way?"):
    player = df[df['PLAYER_NAME'].str.lower() == name.lower()]
    if player.empty:
        return {"error": "Player not found"}
    
    row = player.iloc[0]
    player_data = clean_player(row)
    
    full_context = {
        "player_name": row['PLAYER_NAME'],
        "team": TEAM_NAMES.get(row['TEAM_ABBREVIATION'], row['TEAM_ABBREVIATION']),
        "age": row['AGE'],
        "blocks": row['BLK'],
        "opponent_points_in_paint": row['OPP_PTS_PAINT'],
        "defensive_rating": row['DEF_RATING'],
        "deflections": row['DEFLECTIONS'],
        "steals": row['STL'],
        "charges_drawn": row['CHARGES_DRAWN'],
        "defensive_rebounds": row['DREB'],
        "defensive_boxouts": row['DEF_BOXOUTS'],
        "opponent_fg_pct_allowed": row['avg_fg_pct_allowed'],
        "rim_protection_score": round(row['rim_protection_score'], 1),
        "shot_contesting_score": round(row['shot_contesting_score'], 1),
        "ball_disruption_score": round(row['ball_disruption_score'], 1),
        "on_ball_matchup_def_score": round(row['on_ball_matchup_def_score'], 1),
        "def_reb_score": round(row['def_reb_score'], 1)
    }

    prompt = f"""You're a basketball analyst. Here is a player's defensive profile:

{full_context}

The user asked: "{question}"

Answer using only the data provided above, in 2-3 sentences, in an conversational and informative tone. Don't state the player score, explain why he got this score with their raw stats. Explain the player's biggest strength, how is he best optimally used schematically by teams, and weakness (if they actually have one).
Weakness could be high opponent fg pct allowed and points, age (only older players). Dont mention to the reader but think about the player's positional job (if they're a guard it is okay if they dont have a lot of rebounds compared to forwards and centers) and how that may affect how they are best utilized on the court schematically"""

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt
    )
    
    return {"answer": response.text}


import joblib

dpoy_model = joblib.load('dpoy_model.pkl')

feature_cols = ['rim_protection_score', 'shot_contesting_score', 'ball_disruption_score',
                 'on_ball_matchup_def_score', 'def_reb_score']

df['dpoy_probability'] = dpoy_model.predict_proba(df[feature_cols].fillna(df[feature_cols].mean()))[:, 1]

@app.get("/dpoy-leaderboard")
def dpoy_leaderboard():
    top = df.nlargest(10, 'dpoy_probability')[['PLAYER_NAME', 'dpoy_probability']]
    return top.to_dict(orient='records')

# to run type this in terminal: uvicorn main:app --reload

