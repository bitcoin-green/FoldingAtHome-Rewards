#!/usr/bin/env python3
import psycopg2
import requests
import logging
import json
import os

class UpdateStats:
    def __init__(self, config):
        self.config = config

        self.user       = self.config['user']
        self.passwd     = self.config['password']
        self.host       = self.config['host']
        self.port       = self.config['port']
        self.db         = self.config['database']
        self.table      = self.config['workers_table']
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

    def upd_worker_stats(self):
        logging.debug(f"Running [{self.table}] data update job")
        logging.debug(f"Fetching data from Folding@Home API: {self.team_url}")
        folding_api = self.fetch_json_url(self.team_url)
        new_data = []
        for worker in folding_api['donors']:
            filtered_keys = ['wus', 'credit', 'name', 'id']
            modify_worker_details = list(map(worker.get, filtered_keys))

            # Prepare worker data before insert
            # FORMAT: wus, worker_wus, credits, name, lastupdate, folding_id
            worker_details = tuple(modify_worker_details)
            worker_details = worker_details[:0] + (folding_api['wus'],) + worker_details[0:]    #1st column in table
            worker_details = worker_details[:4] + (folding_api['last'],) + worker_details[4:]   #4th column in table
            new_data.append(worker_details)
        new_data_format = ','.join(['%s'] * len(new_data))

        try:
            postgresql_query = f"INSERT INTO {self.table} (wus, worker_wus, credits, name, lastupdate, folding_id) VALUES {new_data_format}"
            logging.debug(f"Running data INSERT INTO [{self.table}]")
            self.cursor.execute(postgresql_query, new_data)
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

        sql = UpdateStats(config)
        sql.upd_worker_stats()