#!/bin/bash

## this scripts is called by crontab every minutes
## => make 4 loops with 15 sec sleep to perform
##    the measurement every 15 seconds

for loop in {0..3} ; do

  DATE=`date +%s`
  PRESSURE=`./gcdcTool --rawb --num_samples 1 | awk '{print $3}'`
  TEMPERATURE=`./gcdcTool --rawt --num_samples 1 | awk '{print $2}'`

  echo "$DATE	$PRESSURE	$TEMPERATURE" >> /home/supernemo/gcdc/gcdcTool/gcdcTool.log

  sleep 14.9

done
