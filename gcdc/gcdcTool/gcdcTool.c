/*
 */

/*----------------------------------------------------------------------------
*        Headers
*----------------------------------------------------------------------------*/
//#define TRACE_LEVEL TRACE_LEVEL_DEBUG
#include "trace.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>
#include <math.h>	// sqrt
#include <time.h>
#include <sys/time.h>
#ifdef __MINGW32__
#include "asm/types.h"
#endif
#include "gcdc.h"
#include "gcdcInterface.h"
#include "firmwareUpdater.h"
#ifdef PTHREAD_UPDATER
//#warning using pthreads for updating firmware
#include "pthreadUpdater.h"
#endif
#include "atmelsam_ba.h"
#include "jsonformat.h"

extern char* version_string;

int verbose_flag = 0;
#define MAX_SERIAL_NUM 0x80
#define MAX_FILENAME 0x100
#define MAX_DEVICES 0x80
#define US_PER_SEC (1000*1000)
#define ST_HI 3

void usage()
{
	printf("gcdcTool - a tool for working with GCDC USB based devices\n");
	printf("\t for more information contact http://www.gcdataconcepts.com\n");
	printf("gcdcTool [--options] [file] \n");
	printf(" There is no default option, select desired action from list below\n");
	printf("\t--gcdcTool [--options] [arg] \n");
	printf("\t--verbose           provides internal diagnostics\n");
	printf("\t--version           outputs current version\n");
	printf("\t--brief             suppreses chatter\n");
	printf("\t--avail             lists the available device serial numbers\n");
	printf("\t--ignoresn          connects to devices without regard to serial number, usefull for low level programming\n");
	printf("\t--test              calculates mean and std dev of unit(s) with respect to a reference unit\n");
	printf("\t--test2             displays pressure info from connected units\n");
	printf("\t--settime           sets the time to the current time of day for all attached devices\n");
	printf("\t--timeutc           sets the time to the current time of day in UTC\n");
	printf("\t--gettime           reads and displays the internal time of the real time clock\n");
	printf("\t--selfteston 	      turns on the self test feature\n");
	printf("\t--selftestoff	      turns on the self test feature\n");
	printf("\t--raw               reads and displays raw data from an accelerometer\n");
	printf("\t--rawb              reads and displays raw data from a barometer\n");
	printf("\t--rawh              reads and displays raw data from a humidity sensor\n");
	printf("\t--rawm              reads and displays raw data from a magnetometer\n");
	printf("\t--rawf              reads and displays frequency data from tachometer\n");
	printf("\t--rawd              reads and displays adc data\n");
	printf("\t--gps		      displays gps data\n");
	printf("\t--json              output using JSON format\n");
	printf("\t--pps               reads and displays the pulse per second message\n");
	printf("\t--ref serNum        sets the serial number of the reference unit to use in tests\n");
	printf("\t--dut serNum        explicitly calls out the device serial number to test\n");
	printf("\t--update filename   update the firmware on the device filename is a hex file\n");
	printf("\t--sam_ba_program filename   program a sam-ba device filename is a .bin file\n");
	printf("\t--toACM0	      set sam_ba device to go into ACM0 mode and exit\n");
	printf("\t--num_samples n     set the number of samples to use in the test\n");
	printf("\t--offset  microsec  adjust the time given to the unit by this number of microseconds, useful when nulling out system delays\n");
	printf("\t--smbusread  	      get values from an smbus device\n");
	printf("\t--cmd string        send ascii command to device an get response\n");
	printf("\t--addr 0xaa  	      when smbus is selected, used to provide the device address, default is 0xD0\n");
	printf("\t--start nn  	      when smbus is selected, used to provide the starting offset register, default is 0\n");
	printf("\t--len  nn  	      when smbus is selected, used to provide the number of bytes to transfer, default is 1\n");
	printf("\t--raw_td            during test3, outputs raw test data\n");
	printf("\t--help              this help info\n");
}

#define MAX_CMD_STRING 0x40

static uint8_t* binToInt32(int32_t* dst, uint8_t* src)
{
	*dst = *src++;
	*dst |= *(src++) <<8;
	*dst |= *(src++) <<16;
	*dst |= *(src++) <<24;
	return(src);
}

static void printGpsLlhReport(uint8_t* p1)
{
	uint8_t* ptr = p1;

	uint32_t tow;
	ptr= binToInt32((int32_t*)&tow, ptr);
	double ftow = tow;
	ftow = ftow / 1000.0;

	int32_t lat;
	int32_t lon;
	ptr = binToInt32(&lon,ptr);
	ptr = binToInt32(&lat, ptr);
	double flat = lat;
	double flon = lon;
	flat = flat/1e7;
	flon = flon/1e7;

	int32_t height;
	int32_t hMSL;
	ptr = binToInt32(&height,ptr);
	ptr = binToInt32(&hMSL, ptr);
	double fheight = height;
	fheight = fheight / 1000.0;
	double fhMSL = hMSL;
	fhMSL = fhMSL / 1000.0;

	uint32_t hAcc;
	ptr = binToInt32((int32_t*)(&hAcc),ptr);
	uint32_t vAcc;
	ptr = binToInt32((int32_t*)(&vAcc),ptr);
	double fhAcc = hAcc;
	double fvAcc = vAcc;
	fhAcc /=1000.0;
	fvAcc /=1000.0;
//	int i;
	printf("%8.3f, %3.7f, %4.7f, %4.3f, %4.3f, %3.3f, %3.3f", ftow, flat, flon, fheight, fhMSL, fhAcc, fvAcc);
//	for(i=0; i<64-9; i++)
//	{
//		printf("%02x ", p1[i]);
//		if(i%16==15) printf("\n");
//	}
}

int main(int argc, char *argv[])
{
//	struct sigaction sigact;
	int r = 1;
	int i;
	int c;
	char refSerialNum[MAX_SERIAL_NUM];
	char dutSerialNum[MAX_SERIAL_NUM];
	gusb_device_handle* devh[MAX_DEVICES];
	gusb_device_handle* refDevh = NULL;
	gusb_device_handle* dutDevh = NULL;
	char filename[MAX_FILENAME];
	static int update_flag = 0;
	static int sam_ba_prog_flag = 0;
	static int toACM0_flag = 0;
	static int show_avail_flag = 0;
	static int test_flag = 0;
	static int raw_flag = 0;
	static int rawb_flag = 0;
	static int raw_gps_flag = 0;
	static int raw_lux_flag = 0;
	static int raw_ppg_flag = 0;
	static int rawh_flag = 0;
	static int pps_flag = 0;
	static int json_flag = 0;
	static int rawg_flag = 0;
	static int rawa_flag = 0;
	static int rawq_flag = 0;
	static int rawt_flag = 0;
	static int rawm_flag = 0;
	static int rawf_flag = 0;
	static int rawd_flag = 0;
	static int settime_flag = 0;
	static int utc_flag = 0;
	static int gettime_flag = 0;
	static int test2_flag = 0;
	static int test3_flag = 0;
	static int flagIgnoreSerialNums = 0;
	int settleTime = 8;
	int baroSettleTime = 0;

	static int smbus_flag = 0;
	static int smbus_write_flag = 0;
	static uint8_t smbusDevice = 0xD0;	//default device address, ds3231 rtc
	static uint8_t smbusOffset = 0;	//default smbus offset
	static uint8_t smbusLen = 1;		//default number of smbus bytes to read

	static int gain_hi_flag = 0;
	static int gain_low_flag = 0;
	static int selftest_on_flag = 0;
	static int selftest_off_flag = 0;
	static int numTestSamples = 16;
	static int bFlagCount;
	static int offsetTime = 0;

	int raw_num = -1;

	char* serialNums[MAX_DEVICES];
	char temp[MAX_DEVICES][MAX_SERIAL_NUM];

	char cmdString[MAX_CMD_STRING];
	static int sendCmd_flag = 0;

	uint8_t smbusWriteBuffer[0x40];
	int flushCount=32;
	int retval;
	FILE* rawdata_fd = NULL;



	for(i=0;i<MAX_DEVICES;i++)
	{
		serialNums[i] = temp[i];
	}
	int numDevicesFound=0;

	refSerialNum[0] = '\0';
	dutSerialNum[0] = '\0';

	// Parse command-line options.
	while(1)
	{
		static struct option long_options[] =
		{
		/* These options set a flag. */
			{"verbose", 	no_argument,	&verbose_flag,	1},
			{"brief",   	no_argument,	&verbose_flag,	0},
			{"avail",   	no_argument,	&show_avail_flag, 1},
			{"ignoresn",   	no_argument,	&flagIgnoreSerialNums, 1},
			{"test", 	no_argument,	&test_flag,	1},
			{"test2", 	no_argument,	&test2_flag,	1},
			{"test3", 	no_argument,	&test3_flag,	1},
			{"higain",	no_argument,	&gain_hi_flag,	1},
			{"lowgain",	no_argument,	&gain_low_flag,	1},
			{"selfteston",	no_argument,	&selftest_on_flag,	1},
			{"selftestoff",	no_argument,	&selftest_off_flag,	1},
//			{"raw", 	no_argument,	&raw_flag,	1},
//			{"rawb",	no_argument,	&rawb_flag,	1},
//			{"rawg",	no_argument,	&rawg_flag,	1},
//			{"rawt",	no_argument,	&rawt_flag,	1},
//			{"rawm",	no_argument,	&rawm_flag,	1},
			{"toACM0",	no_argument,	&toACM0_flag,	1},
			{"smbusread",	no_argument,	&smbus_flag,	1},
			{"smbuswrite",	no_argument,	&smbus_write_flag,	1},
			{"settime",	no_argument,	&settime_flag,	1},
			{"timeutc",	no_argument,	&utc_flag,	1},
			{"gettime",	no_argument,	&gettime_flag,	1},
			/* These options don't set a flag. We distinguish them by their indices. */
			{"ref",  	required_argument, 0, 'a'},
			{"dut",  	required_argument, 0, 'b'},
			{"update",  	required_argument, 0, 'u'},
			{"sam_ba_program",  	required_argument, 0, 's'},
			{"cmd",  	required_argument, 0, 'C'},
			{"num_samples", required_argument, 0, 'c'},
			{"settle_time", required_argument, 0, 't'},
			{"offset",  	required_argument, 0, 'd'},

			// the following are used the smbus flag
			{"addr",  	required_argument, 0, 'e'},
			{"start",	required_argument, 0, 'f'},
			{"len",		required_argument, 0, 'g'},
			{"ppg",		required_argument, 0, 'k'},

			{"raw_td", 	optional_argument,	0,	'E'},
			{"raw", 	optional_argument,	0,	'h'},
			{"rawb",	optional_argument,	0,	'B'},
			{"rawh",	optional_argument,	0,	'H'},
			{"rawg", 	optional_argument,	0,	'G'},
			{"rawa", 	optional_argument,	0,	'A'},
			{"rawm", 	optional_argument,	0,	'M'},
			{"rawf", 	optional_argument,	0,	'F'},
			{"rawq", 	optional_argument,	0,	'Q'},
			{"rawt", 	optional_argument,	0,	'T'},
			{"rawd",	optional_argument,	0,	'D'},
			{"pps",		optional_argument,	0,	'p'},
			{"gps",		optional_argument,	0,	'P'},
			{"lux",		optional_argument,	0,	'L'},
			{"json",	no_argument, 0,	'j'},
			{"help",	no_argument, 0, '?'},
			{"version",	no_argument, 0, 'v'},
			{0, 0, 0, 0}
		};

		int option_index = 0;
		c = getopt_long (argc, argv, "abc:d:f:s:",long_options, &option_index);
		/* Detect the end of the options. */
		if (c == -1)
		break;

		switch(c)
		{
		case 0:
			/* If this option set a flag, do nothing else now. */
			if (long_options[option_index].flag != 0)
			break;
			printf ("option %s", long_options[option_index].name);
			if (optarg)
				printf (" with arg %s", optarg);
			printf ("\n");
			break;
		case 'a':
			strncpy(refSerialNum,optarg, MAX_SERIAL_NUM);
			if(verbose_flag) printf("Reference Serial Number <%s>\n",refSerialNum);
			break;
		case 'b':
			strncpy(dutSerialNum,optarg, MAX_SERIAL_NUM);
			if(verbose_flag) printf("Device Serial Number <%s>\n",refSerialNum);
			break;
		case 'c':
			numTestSamples = atoi(optarg);
			bFlagCount = 1;
			if(verbose_flag) printf("Num samples %dn",numTestSamples);
			break;
		case 'd':
			offsetTime = atoi(optarg);
			if(verbose_flag) printf("offset for settime %d\n",offsetTime);
			break;
		case 'e':
			smbusDevice = strtol(optarg, NULL ,0);
			if(verbose_flag) printf("smbus device: 0x%02x\n",smbusDevice);
			break;
		case 'f':
			smbusOffset = strtol(optarg, NULL ,0);
			if(verbose_flag) printf("smbus offset: 0x%02x\n",smbusOffset);
			break;
		case 'g':
			smbusLen = strtol(optarg, NULL ,0);
			if(verbose_flag) printf("smbus num Bytes to read: 0x%02x\n",smbusLen);
			break;
		case 'h':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			raw_flag=1;
			break;
		case 'P':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			raw_gps_flag=1;
			break;
		case 'L':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			raw_lux_flag=1;
			break;
		case 'k':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			raw_ppg_flag=1;
			break;
		case 'E':
			if(optarg == NULL)
			{
				rawdata_fd= fopen("rawdata.txt", "w");
			}
			else
			{
				rawdata_fd= fopen(optarg, "w");
//				printf("raw will collect %d samples\n",raw_num);
			}
			break;
		case 'B':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			rawb_flag=1;
			break;
		case 'H':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			rawh_flag=1;
			break;

		case 'p':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			pps_flag=1;
			break;

		case 'G':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawg_flag=1;
		break;
		case 'A':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawa_flag=1;
		break;
		case 'Q':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawq_flag=1;
		break;
		case 'M':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawm_flag=1;
		break;
		case 'F':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawf_flag=1;
		break;
		case 'T':
			if(optarg == NULL)
				raw_num = -1;
			else
				raw_num = atoi(optarg);
			rawt_flag=1;
		break;
		case 'D':
			if(optarg == NULL)
			{
				raw_num = -1;
			}
			else
			{
				raw_num = atoi(optarg);
//				printf("raw will collect %d samples\n",raw_num);
			}
			rawd_flag=1;
			break;
		case 'C':
			strncpy(cmdString, optarg, MAX_CMD_STRING);
			sendCmd_flag = 1;
			if(verbose_flag) printf("cmd string: <%s>",cmdString);
			break;
		case 'u':
			strncpy(filename,optarg, MAX_FILENAME);
			if(verbose_flag) printf("updating with <%s>\n",filename);
			update_flag = 1;
			break;
		case 's':
			strncpy(filename,optarg, MAX_FILENAME);
			if(verbose_flag) printf("programing with <%s>\n",filename);
			sam_ba_prog_flag = 1;
			break;
		case 't':
			settleTime = atoi(optarg);
			baroSettleTime = settleTime;
			if(verbose_flag) printf("settle time %d\nn",settleTime);
			break;
		case 'j':
			json_flag = 1;
			break;
		case 'v':
			printf("gcdcTool Version: %s\n",version_string);
			printf("Copyright 2009, Gulf Coast Data Concepts, LLC\n");
			exit(0);
			break;
		case '?': /* getopt_long already printed an error message. */
			usage("Usage\n");
			exit(0);
			break;
		default:
			usage();
			abort ();
		}
	}
	/* Print any remaining command line arguments (not options). */
	if (optind < argc)
	{
		i=0;
		if(smbus_write_flag)
		{
			while(optind < argc)
			{
				if(verbose_flag) printf("%s ", argv[optind]);
				if(smbus_write_flag) smbusWriteBuffer[i++] = strtol(argv[optind],NULL,0);
				optind++;
			}
			if(smbusLen < i)
				smbusLen = i;
			if(verbose_flag)
				printf("\n");
		}
		else
		{
			printf("non-option ARGV-elements: ");
			while(optind < argc)
			{
				printf("%s ", argv[optind++]);
			}
			printf("\n");
		}
	}
	if(verbose_flag)
	{
		printf("gcdcTool VERSION %s\n",version_string);
	}
	r = gcdcInterfaceInit(verbose_flag);
	if (r < 0) {
		fprintf(stderr, "failed to initialise hardware interface\n");
		exit(1);
	}
	if(verbose_flag) printf("Interface initialized\n");

	numDevicesFound = gcdcInterfaceGetSerialNumbers( serialNums, MAX_DEVICES, MAX_SERIAL_NUM);
	if(numDevicesFound <1)
	{
		if(!sam_ba_prog_flag)
		{
			printf("Wasn't able to find devices %d\n",numDevicesFound);
			r = -2;
			goto out;
		}
		numDevicesFound = 0;
	}
	if( numDevicesFound > MAX_DEVICES) numDevicesFound = MAX_DEVICES;

	if(show_avail_flag)
	{// display available serial numbers
		printf("Devices Found\n");
		for(i=0;i<numDevicesFound;i++)
		{
			printf("\tsn: <%s>\n",serialNums[i]);
		}
	}

	if(!flagIgnoreSerialNums)
	{
		for(i=0;i< numDevicesFound;i++)
		{
			// open devices
			TRACE_INFO("Connecting to <%s>\n",serialNums[i]);
			devh[i] = gcdcInterfaceConnectToSerialNumber(serialNums[i]);
			if(devh[i] == NULL) goto out;
			if(refSerialNum[0])
			{
				if(strncasecmp(serialNums[i],refSerialNum, MAX_SERIAL_NUM) == 0)
				{
					if(verbose_flag) printf("Reference device found\n");
					refDevh = devh[i];
				}
			}
			if(dutSerialNum[0])
			{
				if(strncasecmp(serialNums[i],dutSerialNum, MAX_SERIAL_NUM) == 0)
				{
					if(verbose_flag) printf("Expected device found\n");
					dutDevh = devh[i];
				}
			}
		}
	}
	else
	{
		i = 0;
		gusb_device_handle** newList = gcdcInterfaceConnectToAvailableDevices();
		numDevicesFound = 0;
		while(newList[i])
		{
			devh[i] = newList[i];
			i++;
			numDevicesFound++;
		}
	}

	if(sendCmd_flag)
	{
//		printf("Sending Command <%s> ... ",cmdString);
		fflush(stdout);
		for(i=0;i<numDevicesFound;i++)
		{
			char response_buffer[MAX_CMD_STRING];
			memset(response_buffer,0,MAX_CMD_STRING);
			printf("SN:%s",serialNums[i] );
			fflush(stdout);
			if(gcdcInterfaceDeviceControl(devh[i], cmdString, response_buffer)) continue;
			printf("\n%s\n",response_buffer);

		}
		printf("\n");

	}

	if(settime_flag || utc_flag)	// set times
	{
		printf("Setting time on %d devices ... ",numDevicesFound);
		fflush(stdout);
		for(i=0;i<numDevicesFound;i++)
		{
			printf("%d ",i);
			fflush(stdout);
			gcdcInterfaceSetTimeSync(devh[i], offsetTime, utc_flag);
		}
		printf("\n");
	}

	if(selftest_on_flag)
	{
		for(i=0;i<numDevicesFound;i++)
		{
			gcdcInterfaceSelfTestOn(devh[i]);
		}
	}
	if(selftest_off_flag)
	{
		for(i=0;i<numDevicesFound;i++)
		{
			gcdcInterfaceSelfTestOff(devh[i]);
		}
	}

	if(gain_hi_flag)	// set gain to high
	{
		printf("Hi gain\n");
		for(i=0;i<numDevicesFound;i++)
		{
			gcdcInterfaceGainHi(devh[i]);
		}
	}

	if(gain_low_flag)	// set gain to low
	{
		printf("Low Gain\n");
//		fflush(stdout);
		for(i=0;i<numDevicesFound;i++)
		{
//			printf("%d ",i);
//			fflush(stdout);
			gcdcInterfaceGainLow(devh[i]);
		}
//		printf("\n");
	}

	if(update_flag)	// update unit
	{
		printf("updating firmware on %d devices\n",numDevicesFound);
		fflush(stdout);
#ifdef PTHREAD_UPDATER
		if(numDevicesFound >0)
		{
			struct thread_data* tlist;
			struct thread_data* ptd;
			tlist = createUpdateThread(devh[0],filename);
			ptd = tlist;
			for(i=1;i<numDevicesFound;i++)
			{
				printf("\nDevice %d \n",i);
				fflush(stdout);
				ptd->next = createUpdateThread( devh[i], filename);
				ptd = ptd->next;
			}
			printf("waiting for all units to be updated\n");
			waitComplete(tlist);
			printf("Update completed\n");
		}
#else
		for(i=0;i<numDevicesFound;i++)
		{
			printf("\nDevice %d \n",i);
			fflush(stdout);
			firmwareUpdaterUpdateDevice(devh[i], filename);
		}
#endif
		printf("\n");
	}

	if(sam_ba_prog_flag || toACM0_flag)	// program sam-ba part
	{
		printf("installing firmware on %d Atmel sam-ba devices\n",1);
		fflush(stdout);
		for(i=0;i<numDevicesFound;i++)
		{
			printf("\nDevice %d \n",i);
			fflush(stdout);
			if(enterFlasherCode(devh[i]))
			{
				printf("ERROR could not put device into reprogram mode\n");
				exit(-1);
			}
		}
		if(toACM0_flag)
		{
			printf("Switched to ACM0 mode\n");
			return(0);
		}
		if(numDevicesFound)
		{
			if(verbose_flag) printf("Waiting for target to appear ");
			while(1)
			{
				if(access("/dev/ttyACM0", F_OK) == 0)
				{
					if(verbose_flag) printf(" done\r\n");
					break;
				}
				else
				{
					if(verbose_flag)
					{
						printf(".");
						fflush(stdout);
					}
					usleep(50000);
				}
			}
			usleep(100000);
		}
		atmelsam_ba_handle* pSam = AtmelSam_ba_Init("/dev/ttyACM0");
		if(pSam == NULL)
		{
			printf("ERROR");
			return(-1);
		}
		retval = AtmelSam_ba_programFlash(pSam, filename);
		if(retval)
		{
			printf("%s ERROR %d\r\n",__FUNCTION__,retval);
			return(-1);
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


	// read pressures from several units at a time
	if(test2_flag)
	{
		printf("Ref, P2, P3, P4, d2, d3, d4\n");
		while(1)
		{
			struct pressureReport pr[MAX_DEVICES];
			int delta[MAX_DEVICES];

			for(i=0;i<numDevicesFound;i++)
			{

				if(usbInterfaceGetRealtimePressure(devh[i],	&pr[i]))
				goto out;
			}

			delta[1] = pr[1].pressure-pr[0].pressure;
			delta[2]= pr[2].pressure-pr[0].pressure;
			delta[3] = pr[3].pressure-pr[0].pressure;
			printf("%d, %d, %d, %d, %d, %d, %d\n",pr[0].pressure, pr[1].pressure, pr[2].pressure, pr[3].pressure, delta[1],delta[2],delta[3]);
		}

	}

	if(raw_flag)
	{
		int retval=0;
		if(flushCount !=0 )
		{
			if(dutDevh)
			{
				usbInterfaceFlushQueue(dutDevh, flushCount);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					retval = usbInterfaceFlushQueue(devh[i],flushCount);
				}
			}

		}
		while(1)
		{
			if(raw_num >=0)
			{
				raw_num--;
				if(raw_num <0 ) break;
			}
			if(dutDevh)
			{
				struct accelReport pr;
				retval = usbInterfaceGetRealtimeAcceleration(dutDevh,&pr);

				if(retval)
					continue;
				if(json_flag)
					JSON_PrintAccel(&pr);
				else
					printf("%u.%06u, %d, %d, %d\n", pr.sec,pr.usec, pr.accel[0], pr.accel[1], pr.accel[2]);
				fflush(stdout);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					struct accelReport pr;
					retval = usbInterfaceGetRealtimeAcceleration(devh[i],&pr);

					if(retval)
						continue;
//				printf("data x: %d,  y: %d, z: %d\n", pr.accel[0], pr.accel[1], pr.accel[2]);
					if(json_flag)
						JSON_PrintAccel(&pr);
					else
						printf("%u.%06u, %d, %d, %d\n", pr.sec,pr.usec, pr.accel[0], pr.accel[1], pr.accel[2]);
					fflush(stdout);
				}
			}

		}
	}

	if(rawg_flag || rawm_flag || rawa_flag)
	{
		int retval=0;
		if(flushCount !=0 )
		{
			if(dutDevh)
			{
				usbInterfaceFlushQueue(dutDevh, flushCount);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					retval = usbInterfaceFlushQueue(devh[i],flushCount);
				}
			}

		}
		printf("Time, X, Y, Z\n");
		while(1)
		{
			if(raw_num >=0)
			{
				raw_num--;
				if(raw_num <0 ) break;
			}
			if(dutDevh)
			{
				struct accelReport pr;
				if( rawg_flag)
					retval = usbInterfaceGetRealtimeGyro(dutDevh,&pr);
				else if(rawm_flag)
					retval = usbInterfaceGetRealtimeMagnetic(dutDevh,&pr);
				else
					retval = usbInterfaceGetRealtimeAccel2(dutDevh,&pr);


				if(retval)
					continue;
				printf("%u.%06u, %d, %d, %d\n", pr.sec,pr.usec, pr.accel[0], pr.accel[1], pr.accel[2]);
				fflush(stdout);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					struct accelReport pr;
					if( rawg_flag)
						retval = usbInterfaceGetRealtimeGyro(devh[i],&pr);
					else if( rawm_flag)
						retval = usbInterfaceGetRealtimeMagnetic(devh[i],&pr);
					else
						retval = usbInterfaceGetRealtimeAccel2(devh[i],&pr);

					if(retval)
						continue;
//				printf("data x: %d,  y: %d, z: %d\n", pr.accel[0], pr.accel[1], pr.accel[2]);
					printf("%u.%06u, %d, %d, %d\n", pr.sec,pr.usec, pr.accel[0], pr.accel[1], pr.accel[2]);
					fflush(stdout);
				}
			}

		}
	}

	if(rawq_flag)
	{
		int retval=0;
		if(flushCount !=0 )
		{
			if(dutDevh)
			{
				usbInterfaceFlushQueue(dutDevh, flushCount);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					retval = usbInterfaceFlushQueue(devh[i],flushCount);
				}
			}

		}
		printf("Time, Qw, Qx, Qy, Qz, Qnorm, Pitch, Roll, Yaw\n");
		while(1)
		{
			if(raw_num >=0)
			{
				raw_num--;
				if(raw_num <0 ) break;
			}
			if(dutDevh)
			{
				struct quatReport pr;
				retval = usbInterfaceGetRealtimeQuaternion(dutDevh,&pr);

				if(retval)
					exit(-1);
				{
				float qw, qx, qy, qz, qn;
				qw = ((float)pr.Qw)/65536.0f;
				qx = ((float)pr.Qx)/65536.0f;
				qy = ((float)pr.Qy)/65536.0f;
				qz = ((float)pr.Qz)/65536.0f;
				qn = sqrtf(qw*qw + qx*qx+ qy*qy + qz*qz);
				qw /= qn;
				qx /= qn;
				qy /= qn;
				qz /= qn;
//float pitch = (180.0/M_PI)* atan2(2.0*(qy*qz + qw*qx), qw*qw - qx*qx - qy*qy + qz*qz);
//float roll = (180.0/M_PI) * asin(-2.0*(qx*qz - qw*qy));
//float yaw = (180.0/M_PI) * atan2(2.0*(qx*qy + qw*qz), qw*qw + qx*qx - qy*qy - qz*qz);

// as per http://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
//float pitch = (180.0/M_PI)* atan2(2.0*(qw*qx + qy*qz), 1-2*( qx*qx + qy*qy));
//float roll = (180.0/M_PI) * asin(2.0*(qw*qy - qz*qx));
//float yaw = (180.0/M_PI) * atan2(2.0*(qw*qz + qx*qy), 1-2*(qy*qy + qz*qz ));

double ysqr = qy * qy;
double t0 = -2.0f * (ysqr + qz * qz) + 1.0f;
double t1 = +2.0f * (qx * qy - qw * qz);
double t2 = -2.0f * (qx * qz + qw * qy);
double t3 = +2.0f * (qy * qz - qw * qx);
double t4 = -2.0f * (qx * qx + ysqr) + 1.0f;
t2 = t2 > 1.0f ? 1.0f : t2;
t2 = t2 < -1.0f ? -1.0f : t2;
float roll =  (180.0/M_PI)* asin(t2);
float pitch =  (180.0/M_PI)* atan2(t3, t4);
float yaw =  (180.0/M_PI)* atan2(t1, t0);
//				printf("%u.%06u, %3.2f, %3.2f, %3.2f, %3.2f\n", pr.sec,pr.usec, ((float)pr.Qw)/65536.0f, ((float)pr.Qx)/65536.0f, ((float)pr.Qy)/65536.0f, ((float)pr.Qz)/65536.0f);
//				printf("%u.%06u, %3.2f, %3.2f, %3.2f, %3.2f %3.2f\n", pr.sec,pr.usec, qw, qx, qy, qz, qn);
				printf("%u.%06u, %6.3f, %6.3f, %6.3f, %6.3f,  %8.3g, %6.3f, %6.3f, %6.3f\n", pr.sec,pr.usec, qw, qx, qy, qz, qn, pitch, roll, yaw);
				}
				fflush(stdout);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					struct quatReport pr;
					retval = usbInterfaceGetRealtimeQuaternion(devh[i],&pr);

					if(retval)
						exit(-1);
				{
				float qw, qx, qy, qz, qn;
				qw = ((float)pr.Qw)/65536.0f;
				qx = ((float)pr.Qx)/65536.0f;
				qy = ((float)pr.Qy)/65536.0f;
				qz = ((float)pr.Qz)/65536.0f;
				qn = sqrt(qw*qw + qx*qx+ qy*qy + qz*qz);
				qw /= qn;
				qx /= qn;
				qy /= qn;
				qz /= qn;
#if 0
double ysqr = qy * qy;
double t0 = -2.0f * (ysqr + qz * qz) + 1.0f;
double t1 = +2.0f * (qx * qy - qw * qz);
double t2 = -2.0f * (qx * qz + qw * qy);
double t3 = +2.0f * (qy * qz - qw * qx);
double t4 = -2.0f * (qx * qx + ysqr) + 1.0f;
t2 = t2 > 1.0f ? 1.0f : t2;
t2 = t2 < -1.0f ? -1.0f : t2;
float roll =  -(180.0/M_PI)* atan2(t3, t4);
float pitch =  -(180.0/M_PI)* asin(t2);
float yaw =  (180.0/M_PI)* atan2(t1, t0);
#else
    // roll (x-axis rotation)
    double sinr_cosp = 2 * (qw * qx + qy * qz);
    double cosr_cosp = 1 - 2 * (qx * qx + qy * qy);
    double roll = atan2(sinr_cosp, cosr_cosp);

    // pitch (y-axis rotation)
    double pitch;
    double sinp = 2 * (qw * qy - qz * qx);
    if (fabs(sinp) >= 1)
    {
        pitch = M_PI / 2; // use 90 degrees if out of range
        if( sinp <0)
        	pitch -= pitch;
    }
    else
        pitch = asin(sinp);

    // yaw (z-axis rotation)
    double siny_cosp = 2 * (qw * qz + qx * qy);
    double cosy_cosp = 1 - 2 * (qy * qy + qz * qz);
    double yaw = atan2(siny_cosp, cosy_cosp);

    // convert from rad to degrees
    pitch *= (180/M_PI);
    roll *= (180/M_PI);
    yaw *= (180/M_PI);
#endif
//float pitch = (180.0/M_PI) * atan2( 2.0*(qy*qz + qw*qx), qw*qw - qx*qx - qy*qy + qz*qz);
//float roll =  (180.0/M_PI) *  asin( -2.0*(qx*qz - qw*qy));
//float yaw =   (180.0/M_PI) * atan2( 2.0*(qx*qy + qw*qz), qw*qw + qx*qx - qy*qy - qz*qz);
//				printf("%u.%06u, %3.2f, %3.2f, %3.2f, %3.2f\n", pr.sec,pr.usec, ((float)pr.Qw)/65536.0f, ((float)pr.Qx)/65536.0f, ((float)pr.Qy)/65536.0f, ((float)pr.Qz)/65536.0f);
//				printf("%u.%06u, %3.2f, %3.2f, %3.2f, %3.2f %3.2f\n", pr.sec,pr.usec, qw, qx, qy, qz, qn);
				printf("%u.%06u, %6.3f, %6.3f, %6.3f, %6.3f, %8.3f, %6.3f, %6.3f, %6.3f\n", pr.sec,pr.usec, qw, qx, qy, qz, qn, pitch, roll, yaw);
				}
					fflush(stdout);
				}
			}

		}
	}

	if(rawb_flag)
	{
		struct pressureReport pr;
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		for(i=0;i<numDevicesFound;i++)
		{
			int j;
			for(j=0;j<baroSettleTime;j++)
			{
				if(usbInterfaceGetRealtimePressure(devh[i],&pr))
					goto out;
			}
		}
//		printf("SN,Time, Pressure,  SN,Time,Pressure\n");
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimePressure(devh[i],&pr))
					goto out;
				printf(" %s, %d.%06d, %d", serialNums[i], pr.time_sec, pr.time_usec, pr.pressure);
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");

		}
	}
	if(raw_gps_flag)
	{
		uint8_t rawGpsPacket[66];
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}
		printf("UTC,               TimeOfWk,   Latitude,   Longitude,   Height, hMSL,  hAcc, vAcc\n");
		    //  1578996169.764069, 230587.600, 30.2958461, -89.3669538, -42.709, -15.223, 7.063, 11.821
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetGps(devh[i], rawGpsPacket, 64) <0)
					goto out;
				uint8_t* ptr = &rawGpsPacket[1];
//				printf("gps 0x%02x", rawGpsPacket[0]);
				struct timeval tv;
				tv.tv_sec = *ptr | (*(ptr+1))<<8 | (*(ptr+2))<<16| (*(ptr+3))<<24;
				ptr = &rawGpsPacket[5];
				tv.tv_usec = *ptr | (*(ptr+1))<<8 | (*(ptr+2))<<16| (*(ptr+3))<<24;
				switch(rawGpsPacket[0])
				{
				case GPS_LLH_REPORT_ID:
					printf("%ld.%06ld, ",tv.tv_sec, tv.tv_usec);
					ptr = &rawGpsPacket[9];
					printGpsLlhReport(ptr);
				break;
				default:
					printf(" unknown report type 0x%02x",rawGpsPacket[0]);
				}
//				printf(" %s, %d.%06d, %d", serialNums[i], pr.time_sec, pr.time_usec, pr.pressure);
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");
		}
	}
	if(raw_lux_flag)
	{
		struct luxReport luxReport;

		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}
		printf("Time, Lux\n");
		    //  1578996169.764069, 230587.600, 30.2958461, -89.3669538, -42.709, -15.223, 7.063, 11.821
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimeLux(devh[i], &luxReport) <0)
					goto out;
					printf("%ld.%06ld, %d, %d", luxReport.acqTime.tv_sec, luxReport.acqTime.tv_usec, luxReport.lux[0], luxReport.lux[1]);
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");
		}
	}

	if(raw_ppg_flag)
	{
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("PPG num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				struct accelReport ppg;
				if(usbInterfaceGetRealtimePpg(devh[i],&ppg))
					goto out;
//        uint32_t  sec;
//        uint32_t usec;
//        int32_t accel[3];

				printf(" %s, %d.%06d, %d, %d", serialNums[i], ppg.sec, ppg.usec, ppg.accel[0], ppg.accel[1] );
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");

		}
	}

	if(rawh_flag)
	{
		struct humidityReport humdity;
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		for(i=0;i<numDevicesFound;i++)
		{
			int j;
			for(j=0;j<baroSettleTime;j++)
			{
				if(usbInterfaceGetRealtimeHumidity(devh[i],&humdity))
					goto out;
			}
		}
//		printf("SN,Time, Pressure,  SN,Time,Pressure\n");
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimeHumidity(devh[i],&humdity))
					goto out;
				printf(" %s, %d.%06d, %d", serialNums[i], humdity.time_sec, humdity.time_usec, humdity.humidity);
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");

		}
	}
	if(pps_flag)
	{
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		printf("SN,Time \n");
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				struct tm ppsTm;
				struct timeval hostTv;
				struct timeval deviceTv;
				struct timeval dt, dt2;
				double dt2f, dtf;
				struct timeval inT;
//				char buf[0x040];
//				char* ptr;
//				char sign = ' ';
				if(usbInterfaceGetPps(devh[i], &ppsTm, &deviceTv) )
					goto out;
				gettimeofday(&hostTv, NULL);
				inT.tv_sec =  mktime(&ppsTm);
				inT.tv_usec = 0;
				timersub(&inT, &hostTv,&dt);
				timersub(&deviceTv, &hostTv, &dt2);
				dtf = dt.tv_sec + (double)(dt.tv_usec)/US_PER_SEC;
				dt2f = dt2.tv_sec + (double)(dt2.tv_usec)/US_PER_SEC;
				printf("%s, host,%ld.%06ld, %ld, dt, %8.6f, device,%ld.%06ld dt2,%8.6f", serialNums[i], hostTv.tv_sec, hostTv.tv_usec, inT.tv_sec, dtf, deviceTv.tv_sec, deviceTv.tv_usec, dt2f);
//				asctime_r(&ppsTm, buf);
//				ptr = buf;
//				while(*ptr)
//				{
//					if( (*ptr =='\r') || (*ptr =='\n'))
//					{
//						*ptr='\0';
//						break;
//					}
//					ptr++;
//				}
//				printf("  %s", buf);
				fflush(stdout);
			}
			printf("\n");

		}
	}

	if(rawf_flag)
	{
		struct tachReport pr;
		if(raw_num >= 0)
		{
			numTestSamples = raw_num;
		}
		else if((bFlagCount == 0) )
			numTestSamples = -1;
		TRACE_INFO("num devices found: %d  numTestSample: %d\n", numDevicesFound, numTestSamples);
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		for(i=0;i<numDevicesFound;i++)
		{
			int j;
			for(j=0;j<baroSettleTime;j++)
			{
				if(usbInterfaceGetRealtimeTach(devh[i],&pr))
					goto out;
			}
		}
//		printf("SN,Time, Pressure,  SN,Time,Pressure\n");
		while(numTestSamples--)
		{
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimeTach(devh[i],&pr))
					goto out;
				printf(" %s, %d.%06d, %d", serialNums[i], pr.time_sec, pr.time_usec, pr.freq);
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");

		}
	}

	if(rawt_flag)
	{
		struct temperatureReport tReport;
		if(bFlagCount == 0)
			numTestSamples = -1;
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		for(i=0;i<numDevicesFound;i++)
		{
			int j;
			for(j=0;j<baroSettleTime;j++)
			{
				if(usbInterfaceGetRealtimeTemperature(devh[i],&tReport))
					goto out;
			}
		}
//		printf("Time, Temperature\n");
		while(numTestSamples--)
		{
			if(raw_num >=0)
			{
				raw_num--;
				if(raw_num <0 ) break;
			}
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimeTemperature(devh[i],&tReport))
					goto out;
				if(tReport.temperature > 0)
				{
					printf("%d.%06d, %d.%03d", tReport.time_sec, tReport.time_usec, tReport.temperature/1000, tReport.temperature%1000);
				}
				else
				{
					int32_t tTemp = - tReport.temperature;
					printf("%d.%06d, -%d.%03d", tReport.time_sec, tReport.time_usec, tTemp/1000, tTemp%1000);
				}
				if(i < numDevicesFound-1)
					printf(",  ");
				fflush(stdout);
			}
			printf("\n");
		}
	}

	if(rawd_flag)
	{
		if(raw_num >=0)
		{
			numTestSamples = raw_num;
		}
		else
			numTestSamples = -1;
		if(flushCount !=0 )
		{
			if(dutDevh)
			{
				usbInterfaceFlushQueue(dutDevh, flushCount);
			}
			else
			{
				for(i=0;i<numDevicesFound;i++)
				{
					retval = usbInterfaceFlushQueue(devh[i],flushCount);
				}
			}
		}

		while(numTestSamples--)
		{
			adcDataReport adr;
			for(i=0;i<numDevicesFound;i++)
			{
				if(usbInterfaceGetRealtimeAdcData(devh[i],&adr) <0)
					goto out;
				if(json_flag)
					JSON_PrintAdc(&adr);
				else
				{
					printf("%lu.%06lu, ", adr.header.tm.tv_sec,adr.header.tm.tv_usec);
					for(i=0;i<adr.header.numValid-1;i++)
						printf("%d, ", (int16_t)adr.sample[i]);
					printf("%d\r\n", (int16_t)adr.sample[adr.header.numValid-1]);
				}
				fflush(stdout);
			}
		}
	}

	if(smbus_flag)
	{
		uint8_t temp[0x40];
		if(dutDevh)
		{
			r =gcdcInterfaceSmbusRead(dutDevh, smbusDevice, smbusOffset, temp, smbusLen );
		}
		else
		{
			r =gcdcInterfaceSmbusRead(devh[0], smbusDevice, smbusOffset, temp, smbusLen );
		}
		if(r)
		{
			printf("transaction error %d\n",r);
		}
		else
		{
			if(verbose_flag)
			{
				for(i=0;i<4;i++)
					printf("%02x ",temp[i]);
				printf("\n");
			}
			for(i=4;i<smbusLen+4;i++)
				printf("%02x ",temp[i]);
			printf("\n");
		}
	}

	if(smbus_write_flag)
	{
		if(verbose_flag)
		{
			printf("smbus write to 0x%02x at offset 0x%02x, 0x%02x bytes:  <",smbusDevice,smbusOffset,smbusLen);
			for(i=0;i<smbusLen; i++) printf(" %02x",smbusWriteBuffer[i]);
			printf(" >\n");
		}
		r =gcdcInterfaceSmbusWrite(dutDevh, smbusDevice, smbusOffset, smbusWriteBuffer, smbusLen );
		if(r)
		{
			printf("transaction error %d\n",r);
		}
	}

	// read pressures from several units at a time
	if(test_flag)
	{
		int j;
		int k = 0;
		float M[MAX_DEVICES];
		float S[MAX_DEVICES];
		float dM[MAX_DEVICES];
		float dS[MAX_DEVICES];
		float refM = 0.0;
		float refS = 0;
		char* devSn[MAX_DEVICES];
		time_t startTestTime;

		struct timespec usbLastTime;
		struct timespec usbNowTime;
		struct timespec acqLastTime;
		struct timespec acqNowTime;
//				int n1 = 128;
		float usbTimeMd =0;
		float usbTimeSd = 0;
		float acqTimeMd =0;
		float acqTimeSd = 0;
		float x =0;
		int n1 = numTestSamples;

		struct pressureReport pr[MAX_DEVICES];
		struct pressureReport ref;
		long int usbDelta;
		long int acqDelta;


		time(&startTestTime);
		printf("GCDC B1100 Quality Assurance Test Report\n\tTest Date: %s\n",ctime(&startTestTime));
		for(i=0;i<numDevicesFound;i++)
		{
			usbInterfaceFlushQueue(devh[i],flushCount);
		}

		for(i=0;i<numDevicesFound;i++)
		{
			if(refDevh == devh[i])
			{
				if(usbInterfaceGetRealtimePressure(devh[i], &ref))
					goto out;
			}
			else
			{
				devSn[k] = serialNums[i];
				if(usbInterfaceGetRealtimePressure(devh[i],	&pr[k]))
					goto out;

				clock_gettime(CLOCK_MONOTONIC, &usbNowTime);
				acqNowTime.tv_sec = pr[k].time_sec;
				acqNowTime.tv_nsec = pr[k].time_usec*1000;

				acqDelta = acqNowTime.tv_nsec - acqLastTime.tv_nsec;
				acqDelta += (acqNowTime.tv_sec - acqLastTime.tv_sec) * 1000000000L;
				acqLastTime.tv_sec = acqNowTime.tv_sec;
				acqLastTime.tv_nsec = acqNowTime.tv_nsec;

				usbDelta = usbNowTime.tv_nsec - usbLastTime.tv_nsec;
				usbDelta += (usbNowTime.tv_sec - usbLastTime.tv_sec) * 1000000000L;
				usbLastTime.tv_sec = usbNowTime.tv_sec;
				usbLastTime.tv_nsec = usbNowTime.tv_nsec;

			}
		}

		for(j=0;j<numTestSamples;j++)
		{
			int delta[MAX_DEVICES];
			k = 0;

			for(i=0;i<numDevicesFound;i++)
			{
				if(refDevh == devh[i])
				{
					if(usbInterfaceGetRealtimePressure(devh[i],	&ref))
					goto out;
				}
				else
				{
					devSn[k] = serialNums[i];
					if(usbInterfaceGetRealtimePressure(devh[i],	&pr[k]))
					goto out;

					// get and calculate a USB arrival time delta
					clock_gettime(CLOCK_MONOTONIC, &usbNowTime);
					usbDelta = usbNowTime.tv_nsec - usbLastTime.tv_nsec;
					usbDelta += (usbNowTime.tv_sec - usbLastTime.tv_sec) * 1000000000L;
					usbLastTime.tv_sec = usbNowTime.tv_sec;
					usbLastTime.tv_nsec = usbNowTime.tv_nsec;

					// compute the acquistion time delta between two samples
					acqNowTime.tv_sec = pr[k].time_sec;
					acqNowTime.tv_nsec = pr[k].time_usec*1000;
					acqDelta = acqNowTime.tv_nsec - acqLastTime.tv_nsec;
					acqDelta += (acqNowTime.tv_sec - acqLastTime.tv_sec) * 1000000000L;
					acqLastTime.tv_sec = acqNowTime.tv_sec;
					acqLastTime.tv_nsec = acqNowTime.tv_nsec;

					k++;
				}
			}

			x = (float)(usbDelta)/1e6;	// convert from nsec to millisec
			if(j==0)
			{
				usbTimeMd =  x;
				usbTimeSd = 0;
			}
			else
			{
				float m1 = usbTimeMd;
				usbTimeMd = m1 + ( x - m1)/(j+1);
				usbTimeSd = usbTimeSd + ( (x - m1)*( x - usbTimeMd));
			}

			x = (float)(acqDelta)/1e6;	// convert from nsec to millisec
			if(j==0)
			{
				acqTimeMd =  x;
				acqTimeSd = 0;
			}
			else
			{
				float m1 = acqTimeMd;
				acqTimeMd = m1 + ( x - m1)/(j+1);
				acqTimeSd = acqTimeSd + ( (x - m1)*( x - acqTimeMd));
			}

			// so now the reference value is in the ref pressure field, and the other unit(s) are in the array
			// compile statistics on the unit(s)
			// I think that only deltas are important for the test.
			if(j==0)
			{
				refM =  ref.pressure;
				refS = 0;
			}
			else
			{
				float m1 = refM;
				float x = (float)(ref.pressure);
				refM = m1 + ( x - m1)/(j+1);
				refS = refS + ( x - m1)*( x - refM);
			}

			for(i=0;i<k;i++)
			{
				delta[i] = pr[i].pressure-ref.pressure;
				if(verbose_flag)printf("%d %d ",pr[i].pressure,delta[i]);

				// http://www.johndcook.com/standard_deviation.html
				if(j==0)
				{
					M[i] =  pr[i].pressure;
					S[i] = 0;
					dM[i] =  delta[i];
					dS[i] = 0;
				}else{
					float m1 = M[i];
					float x = (float)(pr[i].pressure);
					float dm1 = dM[i];
					float dx = (float)(delta[i]);
					M[i] = m1 + ( x - m1)/(j+1);
					S[i] = S[i] + ( x - m1)*( x - M[i]);
					dM[i] = dm1 + ( dx - dm1)/(j+1);
					dS[i] = dS[i] + ( dx - dm1)*( dx - dM[i]);
				}
			}
			if(verbose_flag) printf("\n");
		}

		{
			float n = numTestSamples;

			// now just pretty format the resulting dater
			printf("Reference sn: %s,  mean: %5.2f,   var: %3.2f\n",refSerialNum,refM,sqrt(refS/(n-1)));
			for(i=0;i<k;i++)
			{
				printf("sn: %s,    mean: %5.2f,   std dev: %5.2f, ",devSn[i], M[i],sqrt(S[i]/(n-1)));
				printf("    delta mean: %3.2f,   delta std dev: %5.2f\n", dM[i],sqrt(dS[i]/(n-1)));
			}

			printf("USB sample rate, mean: %3.4f,ms,  std dev: %5.7f, (ms)\n",usbTimeMd,sqrt(usbTimeSd/(n1-1)));
			printf("Acq time sample rate, mean: %3.4f,ms,  std dev: %5.7f, (ms)\n",acqTimeMd,sqrt(acqTimeSd/(n1-1)));
		}

	}


	// do an accelerometer gain/sensitivity teste
	if(test3_flag)
	{
		int j;
		int k = 0;

		float M[3*2];
		float S[3*2];
		time_t startTestTime;

		for(i=0;i<numDevicesFound;i++)
		{

			struct accelReport accelR;

			short** testvals = (short**)malloc(sizeof(short*)*numTestSamples);
			for(j=0;j<numTestSamples;j++)
			{
				testvals[j] = malloc(sizeof(short)*6);
			}
			time(&startTestTime);
			printf("Accelerometer Gain Sensitivity Test \n\tTest Date: %s",ctime(&startTestTime));
			printf("\tDevice SN: %s\n",serialNums[i]);
			usbInterfaceFlushQueue(devh[i],flushCount);
			for(j=0;j<numTestSamples;j++)
			{
				// clear self test
				if( gcdcInterfaceSelfTestOff(devh[i]))
					goto out1;

				// let device settle then use last sample
				for(k=0;k<settleTime;k++)
				{
					if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
						goto out1;
				}
				usleep(10000);
				usbInterfaceFlushQueue(devh[i],flushCount);
				if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
					goto out1;

				// compile statistics on mean and stddeviation
				for(k=0;k<3;k++)
				{
					float x = (float)(accelR.accel[k]);

					// http://www.johndcook.com/standard_deviation.html
					if(j==0)
					{
						M[k] =  x;
						S[k] = 0;
					}
					else
					{
						float m1 = M[k];
						M[k] = m1 + ( x - m1)/(j+1);
						S[k] = S[k] + ( x - m1)*( x - M[k]);
					}
				}
				testvals[j][0] = accelR.accel[0];
				testvals[j][1] = accelR.accel[1];
				testvals[j][2] = accelR.accel[2];
				if(verbose_flag) printf("lo %d, %d, %d\n",accelR.accel[0],accelR.accel[1],accelR.accel[2]);

				// set self test feature
				if( gcdcInterfaceSelfTestOn(devh[i]))
					goto out1;

				// let settle, use last sample
				for(k=0;k<settleTime;k++)
				{
					if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
						goto out1;
				}
				usleep(10000);
				usbInterfaceFlushQueue(devh[i],flushCount);

				if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
					goto out1;

				for(k=ST_HI;k<ST_HI+3;k++)
				{
					float x = (float)(accelR.accel[k-ST_HI]);
//					if(verbose_flag)printf("%f ",x);

					// http://www.johndcook.com/standard_deviation.html
					if(j==0)
					{
						M[k] =  x;
						S[k] = 0;
					}
					else
					{
						float m1 = M[k];
						M[k] = m1 + ( x - m1)/(j+1);
						S[k] = S[k] + ( x - m1)*( x - M[k]);
					}
				}
				testvals[j][3] = accelR.accel[0];
				testvals[j][4] = accelR.accel[1];
				testvals[j][5] = accelR.accel[2];
				if(verbose_flag) printf("hi %d, %d, %d\n",accelR.accel[0],accelR.accel[1],accelR.accel[2]);
			}
			if( gcdcInterfaceSelfTestOff(devh[i]))
				goto out1;

			if(verbose_flag)
			{
				printf("Raw samples\nx,   y,   z\n");
				for(j=0;j<numTestSamples;j++)
				{
					printf("lo %d, %d, %d,    ",testvals[j][0],testvals[j][1],testvals[j][2]);
					printf("hi %d, %d, %d\n",testvals[j][3],testvals[j][4],testvals[j][5]);
				}
			}
			if(rawdata_fd)
			{
				fprintf(rawdata_fd,"Raw test data\nlow(x,   y,   z), hi(x, y, z)\n");
				for(j=0;j<numTestSamples;j++)
				{
					fprintf(rawdata_fd,"%d, %d, %d,    ",testvals[j][0],testvals[j][1],testvals[j][2]);
					fprintf(rawdata_fd,"%d, %d, %d\n",testvals[j][3],testvals[j][4],testvals[j][5]);
				}
				fprintf(rawdata_fd,"acq time test data\nsec, nsec\n");
			}

			// this unit has been tested, report the results
			float n = numTestSamples;

			printf("    mean: ");
			for(k=0;k<3;k++)
			{
				printf("%7.1f, ", M[k]);
			}

			printf("\n    sens: ");
			for(k=0;k<3;k++)
			{
				printf("%7.1f, ",M[ST_HI+k]-M[k]);
			}

			printf("\n std dev:");
			for(k=0;k<3;k++)
			{
				float s1 = sqrt(S[+k]/(n-1));
				printf("%7.3f, ",s1);
			}
			printf("\n");

			{// this time measures the sample rate of the device
				struct timespec lastTime;
				struct timespec nowTime;
				struct timespec slaveLastTime;
				struct timespec slaveNowTime;
				int n1 = 128;
				float Md =0;
				float Sd = 0;
				float slaveMd =0;
				float slaveSd = 0;
				float x =0;
				long int delta;
				long int slaveDelta;
//				if(getAccelVals(devh[i], adata))
				if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
					goto out;
				clock_gettime(CLOCK_MONOTONIC, &lastTime);
				slaveLastTime.tv_sec = accelR.sec;
				slaveLastTime.tv_nsec = accelR.usec*1000;

				for(j=0;j<n1;j++)
				{
//					if(getAccelVals(devh[i], adata))
					if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))
						goto out;
					clock_gettime(CLOCK_MONOTONIC, &nowTime);
					slaveNowTime.tv_sec = accelR.sec;
					slaveNowTime.tv_nsec = accelR.usec*1000;
					if(rawdata_fd)
					{
						fprintf(rawdata_fd, "%ld, %ld\n", slaveNowTime.tv_sec,slaveNowTime.tv_nsec);
					}

					delta = nowTime.tv_nsec - lastTime.tv_nsec;
					delta += (nowTime.tv_sec - lastTime.tv_sec) * 1000000000L;

					slaveDelta = slaveNowTime.tv_nsec - slaveLastTime.tv_nsec;
					slaveDelta += (slaveNowTime.tv_sec - slaveLastTime.tv_sec) * 1000000000L;


					lastTime.tv_sec = nowTime.tv_sec;
					lastTime.tv_nsec = nowTime.tv_nsec;

					slaveLastTime.tv_sec = slaveNowTime.tv_sec;
					slaveLastTime.tv_nsec = slaveNowTime.tv_nsec;
//                	        	printf("delta %ld\n",delta);
					// http://www.johndcook.com/standard_deviation.html
					x = (float)(delta)/1e6;
					if(j==0)
					{
						Md =  x;
						Sd = 0;
					}
					else
					{
						float m1 = Md;
						Md = m1 + ( x - m1)/(j+1);
						Sd = Sd + ( (x - m1)*( x - Md));
					}

					x = (float)(slaveDelta)/1e6;
					if(j==0)
					{
						slaveMd =  x;
						slaveSd = 0;
					}
					else
					{
						float m1 = slaveMd;
						slaveMd = m1 + ( x - m1)/(j+1);
						slaveSd = slaveSd + ( (x - m1)*( x - slaveMd));
					}
				}
				printf("USB sample rate, mean: %3.4f,ms,  std dev: %5.7f, (ms)\n",Md,sqrt(Sd/(n1-1)));
				printf("Acq time sample rate, mean: %3.4f,ms,  std dev: %5.7f, (ms)\n",slaveMd,sqrt(slaveSd/(n1-1)));

			}
		}
	}
out1:
	if(rawdata_fd)
	{
		fclose(rawdata_fd);
	}
	for(i=0;i<numDevicesFound;i++)
	{
		gcdcInterfaceRelease(devh[i]);
	}


out:
	gcdcInterfaceDeinit();
	return r >= 0 ? r : -r;
}

