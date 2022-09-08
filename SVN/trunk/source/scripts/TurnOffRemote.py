#!/usr/bin/python

import serial as s
import UsefulFunctionsHaake as uf

# ------------------------------------------------------------- #
# Python script for turning off remote control of Haake. Should 
# used when desired set point has been reached.
# Lauren Dawson, 14.03.2016
# ------------------------------------------------------------- #

# Get data from the Haake over serial interface :
# -----------------------------------------------
ser = s.Serial(port='/dev/haake', baudrate=4800, timeout=2.0, parity=s.PARITY_NONE)


# Disable remote control :
# ------------------------
uf.disable_remote_control("d")
