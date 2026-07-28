from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time

def fetch_season_defense(season, max_retries=5, delay=15):
    for attempt in range(max_retries):
        try:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                season_type_all_star='Regular Season',
                measure_type_detailed_defense='Defense'
            )
            df = stats.get_data_frames()[0]
            if not df.empty:
                return df
            print(f'  {season}: empty, retrying ({attempt+1}/{max_retries})...')
        except Exception as e:
            print(f'  {season}: error {e}, retrying ({attempt+1}/{max_retries})...')
        time.sleep(delay)
    print(f'  {season}: FAILED after {max_retries} attempts')
    return None

seasons_to_test = ['2017-18', '2020-21', '2021-22', '2024-25']

for season in seasons_to_test:
    df = fetch_season_defense(season)
    if df is not None:
        print(f'{season}: SUCCESS - {df.shape[0]} rows')
    time.sleep(10)  # extra pause between different seasons too