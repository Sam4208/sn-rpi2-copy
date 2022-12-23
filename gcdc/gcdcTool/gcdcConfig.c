/*
 */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>
#include <math.h>	// sqrt

#include "gcdc.h"
#include "gcdcInterface.h"
#include "firmwareUpdater.h"
#ifdef PTHREAD_UPDATER
#include "pthreadUpdater.h"
#endif

#include <libxml/xmlreader.h>
#include "constIndeces.h"

extern char* version_string;

int verbose_flag = 0;
#define MAX_SERIAL_NUM 0x80
#define MAX_FILENAME 0x100
#define MAX_DEVICES 0x07f

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
	printf("\t--xml           reads the flash constans and outputs the results in the same format as the input document\n");
	printf("\t--read         reads the flash constants and displays the results\n");
	printf("\t--code filename convert the xml constants document to source format\n");
//	printf("\t--offy val          set the applied y offset\n");
	printf("\t--read              read the config information from the target device\n");
	printf("\t--erase             erase the config page (set to 0xff)\n");
	printf("\t--crc               compute the crc of the config page\n");
	printf("\t--update filename   write the config information to the target device\n");
	printf("\t--help              this help info\n");
}


xmlChar* getTextInNode(xmlTextReaderPtr reader)
{
	xmlChar* value;
	int ret = xmlTextReaderRead(reader);
	while (ret == 1)
	{
		if( xmlTextReaderNodeType(reader)== XML_READER_TYPE_TEXT)
		{
			value = xmlTextReaderValue(reader);
			return(value);
		}
		if(xmlTextReaderNodeType(reader) == XML_READER_TYPE_END_ELEMENT)
			return(NULL);
		ret = xmlTextReaderRead(reader);
	}
	return(NULL);
}

struct configList* rootList = NULL;
struct configList* currentListItem = NULL;


void xmlInsertU16(xmlTextReaderPtr reader, int index)
{
	xmlChar* value = getTextInNode(reader);
	if(value)
	{
		int val = atoi((char*)value);
		currentListItem = insertU16Element(currentListItem, index, val);
		if(verbose_flag) printf("<%d>\n",val);
		xmlFree(value);
	}
}


void xmlInsertU32(xmlTextReaderPtr reader, int index)
{
	xmlChar* value = getTextInNode(reader);
	if(value)
	{
//		uint32_t val = atoi((char*)value);
		uint32_t val = strtol((char*)value, NULL, 0);

		currentListItem = insertU32Element(currentListItem, index, val);
		if(verbose_flag) printf("<%d>\n",val);
		xmlFree(value);
	}
}


void xmlInsertString(xmlTextReaderPtr reader, int index)
{
	xmlChar* value = getTextInNode(reader);
	if(value)
	{
		currentListItem = insertStringElement(currentListItem, index, (char*)value);
		if(verbose_flag) printf("<%s>\n",(char*)value);
		xmlFree(value);
	}
}

struct nameMapping {
int index;
char* name;
char* codeName;
};

struct nameMapping nameMap [] = {
{CONST_USB_SERIAL,"serialNum","defaultUsbSerial"},
{CONST_USB_MANUFACTURER,"manufacturer","defaultUsbManufacturer"},
{CONST_USB_PRODUCT,"product","defaultUsbProduct"},
{CONST_TITLE,"title","defaultTitle"},
{CONST_DIR_NAME,"dataDir","defaultDirName"},
{CONST_X_OFFSET,"xOffset","0"},
{CONST_Y_OFFSET,"yOffset","0"},
{CONST_Z_OFFSET,"zOffset","0"},
{CONST_X_SCALE,"xScale","0"},
{CONST_Y_SCALE,"yScale","0"},
{CONST_Z_SCALE,"zScale","0"},
{0,NULL}
};


char* xmlHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<config lang=\"en-US\">\n";
char* xmlFooter = "</config>\n";

void dumpConfigListAsXml(struct configList* pList)
{
	int i;
	if(pList == NULL)
	{
		printf("dumpConfigList NULL config list\n");
		return;
	}
	printf("%s",xmlHeader);
	do
	{
		i=0;
		while(nameMap[i].name !=NULL)
		{
			if(nameMap[i].index == pList->itemNumber)
			{
				if(pList->type == TYPE_U16)
					printf("<%s>%d</%s>\n", nameMap[i].name, *(short*)(pList->localCopy), nameMap[i].name);
				if(pList->type == TYPE_U32)
					printf("<%s>%d</%s>\n", nameMap[i].name, *(int32_t*)(pList->localCopy), nameMap[i].name);
				if(pList->type == TYPE_STRING) 			
					printf("<%s>%s</%s>\n", nameMap[i].name, pList->localCopy, nameMap[i].name);
         
				break;
			}
			i++;
		}
		pList = pList->next;
	}
	while (pList != NULL);
	printf("%s",xmlFooter);
}

char* cHeader = "// CCONST_PAGE must agree with the number used in Makefile for reloacation of the CCONST segment  \n\
// the start of the segment must be such that the size of this segment does \n\
// the size of this module is less than 0x200 so F800-0x200 = F600 \n\
#define CCONST_BASE 0xF600\n\
#pragma constseg CCONST   \n\
\n\
// SERIAL_NUMBER_PAGE must agree with the number used in Makefile for reloacation of the UPDATER segment\n\
// the start of the segment must be such that the size of this segment does not spill over into the\n\
// reserved area of the 'F340 or 0xFBFF\n\
// the size of this module is less than 0x200 so F800-200 = F600\n\
#define SERIAL_NUMBER_PAGE (0xf600/512)\n\
#pragma codeseg CCONST\n";

void dumpConfigListAsCode(struct configList* pList, unsigned char* image)
{
	int i;
	if(pList == NULL)
	{
		printf("dumpConfigList NULL config list\n");
		return;
	}
	printf("%s",cHeader);
	printf("\n\n#define crcsum 0x%04x\n",crc16(image+2,510));
	printf("\nconst code char* code constTable[] = {(const char code*)crcsum, defaultUsbSerial, defaultUsbManufacturer, defaultUsbProduct, defaultTitle, defaultDirName};\n\n");
	do
	{
		i=0;
		while(nameMap[i].name !=NULL)
		{
			if(nameMap[i].index == pList->itemNumber)
			{
				printf("const code char %s[] = \"%s\";\n", nameMap[i].codeName, pList->localCopy);
				break;
			}
			i++;
		}
		pList = pList->next;
	}
	while (pList != NULL);
	printf("\n");
}



void processNode(xmlTextReaderPtr reader)
{
	/* handling of a node in the tree */
	xmlChar* name;

	name = xmlTextReaderName(reader);
	if (name == NULL)
		name = xmlStrdup(BAD_CAST "--");

	if(xmlTextReaderNodeType(reader) == XML_READER_TYPE_ELEMENT)
	{
		if(strcmp("serialNum", (char*)name) == 0)
		{
			if(verbose_flag) printf("Serial number: ");
			xmlInsertString(reader,CONST_USB_SERIAL);
		}
		else if(strcmp("manufacturer", (char*)name) == 0)
		{
			if(verbose_flag) printf("Manufacturer: ");
			xmlInsertString(reader,CONST_USB_MANUFACTURER);
		}
		else if(strcmp("product", (char*)name) == 0)
		{
			if(verbose_flag) printf("Product: ");
			xmlInsertString(reader,CONST_USB_PRODUCT);
		}
		else if(strcmp("title", (char*)name) == 0)
		{
			if(verbose_flag) printf("Title: ");
			xmlInsertString(reader,CONST_TITLE);
		}

		else if(strcmp("dataDir", (char*)name) == 0)
		{
			if(verbose_flag) printf("Data Dir: ");
			xmlInsertString(reader,CONST_DIR_NAME);
		}
		else if(strcmp("xOffset", (char*)name) == 0)
		{
			if(verbose_flag) printf("X offsetElement, ");
			xmlInsertU16(reader,CONST_X_OFFSET);
		}
		else if(strcmp("yOffset", (char*)name) == 0)
		{
			if(verbose_flag) printf("Y offsetElement, ");
			xmlInsertU16(reader,CONST_Y_OFFSET);
		}
		else if(strcmp("zOffset", (char*)name) == 0)
		{
			if(verbose_flag) printf("Z offsetElement, ");
			xmlInsertU16(reader,CONST_Z_OFFSET);
		}
		else if(strcmp("xScale", (char*)name) == 0)
		{
			if(verbose_flag) printf("X Scale, ");
			xmlInsertU32(reader,CONST_X_SCALE);
		}
		else if(strcmp("yScale", (char*)name) == 0)
		{
			if(verbose_flag) printf("Y Scale, ");
			xmlInsertU32(reader,CONST_Y_SCALE);
		}
		if(strcmp("zScale", (char*)name) == 0)
		{
			if(verbose_flag) printf("Z Scale, ");
			xmlInsertU32(reader,CONST_Z_SCALE);
		}

	}
	else if(xmlTextReaderNodeType(reader) == XML_READER_TYPE_SIGNIFICANT_WHITESPACE);
	else if(xmlTextReaderNodeType(reader) == XML_READER_TYPE_END_ELEMENT);
	else if(verbose_flag)
	{
	xmlChar* value;
		value = xmlTextReaderValue(reader);

		printf("%s unmatched element %d %d %s %d",__FUNCTION__,xmlTextReaderDepth(reader),xmlTextReaderNodeType(reader),name, xmlTextReaderIsEmptyElement(reader));
		if (value == NULL)
			printf("\n");
		else
		{
			printf(" <%s>\n", value);
			xmlFree(value);
		}
	}
	xmlFree(name);

}


int streamFile(char *filename)
{
	xmlTextReaderPtr reader;
	int ret;

	reader = xmlNewTextReaderFilename(filename);
	if (reader != NULL)
	{
		ret = xmlTextReaderRead(reader);
		while (ret == 1)
		{
			processNode(reader);
			ret = xmlTextReaderRead(reader);
		}
		xmlFreeTextReader(reader);
		if (ret != 0)
		{
			printf("%s : failed to parse\n", filename);
		}
	}
	else
	{
		printf("Unable to open %s\n", filename);
		return(-1);
	}
	return(ret);
}


int main(int argc, char *argv[])
{
	int retval = 1;
	int i;
	int c;
	char refSerialNum[MAX_SERIAL_NUM];
	char dutSerialNum[MAX_SERIAL_NUM];
	gusb_device_handle* devh[MAX_DEVICES];
	char filename[MAX_FILENAME];
	static int update_flag = 0;
	static int read_flag = 0;
	static int dump_flag = 0;
	static int xml_flag =0;
	static int erase_flag=0;
	static int erase_page=-1;
	static int crc_flag=0;
	static int code_flag =0;
	static int show_avail_flag = 0;
//	static int numTestSamples = 16;
	static int offsetTime = 0;

	char* serialNums[MAX_DEVICES];
	char temp[MAX_DEVICES][MAX_SERIAL_NUM];
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
			{"verbose", 	no_argument,		&verbose_flag, 1},
			{"xml",   	no_argument,		&xml_flag, 1},
			{"code",   	required_argument, 	0, 'c'},
			{"read",   	no_argument,       	&read_flag, 1},
			{"crc",   	no_argument,       	&crc_flag, 1},
			{"dump_flash",  no_argument,   		&dump_flag, 1},
			/* These options don't set a flag. We distinguish them by their indices. */
			{"offx",  	required_argument, 	0, 	'a'},
			{"sernum",  	required_argument, 	0, 	'b'},
			{"update",  	required_argument, 	0, 	'u'},
			{"offset",  	required_argument, 	0, 	'd'},
			{"help",    	no_argument, 		0, 	'?'},
			{"version",    	no_argument, 		0, 	'v'},
			{"erase", 	optional_argument,      0,	'e'},
			{0, 0, 0, 0}
		};

		int option_index = 0;
		c = getopt_long (argc, argv, "axr:d:f:",long_options, &option_index);
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
		case 'b':
			strncpy(dutSerialNum,optarg, MAX_SERIAL_NUM);
			if(verbose_flag) printf("Device Serial Number <%s>\n",refSerialNum);
			break;
		case 'e':
			erase_flag = 1;
			if(optarg ==NULL)
			{
				erase_page = -1;
			}
			else
			{
				erase_page = strtoul (optarg,NULL,0);
				if(verbose_flag) printf("Erasing page: 0x%02x  Addr:0x%04x\n",erase_page,erase_page<<9);
			}
			break;
		case 'c':
			strncpy(filename,optarg, MAX_FILENAME);
			if(verbose_flag) printf("updating with <%s>\n",filename);
			code_flag = 1;
			break;
		case 'd':
			offsetTime = atoi(optarg);
			if(verbose_flag) printf("offset for x %d\n",offsetTime);
			break;
		case 'u':
			strncpy(filename,optarg, MAX_FILENAME);
			if(verbose_flag) printf("updating with <%s>\n",filename);
			update_flag = 1;
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
		printf("non-option ARGV-elements: ");
		while(optind < argc)
			printf("%s ", argv[optind++]);
		printf("\n");
	}

	if(verbose_flag)
	{
		printf("gcdcTool VERSION %s\n",version_string);
	}

	retval = gcdcInterfaceInit(verbose_flag);
	if (retval < 0)
	{
		fprintf(stderr, "failed to initialise usb\n");
		exit(1);
	}
	if(verbose_flag) printf("Interface initialized\n");

	numDevicesFound = gcdcInterfaceGetSerialNumbers(serialNums, MAX_DEVICES, MAX_SERIAL_NUM);
	if(numDevicesFound <1)
	{
		printf("Wasn't able to find devices %d\n",numDevicesFound);
		retval = -2;
		goto out;
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

	for(i=0;i< numDevicesFound;i++)
	{
		// open devices
		if(verbose_flag) printf("Connecting to <%s>\n",serialNums[i]);
		devh[i] = gcdcInterfaceConnectToSerialNumber(serialNums[i]);
		if(devh[i] == NULL)
		{
			retval = -3;
			goto out;
		}
	}

	if(dump_flag )	// dump contents of entire flash
	{
		int j;
		unsigned char* image;
		int page = 0;
		fflush(stdout);
		image = malloc(512);

		for(i=0;i<numDevicesFound;i++)
		{
			fflush(stdout);
			for(page=0;page<0x7E;page++)
			{
				printf("Page 0x%02x Addr: %04x",page,page<<9);
				firmwareUpdaterPageRead(devh[i],image, page);
				for( j=0; j<512; j++)
				{
					if( j%32 == 0) printf("\n0x%04x:  ",(page<<9)+j);
					printf("%02x ",(unsigned char)(image[j]));
				}
				printf("\n");
			}
			resetFirmware(devh[i]);
		}
		retval=0;
		goto out;
	}

	if(update_flag || code_flag)	// update unit
	{
		if(verbose_flag) printf("z reading config file <%s>\n",filename);
		fflush(stdout);
		streamFile(filename);
		rootList = getListRoot(currentListItem);
		if(verbose_flag) printf("z config file read\n");
	}


	if(erase_flag)
	{
		for(i=0;i<numDevicesFound;i++)
		{
			printf("\neraseing config page on Device %d \n",i);
			fflush(stdout);
			if(erase_page<0)
			{
				if(configPageErase(devh[i]))
				{
					printf("Error eraseing page\n");
					exit(-1);
				}
			}
			else
			{
				if(firmwareUpdaterPageErase(devh[i],erase_page))
				{
					printf("Error eraseing page\n");
					exit(-1);
				}
			}
			resetFirmware(devh[i]);
		}
	}

	if(crc_flag)
	{
		for(i=0;i<numDevicesFound;i++)
		{
			printf("\nDevice: %d Config Page ",i);
			fflush(stdout);
			int crc = firmwareUpdaterPageCRC(devh[i],0x7B);
			printf("crc: 0x%04x\n",crc);
		}
	}

	if(update_flag)	// update unit
	{
		int j;
		unsigned char* image;
		printf("updating firmware on %d devices\n",numDevicesFound);
		fflush(stdout);
		image = malloc(512);

		//make image of 512 byte sector of config data here

		for(i=0;i<numDevicesFound;i++)
		{
			printf("\nDevice %d \n",i);
			fflush(stdout);
			configPageRead(devh[i],image);
			struct configList* remade = pageToConfigList(image);
			dumpConfigList(remade);
			rootList = getListRoot(currentListItem);

			rootList = mergeConfigLists(remade, rootList);

			dumpConfigList(rootList);
			image = configListToPage(NULL,rootList);

			if(verbose_flag)
			{
			printf("Image to write\n");
				for(j=0;j<512;j++)
				{
					if(j%32 == 0) printf("\n0x%04x:  ",j);
					printf("%02x ",(unsigned char)(image[j]));
				}
				printf("\n");
			}

			retval = configPageWrite(devh[i], image);
			resetFirmware(devh[i]);
			if(retval)
			{
				exit(-1);
			}

		}
		printf("\n");
		exit(0);
	}

	if(read_flag || xml_flag)	// update unit
	{
		int j;
		unsigned char* image;
//		printf("reding config info %d devices\n",numDevicesFound);
		fflush(stdout);
		image = malloc(512);

		for(i=0;i<numDevicesFound;i++)
		{
//			printf("\nDevice %d \n",i);
			fflush(stdout);

			configPageRead(devh[i],image);
			if(verbose_flag)
			{
				for( j=0; j<512; j++)
				{
					if( j%32 == 0) printf("\n0x%04x:  ",j);
					printf("%02x ",(unsigned char)(image[j]));
				}
				printf("\n");
			}

			struct configList* remade = pageToConfigList(image);
			if(xml_flag) dumpConfigListAsXml(remade);
			else dumpConfigList(remade);

			resetFirmware(devh[i]);
		}
//		printf("\n");
	}

	if(code_flag)
	{
		unsigned char* image = configListToPage(NULL,rootList);
		dumpConfigListAsCode(rootList, image);
	}


	for(i=0;i<numDevicesFound;i++)
	{
		gcdcInterfaceRelease(devh[i]);
	}


out:
	gcdcInterfaceDeinit();
	return retval >= 0 ? retval : -retval;
}

