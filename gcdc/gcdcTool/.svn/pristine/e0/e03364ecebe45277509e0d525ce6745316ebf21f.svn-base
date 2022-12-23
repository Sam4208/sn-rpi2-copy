
#include <stdio.h>

struct chipInfo
{
	uint32_t id_cidr;
	const char* name;
	uint32_t flash0_start_addr;
	uint32_t efcBaseAddr;
	uint32_t rstcBaseAddr;
	uint32_t efc2BaseAddr;
};

typedef struct _atmelsam_ba_handle
{
int fd;
_Bool isLowLevelInitDone;
char* lowLevelAppletFname;
char* flashAppletFname;
uint32_t flashCurrentAddr;
struct chipInfo* chip;
} atmelsam_ba_handle;


int AtmelSam_ba_setFlashAppletFilename(atmelsam_ba_handle* devh1, char* fname);
int AtmelSam_ba_setInitAppletFilename(atmelsam_ba_handle* devh1, char* fname);
int AtmelSam_ba_programFlash(atmelsam_ba_handle* devh1, char* fname);
atmelsam_ba_handle* AtmelSam_ba_Init(char* target);
                                                         