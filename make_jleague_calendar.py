import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import logging

from make_jleague_calendar_const import MakeJleagueCalendarConst as const

class MakeJleagueCalendar():
    # クラス変数
    BASE_URL = const.BASE_URL

    def __init__(self):
        # こちらはインスタンス変数
        self.base_url = MakeJleagueCalendar.BASE_URL

        # loggerの設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # TODOloggerの設定
        # formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        # file_handler = logging.FileHandler('jleague.log')
        # file_handler.setFormatter(formatter)
        # self.logger.addHandler(file_handler)
    
    def main(self):
        # set URL
        url_for_get_teamid = f"{self.base_url}search?teamType=1"
        table_for_get_teamid = self.scraping(url_for_get_teamid, "scheduleTable")

        self.logger.debug(table_for_get_teamid)

    def scraping(self, url:str, tableclass:str) -> BeautifulSoup:
        """
        スクレイピングを行って元データを取得する
        """
        # get HTML
        self.responce= requests.get(url)
        self.html = self.responce.text

        # make beautifulsoup object
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.logger.debug(self.soup)

        # get table data
        self.table = self.soup('table', class_=tableclass)

        return self.table

if __name__ == '__main__':
    make_jleague_calendar = MakeJleagueCalendar()
    make_jleague_calendar.main()