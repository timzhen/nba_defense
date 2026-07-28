from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import leaguehustlestatsplayer
from nba_api.stats.endpoints import leagueseasonmatchups

import pandas as pd


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


def build_defense_scores(season):
    # --- Fetch ---
    general = leaguedashplayerstats.LeagueDashPlayerStats(
        season= season,
        measure_type_detailed_defense='Defense'
    )
    df_general = general.get_data_frames()[0]

    hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
        season=season,
        season_type_all_star='Regular Season',
        per_mode_time='Totals'
    )
    df_hustle = hustle.get_data_frames()[0]

    matchup = leagueseasonmatchups.LeagueSeasonMatchups(
        season=season,
        season_type_playoffs='Regular Season'
    )
    df_matchup = matchup.get_data_frames()[0]
    df_matchup['MATCHUP_MIN_NUM'] = df_matchup['MATCHUP_MIN'].apply(
        lambda x: int(x.split(':')[0]) + int(x.split(':')[1]) / 60
    )

    print(f'  df_general shape: {df_general.shape}')
    print(f'  df_hustle shape: {df_hustle.shape}')
    print(f'  df_matchup shape: {df_matchup.shape}')

    # --- Merge ---
    df_matchup_grouped = df_matchup.groupby(['DEF_PLAYER_ID', 'DEF_PLAYER_NAME']).agg(
        avg_fg_pct_allowed=('MATCHUP_FG_PCT', 'mean'),
        avg_3fg_pct_allowed=('MATCHUP_FG3_PCT', 'mean'),
        total_possessions=('PARTIAL_POSS', 'sum'),
    ).reset_index()

    df_merge = df_general.merge(
        df_hustle,
        on='PLAYER_ID',
        suffixes=('_general', '_hustle')
    )

    df_merge = df_merge.merge(
        df_matchup_grouped,
        left_on='PLAYER_ID',
        right_on='DEF_PLAYER_ID',
        how='left'
    )

    # dropping duplicate columns
    df_merge = df_merge.drop(columns=[
        'PLAYER_NAME_hustle', 'TEAM_ID_hustle', 'TEAM_ABBREVIATION_hustle', 'AGE_hustle', 'MIN_hustle'
    ])

    df_merge = df_merge.rename(columns={
        'PLAYER_NAME_general': 'PLAYER_NAME',
        'TEAM_ID_general': 'TEAM_ID',
        'TEAM_ABBREVIATION_general': 'TEAM_ABBREVIATION',
        'AGE_general': 'AGE',
        'MIN_general': 'MIN'
    })

    print(f'  df_merge shape after merges: {df_merge.shape}')
    
    df = df_merge[(df_merge['GP'] >= 40) & (df_merge['MIN'] >= 1500)].copy()
    
    print(f'  df shape after GP/MIN filter: {df.shape}')

    # --- Normalize & score ---
    df = df_merge[(df_merge['GP'] >= 40) & (df_merge['MIN'] >= 1500)].copy()

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

    return df


# Provide your season list here, e.g. ['2022-23', '2023-24', '2024-25', '2025-26']
seasons = ['2024-25']

dfs = []
for season in seasons:
    try:
        print(f'Building defense scores for {season}...')
        df_season = build_defense_scores(season)
        df_season['SEASON'] = season
        print(f'{season} shape: {df_season.shape}')
        dfs.append(df_season)
    except Exception as e:
        print(f'Warning: failed to build defense scores for {season}: {e}')
        continue

if dfs:
    df_combined = pd.concat(dfs, ignore_index=True)
    print(df_combined.shape)
    print(df_combined[['SEASON', 'PLAYER_NAME', 'rim_protection_score', ]].head(20))
else:
    df_combined = pd.DataFrame()
    print('No seasons processed successfully.')
