/* ----------------------------------------------------------------------------
*        Gulf Coast Data Concepts 2014
* ----------------------------------------------------------------------------
*/

/*! \mainpage GcdcInterface API
 *
 * \section intro_sec Introduction
 *
 * Welcome to the GcdcInterface API documentation. Here you will find detailed descriptions of the functions within gcdcInterface.c.
 * If you are looking for the documentation on our java code it can be found in the "docs" directory within the "gcdc-usb-accel" folder.
 * \n\n
 * The GcdcInterface API is usefull for Gcdc users who are interested in applications that involve realtime use of data.
 * GcdcTool.exe is an example app that uses the GcdcInterface to display realtime acceleration or pressure data to the console as
 * well as get and set the time on the device.
 * \n\n
*/

/** \file gcdcInterface.c
  * This file contains the entire api
*/


/*----------------------------------------------------------------------------
*        Headers
*----------------------------------------------------------------------------*/
//#define TRACE_LEVEL TRACE_LEVEL_DEBUG
#include "trace.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>    //strlen
#include "gcdcInterface.h"


/*----------------------------------------------------------------------------
*        Internal definitions
*----------------------------------------------------------------------------*/
#ifndef HEX2BCD
#define HEX2BCD(x) ((((x) / 10) << 4) + (x) % 10)
#endif


/*----------------------------------------------------------------------------
*        Local variables
*----------------------------------------------------------------------------*/
int verbose_flag2 = 0;
struct timeval deviceTimeval;

/*----------------------------------------------------------------------------
*        Local functions
*----------------------------------------------------------------------------*/
struct luxReport* processLuxReport(unsigned char* temp, struct luxReport* dest);
struct tachReport* processTachReport(unsigned char* temp, struct tachReport* dest);
struct pressureReport* processPressureReport(unsigned char* temp, struct pressureReport* dest);
struct temperatureReport* processTemperatureReport(unsigned char* temp, struct temperatureReport* dest);
struct accelReport* processAccelReport(unsigned char* temp, struct accelReport* dest);
struct accelReport* processGyroReport(unsigned char* temp, struct accelReport* dest);
struct accelReport* processAccel2Report(unsigned char* temp, struct accelReport* dest);
struct accelReport* processMagAccelReport(unsigned char* temp, struct accelReport* dest);
adcDataReport* processAdcDataReport(unsigned char* src, adcDataReport* dest);
void dumpLuxReport(struct luxReport* ptr, char* pstring);
void dumpTachReport(struct tachReport* ptr, char* pstring);
void dumpTemperatureReport(struct temperatureReport* ptr, char* pstring);
void dumpPressureReport(struct pressureReport* ptr, char* pstring);
void dumpHumidityReport(struct humidityReport* ptr, char* pstring);
struct tm* processPpsDataReport(uint8_t* src, struct tm* dest, struct timeval* ptv);
void dumpReport(unsigned char* data, char len);
struct quatReport* processQuatReport(unsigned char* temp, struct quatReport* dest);

/*----------------------------------------------------------------------------
*        Local functions
*----------------------------------------------------------------------------*/
struct luxReport* processLuxReport(unsigned char* temp, struct luxReport* dest)
{
	struct luxReport* pr = dest;
	if(pr == NULL)
		pr = (struct luxReport*)malloc(sizeof(struct luxReport));
	pr->status = LUX_REPORT_ID;
	temp++;
	pr->lux[0] = le32toh(*(uint32_t*)(temp));
	temp+=4;
	pr->lux[1] = le32toh(*(uint32_t*)(temp));
	temp+=4;
	pr->lux[2] = le32toh(*(uint32_t*)(temp));
	temp+=4;
	pr->acqTime.tv_sec = le64toh(*(uint64_t*)(temp));
	temp+=8;
	pr->acqTime.tv_usec = le32toh(*(uint32_t*)(temp));
	return(pr);
}

struct tachReport* processTachReport(unsigned char* temp, struct tachReport* dest)
{
	struct tachReport* pr = dest;
	if(pr == NULL)
		pr = (struct tachReport*)malloc(sizeof(struct tachReport));
	pr->reportId = TACH_REPORT_ID;
	pr->time_sec = le32toh(*(uint32_t*)(temp+5));
	pr->time_usec = le32toh(*(uint32_t*)(temp+9));
	pr->freq = le32toh(*(uint32_t*)(temp+1));
	return(pr);
}


struct pressureReport* processPressureReport(unsigned char* temp, struct pressureReport* dest)
{
	struct pressureReport* pr = dest;
	if(pr == NULL)
		pr = (struct pressureReport*)malloc(sizeof(struct pressureReport));
	pr->reportId = PRESSURE_REPORT_ID;
	pr->time_sec = le32toh(*(uint32_t*)(temp+5));
	pr->time_usec = le32toh(*(uint32_t*)(temp+9));
	pr->pressure = le32toh(*(uint32_t*)(temp+1));
	return(pr);
}

struct humidityReport* processHumidityReport(unsigned char* temp, struct humidityReport* dest)
{
	struct humidityReport* pr = dest;
	if(pr == NULL)
		pr = (struct humidityReport*)malloc(sizeof(struct humidityReport));
	pr->reportId = HUMIDITY_REPORT_ID;
	pr->time_sec = le32toh(*(uint32_t*)(temp+5));
	pr->time_usec = le32toh(*(uint32_t*)(temp+9));
	pr->humidity = le32toh(*(uint32_t*)(temp+1));
	return(pr);
}


struct accelReport* processAccelReport(unsigned char* temp, struct accelReport* dest)
{
	struct accelReport* accelR = dest;
	if(accelR == NULL)
		accelR = (struct accelReport*)malloc(sizeof(struct accelReport));

	accelR->reportId = ACCEL_REPORT_ID;
	accelR->sec = le32toh(*(uint32_t*)(temp+7));
	accelR->usec = le32toh(*(uint32_t*)(temp+11));
	accelR->accel[0]=  le16toh(*(int16_t*)(temp+1));
	accelR->accel[1]=  le16toh(*(int16_t*)(temp+3));
	accelR->accel[2]=  le16toh(*(int16_t*)(temp+5));
	return(accelR);
}

uint8_t* processRawReport(unsigned char* temp, struct accelReport* dest)
{
	uint8_t* ptr = (uint8_t*)dest;
	if(ptr == NULL)
		ptr = (uint8_t*)malloc(64);
//	int i;
//	for(i=0;i<64;i++)
//	{
//		printf(" %02x", temp[i]);
//		if(i%16==15) printf("\n");
//	}
//	printf("\n");

	memcpy(ptr, temp, 64);
	return(ptr);
}

struct accelReport* processAccel32Report(unsigned char* temp, struct accelReport* dest)
{
	struct accelReport* accelR = dest;
	if(accelR == NULL)
		accelR = (struct accelReport*)malloc(sizeof(struct accelReport));

	accelR->reportId = ACCEL_REPORT_ID;
	accelR->sec = le64toh(*(uint64_t*)(temp+(1+3*4)));
	accelR->usec = le32toh(*(uint32_t*)(temp+(1+3*4+8)));
	accelR->accel[0]=  le32toh(*(int32_t*)(temp+1));
	accelR->accel[1]=  le32toh(*(int32_t*)(temp+(1+4)));
	accelR->accel[2]=  le32toh(*(int32_t*)(temp+(1+2*4)));
	return(accelR);
}


struct quatReport* processQuatReport(unsigned char* temp, struct quatReport* dest)
{
	struct quatReport* quatR = dest;
	if(quatR == NULL)
		quatR = (struct quatReport*)malloc(sizeof(struct quatReport));

	quatR->reportId = QUAT_REPORT_ID;
	quatR->sec = le32toh(*(uint32_t*)(temp+17));
	quatR->usec = le32toh(*(uint32_t*)(temp+21));
	quatR->Qw=  le32toh(*(int32_t*)(temp+1));
	quatR->Qx=  le32toh(*(int32_t*)(temp+5));
	quatR->Qy=  le32toh(*(int32_t*)(temp+9));
	quatR->Qz=  le32toh(*(int32_t*)(temp+13));
	return(quatR);
}

struct accelReport* processGyroReport(unsigned char* temp, struct accelReport* dest)
{
	struct accelReport* gyroR = processAccelReport(temp, dest);
	if(gyroR)
		gyroR->reportId = GYRO_REPORT_ID;
	return(gyroR);
}


struct accelReport* processPpgReport(unsigned char* temp, struct accelReport* dest)
{
	struct accelReport* ppgR = processAccel32Report(temp, dest);
	if(ppgR)
		ppgR->reportId = PPG_REPORT_ID;
	return(ppgR);
}


struct accelReport* processAccel2Report(unsigned char* temp, struct accelReport* dest)
{
	struct accelReport* report = processAccelReport(temp, dest);
	if(report)
		report->reportId = ACCEL2_REPORT_ID;
	return(report);
}

struct temperatureReport* processTemperatureReport(unsigned char* temp, struct temperatureReport* dest)
{
	struct temperatureReport* ptr = dest;
	if(ptr == NULL)
		ptr = (struct temperatureReport*)malloc(sizeof(struct temperatureReport));
	ptr->reportId = PRESSURE_REPORT_ID;
	ptr->time_sec = le32toh(*(uint32_t*)(temp+5));
	ptr->time_usec = le32toh(*(uint32_t*)(temp+9));
	ptr->temperature = le32toh(*(uint32_t*)(temp+1));
	return(ptr);
}


adcDataReport* processAdcDataReport(unsigned char* src, adcDataReport* dest)
{
	int i;
	adcDataReport* pr = dest;
	if(pr == NULL)
		pr = (adcDataReport*)malloc(sizeof(adcDataReport));
//dumpReport((unsigned char*)src, 32);
	pr->header.reportId = *src;
	pr->header.numValid = *(src+1);
	pr->header.status = *(src+2);
	pr->header.tm.tv_sec = le32toh(*(uint32_t*)(src+4));
	pr->header.tm.tv_usec = le32toh(*(uint32_t*)(src+8));
	for(i=0; i<pr->header.numValid; i++)
	{
		pr->sample[i] = le16toh(*(uint16_t*)(src+sizeof(uint16_t)*(6+i)));
	}
	return(pr);
}

struct tm* processPpsDataReport(uint8_t* src, struct tm* dest, struct timeval* pTv)
{
		struct tm* retval = dest;
		if(src ==NULL)
			return(NULL);
			
		if(retval == NULL)
			retval = (struct tm*)malloc(sizeof(struct tm));
//dumpReport((unsigned char*)src, 16);
		retval->tm_sec = src[3];
		retval->tm_min = src[4];
		retval->tm_hour = src[5];
//printf("hr: %02x, min:%02x sec %02x\n", src[5], src[4], src[3]);
//printf("yr: %02x, mon:%02x day %02x\n", src[8], src[7], src[6]);
		retval->tm_mday = src[6];
		retval->tm_mon = src[7];
		retval->tm_year = le16toh(*(uint16_t*)(src+8));//-1900;
		if(pTv)
		{
			uint8_t* ptr = &src[10];
//for(int i = 0; i<16;i++)
//	printf("%02x ", ptr[i]);
//printf("\n");
			pTv->tv_sec = le32toh(*(uint32_t*)ptr);
			pTv->tv_usec = le32toh(*(uint32_t*)(ptr+8));
			
		}
		return(retval);
}

void dumpReport(unsigned char* data, char len)
{
	int i;
	for(i=0;i<len;i++)
	{
		if(i%32 == 31) printf("\r\n");
		else printf("%02x ",data[i]);
	}
	printf("\r\n");
}


void dumpLuxReport(struct luxReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	if(pstring)
		printf("%s %d.%06d, %d\n", pstring, ptr->time_sec, ptr->time_usec, ptr->lux[0]);
	else
		printf("%d.%06d, %d\n", ptr->time_sec, ptr->time_usec, ptr->lux[0]);
#endif
}

void dumpTachReport(struct tachReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	if(pstring)
		printf("%s %d.%06d, %d\n", pstring, ptr->time_sec, ptr->time_usec, ptr->freq);
	else
		printf("%d.%06d, %d\n", ptr->time_sec, ptr->time_usec, ptr->freq);
#endif
}


void dumpAccelReport(struct accelReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	if(pstring)
		printf("%s %d.%06d, ", pstring, ptr->sec, ptr->usec);
	else
		printf("%d.%06d, ", ptr->sec, ptr->usec);
	printf("%d, %d, %d\n", ptr->accel[0], ptr->accel[1], ptr->accel[2]);
#endif
}


void dumpTemperatureReport(struct temperatureReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	int tInt = ptr->temperature/10;
	int tFrac = ptr->temperature%10;
	if(pstring)
		printf("%s %d.%06d(sec), %d(mdeg)  %d.%01d(degC)\n", pstring, ptr->time_sec, ptr->time_usec, ptr->temperature, tInt, tFrac);
	else
		printf("%d.%06d(sec), %d(mdeg) %d.%01d(degC)\n", ptr->time_sec, ptr->time_usec, ptr->temperature, tInt, tFrac);
#endif
}


void dumpPressureReport(struct pressureReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	int pInt = ptr->pressure/100;
	int pFrac = ptr->pressure%100;
	if(pstring)
		printf("%s %d.%06d(sec), %d(Pa)  %d.%01d(mbar)\n", pstring, ptr->time_sec, ptr->time_usec, ptr->pressure, pInt, pFrac);
	else
		printf("%d.%06d(sec), %d(Pa) %d.%01d(mbar)\n", ptr->time_sec, ptr->time_usec, ptr->pressure, pInt, pFrac);
#endif
}

void dumpHumidityReport(struct humidityReport* ptr, char* pstring)
{
#if (TRACE_LEVEL >= TRACE_LEVEL_INFO)
	int pInt = ptr->humidity/100;
	int pFrac = ptr->humidity%100;
	if(pstring)
		printf("%s %d.%06d(sec), %d.%d(percent)\n", pstring, ptr->time_sec, ptr->time_usec, pInt, pFrac);
	else
		printf("%d.%06d(sec), %d.%d(percent)\n", ptr->time_sec, ptr->time_usec, pInt, pFrac);
#endif
}


/*----------------------------------------------------------------------------
*        Exported functions
*----------------------------------------------------------------------------*/






//! This is used to read data from the hid device I^2C bus.
//! \param devh handle to the Gcdc device with the I^2C bus that is to be read.
//! \param device this is the hardware part connected to the I^2C bus on a Gcdc Device.
//! \param offset this is the address of the data that is to be read.
//! \param buffer this is were the data being read is stored.
//! \param len this is the length of the data that is to be read.
//! \return 0 on success and error otherwise.
int gcdcInterfaceSmbusRead(gusb_device_handle *devh, uint8_t device, uint8_t offset, uint8_t* buffer, uint8_t len)
{
	int retval=0;

	// set up and do the smbus read, leaving the result in the devices temp buffer
	uint8_t tempBuffer[0x40];
	tempBuffer[0] = SMBUS_ID;
	tempBuffer[1] = device | 0x01;
	tempBuffer[2] = offset;
	tempBuffer[3] = len;
	retval = gcdcInterfaceSetReport(devh,SMBUS_ID,tempBuffer,SMBUS_REPORT_COUNT);
	if(retval)
	{
		printf("%s dev:0x%02x offset:0x%02x len:0x%02x\r\n",__FUNCTION__,tempBuffer[1],tempBuffer[2],tempBuffer[3]);
		printf("%s SetReport Error %d\n",__FUNCTION__,retval);
		 return(retval);
	}
	if(verbose_flag2) printf("%s dev:0x%02x offset:0x%02x len:0x%02x\r\n",__FUNCTION__,tempBuffer[1],tempBuffer[2],tempBuffer[3]);

//        then read the buffer
	return(gcdcInterfaceGetReport(devh, SMBUS_ID,buffer,SMBUS_REPORT_COUNT));
}


//! This is used to send a "serial" command to the device.
//! \param devh handle to the Gcdc device with the I^2C bus that is to be read.
//! \param device this is the hardware part connected to the I^2C bus on a Gcdc Device.
//! \param offset this is the address of the data that is to be read.
//! \param buffer this is were the data being read is stored.
//! \param len this is the length of the data that is to be read.
//! \return 0 on success and error otherwise.
int gcdcInterfaceDeviceControl(gusb_device_handle *devh, char* cmd, char* buffer)
{
	int retval=0;

	// set up and do the smbus read, leaving the result in the devices temp buffer
	uint8_t tempBuffer[0x40];
	memset(tempBuffer,0,0x40);
	tempBuffer[0] = STRING_REPORT_ID;
	strncpy((char*)(tempBuffer+1),cmd,0x40);
	retval = gcdcInterfaceSetReport(devh,STRING_REPORT_ID,tempBuffer,STRING_REPORT_COUNT);
	if(retval)
	{
		printf("%s SetReport Error %d\n",__FUNCTION__,retval);
		 return(retval);
	}
	usleep(100000);
	// then read the buffer
	return(gcdcInterfaceGetReport(devh, STRING_REPORT_ID,(uint8_t*)buffer,STRING_REPORT_COUNT));
}


//! This is used to write data to the hid device I^2C bus.
//! \param devh handle to the Gcdc device with the I^2C bus that is to be wrote to.
//! \param device this is the hardware part connected to the I^2C bus on a Gcdc Device.
//! \param offset this is the address of where the data is to be written.
//! \param buffer this is the data that will be written.
//! \param len this is the length of the data being written.
//! \return 0 on success and error otherwise.
int gcdcInterfaceSmbusWrite(gusb_device_handle *devh, uint8_t device, uint8_t offset, uint8_t* buffer, uint8_t len)
{
	int retval=0;

	// set up and do the smbus read, leaving the result in the devices temp buffer
	uint8_t tempBuffer[0x40];
	tempBuffer[0] = SMBUS_ID;
	tempBuffer[1] = device & ~0x01;
	tempBuffer[2] = offset;
	tempBuffer[3] = len;
	memcpy(&(tempBuffer[4]),buffer,len);
	retval = gcdcInterfaceSetReport(devh,SMBUS_ID,tempBuffer,SMBUS_REPORT_COUNT);
	if(retval)
	{
		printf("%s SetReport Error %d\n",__FUNCTION__,retval);
		 return(retval);
	}

	return(retval);
}


//! set the time of the device to a value expicitly called out in srcTime
//! stores the time in a char array that is passed to gcdcInterfaceSetReport.\n
//! srcTime looks like this:\n
/*!\n 	cmd[0] = TIME_ID;
\n 	cmd[1] = HEX2BCD(srcTime->tm_sec);
\n 	cmd[2] = HEX2BCD(srcTime->tm_min);
\n 	cmd[3] = HEX2BCD(srcTime->tm_hour);
\n 	cmd[5] = HEX2BCD(srcTime->tm_mday);
\n 	cmd[6] = HEX2BCD(srcTime->tm_mon+1);
\n 	cmd[6] = cmd[6] | 0x80;  this sets the century bit in the rtc
\n 	cmd[7] = HEX2BCD(srcTime->tm_year+1900-2000);  hour epoch is 1900, but subtract 100 years for the century bit above
	\param devh handle to the device you would like to set the time of.
	\param srcTime pointer to structure that contains the time to be set
	\return 0 on success
*/
int gcdcInterfaceSetTime(gusb_device_handle *devh, struct tm* srcTime )
{
	unsigned char cmd[TIME_REPORT_COUNT+1];
	int i;

	cmd[0] = TIME_ID;
	cmd[1] = HEX2BCD(srcTime->tm_sec);
	cmd[2] = HEX2BCD(srcTime->tm_min);
	cmd[3] = HEX2BCD(srcTime->tm_hour);
	cmd[5] = HEX2BCD(srcTime->tm_mday);
	cmd[6] = HEX2BCD(srcTime->tm_mon+1);
	cmd[6] = cmd[6] | 0x80; // this sets the century bit in the rtc
	cmd[7] = HEX2BCD(srcTime->tm_year+1900-2000); // hour epoch is 1900, but subtract 100 years for the century bit above
	for(i=0;i<8;i++)
	{
		printf("%02x ", cmd[i]);
	}
	printf("\n");
	return(gcdcInterfaceSetReport(devh, TIME_ID, (unsigned char *)(cmd), TIME_REPORT_COUNT+1));
}

#ifdef MINGW
//! NOT IMPLEMENTED
//!
int gcdcInterfaceSetTimeSync(gusb_device_handle *devh, int microSecOffset)
{
    printf("FIXME %s not implemented\n",__FUNCTION__);
    return(0);
}
#else
//! Set the time of the device to the cpu time with an optional offset.\n
//! Use this when you wish to set the time to real world time
//! \param devh handle of the device you would like to set the time of
//! \param microSecOffset integer of cpu time offset in micro secounds (optional).
//! \return 0 on success
int gcdcInterfaceSetTimeSync(gusb_device_handle *devh, int microSecOffset, int useUtc)
{
	struct timespec tmpTime;
	struct tm* setTime;
	time_t  nowsecs;

	clock_gettime(CLOCK_REALTIME, &tmpTime);

	nowsecs = tmpTime.tv_sec;
	while(tmpTime.tv_sec == nowsecs)
	{
		clock_gettime(CLOCK_REALTIME, &tmpTime);
		if(useUtc)
			setTime = gmtime(&(tmpTime.tv_sec));
		else
			setTime = localtime(&(tmpTime.tv_sec));

	}
	usleep(microSecOffset);
	return( gcdcInterfaceSetTime(devh, setTime ) );
}
#endif


//! Get the time from the device real time clock
//! \param devh handle of device you would like to know the time of.
//! \param data unsigned char array that the time is stored in.
//! \return 0 on success
int gcdcInterfaceGetTime(gusb_device_handle *devh, unsigned char* data)
{
	data[0] =  TIME_ID;
	gcdcInterfaceGetReport(devh, TIME_ID, data, TIME_REPORT_COUNT);
	return(0);
}


//! Checks the device to see if high gain is set.\n
//! \param devh handle of device
//! \return 0 for false and 1 for true.
int isGainHi(gusb_device_handle *devh)
{
	unsigned char command[] = {GAIN_ID,0};
	gcdcInterfaceGetReport(devh, GAIN_ID, command, GAIN_REPORT_COUNT);
	return(command[0]);
}


//! Checks the device to see if Accel is set.\n
//! \param devh handle of device
//! \return 0 for false and 1 for true.
int isAccelOn(gusb_device_handle *devh)
{
	unsigned char command[] = {ACCEL_ON_OFF_ID,0};
	gcdcInterfaceGetReport(devh, ACCEL_ON_OFF_ID, command, ACCEL_ON_OFF_REPORT_COUNT);
	return(command[0]);
}


//! Checkes device to see if Self Test is set.\n
//!Self Test allows to test the mechanical and electric part of the sensor, allowing the seismic
//!mass to be moved by means of an electrostatic test-force.
//! \param devh device handle
//! \return 0 for false and 1 for true.
int isSelfTest(gusb_device_handle *devh)
{
	unsigned char command[] = {SELF_TEST_ID,0};
	gcdcInterfaceGetReport(devh, SELF_TEST_ID,command, SELF_TEST_REPORT_COUNT);
	return(command[0]);
}


//! Sets High Gain for a specific device.
//! \param devh device handle
//! \return 0 on success
int gcdcInterfaceGainHi(gusb_device_handle *devh)
{
	unsigned char	command[] = {GAIN_ID,1};
	return (gcdcInterfaceSetReport(devh, GAIN_ID, command, GAIN_REPORT_COUNT+1));
}


//! Sets Low Gain for a specific device
//! \param devh device handle
//! \return 0 on success
int gcdcInterfaceGainLow(gusb_device_handle *devh)
{
	unsigned char command[] = {GAIN_ID,0};
	return (gcdcInterfaceSetReport(devh, GAIN_ID, command, GAIN_REPORT_COUNT+1));
}


//! Turns Self Test on for a specific device
//! \param devh device handle
//! \return 0 on success
int gcdcInterfaceSelfTestOn(gusb_device_handle *devh)
{
	unsigned char command[] = {SELF_TEST_ID,1};
	return (gcdcInterfaceSetReport(devh, SELF_TEST_ID, command, SELF_TEST_REPORT_COUNT+1));
}


//! Turns Self Test off for a specific device
//! \param devh device handle
//! \return 0 on success
int gcdcInterfaceSelfTestOff(gusb_device_handle *devh)
{
	unsigned char command[] = {SELF_TEST_ID,0};
	return (gcdcInterfaceSetReport(devh, SELF_TEST_ID, command, SELF_TEST_REPORT_COUNT+1));
}




int usbInterfaceGetReport(gusb_device_handle *devh, void** factory)
{
	unsigned char temp[0x40];
	int r;
	r = GUSB_GetRaw(devh, temp, 0x40);
	if (r < 0)
		return( r) ;

	switch(r)
	{
	case PRESSURE_REPORT_ID:
	{
		struct pressureReport* pr;
		*factory = processPressureReport(temp, NULL);
		pr = *factory;
		dumpPressureReport(pr, "Pressure:");
	}
	break;
	case HUMIDITY_REPORT_ID:
	{
		struct humidityReport* pr;
		*factory = processHumidityReport(temp, NULL);
		pr = *factory;
		dumpHumidityReport(pr, "Humidity:");
	}
	break;
	case TEMPERATURE_REPORT_ID:
	{
		struct temperatureReport* pr;
		*factory = processTemperatureReport(temp, NULL);
		pr = *factory;
		dumpTemperatureReport(pr, "Temperature:");
	}
	break;
	case LUX_REPORT_ID:
	{
		struct luxReport* pr;
		*factory = processLuxReport(temp, NULL);
		pr = *factory;
		
		dumpLuxReport(pr, "Lux: ");
	}
	break;
	case TACH_REPORT_ID:
	{
		struct tachReport* pr;
		*factory = processTachReport(temp, NULL);
		pr = *factory;
		
		dumpTachReport(pr, "Tach: ");
	}
	break;
	case PPS_TIME_REPORT_ID:
	{
//		printf("pps\n");
		*factory = processPpsDataReport(temp, NULL, &deviceTimeval);
	}
	break;
	case ADC_REPORT_ID:
		*factory = processAdcDataReport(temp, *factory);
	break;
	case ACCEL_REPORT_ID:
	{
//		struct accelReport* ar;	
		*factory = processAccelReport(temp, *factory);
//		ar = *factory;
//		dumpAccelReport(ar, "Accel:");
	}	
	break;
	case ACCEL32_REPORT_ID:
	{
//		struct accelReport* ar;	
		*factory = processAccel32Report(temp, *factory);
//		ar = *factory;
//		dumpAccelReport(ar, "Accel:");
	}	
	break;
	case PPG_REPORT_ID:
	{
//		struct accelReport* ar;	
		*factory = processPpgReport(temp, *factory);
		
//		ar = *factory;
//		dumpAccelReport(ar, "Accel:");
	}	
	break;
	case ACCEL2_REPORT_ID:
	{
		*factory = processAccel2Report(temp, *factory);
	}	
	break;
	case GYRO_REPORT_ID:
	{
//		struct accelReport* ar;	
		*factory = processGyroReport(temp, *factory);
//		ar = *factory;
//		dumpAccelReport(ar, "Accel:");
	}	
	break;

	case QUAT_REPORT_ID:
	{
//		struct accelReport* ar;	
		*factory = processQuatReport(temp, *factory);
//		ar = *factory;
//		dumpAccelReport(ar, "Accel:");
	}	
	break;

	default:
		*factory = processRawReport(temp, *factory);
		break;
	}
	return(r);
}


int usbInterfaceGetRealtimeAdcData(gusb_device_handle *devh, adcDataReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);
		if(rptType == ADC_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(adcDataReport));
			free( factory );
			return(rptType);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}


//! Obtains a Realtime Pressure report from a gcdc Barameter.
//! Reports are obtained through interrupt transfers.\n \n
//! This function only prints to the console when compiling with mingw 32 bit.
//! Pressure Report structures look like this:\n
/*!	pr->reportId = temp[0];\n
*		pr->time_sec = le32toh(*(uint32_t*)(temp+5));\n
*		pr->time_usec = le32toh(*(uint32_t*)(temp+9));\n
*  	pr->pressure = le32toh(*(uint32_t*)(temp+1));\n\n
* EXAMPLE:\n\n
*			for(i=0;i<numDevicesFound;i++)\n
*			{\n
*
*				if(usbInterfaceGetRealtimePressure(devh[i],	&pr[i]))\n
*				goto out;\n
*			}\n
*			\n
*			delta[1] = pr[1].pressure-pr[0].pressure;\n
*			delta[2]= pr[2].pressure-pr[0].pressure;\n
*			delta[3] = pr[3].pressure-pr[0].pressure;\n
*			printf("%d, %d, %d, %d, %d, %d, %d\n",pr[0].pressure, pr[1].pressure, pr[2].pressure, pr[3].pressure, delta[1],delta[2],delta[3]);\n
*/
//! \param devh handle of device you want to obtain pressure report from
//! \param pr the pressure report is stored in this structure. This includes a time stamp.
//! \return -1 if pr is null, -2 if report id != PRESSURE_REPORT_ID, and 0 when report id == PRESSURE_REPORT_ID.
int usbInterfaceGetRealtimePressure(gusb_device_handle *devh, struct pressureReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == PRESSURE_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct pressureReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}



int usbInterfaceGetGps(gusb_device_handle *devh, uint8_t* raw, int len)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == GPS_LLH_REPORT_ID)
		{
//			printf("got llh %d xfer dest %p, src %p\n", len, raw, factory);
			memcpy(raw, factory, len);
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}

int usbInterfaceGetLux(gusb_device_handle *devh, uint8_t* raw, int len)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == LUX_REPORT_ID)
		{
//			printf("got llh %d xfer dest %p, src %p\n", len, raw, factory);
			memcpy(raw, factory, len);
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}

int usbInterfaceGetPpg(gusb_device_handle *devh, uint8_t* raw, int len)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == PPG_REPORT_ID)
		{
//			printf("got ppg %d xfer dest %p, src %p\n", len, raw, factory);
			memcpy(raw, factory, len);
			free( factory );
			return(0);
		}
		else
			printf("wrong type %d\n", rptType);
		free( factory );
		factory = NULL;
	}
	return(rptType);
}

int usbInterfaceGetRealtimeHumidity(gusb_device_handle *devh, struct humidityReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == HUMIDITY_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct humidityReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}

int usbInterfaceGetRealtimePpg(gusb_device_handle *devh, struct accelReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == PPG_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct accelReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}


int usbInterfaceGetPps(gusb_device_handle *devh, struct tm* dest, struct timeval* ptv)
{
	void* factory = NULL;
	int rptType = 1;
	if(dest == NULL)
		return(-1);
		
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);
		if(rptType == PPS_TIME_REPORT_ID)
		{
//printf("%s processing dst %p, src:%p len:%ld\n", __FUNCTION__, dest, factory, sizeof(struct tm) );
//			processPpsDataReport(factory,dest);
			memcpy(dest, factory, sizeof(struct tm));
			if(ptv)
			{
				memcpy(ptv, &deviceTimeval, sizeof(struct timeval));
			}
//printf("freeing \n");
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}


int usbInterfaceGetRealtimeTemperature(gusb_device_handle *devh, struct temperatureReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == TEMPERATURE_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct temperatureReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}


int usbInterfaceGetRealtimeLux(gusb_device_handle *devh, struct luxReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == LUX_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct luxReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}


int usbInterfaceGetRealtimeTach(gusb_device_handle *devh, struct tachReport* pr)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == TACH_REPORT_ID)
		{
			memcpy(pr, factory, sizeof(struct tachReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}





#define MAX_MULTI_ACCEL_REPORT 8
typedef struct _multiAccelUsbReport
{
	uint8_t id;
	uint8_t numSamples;
	uint32_t first_sec;
	uint32_t first_usec;
	uint32_t delta_usec;
	int16_t samples[3*MAX_MULTI_ACCEL_REPORT];
} __attribute__ ((packed)) multiAccelUsbReport;

multiAccelUsbReport* pMultiData = NULL;
multiAccelUsbReport* pMultiDataGyro = NULL;


int usbInterfaceFlushQueue(gusb_device_handle *devh, int numPackets)
{
	return(GUSB_FlushQueue(devh, numPackets));
}


//! Obtains a realtime acceleration reports from a Gcdc Accelarometer.
//! Acceleration reports are obtained through interrupt_transfers.\n\n
//! Acceleration reports look like this:\n
/*! 		accelR->reportId = ACCEL_REPORT_ID;\n
*		 	accelR->accel[0]=  le16toh(*(s16*)(temp+1));\n
*		 	accelR->accel[1]=  le16toh(*(s16*)(temp+3));\n
*		 	accelR->accel[2]=  le16toh(*(s16*)(temp+5));\n
*			accelR->sec = le32toh(*(uint32_t*)(temp+7));\n
*			accelR->usec = le32toh(*(uint32_t*)(temp+11));\n\n
* EXAMPLE: \n\n
*	if(usbInterfaceGetRealtimeAcceleration(devh[i], &accelR))\n
*	printf("%d, %d, %d,    ",accelR.accel[0],accelR.accel[1],accelR.accel[2]);\n
*
* \param devh handle to device you would like to obtain a acceleration report on.
* \param accelR accelReport structure where the report is placed.
* \return 0 on success. If the report ID is unexpected then the report ID is returned. returns  <0 on an error.
*/
int usbInterfaceGetRealtimeAcceleration(gusb_device_handle *devh, struct accelReport* accelR)
{
	static unsigned char temp[0x40];
	if(pMultiData)
	{ // get data from existing packet with multiple samples in it
		if(verbose_flag2) printf("%s multi first %d delta: %d\r\n",__FUNCTION__, pMultiData->first_usec, pMultiData->delta_usec);

		accelR->reportId = ACCEL_REPORT_ID;
		accelR->accel[0]=  le16toh(pMultiData->samples[(MAX_MULTI_ACCEL_REPORT-pMultiData->numSamples)*3 + 0]);
		accelR->accel[1]=  le16toh(pMultiData->samples[(MAX_MULTI_ACCEL_REPORT-pMultiData->numSamples)*3 + 1]);
		accelR->accel[2]=  le16toh(pMultiData->samples[(MAX_MULTI_ACCEL_REPORT-pMultiData->numSamples)*3 + 2]);
		accelR->sec = le32toh(pMultiData->first_sec);
		accelR->usec = le32toh(pMultiData->first_usec);
		accelR->usec += (MAX_MULTI_ACCEL_REPORT-(int16_t)(pMultiData->numSamples)) * (int32_t)le32toh(pMultiData->delta_usec);
		while(accelR->usec >= 1000000L)
		{
			accelR->sec++;
			accelR->usec -= 1000000L;
		}
		while(accelR->usec < 0L)
		{
			accelR->sec--;
			accelR->usec += 1000000L;
		}
		pMultiData->numSamples--;
		if(pMultiData->numSamples == 0) pMultiData = NULL;
		return(0);
	}

	if(!accelR) return(-1);
	while(1)
	{
		int r;
		r = GUSB_GetRaw(devh, temp, 0x40);
		if (r < 0)
			return( r) ;


		char reportId = temp[0];
//dumpReport(temp,0x40);
TRACE_INFO_WP("%s report id: %d ",__FUNCTION__,reportId);
		switch(reportId)
		{
		case ACCEL_REPORT_ID:
TRACE_INFO_WP(" accel\n");
			accelR->reportId = ACCEL_REPORT_ID;
			accelR->accel[0]=  le16toh(*(int16_t*)(temp+1));
			accelR->accel[1]=  le16toh(*(int16_t*)(temp+3));
			accelR->accel[2]=  le16toh(*(int16_t*)(temp+5));
			accelR->sec = le32toh(*(uint32_t*)(temp+7));
			accelR->usec = le32toh(*(uint32_t*)(temp+11));

			return(0);
			break;
		case ACCEL32_REPORT_ID:
TRACE_INFO_WP(" accel32\n");
			accelR->reportId = ACCEL_REPORT_ID;
			accelR->accel[0]=  le32toh(*(int32_t*)(temp+1));
			accelR->accel[1]=  le32toh(*(int32_t*)(temp+(1+4)));
			accelR->accel[2]=  le32toh(*(int32_t*)(temp+(1+2*4)));
			accelR->sec = le64toh(*(uint64_t*)(temp+(1+3*4)));
			accelR->usec = le32toh(*(uint32_t*)(temp+(1+3*4+8)));

			return(0);
			break;
		case MULTI_ACCEL_REPORT_ID:
			pMultiData = ( multiAccelUsbReport*)temp;
TRACE_INFO_WP("multi numsamples %d\n",pMultiData->numSamples);
			if(pMultiData->numSamples > MAX_MULTI_ACCEL_REPORT)
			{
				pMultiData = NULL;
				printf("mulit sample report to big\n");
				dumpReport(temp,0x40);
				break;
			}

			accelR->reportId = ACCEL_REPORT_ID;
			accelR->accel[0]=  le16toh(pMultiData->samples[0]);
			accelR->accel[1]=  le16toh(pMultiData->samples[1]);
			accelR->accel[2]=  le16toh(pMultiData->samples[2]);
			accelR->sec = le32toh(pMultiData->first_sec);
			accelR->usec = le32toh(pMultiData->first_usec);
			accelR->usec += (MAX_MULTI_ACCEL_REPORT-(int16_t)(pMultiData->numSamples)) * (int32_t)le32toh(pMultiData->delta_usec);
			while(accelR->usec >= 1000000L)
			{
				accelR->sec++;
				accelR->usec -= 1000000L;
			}
			while(accelR->usec < 0L)
			{
				accelR->sec--;
				accelR->usec += 1000000L;
			}
			pMultiData->numSamples--;

			return(0);
			break;
		case PPS_TIME_REPORT_ID:
TRACE_INFO_WP(" PPS_TIME_REPORT_ID\n");

			if(verbose_flag2)
			{
				struct tm tm1;
				struct tm tm2;
				time_t timet1;
				tm1.tm_sec = temp[3];
				tm1.tm_min = temp[4];
				tm1.tm_hour = temp[5];
				tm1.tm_mday = temp[6];
				tm1.tm_mon = temp[7];
				tm1.tm_year = le16toh(*(uint16_t*)(temp+8));//-1900;
				timet1 = mktime(&tm1);
				gmtime_r(&timet1,&tm2);
				printf("%s PPS tick %s",__FUNCTION__, asctime(&tm1));
			}
			continue;
		default:
			if(verbose_flag2)
			{
				printf("%s() unexpected report id %d\n",__FUNCTION__,reportId);
				dumpReport(temp,0x40);
			}

			continue;
//			return(reportId);
		}
	}
	return(-2);
}


int usbInterfaceGetRealtimeGyro(gusb_device_handle *devh, struct accelReport* accelG)
{
	static unsigned char temp[0x40];
	if(pMultiDataGyro)
	{ // get data from existing packet with multiple samples in it
		if(verbose_flag2) printf("%s multi first %d delta: %d\r\n",__FUNCTION__, pMultiDataGyro->first_usec, pMultiDataGyro->delta_usec);

		accelG->reportId = GYRO_REPORT_ID;
		accelG->accel[0]=  le16toh(pMultiDataGyro->samples[(MAX_MULTI_ACCEL_REPORT-pMultiDataGyro->numSamples)*3 + 0]);
		accelG->accel[1]=  le16toh(pMultiDataGyro->samples[(MAX_MULTI_ACCEL_REPORT-pMultiDataGyro->numSamples)*3 + 1]);
		accelG->accel[2]=  le16toh(pMultiDataGyro->samples[(MAX_MULTI_ACCEL_REPORT-pMultiDataGyro->numSamples)*3 + 2]);
		accelG->sec = le32toh(pMultiDataGyro->first_sec);
		accelG->usec = le32toh(pMultiDataGyro->first_usec);
		accelG->usec += (MAX_MULTI_ACCEL_REPORT-(int16_t)(pMultiDataGyro->numSamples)) * (int32_t)le32toh(pMultiDataGyro->delta_usec);
		while(accelG->usec >= 1000000L)
		{
			accelG->sec++;
			accelG->usec -= 1000000L;
		}
		while(accelG->usec < 0L)
		{
			accelG->sec--;
			accelG->usec += 1000000L;
		}
		pMultiDataGyro->numSamples--;
		if(pMultiDataGyro->numSamples == 0) pMultiDataGyro = NULL;
		return(0);
	}

	if(!accelG) return(-1);
	while(1)
	{
		int r;
		r = GUSB_GetRaw(devh, temp, 0x40);
		if (r < 0)
			return( r) ;


		char reportId = temp[0];
if(verbose_flag2) printf("%s report id: %d ",__FUNCTION__,reportId);
		switch(reportId)
		{
		case GYRO_REPORT_ID:
if(verbose_flag2) printf(" gyro\n");
			accelG->reportId = GYRO_REPORT_ID;
			accelG->accel[0]=  le16toh(*(int16_t*)(temp+1));
			accelG->accel[1]=  le16toh(*(int16_t*)(temp+3));
			accelG->accel[2]=  le16toh(*(int16_t*)(temp+5));
			accelG->sec = le32toh(*(uint32_t*)(temp+7));
			accelG->usec = le32toh(*(uint32_t*)(temp+11));

			return(0);
			break;
		case GYRO32_REPORT_ID:
if(verbose_flag2) printf(" gyro32\n");
			accelG->reportId = GYRO32_REPORT_ID;
			accelG->accel[0]=  le32toh(*(int32_t*)(temp+1));
			accelG->accel[1]=  le32toh(*(int32_t*)(temp+5));
			accelG->accel[2]=  le32toh(*(int32_t*)(temp+9));
			accelG->sec = le32toh(*(uint32_t*)(temp+13));
			accelG->usec = le32toh(*(uint32_t*)(temp+21));

			return(0);
			break;
#if 0
		case MULTI_GYRO_REPORT_ID:
			pMultiDataGyro = ( multiAccelUsbReport*)temp;
if(verbose_flag2) printf(" multi numsamples %d\n",pMultiDataGyro->numSamples);
			if(pMultiDataGyro->numSamples > MAX_MULTI_ACCEL_REPORT)
			{
				printf("%s MULTI_GYRO (%d) num samples to big %d > %d\n", __FUNCTION__, MULTI_GYRO_REPORT_ID,pMultiDataGyro->numSamples, MAX_MULTI_ACCEL_REPORT);
				dumpReport(temp,0x40);
				pMultiDataGyro = NULL;
				break;
			}

			accelG->reportId = GYRO_REPORT_ID;
			accelG->accel[0]=  le16toh(pMultiDataGyro->samples[0]);
			accelG->accel[1]=  le16toh(pMultiDataGyro->samples[1]);
			accelG->accel[2]=  le16toh(pMultiDataGyro->samples[2]);
			accelG->sec = le32toh(pMultiDataGyro->first_sec);
			accelG->usec = le32toh(pMultiDataGyro->first_usec);
			accelG->usec += (MAX_MULTI_ACCEL_REPORT-(int16_t)(pMultiDataGyro->numSamples)) * (int32_t)le32toh(pMultiDataGyro->delta_usec);
			while(accelG->usec >= 1000000L)
			{
				accelG->sec++;
				accelG->usec -= 1000000L;
			}
			while(accelG->usec < 0L)
			{
				accelG->sec--;
				accelG->usec += 1000000L;
			}
			pMultiDataGyro->numSamples--;

			return(0);
			break;
#endif
		default:
			if(verbose_flag2)
			{
				printf("%s() unexpected report id %d\n",__FUNCTION__,reportId);
				dumpReport(temp,0x40);
			}

			continue;
//			return(reportId);
		}
	}
	return(-2);
}


//! Obtains a realtime magnetic vector from a Gcdc device
//! Magnetic reports are obtained through interrupt_transfers.\n\n
//! Reports look like this:\n
/*! 		dataR->reportId = MAG_REPORT_ID;\n
*		 	dataR->accel[0]=  le16toh(*(int16_t*)(temp+1));\n
*		 	dataR->accel[1]=  le16toh(*(int16_t*)(temp+3));\n
*		 	dataR->accel[2]=  le16toh(*(int16_t*)(temp+5));\n
*			dataR->sec = le32toh(*(uint32_t*)(temp+7));\n
*			dataR->usec = le32toh(*(uint32_t*)(temp+11));\n\n
* EXAMPLE: \n\n
*	if(usbInterfaceGetRealtimeMagnetic(devh[i], &dataR))\n
*	printf("%d, %d, %d,    ",dataR.accel[0],dataR.accel[1],dataR.accel[2]);\n
*
* \param devh handle to device you would like to obtain a acceleration report on.
* \param dataR dataReport structure where the report is placed.
* \return 0 on success. If the report ID is unexpected then the report ID is returned. returns  <0 on an error.
*/
int usbInterfaceGetRealtimeMagnetic(gusb_device_handle *devh, struct accelReport* dataR)
{
	unsigned char temp[0x40];
	if(!dataR) return(-1);
	while(1)
	{
		int r;
		r = GUSB_GetRaw(devh, temp, 0x40);
		if (r < 0)
			return( r) ;

		char reportId = temp[0];
		switch(reportId)
		{
		case MAG_REPORT_ID:
			if(verbose_flag2)
			{
				printf("%s MagReport", __FUNCTION__);
				dumpReport(temp, 0x40);
			}
			dataR->reportId = MAG_REPORT_ID;
			dataR->accel[0]=  le16toh(*(int16_t*)(temp+1));
			dataR->accel[1]=  le16toh(*(int16_t*)(temp+3));
			dataR->accel[2]=  le16toh(*(int16_t*)(temp+5));
			dataR->sec = le32toh(*(uint32_t*)(temp+7));
			dataR->usec = le32toh(*(uint32_t*)(temp+11));

			return(0);
			break;
		case MAG32_REPORT_ID:
			if(verbose_flag2)
			{
				printf("%s Mag32Report", __FUNCTION__);
				dumpReport(temp, 0x40);
			}
			dataR->reportId = MAG32_REPORT_ID;
			dataR->accel[0]=  le32toh(*(int32_t*)(temp+1));
			dataR->accel[1]=  le32toh(*(int32_t*)(temp+5));
			dataR->accel[2]=  le32toh(*(int32_t*)(temp+9));
			dataR->sec = le64toh(*(uint64_t*)(temp+13));
			dataR->usec = le32toh(*(uint32_t*)(temp+21));

			return(0);
			break;
			

		case PPS_TIME_REPORT_ID:
//		{
//			struct tm tm1;
//			struct tm tm2;
//			time_t timet1;
//			tm1.tm_sec = temp[3];
//			tm1.tm_min = temp[4];
//			tm1.tm_hour = temp[5];
//			tm1.tm_mday = temp[6];
//			tm1.tm_mon = temp[7]-1;
//			tm1.tm_year = le16toh(*(uint16_t*)(temp+8))-1900;
//			timet1 = mktime(&tm1);
//			gmtime_r(&timet1,&tm2);
//			printf("%s PPS tick %s",__FUNCTION__, asctime(&tm2));
//		}
			continue;
		default:
			if(verbose_flag2)
			{
				printf("%s() unexpected report id %d\n",__FUNCTION__,reportId);
				dumpReport(temp, 0x40);
			}
			continue;
//			return(reportId);
		}
	}
	return(-2);
}


int usbInterfaceGetRealtimeQuaternion(gusb_device_handle *devh, struct quatReport* dataR)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == QUAT_REPORT_ID)
		{
			memcpy(dataR, factory, sizeof(struct quatReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}

int usbInterfaceGetRealtimeAccel2(gusb_device_handle *devh, struct accelReport* dataR)
{
	void* factory = NULL;
	int rptType = 1;
	while(rptType > 0)
	{
		rptType = usbInterfaceGetReport(devh, &factory);

		if(rptType == ACCEL2_REPORT_ID)
		{
			memcpy(dataR, factory, sizeof(struct quatReport));
			free( factory );
			return(0);
		}
		free( factory );
		factory = NULL;
	}
	return(rptType);
}




//! Initializes Libusb and sets debugging.
//!	 \n   Level 0: no messages ever printed by the library (default)
//!    \n   Level 1: error messages are printed to stderr
//!    \n   Level 2: warning and error messages are printed to stderr
//!    \n   Level 3: informational messages are printed to stdout, warning and error messages are printed to stderr
/*! EXAMPLE:\n\n
*	int verbose_flag = 0;\n
*	r = gcdcInterfaceInit(verbose_flag);\n
*	if (r < 0) {\n
*	   fprintf(stderr, "failed to initialise\n");\n
*	}\n
*/
//!	\param debug_level the debug level that will be set to
//!	\return 0 on success
int gcdcInterfaceInit(int debug_level)
{
	verbose_flag2 = debug_level;
	return(GUSB_Init(debug_level));
}


//! Deinitializes interface
//! calls os specific exit;
void gcdcInterfaceDeinit(void)
{
	GUSB_Deinit();
}


//!Opens the device of a given serial number and claims the HID interface.
//!This is a convenience funtion that does everything needed to begin working with a device of a specific serial number
/*!EXAMPLE:\n\n
*	gusb_device_handle* devh[MAX_DEVICES];\n
*	for(i=0;i< numDevicesFound;i++)\n
*	{\n
*		// open devices\n
*		if(verbose_flag) printf("Connecting to <%s>\n",serialNums[i]);\n
*		devh[i] = gcdcInterfaceConnectToSerialNumber(serialNums[i]);\n
*		if(devh[i] == NULL) goto out;\n
*	}\n
*/
//! \param serialNumber pointer to char array of the device serial number
//! \return device handle obtained by opening the device
gusb_device_handle* gcdcInterfaceConnectToSerialNumber(char* serialNumber)
{
	return(GUSB_ConnectToSerialNumber( serialNumber));
}


//!Opens all devices with a matching pid and vid  and claims the HID interface.
//!This is a convenience funtion that does everything needed to begin working with a device of a specific serial number
gusb_device_handle** gcdcInterfaceConnectToAvailableDevices()
{
	return(GUSB_ConnectToAvailableDevices());
}


//!Releases the interface and closes the device
//! \param devh handle of device that you a finished with
void gcdcInterfaceRelease(gusb_device_handle *devh)
{
	GUSB_Release(devh);
}


//! sends report data to the device through endpoint 0.
//! This function is used within many other gcdcInterface functions, so you may not find yourself using it.
//! \param devh handle to device you are sending to.
//! \param reportId determines the type of report being sent.
//! \param dataBuffer char array that contains data being sent
//! \param dataBufferSize size of data being sent
//! \return 0 on no error
int gcdcInterfaceSetReport(gusb_device_handle *devh, unsigned char reportId, unsigned char* dataBuffer, int dataBufferSize )
{
	return(GUSB_SetReport(devh,reportId, dataBuffer, dataBufferSize));
}


//! gets report data from the device through endpoint 0.
//! This function is used within many other gcdcInterface functions.
//! \param devh handle of device that you are obtaining report from.
//! \reportId this is used to determine what type of report is being retrieved.
//! \dataBuffer the data obtained is stored in this char array.
//! \dataBufferSize this contains the size of the data that will be recieved.
//! \return 0 if no error.
int gcdcInterfaceGetReport(gusb_device_handle *devh, unsigned char reportId, unsigned char* dataBuffer, int dataBufferSize )
{
	return(GUSB_GetReport(devh, reportId, dataBuffer, dataBufferSize));
}


//! Get the serial number of this device.\n
/*!EXAMPLE:\n\n
*		char snString[MAX_SERIAL_NUM];\n
*		gcdcInterfaceGetSerialNum(NULL, snString,MAX_SERIAL_NUM);\n
*		printf("sn <%s>\n",snString);\n
*/
//! \param devh handle to device that you are requesting the serial number to.
//! \param buffer char array that the serial number is placed in.
//! \param size The size of the serial number.
//! \return 0 on success
int gcdcInterfaceGetSerialNum(gusb_device_handle *devh, char* buffer, int size)
{
	return(GUSB_GetSerialNum(devh, buffer, size));
}


//!	Obtains a list of Serial Numbers for the List of detected Gcdc devices.
/*!EXAMPLE:\n\n
*	for(i=0;i<MAX_DEVICES;i++)\n
*	{\n
*		serialNums[i] = temp[i];\n
*	}\n
*	numDevicesFound = gcdcInterfaceGetSerialNumbers(NULL, serialNums, MAX_DEVICES, MAX_SERIAL_NUM);\n
*	if(numDevicesFound <1)\n
*	{\n
*		printf("Wasn't able to find devices %d\n",numDevicesFound);\n
*	}\n
*/
//!	\param list - an array of strings to fill in
//!	\param maxEntries - size of the list
//!	\param maxSize - max size of each string
//!   \return If successful a list of serial numbers corresponding to devices that this interface can work with will be returned
//!	returns <0 if an error.
int gcdcInterfaceGetSerialNumbers(char* list[], int maxEntries, int maxSize)
{
	return(GUSB_GetSerialNumbers(list, maxEntries, maxSize));
}
