import pandas as pd

df = pd.read_csv('../data/general_defense_stats.csv')  # adjust path if needed
curry = df[df['PLAYER_NAME'].str.contains('Curry', case=False)]
print(curry[['PLAYER_NAME', 'GP', 'MIN']])

df = pd.read_csv('../data/season_2025-26.csv')
print(df[df['TEAM_ABBREVIATION'] == 'GSW'][['PLAYER_NAME', 'GP', 'MIN']])