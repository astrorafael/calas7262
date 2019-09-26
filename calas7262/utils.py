# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import sys
import datetime

# ---------------
# Twisted imports
# ---------------

#--------------
# local imports
# -------------

# ----------------
# Module constants
# ----------------

# -----------------------
# Module global variables
# -----------------------

# setSystemTime function variable
setSystemTime = None

# ------------------------
# Module Utility Functions
# ------------------------

def chop(string, sep=None):
    '''Chop a list of strings, separated by sep and 
    strips individual string items from leading and trailing blanks'''
    chopped = [ elem.strip() for elem in string.split(sep) ]
    if len(chopped) == 1 and chopped[0] == '':
        chopped = []
    return chopped



def _win_set_time(dati):
    '''
    dati is a datetime.datetime object
    '''
    
    # http://timgolden.me.uk/pywin32-docs/win32api__SetSystemTime_meth.html
    # pywin32.SetSystemTime(year, month , dayOfWeek , day , hour , minute , second , millseconds )
    ##dayOfWeek = datetime.datetime(time_tuple).isocalendar()[2]
    ##pywin32.SetSystemTime( time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])
    time_tuple = dati.timetuple()
    dayOfWeek = dati.isocalendar()[2]
    pywin32.SetSystemTime( time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])


def _linux_set_time(dati):
    '''
    dati is a datetime.datetime object
    '''
    # /usr/include/linux/time.h:
    #
    # define CLOCK_REALTIME                     0
    CLOCK_REALTIME = 0

    # /usr/include/time.h
    #
    # struct timespec
    #  {
    #    __time_t tv_sec;            /* Seconds.  */
    #    long int tv_nsec;           /* Nanoseconds.  */
    #  };
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))

    ts = timespec()
    time_tuple = dati.timetuple()
    ts.tv_sec = int( time.mktime( dati )) 
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))



if sys.platform=='linux2':
    import ctypes
    import ctypes.util
    import time
    setSystemTime =  _linux_set_time
elif sys.platform=='win32':
    import win32api
    setSystemTime = _win_set_time


__all__ = ["chop", "setSystemTime"]
