

#include "json.h"
#include "gcdcInterface.h"


int JSON_snprintfTimestamp(char* dest, int len,  struct timeval* pTime, const char* pType)
{
	return(snprintf(dest, len,"\"%s\":%ld.%03ld",pType, pTime->tv_sec, pTime->tv_usec/1000));
}

int JSON_snprintfAccel(char* outString, int len, struct accelReport* ptr)
{
	char* pString = outString;
	int wrote = 0;
	int i;
	char sensName[3][2] = {"x", "y", "z"};
	struct timeval* acqTime;
	struct timeval zTime;
	acqTime = &zTime;
	zTime.tv_sec = ptr->sec;
	zTime.tv_usec = ptr->usec;
	wrote = JSON_SprintfStartObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	wrote = JSON_SprintfStartObject(pString, "accel");
	len -=wrote;
	pString +=wrote;
	wrote = JSON_snprintfTimestamp(pString, len, acqTime, "Timestamp");
	len -= wrote;
	pString += wrote;
	for(i=0;i<3;i++)
	{
		*pString++ = ',';
		len -= 1;
		wrote = JSON_SprintfInt(pString, sensName[i], ptr->accel[i]);
		len -= wrote;
		pString += wrote;
	}
	wrote = JSON_SprintfEndObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	wrote = JSON_SprintfEndObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	return(wrote);
}



#define MAX_TS_STRING 0x100

void JSON_PrintAccel(struct accelReport* ptr)
{
	char tempString[MAX_TS_STRING];
	JSON_snprintfAccel(tempString, MAX_TS_STRING, ptr);
	printf("%s\n", tempString);
}


int JSON_SnprintfAdc(char* outString, int len, adcDataReport* ptr)
{
	char* pString = outString;
	int wrote = 0;

	struct timeval* acqTime;
	struct timeval zTime;
	acqTime = &zTime;
	zTime.tv_sec = ptr->header.tm.tv_sec;
	zTime.tv_usec = ptr->header.tm.tv_usec;

	wrote = JSON_SprintfStartObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	wrote = JSON_SprintfStartObject(pString, "adc");
	len -=wrote;
	pString +=wrote;
	wrote = JSON_snprintfTimestamp(pString, len, acqTime, "Timestamp");
	len -= wrote;
	pString += wrote;
	*pString++=',';
	len--;
	wrote = JSON_SprintfArray_Int16(pString, "data", (int16_t*)ptr->sample, ptr->header.numValid);
	len -= wrote;
	pString += wrote;

	
	wrote = JSON_SprintfEndObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	wrote = JSON_SprintfEndObject(pString, NULL);
	len -=wrote;
	pString +=wrote;
	return(wrote);
}




void JSON_PrintAdc(adcDataReport* ptr)
{
	char tempString[MAX_TS_STRING];
	JSON_SnprintfAdc(tempString, MAX_TS_STRING, ptr);
	printf("%s\n", tempString);
}


#if 0
typedef struct _rptHeader
{
        uint8_t reportId;
        uint8_t numValid;
        uint8_t status;
        uint8_t reserved;
        struct timeval tm;
}  __attribute__ ((packed)) rptHeader;

#define MAX_PAYLOAD (64-sizeof( rptHeader))
typedef struct _adcDataReport
{
        rptHeader header;
        uint16_t sample[MAX_PAYLOAD/sizeof(uint16_t)];
} __attribute__ ((packed)) adcDataReport;


#endif
