/**
* gcdc1343 datalogger board
* Authors: Mike Crowe
* Copyright (C) 2018,  Gulf Coast Data Concepts, LLC
*/
//#define TRACE_LEVEL TRACE_LEVEL_DEBUG

#ifdef S_SPLINT_S
#include "../splint.h"
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <ctype.h>

//#include <stdbool.h>
#include <stdint.h>
#include <sys/time.h>
//#include <assert.h>
//#include <sys/time.h>
//#include "timer.h" //pTimestamp()
#include "json.h"
#ifndef __VALIST
#ifdef __GNUC__
#define __VALIST __gnuc_va_list
#else
#define __VALIST char*
#endif
#endif


/*----------------------------------------------------------------------------
 *        Local definitions
 *----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
*        Local variables
*----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------
 *        Local functions
 *----------------------------------------------------------------------------*/
#define printf_fast printf

void JSON_PrintfInt(const char* name, int32_t val)
{
	printf_fast("\"%s\":%d",name,val);
}


void JSON_PrintfString(const char* name, char* val)
{
	printf_fast("\"%s\":\"%s\",\r\n",name,val);
}


void JSON_PrintfStringObject(const char* name, const char* format, ...)
{
//	int retval;
	__VALIST args;
	printf_fast("{\"%s\":\"",name);

	va_start(args, format);
//        if( stdOut == 0)
		vprintf(format, args);
//        else
//        {
//                retval = vf_printf(stdOut,format, args);
//                if(retval < 0)
//                        printf("f_printf error %d %p\r\n",retval,stdOut);
//        }
	va_end(args);

	printf_fast("\"}\r\n");
}


void JSON_PrintfStartObject( const char* name)
{
	if(name == NULL)
		printf_fast("{");
	else
		printf_fast("\"%s\":{",name);
}


void JSON_PrintfEndObject( void)
{
	printf_fast("}\r\n");
}


void JSON_PrintfObject( const char* name, char* val)
{
	printf_fast("\"%s\":{%s}",name,val);
}


int JSON_SprintfInt(char* dest, const char* name, int32_t val)
{
	return(sprintf(dest,"\"%s\":%d",name,val));
}


int JSON_SprintfString(char* dest, const char* name, char* val)
{
	return(sprintf(dest, "\"%s\":\"%s\"",name,val));
}


int JSON_SprintfObject(char* dest, const char* name, char* val)
{
	return(sprintf(dest, "\"%s\":{%s}",name,val));
}


int JSON_SprintfStartObject(char* dest, const char* name)
{
	if(name ==NULL)
		return(sprintf(dest, "{"));
	else
		return(sprintf(dest, "\"%s\":{",name));
}


int JSON_SprintfEndObject(char* dest, const char* trailer)
{
	if(trailer ==NULL)
		return(sprintf(dest, "}"));
	else
		return(sprintf(dest, "}%s",trailer));
}

#define pTimeStamp(x) gettimeofday(x,NULL)
#pragma GCC diagnostic ignored "-Wsuggest-attribute=format"
static int json_vasprintfLogMessage(char* dest, int len, const char* format, __VALIST args)
{
	struct timeval xtime;
	if(dest == NULL)
		return(0);
	pTimeStamp(&xtime);
	char* ptemp = dest;
	int llen = len;
	int wrote;

	wrote = snprintf(dest, len,"\"log\":\"%ld.%03ld, ", xtime.tv_sec, xtime.tv_usec/1000);
	ptemp += wrote;
	len -= wrote;

	wrote = vsnprintf(ptemp, len, format, args);
	ptemp += wrote;
	len -= wrote;

	wrote = snprintf(ptemp, len,"\"\r\n");
	len -= wrote;

	return(llen-len);
}
#pragma GCC diagnostic pop


int __attribute__ ((format (gnu_printf, 3, 4))) JSON_SprintfLogMessage(char* dest, int len, const char* format, ...)
{
	int wrote;
	  __VALIST args;
	va_start(args, format);
		wrote = json_vasprintfLogMessage(dest, len, format, args);
	va_end(args);
	return(wrote);
}


void __attribute__ ((format (gnu_printf, 1, 2))) JSON_PrintfLogMessage(const char* format, ...)
{
	char temp[0x100];
	  __VALIST args;
	va_start(args, format);
		json_vasprintfLogMessage(temp, 0x100, format, args);
	va_end(args);
	printf_fast("{%s}", temp);
}


int JSON_SprintfArray_Int16(char* dest, const char* name, int16_t* src, int len)
{
	int i = 0;
	int retval = 0;
	int wrote;
	char* ptr = dest;

	wrote= sprintf(ptr,"\"%s\":[", name);
	ptr += wrote;
	retval += wrote;
	
	for(i=0;i<len;i++)
	{
		wrote= sprintf(ptr,"%d,",src[i]);
		ptr += wrote;
		retval += wrote;
	}
	ptr--;	// remove the last ',' from the list and replace it with a ']'
	*ptr++ = ']';
	*ptr++ = '\0';
	return(retval);
}


int JSON_SprintfArray_Int32(char* dest, const char* name, int32_t* src, int len)
{
	int i = 0;
	int retval = 0;
	int wrote;
	char* ptr = dest;

	wrote= sprintf(ptr,"\"%s\":[", name);
	ptr += wrote;
	retval += wrote;
	
	for(i=0;i<len;i++)
	{
		wrote= sprintf(ptr,"%d,",src[i]);
		ptr += wrote;
		retval += wrote;
	}
	ptr--;	// remove the last ',' from the list and replace it with a ']'
	*ptr++ = ']';
	*ptr++ = '\0';
	return(retval);
}


