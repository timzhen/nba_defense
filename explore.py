from nba_api.stats.endpoints import leaguedashplayerstats 
# each endpoint is a different page on NBA.com's stats site
# league dashplayerstats corresponds to stats.nba.com/players/defense — the league-wide player stats dashboard.

from nba_api.stats.endpoints import leaguehustlestatsplayer
from nba_api.stats.endpoints import leagueseasonmatchups


import pandas as pd 


general = leaguedashplayerstats.LeagueDashPlayerStats(    # returns wrapper object (metadata and meta info included with the raw data)
    season='2025-26',    # which season we want
    measure_type_detailed_defense='Defense' # we want defensive stats view
)

df_general = general.get_data_frames()[0] # stores first item from stats in df (dataframe - 2d table)
#print(df.columns.tolist())  # prints every column name to see what stats are a avaliable
#print(df.head(50))  # prints first 10 rows

df_general_filter = df_general[(df_general['GP'] >= 40) & (df_general['MIN'] >= 1500)] 

# print(df_general_filter.sort_values('OPP_PTS_PAINT_RANK', ascending=True).head(20)[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'BLK', 'DEF_RATING', 'OPP_PTS_PAINT', 'OPP_PTS_PAINT_RANK']])

df_general.to_csv('data/general_defense_stats.csv', index = False) # turns general_defense_stats into a tabular data file (csv), index = false means dont have row numbers in the file



hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer (
    season = '2025-26',
    season_type_all_star = 'Regular Season',
    per_mode_time = 'Totals'
)

df_hustle = hustle.get_data_frames()[0]
df_hustle_filter = df_hustle[(df_hustle['G'] >= 40) & (df_hustle['MIN'] >= 1500)]
#print(df_hustle.columns.tolist())

#print(df_hustle_filter.sort_values(['DEFLECTIONS'], ascending = False).head(20)[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT' ,'DEFLECTIONS', 'DEF_LOOSE_BALLS_RECOVERED']])
df_hustle.to_csv('data/hustle_stats.csv', index = False)


matchup = leagueseasonmatchups.LeagueSeasonMatchups(
    season = '2025-26',
    season_type_playoffs = 'Regular Season'
)

df_matchup = matchup.get_data_frames()[0]
df_matchup['MATCHUP_MIN_NUM'] = df_matchup['MATCHUP_MIN'].apply(
    lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60
)
df_matchup_filter = df_matchup[(df_matchup['GP'] >= 3) & (df_matchup['MATCHUP_MIN_NUM'] >= 20)]
print(df_matchup.columns.tolist())
print(df_matchup_filter.head(20))
print(df_matchup_filter.sort_values(['MATCHUP_FG_PCT'], ascending = True).head(20)[['OFF_PLAYER_NAME','DEF_PLAYER_NAME', 'MATCHUP_MIN', 'PLAYER_PTS', 'MATCHUP_FG_PCT', 'MATCHUP_FG3_PCT', 'HELP_FG_PERC']])

df_matchup_filter.to_csv('data/matchup_stats.csv', index = False)