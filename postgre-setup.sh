#!/bin/bash
# Copyright (C) 2018-2020 The BitGreen Core developers Folding@Home Project
# Enviroment: Ubuntu 18.04

#apt update
#apt install postgresql postgresql-contrib
#apt install jq
#apt install cowsay

usr=`cat configs/data-source.json | jq -r '.user'`
db=`cat configs/data-source.json | jq -r '.database'`
ts_table_name=`cat configs/data-source.json | jq -r '.team_stats_table' `s
worker_table_name=`cat configs/data-source.json | jq -r '.workers_table' `s

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

## CREATE TABLE: FaTH_Team_Stats ####
echo "+ Creating table: '$ts_table_name'"
create_ts_table="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$ts_table_name
                                                                      (
                                                                        wus bigint NOT NULL UNIQUE,
                                                                        rank bigint NOT NULL,
                                                                        active_50 bigint NOT NULL,
                                                                        lastupdate timestamp without time zone NOT NULL,
                                                                        credits bigint NOT NULL
                                                                      )" 2>&1)"
postgre_handler "$create_ts_table"

## CREATE TABLE: FaTH_Workers #######
echo "+ Creating table: '$worker_table_name'"
create_worker_table="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$worker_table_name
                                                                          (
                                                                              wus bigint NOT NULL,
                                                                              worker_wus bigint NOT NULL,
                                                                              credits bigint NOT NULL,
                                                                              name VARCHAR(125),
                                                                              lastupdate timestamp without time zone NOT NULL,
                                                                              folding_id bigint NOT NULL
                                                                          )" 2>&1)"
postgre_handler "$create_worker_table"

## CREATE TABLE: FaTH_Workers #######
echo "+ Creating table: '$worker_table_name'"
create_worker_table="$(psql "postgresql://$usr:$passwd@localhost/$db" -c "CREATE TABLE public.$worker_table_name
                                                                          (
                                                                              wus bigint NOT NULL,
                                                                              worker_wus bigint NOT NULL,
                                                                              credits bigint NOT NULL,
                                                                              name VARCHAR(125),
                                                                              lastupdate timestamp without time zone NOT NULL,
                                                                              folding_id bigint NOT NULL
                                                                          )" 2>&1)"
postgre_handler "$create_worker_table"
