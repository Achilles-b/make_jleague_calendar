import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
from typing import Tuple
import os
import sys
import shutil
from datetime import datetime

from make_jleague_calendar_const import MakeJleagueCalendarConst as const

class MakeJleagueCalendar():
    # クラス変数
    BASE_URL = const.BASE_URL

    def __init__(self):
        # インスタンス変数
        self.base_url = MakeJleagueCalendar.BASE_URL

        # loggerの設定
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)
    
    def main(self):
        # スクレイピングによりチームIDとチーム名の対応表を取得
        self.logger.info("処理No1：スクレイピングによりチームIDとチーム名を取得")
        df_team_id = self.scraping_get_team_id()

        # 対象チーム名を入力し、それに対応するチームIDを取得
        self.logger.info("処理No2：カレンダーを作成したいチームを指定")
        self.team_name, team_id = self.input_team_name(df_team_id)

        # チームIDをもとにスクレイピングをし、取得したい年のスケジュールを得る
        self.logger.info("処理No3：対象チーム・対象年度のスケジュール取得")
        self.df_schedule, self.schedule_year = self.scraping_get_schedule(team_id)

        # dfをGoogleカレンダー登録用に整形
        self.logger.info("処理No4：データの整形")
        self.edited_df = self.edit_df(self.df_schedule)
        
        # csvで結果を出力
        self.logger.info("処理No5：データの出力")
        self.output_csv(self.edited_df)
    
    def scraping_get_team_id(self) -> pd.DataFrame:
        """
        スクレイピングによりチームIDとチーム名を取得

        Returns:
            pd.DataFrame: チームIDとチーム名が格納されたDataFrame
        """
        try:
            #set url
            url_for_get_dataframe = const.BASE_URL_FOR_SEARCH
            soup_for_df_team = self.get_responce(url_for_get_dataframe)

            # チーム情報が記載されている要素を取得
            team_ids_check_box = soup_for_df_team.select_one('div.box-s-base select[name="team_ids"]')

            # チーム情報を抽出してDataFrameに格納
            team_id_list = []
            team_name_list = []
            for team in team_ids_check_box.find_all('option'):
                team_id = team.get('value')
                team_name = team.text
                team_id_list.append(team_id)
                team_name_list.append(team_name)

            df_team = pd.DataFrame({'team_id': team_id_list, 'team_name': team_name_list})
            self.logger.debug(df_team)
            return df_team

        except Exception as e:
            self.logger.error(str(e))

    def get_responce(self, url:str) -> BeautifulSoup:
        """Beautifulsoupを用いてスクレイピング

        Args:
            url (str): 対象URL

        Returns:
            BeautifulSoup: スクレイピング結果
        """
        try:
            response = requests.get(url)
            
            # スクレイピング結果からHTML抽出
            soup = BeautifulSoup(response.text, "html.parser")
            return soup

        except Exception as e:
            self.logger.error(str(e))


    def input_team_name(self, df_team:pd.DataFrame) -> Tuple[str, int]:
        """チーム名を入力することでスクレイピングに必要な数字を返却する

        Returns:
            Tuple[str, int]: チーム名とスクレイピングで用いるチームIDのタプル
        """
        self.logger.info(f"チーム名を入力してください\nチーム名一覧はこちら：\n{df_team['team_name'].tolist()}\n######")
        search_team_name = str(input("チーム名："))
        try:
            # データフレームからチーム名を検索
            team_id = df_team.loc[df_team['team_name'] == search_team_name, 'team_id'].values[0]
            self.logger.info(f"{search_team_name}のidを入手できました。idは{team_id}です。")
            return search_team_name, team_id
            
        except:
            self.logger.error("正しくデータ取得ができなかったため終了します")
        
    def scraping_get_schedule(self, team_id:int) -> Tuple[pd.DataFrame, int]:
        """取得したチームIDをもとにスクレイピングを行い、スケジュールを取得

        Args:
            team_id (int): 日程を取得したいチームID

        Returns:
            Tuple[pd.DataFrame, int]: スケジュールと取得したスケジュールの年
        """
        try:
            year = int(input("スケジュールを取得したい年をyyyyで記載 (例: 2023):"))
            url_for_schedule = const.BASE_URL_FOR_SCHEDULE.format(
                year = year,
                team_id = team_id
            )
            soup_for_schedule = self.get_responce(url_for_schedule)

            # スケジュールが書いてある部分を見つける
            schedule = soup_for_schedule.find("table", class_="table-base00 search-table").find('tbody').find_all('tr')

            # 列のラベルを取得してリストに格納する
            columns = []
            thead = soup_for_schedule.find('table', class_='table-base00 search-table').find('thead')
            for th in thead.find_all('th'):
                columns.append(th.get_text(strip=True))
            
            # 取得結果をデータフレームに変換
            data = []
            for row in schedule:
                cells = row.find_all('td')
                if len(cells) > 0:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    data.append(row_data)

            df_scledule = pd.DataFrame(data, columns=columns)
            self.logger.debug(f"columns: {df_scledule.columns}")
            self.logger.debug(f"df_schedule.head: {df_scledule.head()}")

            return df_scledule, year
        
        except Exception as e:
            self.logger.error(str(e))
            
    def edit_df(self, df_schedule: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrameをGoogleカレンダーに登録できる形に成形する
        Args:
            df_schedule (pd.DataFrame): スクレイピングで取得したデータフレーム
        
        Returns:
            pd.DataFrame: 整形後のDataFrame
        """
        try:
            # 必要なカラムを選択し、日付や時間を整形する
            edited_df = pd.DataFrame({
                'Subject': df_schedule['ホーム'] + ' vs ' + df_schedule['アウェイ'] + ' @ ' + df_schedule['スタジアム'],
                'Start Date': '2023/' + df_schedule['試合日'].str[:2] + '/' + df_schedule['試合日'].str[3:5],
                'End Date': '2023/' + df_schedule['試合日'].str[:2] + '/' + df_schedule['試合日'].str[3:5],
                'Start Time': df_schedule['K/O時刻'],
                'End Time': pd.to_datetime(df_schedule['K/O時刻']) + pd.to_timedelta('2 hours')
            })


            # # カラムを結合する
            # edited_df['Subject'] = edited_df['Subject'] + ' ' + edited_df['Start Date'].dt.strftime('%m/%d(%a)')
            # edited_df['Start Time'] = edited_df['Start Date'].dt.strftime('%m/%d/%Y ') + edited_df['Start Time'].astype(str)
            # edited_df['End Time'] = edited_df['End Date'].dt.strftime('%m/%d/%Y ') + edited_df['End Time'].astype(str)

            self.logger.debug(f"edited_df: {edited_df.head()}")
            return edited_df

        except Exception as e:
            self.logger.error(str(e))
            sys.exit


    def output_csv(self, edited_df) -> None:
        """
        dataframeをcsvに変換し、出力する

        Args:
            None
        """
        # make_jleague_calendar.pyの実行ファイルが存在するディレクトリを取得
        script_dir = os.path.dirname(__file__)

        # ディレクトリを作成
        data_dir = os.path.join(script_dir, 'data')
        self.logger.debug(f"data_dir:{data_dir}")

        # dataディレクトリが存在しない場合には作成
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.logger.debug(f"data_dir: {data_dir}")

        # データフレームをcsvに変換
        self.logger.info("データフレームをcsvに変換します。")

        now = datetime.now()
        now_string = now.strftime("%Y%m%d%H%M%S")
        csv_file_path = f"JLeagueSChedule_{self.team_name}_{self.schedule_year}_{now_string}.csv"
        schedule_csv = edited_df.to_csv(os.path.join(data_dir, csv_file_path), index=False)

        self.logger.info("データフレームをcsvに変換しました。")


if __name__ == '__main__':
    make_jleague_calendar = MakeJleagueCalendar()
    make_jleague_calendar.main()
