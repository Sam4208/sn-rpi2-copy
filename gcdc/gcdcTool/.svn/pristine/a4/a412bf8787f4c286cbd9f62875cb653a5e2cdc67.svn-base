

#include "asm/types.h"

#include <windows.h>
#include <setupapi.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <process.h>
#include <stdio.h>
#include <inttypes.h>
#include <objbase.h>  // for string to GUID conv. requires libole32.a
#define LIBUSB_SUCCESS 0
#define LIBUSB_ERROR_OTHER 1
#define LIBUSB_ERROR_INVALID_PARAM 2
#define TIMER_REQUEST_RETRY_MS            100
#define usbi_dbg printf

uint64_t hires_frequency, hires_ticks_to_ps;
const uint64_t epoch_time = UINT64_C(116444736000000000);	// 1970.01.01 00:00:000 in MS Filetime

HANDLE timer_mutex = NULL;

struct timespec timer_tp;
volatile LONG request_count[2] = {0, 1};  // last one must be > 0

HANDLE timer_request[2] = { NULL, NULL };
HANDLE timer_response = NULL;

int windows_clock_gettime(int clk_id, struct timespec *tp)
{
	FILETIME filetime;
	ULARGE_INTEGER rtime;
	DWORD r;
	switch(clk_id) {
	case USBI_CLOCK_MONOTONIC:
		if (hires_frequency != 0) {
			while (1) {
				InterlockedIncrement((LONG*)&request_count[0]);
				SetEvent(timer_request[0]);
				r = WaitForSingleObject(timer_response, TIMER_REQUEST_RETRY_MS);
				switch(r) {
				case WAIT_OBJECT_0:
					WaitForSingleObject(timer_mutex, INFINITE);
					*tp = timer_tp;
					ReleaseMutex(timer_mutex);
					return LIBUSB_SUCCESS;
				case WAIT_TIMEOUT:
					usbi_dbg("could not obtain a timer value within reasonable timeframe - too much load?");
					break; // Retry until successful
				default:
					//usbi_dbg("WaitForSingleObject failed: %s", windows_error_str(0));
					return LIBUSB_ERROR_OTHER;
				}
			}
		}
		// Fall through and return real-time if monotonic was not detected @ timer init
	case USBI_CLOCK_REALTIME:
		// We follow http://msdn.microsoft.com/en-us/library/ms724928%28VS.85%29.aspx
		// with a predef epoch_time to have an epoch that starts at 1970.01.01 00:00
		// Note however that our resolution is bounded by the Windows system time
		// functions and is at best of the order of 1 ms (or, usually, worse)
		GetSystemTimeAsFileTime(&filetime);
		rtime.LowPart = filetime.dwLowDateTime;
		rtime.HighPart = filetime.dwHighDateTime;
		rtime.QuadPart -= epoch_time;
		tp->tv_sec = (long)(rtime.QuadPart / 10000000);
		tp->tv_nsec = (long)((rtime.QuadPart % 10000000)*100);
		return LIBUSB_SUCCESS;
	default:
		return LIBUSB_ERROR_INVALID_PARAM;
	}
}


