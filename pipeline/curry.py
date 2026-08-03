import pandas as pd
df = pd.read_csv('../data/season_2025-26.csv')  # adjust path to wherever you're checking from
print(df.columns.tolist())
print(df[['PLAYER_NAME', 'rim_protection_percentile', 'rim_protection_label']].head(5))