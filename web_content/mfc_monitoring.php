<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
    "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <title>SuperNEMO MFC Monitoring</title>
    </head>
    <body>

      <pre>

        <?php
	   echo "\n";
           echo "Mass Flow Controller Status \n";
           echo "=========================== \n";
	   echo "\nCurrent reading :           \n";
	   echo file_get_contents("/home/supernemo/FlowRateMonitoring/PR4000B_cur.txt");
           echo " \nLog : ";
	   /* echo file_get_contents("/home/supernemo/FlowRateMonitoring/PR4000B_log.txt"); */
	   echo file_get_contents("/home/supernemo/FlowRateMonitoring/PR4000B_log.txt", false, null, (filesize("/home/supernemo/FlowRateMonitoring/PR4000B_log.txt") - 1039)); 
        ?>

	</pre>

    </body>
</html>
