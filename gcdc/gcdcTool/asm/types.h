
#ifndef _TYPES
#define _TYPES

//#include <os/threads_windows.h>
struct timespec {
		long tv_sec;
		long tv_nsec;
};


#ifndef CLOCK_REALTIME
enum {
  USBI_CLOCK_MONOTONIC,
  USBI_CLOCK_REALTIME
};

int windows_clock_gettime(int clk_id, struct timespec *tp);

#define CLOCK_REALTIME USBI_CLOCK_REALTIME
#define CLOCK_MONOTONIC USBI_CLOCK_MONOTONIC
#define clock_gettime windows_clock_gettime

#endif

#ifndef false
#define false 0
#endif

#ifndef true
#define true !false
#endif

//taylor these to your needs. This may be different on Windows Vista.
typedef unsigned short __u16;
typedef short __s16;
typedef unsigned char __u8;
typedef int __s32;
typedef unsigned int __u32;
typedef unsigned char bool;

//#ifndef MINGW
//#define MINGW
//#endif

#define le32toh(x) (x)
#define le16toh(x) (x)
#define htole16(x) (x)
#define htole32(x) (x)


#endif
