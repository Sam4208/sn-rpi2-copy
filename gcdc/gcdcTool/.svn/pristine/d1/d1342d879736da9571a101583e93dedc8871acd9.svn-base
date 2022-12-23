# Authors: mcrowe@gcdataconcepts.com
#
# DESCRIPTION: 
#
# Changes:
#

WIN_CC = i686-pc-mingw32-gcc

PROJECT = gcdcTool
PROJECT2 = gcdcConfig
PROJECT3 = gcdcSetTime
#DEBUG = --debug
CC = gcc
SRC_MIN = gcdcInterface.c gusb.c
OBJ_MIN = gcdcInterface.o gusb.o json.o jsonformat.o
OBJECTS = $(OBJ_MIN) ihex.o version.o firmwareUpdater.o atmelsam_ba.o
SRCS = gcdcTool.c $(SRC_MIN) ihex.c version.c firmwareUpdater.c pthreadUpdater.c gcdcConfig.c json.c jsonformat.c
AUX = Makefile ihex.h gcdcInterface.h gcdc.h constIndeces.h Makefile.orig README firmwareUpdater.h pthreadUpdater.h CHANGELOG
PREMADES = 
LIBS=-lusb-1.0  -lm
LIBS_MIN=-lusb-1.0 -lrt
prefix=/usr/local
bindir=$(prefix)/bin
INSTALL = /usr/bin/install  

UNAME := $(shell uname)
ifeq ($(UNAME), Linux)
#LIBUSB_INCLUDE_PATH=/usr/include
OBJECTS += pthreadUpdater.o
LIBUSB_INCLUDE_PATH=/usr/include
CFLAGS =  -I/usr/include/libxml2 -I$(LIBUSB_INCLUDE_PATH) -DPTHREAD_UPDATER -Wall
ALIBS = -lrt -L$(prefix)/lib $(LIBS) -Wl,-rpath=$(prefix)/lib -lpthread
ALIBS_MIN = -L$(prefix)/lib $(LIBS_MIN) -Wl,-rpath=$(prefix)/lib 
# do something Linux-y
ALIBS_XML = -lxml2
else
OS_EXTENSION=.exe
LIBUSB_INCLUDE_PATH=/usr/local/include
CFLAGS = -I/usr/include -I. -I$(LIBUSB_INCLUDE_PATH) -Wall
OBJECTS += windows.o
ALIBS = $(LIBUSB_A) -lsetupapi -lole32 -ladvapi32 -L/usr/local/lib
ALIBS_XML = /usr/local/lib/libxml2.dll
endif

CFLAGS += -DTRACE_LEVEL=NO_TRACE

#LIBUSB_AUX_INCLUDE = /home/Joey/libusb-pbatard/libusb
#CFLAGS = -I/usr/include -I. -I$(LIBUSB_INCLUDE_PATH) -DPTHREAD_UPDATER -Wall


#LINK = ../libtool --tag=CC --mode=link -o $@
#LIBS = -lsetupapi -lole32 -ladvapi32
#LDADD = /usr/local/lib/libusb-1.0.la -lusb-1.0
#LINK = /bin/sh ../libtool --tag=CC --mode=link gcc -Wshadow -std=gnu99 -Wall \
#-Wundef -Wunused -Wstrict-prototypes -Werror-implicit-function-declaration -g -O2\
#-no-undefined -avoid-version -o $@

#LFLAGS= -L$(prefix)/lib $(LIBS) -Wl,-rpath=/usr/local/lib/libusb-1.0.la 
# this last part is VERY important, it instructs the runtime to search the lib where the hid is!

LIBUSB_A = /usr/local/lib/libusb-1.0.dll.a

ALFLAGS = -Wshadow -std=gnu99 -Wall -Wundef -Wunused -Wstrict-prototypes -Werror-implicit-function-declaration -g -O2
ALINK = $(CC)  $(ALFLAGS)


all:	$(PROJECT)$(OS_EXTENSION) $(PROJECT2)$(OS_EXTENSION) $(PROJECT3)$(OS_EXTENSION)
#docs

docs:
	doxygen Doxyfile

distclean: clean
	svn st | grep ^\? | awk '{print $2}' | xargs -r rm -rf
        
clean:
	rm -rf $(PROJECT)$(OS_EXTENSION) $(PROJECT2)$(OS_EXTENSION) $(PROJECT3)$(OS_EXTENSION) *~ $(PROJECT).o $(PROJECT2).o $(PROJECT3).o $(OBJECTS) doc

$(PROJECT)$(OS_EXTENSION): $(PROJECT).o $(PREMADES) $(OBJECTS)
	$(ALINK) -o $@ $(PROJECT).o $(OBJECTS) $(ALIBS)

$(PROJECT2)$(OS_EXTENSION): $(PROJECT2).o $(OBJECTS)
	$(ALINK) -o $@ $(PROJECT2).o $(OBJECTS) $(ALIBS) $(ALIBS_XML)

$(PROJECT3)$(OS_EXTENSION): $(PROJECT3).o $(OBJ_MIN)
	$(ALINK) -o $@ $(PROJECT3).o $(OBJ_MIN) $(ALIBS_MIN)

%.o: %.c
	$(CC) -c $(CFLAGS) $(DEBUG) $<

atmelsam_ba.o: atmelsam_ba.c flashApplet3s4.h lowLevelApplet3s4.h flashApplet3u4.h lowLevelApplet3u4.h flashApplet3u2.h lowLevelApplet3u2.h  flashApplet3u1.h lowLevelApplet3u1.h
	$(CC) -c $(CFLAGS) $(DEBUG) $<

#flashApplet3s4.h: applet-flash-atsam3s4.bin
#	 bin2c --static --const --name flashApplet3s4 $< >$@

#flashApplet3u4.h: applet-flash-at91sam3u4.bin
#	 bin2c --static --const --name flashApplet3u4 $< >$@
#flashApplet3u2.h: applet-flash-at91sam3u2.bin
#	 bin2c --static --const --name flashApplet3u2 $< >$@
#flashApplet3u1.h: applet-flash-at91sam3u1.bin
#	 bin2c --static --const --name flashApplet3u1 $< >$@
	 
#lowLevelApplet3s4.h: applet-lowlevelinit-atsam3s4.bin
#	 bin2c --static --const --name lowLevelApplet3s4 $< >$@

#lowLevelApplet3u4.h: applet-lowlevelinit-at91sam3u4.bin
#	 bin2c --static --const --name lowLevelApplet3u4 $< >$@
#lowLevelApplet3u2.h: applet-lowlevelinit-at91sam3u2.bin
#	 bin2c --static --const --name lowLevelApplet3u2 $< >$@
#lowLevelApplet3u1.h: applet-lowlevelinit-at91sam3u1.bin
#	 bin2c --static --const --name lowLevelApplet3u1 $< >$@

install: all
	$(INSTALL) $(PROJECT) $(bindir)/$(PROJECT)
	$(INSTALL) $(PROJECT2) $(bindir)/$(PROJECT2)
	$(INSTALL) $(PROJECT3) $(bindir)/$(PROJECT3)
	$(INSTALL) 51-gcdc.rules /etc/udev/rules.d/51-gcdc.rules
	udevadm control --reload-rules && udevadm trigger
	
dist: $(SRCS) $(AUX)
#	echo gcdc_tool-`sed -e '/version_string/!d' -e 's/[^0-9.]*\([0-9.]*\).*/\1/' -e q version.c` > .fname
	echo gcdc_tool-r`svnversion .` > .fname
	-rm -rf `cat .fname`
	mkdir `cat .fname`
	ln $(SRCS) $(AUX) `cat .fname`
	tar chjf `cat .fname`.tar.bz2 `cat .fname`
	-rm -rf `cat .fname` .fname


# DO NOT DELETE

