import pandas as pd

df_matchup = pd.read_csv('data/matchup_stats.csv')
df_general = pd.read_csv('data/general_defense_stats.csv')
df_hustle = pd.read_csv('data/hustle_stats.csv')

df_matchup_grouped = df_matchup.groupby(['DEF_PLAYER_ID', 'DEF_PLAYER_NAME']).agg(
    avg_fg_pct_allowed = ('MATCHUP_FG_PCT', 'mean'),
    avg_3fg_pct_allowed = ('MATCHUP_FG3_PCT', 'mean'),
    total_possessions = ('PARTIAL_POSS', 'sum'),
).reset_index()

print(df_matchup_grouped.shape)
print(df_matchup_grouped.head(100))


df_merge = df_general.merge(
    df_hustle,
    on= 'PLAYER_ID',
    suffixes= ('_general', '_hustle')
)

df_merge = df_merge.merge(
    df_matchup_grouped,
    left_on = 'PLAYER_ID',
    right_on = 'DEF_PLAYER_ID',
    how = 'left'
)

"""
print(df_merged.shape)
print(df_merged.columns.tolist())
print(df_merged[['PLAYER_NAME_general', 'BLK', 'CONTESTED_SHOTS_2PT', 'avg_fg_pct_allowed']].head(10))

"""

#dropping duplicate columns
df_merge = df_merge.drop(columns = [
    'PLAYER_NAME_hustle', 'TEAM_ID_hustle', 'TEAM_ABBREVIATION_hustle', 'AGE_hustle', 'MIN_hustle'
])

df_merge = df_merge.rename(columns = {
    'PLAYER_NAME_general': 'PLAYER_NAME',
    'TEAM_ID_general': 'TEAM_ID',
    'TEAM_ABBREVIATION_general': 'TEAM_ABBREVIATION',
    'AGE_general': 'AGE',
    'MIN_general': 'MIN'
})

"""
print(df_merge[[
    'PLAYER_NAME', 'BLK', 'CONTESTED_SHOTS_2PT','CONTESTED_SHOTS_3PT', 'avg_fg_pct_allowed'
    ]].sort_values('CONTESTED_SHOTS_3PT', ascending = False).head(10))
"""

df_merge.to_csv('data/merged_defense_stats.csv', index = False)