import pandas as pd
import datetime
import os

class MakeJleagueCalendar():
    def __init__():
        pass

    def main():
        print("hoge")

    def scraping():
        """
        スクレイピングを行って元データを取得する
        """
        
        url = f"https://data.j-league.or.jp/SFMS01/search?competition_years={year}&competition_frame_ids=1&competition_frame_ids=11&team_ids={team_id}&home_away_select=0&tv_relay_station_name="



url = "https://data.j-league.or.jp/SFMS01/search?competition_years=2023&competition_frame_ids=1&competition_frame_ids=11&team_ids=18&home_away_select=0&tv_relay_station_name="
df = pd.read_html(url, attrs={'class': 'table-base00 search-table'}, skiprows=0)
print(type(df))
print(df)

if __name__ == '__main__':

    make_jleague_calendar = MakeJleagueCalendar()
    make_jleague_calendar.main()