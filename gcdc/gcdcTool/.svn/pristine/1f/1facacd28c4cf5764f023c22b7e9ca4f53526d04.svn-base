#ifndef _JSON
#define _JSON 1
#include <stdint.h>

void JSON_PrintfInt( const char* name, int32_t val);
void JSON_PrintfString( const char* name, char* val);
void JSON_PrintfObject( const char* name, char* val);
void JSON_PrintfStartObject( const char* name);
void JSON_PrintfEndObject( void);
//void JSON_PrintfStringObject(const char* name, char* val);
void JSON_PrintfStringObject(const char* name, const char* format, ...) __attribute__ ((format (gnu_printf, 2, 3)));


int JSON_SprintfInt(char* dest, const char* name, int32_t val);
int JSON_SprintfString(char* dest, const char* name, char* val);
int JSON_SprintfObject(char* dest, const char* name, char* val);

int JSON_SprintfStartObject(char* dest, const char* name);
int JSON_SprintfEndObject(char* dest, const char* trailer);
int JSON_SprintfLogMessage(char* dest, int len, const char* format, ...)   __attribute__ ((format (gnu_printf, 3, 4)));
void   __attribute__ ((format (gnu_printf, 1, 2))) JSON_PrintfLogMessage(const char* format, ...);

int JSON_SprintfArray_Int16(char* dest, const char* name, int16_t* src, int len);
int JSON_SprintfArray_Int32(char* dest, const char* name, int32_t* src, int len);

#endif