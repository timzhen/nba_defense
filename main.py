from fastapi import FastAPI
import pandas as pd

app = FastAPI() # creates web application

df = pd.read_csv('data/season_2025-26.csv')

def clean_player(row):
    return {
        "player_name": row['PLAYER_NAME'],
        "team": row['TEAM_ABBREVIATION'],
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
