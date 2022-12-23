#ifndef _GCDC
#define _GCDC

#define GCDC_VID 0x10C4
#define GCDC_PID 0x84D1

/** Device product ID. */
#define HIDMSDDDriverDescriptors_PRODUCTID       0x6135
/** Device vendor ID (Atmel). */
#define HIDMSDDDriverDescriptors_VENDORID        0x03EB

#define GCDC_VID2 HIDMSDDDriverDescriptors_VENDORID
#define GCDC_PID2 HIDMSDDDriverDescriptors_PRODUCTID

#define GCDC_HID_INTERFACE 1
#define GCDC_HID_DATA_IN 0x83



#define SMBUS_ID 2
#define SMBUS_REPORT_COUNT 0x40

#define TIME_ID 1
#define TIME_REPORT_COUNT 0x13

#define GAIN_ID 3
#define GAIN_REPORT_COUNT 1

#define SELF_TEST_ID 5
#define SELF_TEST_REPORT_COUNT 1

#define ACCEL_ON_OFF_ID 7
#define ACCEL_ON_OFF_REPORT_COUNT 1

#define REPROGRAM_ID 19
#define REPROGRAM_REPORT_COUNT 3

//Unique ID sent to bootloader and required to put into a bootload state
#define UNIQUE_BL_ID    0x34

#define RESPONSE_REPORT 22

//#define DATA_REPORT 0x12
#define DATA_REPORT_COUNT 2*NUM_CHAN

#define TEMPERATURE_REPORT_ID 8
#define TEMPERATURE_REPORT_COUNT 17

#define PRESSURE_REPORT_ID 10
#define PRESSURE_REPORT_COUNT 17

#define HUMIDITY_REPORT_ID 11
#define PRESSURE_REPORT_COUNT 17

#define OLD_TEMPERATURE_REPORT_ID 2
#define OLD_PRESSURE_REPORT_ID 4
#define PPS_TIME_REPORT_ID 6
#define PPS_TIME_REPORT_COUNT 13

#define ACCEL32_REPORT_ID 17
#define ACCEL_REPORT_ID 18
#define ACCEL_REPORT_COUNT 22

#define GYRO_REPORT_ID 25
#define GYRO32_REPORT_ID 9
#define GYRO_REPORT_COUNT 22

#define QUAT_REPORT_ID 26
#define QUAT_REPORT_COUNT 62

#define ACCEL2_REPORT_ID 28
#define ACCEL2_REPORT_COUNT 22

#define MULTI_ACCEL_REPORT_ID 20
#define MULTI_ACCEL_REPORT_COUNT 62

#define MAG32_REPORT_ID 15
#define MAG_REPORT_ID 14
#define MAG_REPORT_COUNT 22

#define ERROR_REPORT_ID 16
#define ERROR_REPORT_COUNT 22

#define STRING_REPORT_ID 12
#define STRING_REPORT_COUNT 64

#define ADC_REPORT_ID 23

#define LUX_REPORT_ID 24
#define TACH_REPORT_ID 29       // 0x1D

#define GPS_LLH_REPORT_ID 21    // 0x15

#define PPG_REPORT_ID 4    // 0x04


#endif