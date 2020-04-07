#!/usr/bin/env python3
# Copyright (C) 2018-2020 The BitGreen Core developers
# WUS is the PRIMARY KEY
# INSERT team stats from https://stats.foldingathome.org/api/team/251327 INTO [public.fath_team_stats]

from datetime import datetime
import psycopg2
import requests
import logging
import json
import os

logging.basicConfig(
    filename=f"{os.path.dirname(os.path.realpath(__file__))}/logs/F@H_Team_Stats.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

def fetch_json_file(path):
    with open(path) as json_file:
        data = json.load(json_file)
        return data

class UpdateStats:
    def __init__(self, user, passwd, host, port, db, team_url):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.db = db
        self.team_url = team_url

        # PostgreSQL connection details
        self.connection = psycopg2.connect(
            user        = self.user,
            password    = self.passwd,
            host        = self.host,
            port        = self.port,
            database    = self.db
        )
        self.cursor = self.connection.cursor()

    def fetch_json_url(self, url):
        r = requests.get(url)
        return r.json()

    def upd_team_stats(self):
        folding_api = self.fetch_json_url(self.team_url)
        try:
            self.cursor.execute(f""" INSERT INTO FatH_Team_Stats (wus, rank, active_50, lastupdate, credits)
                                     VALUES ('{folding_api['wus']}', '{folding_api['rank']}', '{folding_api['active_50']}', '{folding_api['last']}', '{folding_api['credit']}') """)
            self.connection.commit()

            print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] - FatH_Team_Stats' has been successfully updated")
            logging.debug(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] - 'FatH_Team_Stats' has been successfully updated")

        except (Exception, psycopg2.Error) as postgre_sql_error:
            print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] - An error has occurred, {postgre_sql_error} (check: 'F@H_Team_Stats.log')")
            logging.debug(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] - An error has occurred, {postgre_sql_error}")

if __name__ == '__main__':
    config = fetch_json_file(f"{os.path.dirname(os.path.realpath(__file__))}/configs/data-source.json")
    sql = UpdateStats(config['user'],
                      config['password'],
                      config['host'],
                      config['port'],
                      config['database'],
                      config['folding-api'])
    sql.upd_team_stats()