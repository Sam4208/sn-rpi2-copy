#include <unistd.h>

#include <stdio.h>
#include <asm/types.h>
#include <stdlib.h>	// malloc
#include <string.h>    //strstr function
#include "gcdc.h"
#include "ihex.h"
#include "gcdcInterface.h"
#include "firmwareUpdater.h"
#include "constIndeces.h"

extern int verbose_flag;



//Buffer sizes
#define COMMAND_BUFFER_SIZE 4
#define RESPONSE_BUFFER_SIZE 2
#define TARGET_EP0_BUFFER_SIZE 64
#define CRC_BUFFER_SIZE 3

//Bootlaoder commands
#define GET_SW_VERSION_COMMAND  0x00
#define GET_HW_VERSION_COMMAND  0x07
#define SET_PAGE_COMMAND 0x01
#define ERASE_PAGE_COMMAND 0x02
#define WRITE_PAGE_COMMAND 0x03
#define CRC_ON_PAGE_COMMAND 0x04
#define READ_FLASH_BYTE_COMMAND 0x05
#define RESET_DEVICE_COMMAND 0x06
#define BLANK 0xFF

// ARM specific commands
#define WRITE_CONFIG_PAGE_COMMAND 0x09
#define READ_CONFIG_PAGE_COMMAND 0x0A
#define READ_INT32_COMMAND READ_FLASH_BYTE_COMMAND

#define MAX_PAGES 128
#define PAGE_SIZE 512
#define RESERVED_START (0xF800>>9)
#define CONFIG_PAGE (0xF600>>9)
//#define CONFIG_PAGE (0xF400>>9)

struct targetPageInfo
{
	uint8_t* data;
	int pageNumber;
	uint16_t crc16;
	char fIsUsed;
	char fOverwrite;
};

#define FLASH_BUFFER_SIZE 64

typedef uint8_t FLASH_BUFFER[FLASH_BUFFER_SIZE];
#define FLASH_REPORT	20
#define FLASH_DATA_MASK	0x55
#define CRC_REPORT	21


int sendCommandWaitResponse(gusb_device_handle *devh1, unsigned char command[])
{
	int retval = 0;
	unsigned char response[] = {RESPONSE_REPORT, 0};

	retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 4);
	if( retval )
	{
		printf("firmwareUpdater:sendCommandWaitResponse, ERROR sending command, retval %d\r\n",retval);
		return(-2);
	}

	retval = gcdcInterfaceGetReport(devh1, RESPONSE_REPORT,response, 2);
	if( retval )
	{
		if(verbose_flag) printf("firmwareUpdater:sendCommandWaitResponse, ERROR Reading Data returned %d\r\n",retval);
		return(-1);
	}
	return(response[1]);
}


int sendCommandNoWaitResponse(gusb_device_handle *devh1, unsigned char command[])
{
	int retval = 0;
	retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 4);
	if( retval )
	{
		printf("firmwareUpdater:sendCommandWaitResponse, ERROR sending command, retval %d\r\n",retval);
		return(-2);
	}
	return(retval);
}


int enterBootloadMode(gusb_device_handle *devh1, uint8_t swVersion, uint8_t hwVersion)
{
	unsigned char command[] = {REPROGRAM_ID, UNIQUE_BL_ID, swVersion, hwVersion};
	return( gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, COMMAND_BUFFER_SIZE));
}


int getSoftwareVersion(gusb_device_handle *devh1)
{
	unsigned char command[] = {REPROGRAM_ID, GET_SW_VERSION_COMMAND, BLANK, BLANK};
	int retval = sendCommandWaitResponse(devh1, command);
	if(retval <0) printf("%s error\r\n",__FUNCTION__);
	return(retval);
}


int getHardwareVersion(gusb_device_handle *devh1)
{
	unsigned char command[] = {REPROGRAM_ID, GET_HW_VERSION_COMMAND, BLANK, BLANK};
	int retval = sendCommandWaitResponse(devh1, command);
	if(retval <0) printf("%s error\r\n",__FUNCTION__);
	return(retval);
}


int setPage(gusb_device_handle *devh1, uint16_t page)
{
	unsigned char command[] = {REPROGRAM_ID, SET_PAGE_COMMAND, page, page>>8};
	return(sendCommandWaitResponse(devh1, command));
}


int erasePage(gusb_device_handle *devh1)
{
	unsigned char command[] = {REPROGRAM_ID, ERASE_PAGE_COMMAND, BLANK, BLANK};
	return(sendCommandWaitResponse(devh1, command));
}

#define MAX_WRITE (TARGET_EP0_BUFFER_SIZE-4)
int sambaWriteToFlash(gusb_device_handle *devh1, uint8_t* data, int32_t dataSize, int pageOffset, int commandType)
{
	uint8_t command[TARGET_EP0_BUFFER_SIZE];
	int bytesRemaining = dataSize;
	int num;
	uint8_t* ptr = data;
	int retval = 0;
	int pageCount = pageOffset;
	uint8_t offset = pageOffset;

	memset(command, BLANK, TARGET_EP0_BUFFER_SIZE);
	command[0] = REPROGRAM_ID;
	command[1] = commandType;
	command[2] = offset;
	command[3] = MAX_WRITE;
	memset(command, BLANK, MAX_WRITE);
	while(dataSize > 0x100)
	{
//printf("%s page: %d\r\n",__FUNCTION__, pageCount);
        	setPage(devh1,pageCount++);
		bytesRemaining = 0x100;
		while( bytesRemaining)
		{
			num = (bytesRemaining < MAX_WRITE)? bytesRemaining : MAX_WRITE;
			memcpy(&command[4], ptr,num);
			command[3] = num;
			command[2] = offset;
			command[0] = REPROGRAM_ID;
			command[1] = commandType;
//printf("%s num: %d, offset:%d type:0x%02x\r\n",__FUNCTION__, num,offset,commandType);

			retval = gcdcInterfaceSetReport(devh1,  REPROGRAM_ID, command , 0x40);//TARGET_EP0_BUFFER_SIZE);
			if (retval)
			{
				printf("%s ERROR %d\n", __FUNCTION__, retval);
				return(retval);
			}
			ptr += num;
			offset +=num;
			bytesRemaining -= num;
		}
		dataSize -= 0x100;
	}

	bytesRemaining = dataSize;
//printf("%s page: %d\r\n",__FUNCTION__, pageCount);
       	setPage(devh1,pageCount);
	while( bytesRemaining)
	{
		num = (bytesRemaining < MAX_WRITE)? bytesRemaining : MAX_WRITE;
		memcpy(&command[4], ptr,num);
		command[3] = num;
		command[2] = offset;
		command[0] = REPROGRAM_ID;
		command[1] = commandType;

//printf("%s num: %d, offset:%d type:0x%02x\r\n",__FUNCTION__, num,offset,commandType);
		retval = gcdcInterfaceSetReport(devh1,  REPROGRAM_ID, command , TARGET_EP0_BUFFER_SIZE);
		if (retval)
		{
			printf("%s ERROR %d\n", __FUNCTION__, retval);
			return(retval);
		}
		ptr += num;
		offset +=num;
		bytesRemaining -= num;
	}
	return(retval);
}


int writeToFlash( gusb_device_handle *devh1, uint8_t* data, int32_t dataSize)
{
	unsigned char* psrc;
	unsigned char* pdest;
	unsigned char command[] = {REPROGRAM_ID, WRITE_PAGE_COMMAND, BLANK, BLANK};
//	unsigned char response[] = {RESPONSE_REPORT, BLANK};
	FLASH_BUFFER flashBuffer;
	int retval = 0;

	memset(flashBuffer, BLANK, TARGET_EP0_BUFFER_SIZE);
	flashBuffer[0] = FLASH_REPORT;
	psrc = data;
	retval = gcdcInterfaceSetReport(devh1, FLASH_REPORT, command, 4);
	if(retval)
	{
		printf("writeToFlash, ERROR Sending writePage Code\r\n");
		return(retval);
	}

	int32_t i;
//	printf("\r\nwrite command sent, sending data\r\n");
	for (i=0; i<dataSize; i += (TARGET_EP0_BUFFER_SIZE-1) )
	{
//		printf("constructing index: %d\r\n",i);
		pdest = &flashBuffer[1];
		int32_t j;
		for ( j=i; ((j < (i + (TARGET_EP0_BUFFER_SIZE - 1))) && (j < dataSize)); j++)
		{
//	flashBuffer[(j - i) + 1] = data[j] ^ FLASH_DATA_MASK;
			*pdest++ = (*psrc++) ^ FLASH_DATA_MASK;
		}
		retval = gcdcInterfaceSetReport(devh1, FLASH_REPORT, flashBuffer, TARGET_EP0_BUFFER_SIZE);
		if (retval)
		{
			printf("writeToFlash ERROR %d\n",retval);
			return(retval);
		}
//		printf("write report sent index %d\r\n",j);
		memset(&flashBuffer[1], BLANK, (TARGET_EP0_BUFFER_SIZE - 1));
	}
	return(retval);
}


int readFromFlash( gusb_device_handle *devh1, int startAddress, int length, uint8_t* data)
{
	unsigned char* pdest;
	unsigned char command[] = {REPROGRAM_ID, READ_FLASH_BYTE_COMMAND, BLANK, BLANK};
	int retval =0;
	int addr;

	memset(data, 0, length);
	pdest = data;

	for(addr = startAddress; addr < startAddress+length; addr++)
	{
		command[2] = (addr>>8) & 0xff;
		command[3] = addr & 0x00ff;
//printf("addr 0x%04x ",addr);
		retval = sendCommandWaitResponse(devh1,command);
		if(retval < 0) return(retval);
//printf("0x%x   ",retval);
		*pdest++ = (retval & 0x00ff);
	}
//printf("done\n");
	return(0);
}


int sambaRead( gusb_device_handle *devh1, int32_t startAddress, int32_t length, uint32_t* data)
{
	uint32_t* pdest;
	uint8_t command[] = {REPROGRAM_ID, READ_INT32_COMMAND, BLANK, BLANK, BLANK, BLANK};
        unsigned char response[] = {REPROGRAM_ID, READ_INT32_COMMAND, BLANK,BLANK,BLANK,BLANK};
        int retval =0;
	int32_t addr;

	memset(data, 0, length/sizeof(uint32_t));
	pdest = data;

	for(addr = startAddress; addr < startAddress+length*sizeof(uint32_t); addr+=sizeof(uint32_t))
	{
		command[2] = (addr) & 0xff;
		command[3] = (addr>>8) & 0x00ff;
		command[4] = (addr>>16) & 0x00ff;
		command[5] = (addr>>24) & 0x00ff;
		retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 6);
        	if( retval )
        	{
		    printf("firmwareUpdater:sendCommandWaitResponse, ERROR sending command, retval %d\r\n",retval);
		    return(-2);
        	}
        	retval = gcdcInterfaceGetReport(devh1, REPROGRAM_ID,response, 6);
        	if( retval )
        	{
        		if(verbose_flag) printf("firmwareUpdater:sendCommandWaitResponse, ERROR Reading Data returned %d\r\n",retval);
        		return(-1);
        	}

		*pdest++ = ((response[2]) | (response[3]<<8) | (response[4]<<16) | (response[5]<<24));
	}
	return(0);
}


int internalReadPage( gusb_device_handle *devh1, int pageNumber, uint8_t* data)
{
    int startAddress = (pageNumber << 9) & 0xfe00;
    return(readFromFlash(devh1, startAddress, 512, data));
}

/* computes the crc on a block of 512 bytes similar to how the 8051 does it
* data  - pointer to the block to be tested
* returns the CRC value
*/
uint16_t calcCRCPage(unsigned char* data, int len)
{
	unsigned int k, j;
	uint16_t CRC;
	unsigned char *FlashPtr;

	FlashPtr = data;
	CRC = 0x0000;

	// Process each byte in the page into the running CRC
	for (k = 0; k < len; k++)
	{
	// Read the next Flash byte and XOR it with the upper 8 bits
	// of the running CRC.
		CRC ^= (*FlashPtr++ << 8);
		// For each bit in the upper byte of the CRC, shift CRC
		// left, test the MSB, and if set, XOR the CRC with the
		// polynomial coefficients (0x1021)
		for (j = 0; j < 8; j++)
		{
			CRC = CRC << 1;
			if (CRC & 0x8000 ) CRC ^= 0x1021;
		}
	}
	return(CRC);
}

uint16_t checkCRCPage(gusb_device_handle *devh1)
{
	int retval =0;
	uint16_t pageCRC;

	unsigned char command[] = {REPROGRAM_ID, CRC_ON_PAGE_COMMAND, BLANK, BLANK};
	unsigned char response[] = {CRC_REPORT, BLANK, BLANK };
	retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 4);
	if( retval)
	{
		printf("Error Sending CRC Code retval %d\n",retval);
		return(-2);
	}
	retval = gcdcInterfaceGetReport(devh1, REPROGRAM_ID, response, 3);
	if(retval)
	{
		printf("Error Reading CRC Data %d\n",retval);
		return(-1);
	}
	pageCRC = (unsigned char)(response[1]) | ((unsigned char)(response[2]) << 8);
	return(pageCRC);
}


uint16_t sambaCheckCRCPage(gusb_device_handle *devh1, int commandType)
{
	int retval =0;
	uint16_t pageCRC;

	unsigned char command[] = {REPROGRAM_ID, CRC_ON_PAGE_COMMAND, commandType, BLANK};
	unsigned char response[] = {CRC_REPORT, BLANK, BLANK };
	retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 4);
	if( retval)
	{
		printf("Error Sending CRC Code retval %d\n",retval);
		return(-2);
	}
	retval = gcdcInterfaceGetReport(devh1, REPROGRAM_ID, response, 4);
	if(retval)
	{
		printf("Error Reading CRC Data %d\n",retval);
		return(-1);
	}
//printf("%s 0x%02x %02x %02x %02x\r\n",__FUNCTION__,response[0],response[1],response[2],response[3]);
	pageCRC = (unsigned char)(response[2]) | ((unsigned char)(response[3]) << 8);
	return(pageCRC);
}

int isInFlasherMode = 0;
int shwVersion = 0;
int sswVersion = 0;
#define SAM_BA_HARDWARE_VERSION 0xBA

int resetFirmware(gusb_device_handle *devh1)
{
	unsigned char command[] = {REPROGRAM_ID, RESET_DEVICE_COMMAND, BLANK, BLANK};
	if(shwVersion == SAM_BA_HARDWARE_VERSION) 
		sendCommandNoWaitResponse(devh1,command);
	else 
		sendCommandWaitResponse(devh1, command);
	isInFlasherMode = 0;

	return(0);

}

#define REBOOT_TO_SAM_BA_COMMAND 8

int rebootToSamBaMode(gusb_device_handle *devh1)
{
	unsigned char command[] = {REPROGRAM_ID, REBOOT_TO_SAM_BA_COMMAND, BLANK, BLANK};

	sendCommandWaitResponse(devh1, command);
	isInFlasherMode = 0;
	return(0);
}


int readFlashByte(gusb_device_handle *devh1, uint8_t* data, int32_t address)
{
	unsigned char command[] = {REPROGRAM_ID, READ_FLASH_BYTE_COMMAND, ((address & 0xFF00) >> 8), (address & 0xFF)};
	unsigned char response[] = {RESPONSE_REPORT, BLANK};
	int retval = 0;

	retval = gcdcInterfaceSetReport(devh1, REPROGRAM_ID, command, 4);
	if(retval)
	{
	    printf("ReadFlashByte ERROR %d\n",retval);
	    return(-1);
	}

	retval = gcdcInterfaceGetReport(devh1,REPROGRAM_ID, response, 2);
	if(retval)
	{
	    printf("ReadFlashByte ERROR %d\n",retval);
	    return(-2);
	}

	*data = response[1];
	return(0);
}

int samBa_rebootToSamBaMode= 1;
int enterFlasherCode(gusb_device_handle *devh1)
{

	if(enterBootloadMode(devh1, 7, 1)) 		//Enter bootload mode by specifying the current hw/sw version
	{
//		printf("firmwareUpdater enterFlasherCode, ERROR, could not enter update mode\n");
		return(-1);
	}

	if(verbose_flag) printf("entered Flash read/write mode\n");
	shwVersion = getHardwareVersion(devh1);
	sswVersion = getSoftwareVersion(devh1);

	if(verbose_flag)
	{ 	
		printf("Target Versions, Hardware: 0x%02x, software:0x%02x\r\n\r\n\r\n",shwVersion,sswVersion);
	}
	if(shwVersion == SAM_BA_HARDWARE_VERSION)
	{
//setPage(devh1, 14); 
                if(samBa_rebootToSamBaMode)
                {
        	        rebootToSamBaMode(devh1);
	                resetFirmware(devh1);
                	return(0);
                }
        }
        else
        {
       		printf("ERROR hwversion mismatch expected 0x%x, received 0x%x\n", SAM_BA_HARDWARE_VERSION, shwVersion);
       		return(-2);
        }

	return(0);
}



int erase(gusb_device_handle* devh1, int pageNumber)
{
    int loopCount = 0;
    while(loopCount < 8)
    {
	if(verbose_flag) printf("setting page 0x%02x\n",pageNumber);
	int retval = setPage(devh1,pageNumber);
	if(retval != 1 )
	{
	    printf("warning page did not set corretly %d, retrying\n",retval);
	    if(loopCount++ > 3)
	    {
		printf("ERROR: %s retries exceeded setting page, FLASH locked?\r\n",__FUNCTION__);
		return(-1);
	    }
	    continue;
	}
	retval =erasePage(devh1);
	if(retval != 1)
	{
	    printf("Warning %s page did not erase corretly (%d), retrying\n",__FUNCTION__,retval);
	    if(loopCount++ > 3)
	    {
		printf("ERROR: %s retries exceeded, FLASH locked?\r\n",__FUNCTION__);
		return(-1);
	    }
	    continue;
	}
	break;
    }
    return(0);
}

int sambaWritePage(gusb_device_handle *devh1, int pageNumber, unsigned char* data, uint32_t len, uint32_t crc16, int commandType)
{
	int loopCount = 0;
	uint16_t crc;
	while(loopCount < 1)
	{
		sambaWriteToFlash(devh1, data, len, pageNumber, commandType);
                setPage(devh1,pageNumber);
		crc = sambaCheckCRCPage(devh1,commandType);
		if(crc != crc16)
		{
			printf("%s Warning, crc's do not match, life is not good %x != %x\r\n", __FUNCTION__,crc, crc16);
			if(loopCount++ > 4)
			{
				printf("%s ERROR: retries exceeded\r\n", __FUNCTION__);
				return(-1);
			}
			continue;
		}
		else
                    return(0);
	}
	return(-1);

}

int writePage(gusb_device_handle *devh1, int pageNumber, unsigned char* data, unsigned int crc16)
{
    int loopCount = 0;
    uint16_t crc;
//    int retval;
    while(loopCount < 8)
    {

	int retval = erase(devh1, pageNumber);
	if(retval)
	{
	    if(loopCount++ > 4)
	    {
		printf("ERROR: %s retries exceeded, FLASH locked?\r\n",__FUNCTION__);
		return(-1);
	    }
	    continue;
	}
//        if(verbose_flag) printf("setting page 0x%02x\n",pageNumber);
//        int retval = setPage(devh1,pageNumber);
//        if(retval != 1 )
//        {
//            printf("warning page did not set corretly %d, retrying\n",retval);
//            if(loopCount++ > 4)
//            {
//                printf("ERROR: retries exceeded\r\nSomething is crazy wrong, time to low level reprogram the target, sorry\r\n");
//                return(-1);
//            }
//            continue;
//        }
//        retval =erasePage(devh1);
//        if(retval != 1)
//        {
//            printf("warning page did not erase corretly (%d), retrying\n",retval);
//            if(loopCount++ > 4)
//            {
//                printf("ERROR: retries exceeded during erasePage\r\nSomething is crazy wrong, time to low level reprogram the target, sorry\r\n");
//                return(-1);
//            }
//            continue;
//        }
//
	writeToFlash(devh1, data,512);
	usleep(10000);
	crc = checkCRCPage(devh1);
	if(crc != crc16)
	{
	    printf("Warning, crc's do not match, life is not good %x != %x\r\n",crc, crc16);
	    if(loopCount++ > 4)
	    {
		printf("ERROR: %s retries exceeded\r\n",__FUNCTION__);
		return(-1);
	    }
	    continue;
	}
	return(0);
    }
    return(-1);
}


int bootloadMCU(gusb_device_handle *devh1, uint8_t swVersion, uint8_t hwVersion, struct targetPageInfo* tpi)
{
	//Initialize status and error to false
	int retval = 0;
	int i;
	samBa_rebootToSamBaMode = 1;
	retval = enterFlasherCode(devh1);
	if(retval) return(retval);
	printf("Your USB Device is being updated. Do not remove the device until update is completed.\n");

	for(i=0;i<MAX_PAGES;i++)
	{
		struct targetPageInfo* ptpi = &tpi[i];
		if(ptpi->pageNumber < 0) break;
		if(ptpi->fIsUsed == 0) continue;

		if(ptpi->pageNumber >= RESERVED_START)
		{
			if(verbose_flag) printf("INFO: reserved page encounterd 0x%x\r\n",ptpi->pageNumber);
			continue;
		}
		if((ptpi->pageNumber == CONFIG_PAGE) && (ptpi->fOverwrite == 0) ) continue;
		// need to add code here to test for black-listed pages of code
		// give info of black listed page and continue as it isn't a big deal
		if(writePage(devh1,ptpi->pageNumber,ptpi->data,ptpi->crc16))
		{
usleep(10000);
resetFirmware(devh1);
		  usleep(10000);
		  return(-1);
		}
	}

	if(verbose_flag) printf("Reprograming completed, resetting device with new code\r\n");
	usleep(10000);
	resetFirmware(devh1);
	usleep(10000);

	return(retval);
}

#define MAX_IMAGE_SIZE 0x10000
int firmwareUpdaterUpdateDevice(gusb_device_handle *devh1, char* filename)
{
	uint8_t* targetImage;
	uint32_t imageStart =-1;
	uint32_t imageEnd =-1;
	int pagesToProgram = 0;
	int lastPageUsed = 0;
	int i;
	int j;
	int retval =0;
	struct targetPageInfo* tpi;

	if(verbose_flag) printf("reading from <%s>\r\n",filename);

	// open and test hex file before attempting to program device
	targetImage = (uint8_t*)malloc(MAX_IMAGE_SIZE);
	memset(targetImage,0xff,MAX_IMAGE_SIZE);

	tpi = (struct targetPageInfo*)malloc(sizeof(struct targetPageInfo)*MAX_PAGES);
	memset(tpi,0x00,sizeof(struct targetPageInfo)*MAX_PAGES);

	retval = ihex_load_file(filename,targetImage,&imageStart, &imageEnd, 0xff, MAX_IMAGE_SIZE);
	{
	  if(retval <0)
	  {
	    printf("Error loading or processing hex file, device NOT reprogramed!\n");
	    return(retval);
	  }
	}
	if(imageStart <0)
	{
		printf("updateDevice, ERROR, no image found\n");
		return(-1);
	}


	for(i=imageStart/PAGE_SIZE; i<=imageEnd/PAGE_SIZE;i++)
	{// walk through image finding pages that are not all 0xff (needing programing)
		uint8_t* pdata;
		tpi[i].data=targetImage+i*PAGE_SIZE;
		pdata=tpi[i].data;
		tpi[i].pageNumber=i;
		if(tpi[i].pageNumber == CONFIG_PAGE)
		{
		    tpi[i].fIsUsed = 0;
		    continue;
		}
		for(j=0;j<PAGE_SIZE;j++)
		{
		  if(*pdata++ != 0xff)
		  {
		    tpi[i].fIsUsed = 1;
		    pagesToProgram++;
		    lastPageUsed=i;
		    break;
		  }
		}
		if(tpi[i].fIsUsed)
		{
		    tpi[i].crc16 = calcCRCPage(tpi[i].data, 512);
//        printf("page: %3d  CRC: 0x%04x\r\n",tpi[i].pageNumber,tpi[i].crc16);
		}
	}

	if( verbose_flag)
	{
	    uint32_t startAddr = 0;
	    uint32_t len = 0xffff;
	    uint8_t image[MAX_IMAGE_SIZE];

	    memset(image,0xff,len);
	    for(i=imageStart/PAGE_SIZE; i<=imageEnd/PAGE_SIZE;i++)
	    {// walk through image finding pages that are not all 0xff (needing programing)
		uint8_t* pdata;
		pdata=tpi[i].data;
//                if(tpi[i].pageNumber == CONFIG_PAGE)
//                {
//                    tpi[i].fIsUsed = 0;
//                    continue;
//                }
		if(tpi[i].fIsUsed)
		{
		    int offset = tpi[i].pageNumber*PAGE_SIZE;
		    for(j=0;j<PAGE_SIZE;j++)
		    {
			image[offset+j] = *pdata++;
		    }
		}
	    }
	    ihex_save_file( "temp.hex", image,startAddr, len );
	}

	if(verbose_flag) printf("Pages to program: %d, last page: %d\r\n",pagesToProgram,lastPageUsed);
	if(pagesToProgram==0)
	{
		printf("parsing image indicates no work to be performed (all 0xff?)\r\n");
		return(-1);
	}

	// so at this point targetImage contains an image of the target flash prom
	// and that file has been parsed into pages with the CRC computed
	// next the usbhid stuff must make a connection to the target
	// and finally reprogram the target
	// we do it this way (order, parse file, test image, connect to device, program device
	// because we don't want a parse error in the middle of
	// reprogramming the target! :=)
	if(verbose_flag) printf("image parsing complete\r\n\r\n");

	retval = bootloadMCU(devh1, 7,1, tpi);

	free(tpi);
	free(targetImage);
	return(retval);
}



int firmwareUpdaterPageErase(gusb_device_handle* devh1, int page)
{
    if(isInFlasherMode == 0)
    {
        samBa_rebootToSamBaMode = 0;
	if(enterFlasherCode(devh1))
	    return(-1);
	isInFlasherMode = 1;
    }
    return(erase(devh1,page ));
}

int firmwareUpdaterPageCRC(gusb_device_handle* devh1, int pageNumber)
{
    if(isInFlasherMode == 0)
    {
        samBa_rebootToSamBaMode = 0;
	if(enterFlasherCode(devh1))
	    return(-1);
	isInFlasherMode = 1;
    }
    int retval = setPage(devh1,pageNumber);
    if(retval != 1 )
    {
        printf("ERROR: %s retries exceeded, FLASH locked?\r\\n",__FUNCTION__);
        return(-1);
    }

    return(checkCRCPage(devh1));
}


int configPageErase(gusb_device_handle* devh1)
{
    return(firmwareUpdaterPageErase(devh1,CONFIG_PAGE));
}


int configPageWrite(gusb_device_handle *devh1, unsigned char* data)
{
    int retval = 0;
    if(isInFlasherMode == 0)
    {
        samBa_rebootToSamBaMode = 0;
	if(enterFlasherCode(devh1))
	    return(-1);
	isInFlasherMode = 1;
    }

    if(shwVersion == SAM_BA_HARDWARE_VERSION)
    {
                int crc16 = calcCRCPage(data, 512);
		retval = sambaWritePage(devh1, 0 , data, 512, crc16, WRITE_CONFIG_PAGE_COMMAND);
		return(retval);
    }
    else
    {
        int crc16 = calcCRCPage(data, 512);
	if(verbose_flag)
	{
	    int sswVersion = getSoftwareVersion(devh1);
	    int shwVersion = getHardwareVersion(devh1);
	    printf("Target Versions, Hardware: 0x%02x, software:0x%02x\r\n\r\n\r\n",shwVersion,sswVersion);
	}
	retval = writePage(devh1, CONFIG_PAGE, data, crc16);
	return(retval);
    }
}


// pages are 512 byte blocks so page number 0x7f --> address FE00
int firmwareUpdaterPageRead(gusb_device_handle *devh1, unsigned char* data, unsigned char pageNum )
{
    if(data ==NULL) return(-1);
    samBa_rebootToSamBaMode = 0;
    if(isInFlasherMode == 0)
    {
	if(enterFlasherCode(devh1))
	    return(-1);
	isInFlasherMode = 1;
    }
    if(shwVersion == SAM_BA_HARDWARE_VERSION)
    {
	sambaRead(devh1, pageNum<<8, 512/sizeof(uint32_t), (uint32_t*)data);
	return(0);
    }
    else
    {
        return( internalReadPage(devh1, pageNum, data));
    }
}


int configPageRead(gusb_device_handle *devh1, unsigned char* data)
{
    samBa_rebootToSamBaMode = 0;
    if(isInFlasherMode == 0)
    {
	if(enterFlasherCode(devh1))
	    return(-1);
	isInFlasherMode = 1;
    }

    if(shwVersion == SAM_BA_HARDWARE_VERSION)
    {
        sambaRead(devh1, 0xFF000000, 512/sizeof(uint32_t), (uint32_t*)data );
        return(0);
    }
    else
    {
        return(firmwareUpdaterPageRead(devh1,data, CONFIG_PAGE));
    }
}


/*struct configList
{
    int length;
    int itemNumber;
    unsigned char* localCopy;
    struct configList* next;
};
*/
struct configList* insertStringElement(struct configList* prev, int itemNumber, char* string)
{
    struct configList* newList = malloc(sizeof(struct configList));
    memset(newList, 0, sizeof(struct configList));

    newList->length = strlen(string)+1;
    newList->itemNumber = itemNumber;
    newList->localCopy = (unsigned char*)malloc(newList->length);
    newList->type = TYPE_STRING;
    memcpy(newList->localCopy,string,newList->length);
    if(prev) prev->next = newList;
    newList->prev = prev;
//    newList->type = TYPE_STRING;
    return(newList);
}

struct configList* getListRoot(struct configList* member)
{
    struct configList* retval = member;
    while(retval->prev) retval = retval->prev;
    return(retval);
}

struct configList* insertU16Element(struct configList* prev, int itemNumber, unsigned short data)
{
    struct configList* newList = malloc(sizeof(struct configList));
    memset(newList, 0, sizeof(struct configList));

    newList->itemNumber = itemNumber;
    newList->length = 2;
    newList->localCopy = malloc(newList->length);
    newList->type = TYPE_U16;
    memcpy(newList->localCopy,&data,newList->length);
    if(prev) prev->next = newList;
    newList->prev = prev;
    return(newList);
}

struct configList* insertU32Element(struct configList* prev, int itemNumber, uint32_t data)
{
    struct configList* newList = malloc(sizeof(struct configList));
    memset(newList, 0, sizeof(struct configList));

    newList->itemNumber = itemNumber;
    newList->length = 4;
    newList->localCopy = malloc(newList->length);
    newList->type = TYPE_U32;
    memcpy(newList->localCopy,&data,newList->length);
    if(prev) prev->next = newList;
    newList->prev = prev;
//    printf("%s item#:%d len:%d data: %08x\r\n",__FUNCTION__, newList->itemNumber, newList->length, *(uint32_t*)(newList->localCopy));
    return(newList);
}

#define CRC_POLYNOM 0x8408
#define CRC_PRESET 0xFFFF

unsigned int crc16(unsigned char* ptr, int cnt)
{
    unsigned int crc = CRC_PRESET;
    unsigned char j;
    while(cnt--) // cnt = number of protocol bytes without CRC
    {
	crc ^= *ptr++;
	for (j = 0; j < 8; j++)
	{
	    if (crc & 0x0001)
		crc = (crc >> 1) ^ CRC_POLYNOM;
	    else
		crc = (crc >> 1);
	}
    }
    return(crc);
}

unsigned char* configListToPage(unsigned char* dest, struct configList* list)
{
    unsigned char* retval;
    unsigned char* scratch;
    int startScratch;
    struct configList* p;
    int maxItemNumber = 0;
    unsigned char* lookupTable;

    if(dest == NULL)
    {
	retval = malloc(512);
    }
    else retval = dest;
    memset(retval, 0xff , 512);

    // find the end of the lookuptable
    p = list;
    while(p)
    {
	if(p->itemNumber > maxItemNumber) maxItemNumber = p->itemNumber;
	p = p->next;
    }

    // compute scratchpad which starts right after the lookup table;
    startScratch = (maxItemNumber+2)*2;
    scratch = retval+startScratch;
//printf("scratch offset 0x%02x\n",startScratch);

    p= list;
    while(p)
    {
	// compute the location in the lookup table
	lookupTable = retval+ 2*p->itemNumber;

	//compute the absolute value for the lookup table
	*(unsigned short*)(lookupTable) =htole16( (CONFIG_PAGE<<9) + startScratch);
//printf("item %d, addr %04x\n",p->itemNumber,*(unsigned short*)lookupTable);
	memcpy(scratch,p->localCopy,p->length);

	// compute the next position in the scratchpad
	startScratch += p->length;
	scratch += p->length;
	p = p->next;
    }
    *(unsigned short*)retval = htole16(crc16(retval+2,510));
    return(retval);
}

void dumpConfigList(struct configList* pList)
{
    if(pList == NULL)
    {
	printf("dumpConfigList NULL config list\n");
	return;
    }

    do
    {
	if(pList->type == TYPE_STRING) printf("item Num: %d length %d, val: <%s>\n",pList->itemNumber,pList->length,pList->localCopy);
	else if(pList->type == TYPE_U16) printf("item Num: %d length %d, val: <%d>\n",pList->itemNumber,pList->length,*(short*)(pList->localCopy));
	else if(pList->type == TYPE_U32) printf("item Num: %d length %d, val: <%d>\n",pList->itemNumber,pList->length,*(uint32_t*)(pList->localCopy));
	pList = pList->next;
    }
    while (pList != NULL);


}

// two lists are merged together, with b taking precidence over a
struct configList* mergeConfigLists(struct configList* a, struct configList* b)
{
    if(a==NULL) return(b);
    if(b==NULL) return(a);

    struct configList* rootA = getListRoot(a);
    struct configList* rootB = getListRoot(b);

    struct configList* ptr = rootA;
    while( ptr)
    {
	struct configList* ptrb = rootB;
	while( ptrb)
	{
	    if(ptr->itemNumber == ptrb->itemNumber)
	    { // if the item in A is found in B, remove from A
		if(ptr->prev)
		    ptr->prev->next = ptr->next;
		else
		    rootA = ptr->next;

		if(ptr->next) ptr->next->prev= ptr->prev;

	    }
	    ptrb = ptrb->next;
	}
	ptr = ptr->next;
    }

    // at this point rootA contains all elements not found in B, now append B
    if(rootA == NULL) return(rootB);
    ptr = rootA;
    while(ptr->next !=NULL)
    {
	ptr = ptr->next;
    }
    ptr->next = rootB;

    return(rootA);
}

struct configList* pageToConfigList(unsigned char* src)
{
    struct configList* retval = NULL;
    struct configList* next = NULL;
    int i;
    int firstFound =0;

    unsigned int calcCrc = crc16(src+2, 510);
    unsigned int pageCrc = le16toh(*(unsigned short*)(src));
    if(calcCrc != pageCrc)
    {
	printf("crc's do not match computed 0x%04x found 0x%04x\n",calcCrc,pageCrc);
	return(retval);
    }

    for(i=1;i<=CONST_END_TABLE_STRINGS;i++)
    {
	int address = le16toh(*(unsigned short*)(src+2*i));
	int offset = address -(CONFIG_PAGE<<9);
//        printf("addr: %04x   offset %d\n",address, offset);
	if( (offset >((CONST_END_TABLE_STRINGS)*2)) && (offset < 512))
	{ // if the offset is valid, insert the entry into the list
	    unsigned char* pstr = src+offset;
	    next = insertStringElement(next,i,(char*)pstr);
	    if(!firstFound)
	    {
		retval = next;
		firstFound = 1;
	    }
	}
	else printf("bad address %d < %d\n", offset, ((CONST_END_TABLE_U16)*2));
    }

    for(i=1+CONST_END_TABLE_STRINGS;i<=CONST_END_TABLE_U16;i++)
    {
	int address = le16toh(*(unsigned short*)(src+2*i));
	int offset = address -(CONFIG_PAGE<<9);
//        printf("addr: %04x   offset %d\n",address, offset);
	if( (offset >(1+CONST_END_TABLE_U16)*2) && (offset < 512))
	{ // if the offset is valid, insert the entry into the list
	    unsigned short* pstr = (unsigned short*)(src+offset);
	    next = insertU16Element(next,i,le16toh(*pstr));
	    if(!firstFound)
	    {
		retval = next;
		firstFound = 1;
	    }
	}
    }

    for(i=1+CONST_END_TABLE_U16;i<=CONST_END_TABLE_U32;i++)
    {
	int address = le16toh(*(unsigned short*)(src+2*i));
	int offset = address -(CONFIG_PAGE<<9);
//        printf("addr: %04x   offset %d\n",address, offset);
	if( (offset >(1+CONST_END_TABLE_U32)*4) && (offset < 512))
	{ // if the offset is valid, insert the entry into the list
	    uint32_t* pstr = (uint32_t*)(src+offset);
	    next = insertU32Element(next,i,le32toh(*pstr));
	    if(!firstFound)
	    {
		retval = next;
		firstFound = 1;
	    }
	}
	else if(address == 0xffff)
	{
	    if(verbose_flag) printf("%s Found end table delimeter 0xffff\r\n",__FUNCTION__);
	    break;
        }
        else
	{
	    printf("%s Internal ERROR at U32 insert offset:%04x address:%04x\r\n",__FUNCTION__,offset,address);
//	    exit(-1);
        }
	    
    }

    return(retval);
}


