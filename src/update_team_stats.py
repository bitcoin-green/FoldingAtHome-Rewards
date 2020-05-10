#!/usr/bin/env python3
import psycopg2
import requests
import logging
import json
import os

class updateTeamStats:
    def __init__(self, config):
        self.config     = config

        self.user       = self.config['user']
        self.passwd     = self.config['password']
        self.host       = self.config['host']
        self.port       = self.config['port']
        self.db         = self.config['database']
        self.table      = self.config['team_stats_table']
        self.team_url   = self.config['folding-api']

        # PostgreSQL connection details
        self.connection = psycopg2.connect(
            user        = self.user,
            password    = self.passwd,
            host        = self.host,
            port        = self.port,
            database    = self.db
        )
        self.cursor     = self.connection.cursor()

    def fetch_json_url(self, url):
        r = requests.get(url)
        return r.json()

    def upd_team_stats(self):
        logging.debug(f"Running [{self.table}] data update job")
        logging.debug(f"Fetching data from Folding@Home API: {self.team_url}")
        folding_api = self.fetch_json_url(self.team_url)
        try:
            logging.debug(f"Running data INSERT INTO [{self.table}]")
            self.cursor.execute(f""" INSERT INTO {self.table} (wus, rank, active_50, lastupdate, credits)
                                     VALUES ('{folding_api['wus']}', 
                                             '{folding_api['rank']}', 
                                             '{folding_api['active_50']}', 
                                             '{folding_api['last']}', 
                                             '{folding_api['credit']}') """)
            self.connection.commit()
            logging.debug(f"[{self.table}] has been successfully updated\n")

        except (Exception, psycopg2.Error) as postgre_sql_error:
            logging.debug(f"An error has occurred, {postgre_sql_error}\n")

if __name__ == '__main__':
    with open(f"{os.path.dirname(os.path.realpath(__file__)).replace('/src', '')}/configs/data-source.json") as config:
        config = json.load(config)

        logging.basicConfig(
            filename=f"{os.path.dirname(os.path.realpath(__file__)).replace('/src', '')}{config['logging_path']}",
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s:%(message)s"
        )

        sql = updateTeamStats(config)
        sql.upd_team_stats()