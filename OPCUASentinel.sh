#!/bin/bash
# a mettre dans /etc/crontab: * *     * * *   /root/sentinelleOPCUA.sh >> newPID.log
LIMIT=3610 #limite de temps de process a surveiller: 60min et 10sec
PROCESS="MOS_Device" # nom du process a surveiller

export MOS_LIB_PATH="/MOS_ARM_4.0.1/lib"
export MOS_PATH="/MOS_ARM_4.0.1/bin"

DIRECTORY="/MOS_ARM_4.0.1/bin"
CMD_PROCESS="./MOS_Device -d /home/supernemo/OPCUAtest/testGasSystem/NewGas/trunk/resources/config/Gas_System_testV2.xml -i -p 48010 -R CMS"

count=`ps aux | grep -v grep | grep $PROCESS | awk {'print $9'} | wc -l` # le  grep -v grep evite de prendre aussi le PID du grep $PROCESS
if [ "$count" = 0 ]; then 
       echo "pas d'instance du Serveur_OPCUA, demarrage..."
       cd $DIRECTORY
       $CMD_PROCESS &

       newPID=`ps aux | grep -v grep | grep $PROCESS | awk {'print $1'} | head -$i | tail -1`
       chaine="$(date) => startPID=$newPID" 
       echo $chaine
fi
