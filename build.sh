#!/bin/bash
# Copyright (C) 2018-2020 The BitGreen Core developers

FatH_Team_Stats=`readlink -f src/update_team_stats.py`
root_folder=`pwd`

# set chmod +x on relevant files
if ! [ -x $FatH_Team_Stats ]; then
  echo "Setting $FatH_Team_Stats with the correct file permissions"
  chmod +x $FatH_Team_Stats
  echo " -   chmod +x applied to $FatH_Team_Stats"
fi


# check for team stat updates (every 3 hrs)
(crontab -l ; echo "0 */3 * * * ${FatH_Team_Stats} >> ${root_folder}/logs/CRONJOB.log 2>&1") | sort - | uniq - | crontab -
