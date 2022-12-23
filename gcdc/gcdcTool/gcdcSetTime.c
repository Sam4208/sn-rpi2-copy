/*
 */
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "gcdcInterface.h"

#define MAX_DEVICES 0x80

int main(int argc, char *argv[])
{
	int r = 1;
	int i;
	gusb_device_handle* devh[MAX_DEVICES];
	static int gettime_flag = 0;
	int numDevicesFound = 0;
	int verbose_flag = 0;

	r = gcdcInterfaceInit(verbose_flag);
	if (r < 0)
	{
		fprintf(stderr, "failed to initialise hardware interface\n");
		exit(1);
	}
	if(verbose_flag) printf("Interface initialized\n");

	gusb_device_handle** newList = gcdcInterfaceConnectToAvailableDevices();
	i = 0;
	while(newList[i])
	{
		devh[i] = newList[i];
		i++;
		numDevicesFound++;
	}

	{
		printf("Setting time on %d devices ... ",numDevicesFound);
		fflush(stdout);
		for(i=0;i<numDevicesFound;i++)
		{
			printf("%d ",i);
			fflush(stdout);
			gcdcInterfaceSetTimeSync(devh[i], 0, 0);
		}
		printf("\n");
	}

	if(gettime_flag) // get time from a device and display it
	{
		unsigned char timeData[TIME_REPORT_COUNT];
		for(i=0;i<numDevicesFound;i++)
		{
			int j;
			gcdcInterfaceGetTime(devh[i], timeData);
			printf("RTC Raw Time: 0x");
			for(j=0;j<TIME_REPORT_COUNT;j++) printf("%02x, ",timeData[j]);
			printf("\n");
		}
	}

//out1:
	for(i=0;i<numDevicesFound;i++)
	{
		gcdcInterfaceRelease(devh[i]);
	}

//out:
	gcdcInterfaceDeinit();
	return r >= 0 ? r : -r;
}
