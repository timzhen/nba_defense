from nba_api.stats.endpoints import leaguedashplayerstats 
# each endpoint is a different page on NBA.com's stats site
# league dashplayerstats corresponds to stats.nba.com/players/defense — the league-wide player stats dashboard.

import pandas as pd 


stats = leaguedashplayerstats.LeagueDashPlayerStats(    # returns wrapper object (metadata and meta info included with the raw data)
    season='2017-18',    # which season we want
    measure_type_detailed_defense='Defense' # we want defensive stats view
)

df = stats.get_data_frames()[0] # stores first item from stats in df (dataframe - 2d table)
print(df.columns.tolist())  # prints every column name to see what stats are a avaliable
#print(df.head(50))  # prints first 10 rows

df_atLeast40 = df[(df['GP'] >= 40) & (df['MIN'] >= 1500)] 

print(df_atLeast40.sort_values('DEF_RATING', ascending=True).head(20)[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'BLK', 'DEF_RATING']])
