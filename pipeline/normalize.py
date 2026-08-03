import pandas as pd

df = pd.read_csv('data/merged_defense_stats.csv')

df = df[(df['GP'] >= 40) & (df['MIN'] >= 1500)]

# min max scaling
def normalize(column):
    # higher = better
    max_val = column.max()
    min_val = column.min()
    score = (column - min_val) / (max_val - min_val) * 100 
        # (column - min val) ~ gives the worst player a score of 0
        # / (max_val - min_val) ~ divide by range of data -- best player becomes 1.00
    return score

def inverted_normalize(column):
    # lower = better
    max_val = column.max()
    min_val = column.min()
    score = (max_val - column) / (max_val - min_val) * 100
    return score


# Rim Protection
df['BLK_score'] = normalize(df['BLK'])
df['OPP_PTS_PAINT_score'] = inverted_normalize(df['OPP_PTS_PAINT'])
df['DEF_RATING_score'] = inverted_normalize(df['DEF_RATING'])
df['rim_protection_score'] = (
    df['BLK_score'] * 0.40 +
    df['OPP_PTS_PAINT_score'] * 0.35 +
    df['DEF_RATING_score'] * 0.25
)

# Shot Contesting
df['CONTESTED_SHOTS_2PT_score'] = normalize(df['CONTESTED_SHOTS_2PT'])
df['CONTESTED_SHOTS_3PT_score'] = normalize(df['CONTESTED_SHOTS_3PT'])
df['shot_contesting_score'] = (
    df['CONTESTED_SHOTS_2PT_score'] * 0.4 +
    df['CONTESTED_SHOTS_3PT_score'] * 0.6
)

# Ball Disruption
df['DEFLECTIONS_score'] = normalize(df['DEFLECTIONS'])
df['STL_score'] = normalize(df['STL'])
df['CHARGES_DRAWN_score'] = normalize(df['CHARGES_DRAWN'])
df['ball_disruption_score'] = (
    df['DEFLECTIONS_score'] * 0.40 +
    df['STL_score'] * 0.35 + 
    df['CHARGES_DRAWN_score'] * 0.25
)

# On Ball Matchup Defense
df['avg_fg_pct_allowed_score'] = inverted_normalize(df['avg_fg_pct_allowed'])
df['avg_3fg_pct_allowed_score'] = inverted_normalize(df['avg_3fg_pct_allowed'])
df['on_ball_matchup_def_score'] = (
    df['avg_fg_pct_allowed_score'] * 0.5 +
    df['avg_3fg_pct_allowed_score'] * 0.5
)

# Defensive Rebounding
df['DREB_score'] = normalize(df['DREB'])
df['DEF_BOXOUTS_score'] = normalize(df['DEF_BOXOUTS'])
df['def_reb_score'] = (
    df['DREB_score'] * 0.55 + 
    df['DEF_BOXOUTS_score'] * 0.45
)

print(df.columns.tolist())
"""
print(df[[
    'PLAYER_NAME', 'BLK', 'BLK_score', 'CONTESTED_SHOTS_2PT_score', 'CONTESTED_SHOTS_3PT_score', 'avg_fg_pct_allowed_score', 'DEFLECTIONS', 'DEFLECTIONS_score'
    ]].sort_values('DEFLECTIONS', ascending=False).head(10))
"""
print(df[['PLAYER_NAME', 'rim_protection_score']].sort_values('rim_protection_score', ascending=False).head(10))
print(df[['PLAYER_NAME', 'shot_contesting_score']].sort_values('shot_contesting_score', ascending=False).head(10))
print(df[['PLAYER_NAME', 'ball_disruption_score']].sort_values('ball_disruption_score', ascending=False).head(10))
print(df[['PLAYER_NAME', 'on_ball_matchup_def_score']].sort_values('on_ball_matchup_def_score', ascending=False).head(10))
print(df[['PLAYER_NAME', 'def_reb_score']].sort_values('def_reb_score', ascending=False).head(10))


df.to_csv('data/scored_defense_stats.csv')