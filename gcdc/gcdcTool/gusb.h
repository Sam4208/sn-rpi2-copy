#ifndef _USB
#define _USB
/* ----------------------------------------------------------------------------
*        Gulf Coast Data Concepts 2014
* ----------------------------------------------------------------------------
*/
struct gusb_device_handle {
  void* osSpecific;	// this is a os specific pointer to the device we are using, for libusb, winusb, ...
  int hidIfaceNum;
  int hidEndpointIn;
  int hidBInterval;
};

typedef struct gusb_device_handle gusb_device_handle;

/*----------------------------------------------------------------------------
*        Exported functions
*----------------------------------------------------------------------------*/
// interaction with underlying hardware
int GUSB_SetReport(gusb_device_handle *devh, unsigned char reportId, unsigned char* dataBuffer, int dataBufferSize );
int GUSB_GetReport(gusb_device_handle *devh, unsigned char reportId, unsigned char* dataBuffer, int dataBufferSize );
int GUSB_GetSerialNum(gusb_device_handle *devh, char* buffer, int size);
int GUSB_GetRaw(gusb_device_handle *devh, unsigned char *buffer, int length);
int GUSB_FlushQueue(gusb_device_handle *devh, int numPackets);

// open/close hardware instance(s)
gusb_device_handle* GUSB_ConnectToSerialNumber(char* serialNumber);
gusb_device_handle** GUSB_ConnectToAvailableDevices(void);
void GUSB_Release(gusb_device_handle *devh);

// querry of available devices
int GUSB_GetSerialNumbers(char* list[], int maxEntries, int maxSize);

// open/close underlying hardware interface libusb, winusb, ...
int GUSB_Init(int debug_level);
void GUSB_Deinit(void);
#endif
