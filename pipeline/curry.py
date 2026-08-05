import pandas as pd

df = pd.read_csv('../data/season_2025-26.csv')

print(df[['PLAYER_NAME', 'total_possessions', 'on_ball_matchup_def_score', 'on_ball_matchup_def_percentile', 'on_ball_matchup_def_label']]
      .sort_values('on_ball_matchup_def_percentile', ascending=False)
      .head(15))

# after generating predictions, check them against known 2025-26 results

