#!/bin/bash

FatH_Team_Stats=`readlink -f src/update_team_stats.py`
FatH_Workers=`readlink -f src/update_workers_stats.py`
FatH_Payment=`readlink -f src/payout.py`
root_folder=`pwd`

chmod_file(){
  if ! [ -x $1 ]; then
    echo "Setting $1 with the correct permissionns."
    chmod +x $1
    echo " - chmod +x applied!"
  fi
}

# set chmod +x on relevant files
chmod_file "$FatH_Team_Stats"
chmod_file "$FatH_Workers"
chmod_file "$FatH_Payment"

# check for team stat updates (every 3 hrs)
(crontab -l ; echo "0 */3 * * * ${FatH_Team_Stats} >> ${root_folder}/logs/CRONJOB.log 2>&1") | sort - | uniq - | crontab -
(crontab -l ; echo "1 */3 * * * ${FatH_Workers} >> ${root_folder}/logs/CRONJOB.log 2>&1") | sort - | uniq - | crontab -
(crontab -l ; echo "3 */3 * * * ${FatH_Payment} >> ${root_folder}/logs/CRONJOB.log 2>&1") | sort - | uniq - | crontab -