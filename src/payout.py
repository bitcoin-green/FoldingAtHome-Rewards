#!/usr/bin/env python3
from cryptography.fernet import Fernet
from lib.custom import wallet_rpc
from datetime import datetime
import psycopg2
import logging
import json
import os

class Payout:
    def __init__(self, config):
        self.config     = config

        self.user       = self.config['user']
        self.passwd     = self.config['password']
        self.host       = self.config['host']
        self.port       = self.config['port']
        self.db         = self.config['database']
        self.sql        = f"{self.config['stored_sql']}workers_payout.sql"
        self.root_path  = os.path.dirname(os.path.realpath(__file__)).replace('/src', '')

        # PostgreSQL connection details
        self.connection = psycopg2.connect(
            user        = self.user,
            password    = self.passwd,
            host        = self.host,
            port        = self.port,
            database    = self.db
        )
        self.cursor = self.connection.cursor()

    def decrypt_passphrase(self, public_key):
        with open(f"{self.root_path}/configs/WPK.key") as private_key:
            p_key = Fernet(private_key.readline().encode('utf-8'))
            return p_key.decrypt(public_key.encode("utf-8"))

    def payout(self):
        logging.info(f"Running query on server, 'workers_payout.sql'")
        transacted, paid_workers, last_tx = 0, 0, wallet_rpc.lastTx()

        try:
            self.cursor.execute(open(f"{self.root_path}{self.sql}", "r").read())
            active_workers = self.cursor.fetchall()
            blockheight = wallet_rpc.block_height()

            # Adjust rewards each block halving. MAX BLOCKS: 2275000 (subject to change)
            # Once block 2,275,000 has been reached, the rewards will stay fixed to the following values until reviewed
            #   + WORK UNITS = 0.0156
            #   + CREDITS    = 0.00000003125
            if (blockheight >= 2275000):
                wu_reward = 0.0078
                credit_reward = 0.00000003125
            elif (blockheight >= 1750000):
                wu_reward = 0.0156
                credit_reward = 0.0000000625
            elif (blockheight >= 1225000):
                wu_reward = 0.0312
                credit_reward  = 0.000000125
            elif (blockheight >= 700000):
                wu_reward = 0.0625
                credit_reward  = 0.00000025
            elif (blockheight >= 175000):
                wu_reward = 0.125
                credit_reward  = 0.00000050
            else:
                wu_reward = 0.25
                credit_reward = 0.00000100

            logging.info(f"Block height: {wallet_rpc.block_height()}")
            logging.info(f"{float(wu_reward)} BITG per work unit")
            logging.info(f"{format(float(credit_reward), '.8f')} BITG per credit")

            # Check if transaction has already been sent by selecting the WUS height from transaction_audit
            # and assigning the output to variable PK_wus.
            self.cursor.execute(f"""SELECT wus
                                    FROM transaction_audit
                                    ORDER BY timestamp DESC
                                    LIMIT 1""")

            # [0][0] added to convert from list -> tuple -> integer
            # set PK_wus to zero if no transaction has ever been recorded on table [transaction_audit]
            PK_wus = self.cursor.fetchall()
            if not PK_wus:
                PK_wus = 0
            else:
                PK_wus = PK_wus[0][0]

            # useful information regarding variable 'worker':
            # wus[0] - worker_wus[1] - credits[2] - name[3] - lastupdate[4] - credit_diff[5] - wus_diff[6]
            for worker in active_workers:

                # split into ['name', 'address']
                worker_id = worker[3].split('_')

                # when split, the worker len() should be no higher than 2
                # ['cmarina', 'GcCfvEuJAbu5Tys6Nw85iCPdRYAzkApo5p']
                if len(worker_id) <= 1 or len(worker_id) > 2:

                    # One off resolution for workers with an underscore at the start of their name.
                    # EXAMPLE: '_satoshi_GXDoPDsnMdKutWwQVJNvb2iMuwFyAvUvRb'
                    # .pop(0) if worker_id length is equal to 3 and worker_id[0] is empty
                    # BEFORE: ['', 'satoshi', 'GXDoPDsnMdKutWwQVJNvb2iMuwFyAvUvRb']
                    # AFTER: ['satoshi', 'GXDoPDsnMdKutWwQVJNvb2iMuwFyAvUvRb']
                    if not worker_id[0] and len(worker_id) == 3:
                        worker_id.pop(0)
                    else:
                        continue

                # check if the wallet address is valid
                if wallet_rpc.validate_address(worker_id[1])['isvalid'] is not True:
                    continue

                # calculate rewards depending on how many work units and credits the worker has earned since
                # the last pay-out
                cr_payout = float(credit_reward) * worker[5]
                wu_payout = float(wu_reward) * worker[6]
                coin_payout = float(cr_payout) + float(wu_payout)

                # total amount of coins transacted/total workers paid during the pay-out
                transacted += coin_payout
                paid_workers = paid_workers + 1

                # add worker to payroll
                wallet_rpc.process_worker(worker_id[1], round(coin_payout, 3)) # 3 decimal places

            # send pay-out to workers
            # RPC errors reference: https://github.com/bitcoin/bitcoin/blob/v0.15.0.1/src/rpc/protocol.h#L32L87
            logging.info(json.dumps(wallet_rpc.workers, indent=4))

            # check if workers have already been paid by comparing
            # worker[0] from public.FatH_workers Column: WUS
            if int(worker[0]) != int(PK_wus):
                # decrypt wallet passphrase using private_key and unlock for 10 seconds
                # make payment before locking wallet
                password = self.decrypt_passphrase(self.config['wallet_passphrase']).decode('utf-8')
                logging.info(wallet_rpc.unlock_wallet(password, 10))
                #logging.info(wallet_rpc.pay_workers())
                wallet_rpc.lock_wallet()

                if wallet_rpc.lastTx() != last_tx:
                    logging.info("Successfully sent")
                    logging.info(f"Latest txid: {wallet_rpc.lastTx()}")
                    logging.info(f"Previous txid: {last_tx}")
                    logging.info(f"{transacted} coins transacted")
                    logging.info(f"{paid_workers} users paid")
                else:
                    logging.info("Unable to send transaction")
                    return
            else:
                logging.info("Workers already paid")

            try:
                self.cursor.execute(f""" INSERT INTO public.transaction_audit (wus, txid, transacted, total_workers, timestamp)
                                         VALUES('{worker[0]}',
                                                '{wallet_rpc.lastTx()}',
                                                '{float(transacted)}',
                                                '{paid_workers}',
                                                '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                                                """)
                self.connection.commit()
            except (Exception, psycopg2.Error) as postgre_sql_error:
                logging.info(f"An error has occurred -a, {postgre_sql_error}\n")

        except (Exception, psycopg2.Error) as postgre_sql_error:
            logging.info(f"An error has occurred -b, {postgre_sql_error}")

if __name__ == '__main__':
    with open(f"{os.path.dirname(os.path.realpath(__file__)).replace('/src', '')}/configs/data-source.json") as config:
        config = json.load(config)

        logging.basicConfig(
            filename=f"{os.path.dirname(os.path.realpath(__file__)).replace('/src', '')}{config['logging_path']}",
            level=logging.INFO,
            format="%(asctime)s:%(levelname)s:%(message)s"
        )

        sql = Payout(config)
        sql.payout()