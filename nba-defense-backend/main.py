from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

app = FastAPI() # creates web application

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

def clean_player(row):
    return {
        "player_name": row['PLAYER_NAME'],
        "team": TEAM_NAMES.get(row['TEAM_ABBREVIATION'], row['TEAM_ABBREVIATION']),
        "age": row['AGE'],
        "rim_protection_score": round(row['rim_protection_score'], 1),
        "shot_contesting_score": round(row['shot_contesting_score'], 1),
        "ball_disruption_score": round(row['ball_disruption_score'], 1),
        "on_ball_matchup_def_score": round(row['on_ball_matchup_def_score'], 1),
        "def_reb_score": round(row['def_reb_score'], 1)
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

# to run type this in terminal: uvicorn main:app --reload
