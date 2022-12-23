#include <stdint.h>
int firmwareUpdaterUpdateDevice(gusb_device_handle *devh1, char* filename);
int configPageWrite(gusb_device_handle *devh1, unsigned char* data);
int configPageRead(gusb_device_handle *devh1, unsigned char* data);
int configPageErase(gusb_device_handle *devh1);
int resetFirmware(gusb_device_handle *devh1);

// pages are 512 byte blocks so page number 0x7f --> address FE00
int firmwareUpdaterPageRead(gusb_device_handle *devh1, unsigned char* data, unsigned char pageNum );
int firmwareUpdaterPageErase(gusb_device_handle* devh1, int page);
int firmwareUpdaterPageCRC(gusb_device_handle* devh1, int pageNumber);


#define TYPE_STRING 1
#define TYPE_U16 2
#define TYPE_U32 3
#define TYPE_UNKNOWN 0

struct configList {
  int length;
  int itemNumber;
  unsigned char* localCopy;
  int type;
  struct configList* prev;
  struct configList* next;
};

struct configList* insertStringElement(struct configList* last, int itemNumber, char* string);
struct configList* insertU16Element(struct configList* last, int itemNumber, unsigned short data);
struct configList* insertU32Element(struct configList* last, int itemNumber, uint32_t data);
struct configList* getListRoot(struct configList* member);
unsigned char* configListToPage(unsigned char* dest, struct configList* list);
struct configList* pageToConfigList(unsigned char* src);
void dumpConfigList(struct configList* pList);
struct configList* mergeConfigLists(struct configList* a, struct configList* b);
unsigned int crc16(unsigned char* ptr, int cnt);
int enterFlasherCode(gusb_device_handle *devh1);
