#!/usr/bin/env python3
from datetime import datetime
import xmltodict
import psycopg2
import requests
import logging
import json
import os

class updateTeamStats:
    def __init__(self, config):
        self.config     = config

        self.user             = self.config['user']
        self.passwd           = self.config['password']
        self.host             = self.config['host']
        self.port             = self.config['port']
        self.db               = self.config['database']
        self.table            = self.config['team_stats_table']
        self.indepth_table    = self.config['team_stats_indepth_table']
        self.team_url         = self.config['folding-api']
        self.extreme_url      = self.config['extreme-api']

        # PostgreSQL connection details
        self.connection = psycopg2.connect(
            user        = self.user,
            password    = self.passwd,
            host        = self.host,
            port        = self.port,
            database    = self.db
        )
        self.cursor     = self.connection.cursor()

    def timestamp(self):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object

    def fetch_json_url(self, url):
        r = requests.get(url)
        return r.json()

    def fetch_xml_url(self, url):
        headers = {
            'User-Agent': 'BitGreen Folding@Home Project',
            'Contact': 'https://bitg.org'
        }

        r = requests.get(url, headers=headers)
        xpars = xmltodict.parse(r.text)
        json_output = json.dumps(xpars)
        return json.loads(json_output)

    def upd_team_stats(self):
        try:
            # Folding@Home stats integration
            logging.debug(f"Running [{self.table}] data update job")
            logging.debug(f"Fetching data from Folding@Home API: {self.team_url}")
            folding_api = self.fetch_json_url(self.team_url)

            logging.debug(f"Running data INSERT INTO [{self.table}]")
            self.cursor.execute(f""" INSERT INTO {self.table} (wus, rank, active_50, lastupdate, credits)
                                     VALUES ('{folding_api['wus']}',
                                             '{folding_api['rank']}',
                                             '{folding_api['active_50']}',
                                             '{folding_api['last']}',
                                             '{folding_api['credit']}') """)
            self.connection.commit()
            logging.debug(f"[{self.table}] has been successfully updated\n")

            # ExtremeOverclocking stats integration
            logging.debug(f"Running [{self.indepth_table}] data update job")
            logging.debug(f"Fetching data from ExtremeOverclocking API: {self.indepth_table}")
            extreme_api = self.fetch_xml_url(self.extreme_url)
            logging.debug(f"Running data INSERT INTO [{self.indepth_table}]")
            self.cursor.execute(f""" INSERT INTO {self.indepth_table} (rank, active_users, 
                                                                       total_users, change_rank_24hr, 
                                                                       points_24hr_avg, points_last_24hr, 
                                                                       points_update, points_today, 
                                                                       points_week, timestamp)
                                     VALUES ('{extreme_api['EOC_Folding_Stats']['team']['Rank']}', 
                                             '{extreme_api['EOC_Folding_Stats']['team']['Users_Active']}', 
                                             '{extreme_api['EOC_Folding_Stats']['team']['Users']}', 
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_24hr_Avg']}', 
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_Last_24hr']}',
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_Last_7days']}',
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_Update']}',
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_Today']}',
                                             '{extreme_api['EOC_Folding_Stats']['team']['Points_Week']}',
                                             '{self.timestamp()}') """)
            self.connection.commit()
            logging.debug(f"[{self.indepth_table}] has been successfully updated\n")

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