
#include <pthread.h>
#include "gusb.h"

struct thread_data {
  int  thread_id;
  gusb_device_handle* devh;
  char* filename;
  int retval;
  pthread_t thread;
  int exit_code;
  struct thread_data* next;
};



struct thread_data* createUpdateThread( gusb_device_handle* devh1, char* filename);

int waitComplete(struct thread_data* threads);
