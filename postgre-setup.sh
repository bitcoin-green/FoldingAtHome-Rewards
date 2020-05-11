#!/bin/bash
# Enviroment: Ubuntu 18.04

apt-get jq cowsay -y

usr=`cat configs/data-source.json | jq -r '.user'`
db=`cat configs/data-source.json | jq -r '.database'`
teamstats_tbl_name=`cat configs/data-source.json | jq -r '.team_stats_table' `s
worker_tbl_name=`cat configs/data-source.json | jq -r '.workers_table' `s
txaudit_tbl_name=`cat configs/data-source.json | jq -r '.tx_audit' `s

cowsay "Folding@Home PostgreSQL setup"
read -p "Enter PostgreSQL server password: " -s passwd; printf "\n"

postgre_handler(){
  case $1 in
    *"already exists"*)
      echo "    - Already exists! - case test"
    ;;
    *"CREATE DATABASE"*)
      echo "    - successfully created!"
    ;;
    *"CREATE TABLE"*)
      echo "    - successfully created!"
    ;;
    *"authentication failed"*)
      echo "    - [AUTHENTICATION FAILED]"
    ;;
  esac
}

## CREATE DATABASE: foldingathome ###
echo "+ Creating database: $db"
create_db="$(psql "postgresql://$usr:$passwd@localhost/postgres" -c "CREATE DATABASE $db" 2>&1)"
postgre_handler "$create_db"

create_teamstats_tbl="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$teamstats_tbl_name
                                                                      (
                                                                        wus bigint NOT NULL UNIQUE,
                                                                        rank bigint NOT NULL,
                                                                        active_50 bigint NOT NULL,
                                                                        lastupdate timestamp without time zone NOT NULL,
                                                                        credits bigint NOT NULL
                                                                      )" 2>&1)"
                                                                      
create_workers_tbl="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$worker_tbl_name
                                                                          (
                                                                              wus bigint NOT NULL,
                                                                              worker_wus bigint NOT NULL,
                                                                              credits bigint NOT NULL,
                                                                              name VARCHAR(125),
                                                                              lastupdate timestamp without time zone NOT NULL,
                                                                              folding_id bigint NOT NULL
                                                                          )" 2>&1)"
create_txaudit_tbl="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$worker_tbl_name
                                                                          (
                                                                              wus bigint NOT NULL,
                                                                              txid varchar(125) NOT NULL,
                                                                              transacted numeric NOT NULL,
                                                                              total_workers bigint NOT NULL,
                                                                              'timestamp' timestamp without time zone NOT NULL
                                                                          )" 2>&1)"

echo "+ Creating table(s): '$teamstats_tbl_name'\n$worker_tbl_name\n$txaudit_tbl_name"
postgre_handler "$create_teamstats_tbl"
postgre_handler "$create_workers_tbl"
postgre_handler "$create_txaudit_tbl"
