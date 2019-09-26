# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import os
import sys

# ---------------
# Twisted imports
# ---------------

from twisted.logger   import (
    Logger, LogLevel, globalLogBeginner, textFileLogObserver, 
    FilteringLogObserver, LogLevelFilterPredicate)

# ----------------
# Module constants
# ----------------

# -----------------------
# Module global variables
# -----------------------

# Global object to control globally namespace logging
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.info)

# ------------------------
# Module Utility Functions
# ------------------------

def startLogging(console=True, filepath=None):
    '''
    Starts the global Twisted logger subsystem with maybe
    stdout and/or a file specified in the config file
    '''
    global logLevelFilterPredicate
   
    observers = []
    if console:
        observers.append( FilteringLogObserver(observer=textFileLogObserver(sys.stdout),  
            predicates=[logLevelFilterPredicate] ))
    
    if filepath is not None and filepath != "":
        observers.append( FilteringLogObserver(observer=textFileLogObserver(open(filepath,'a')), 
            predicates=[logLevelFilterPredicate] ))
    globalLogBeginner.beginLoggingTo(observers)


def setLogLevel(namespace=None, levelStr='info'):
    '''
    Set a new log level for a given namespace
    LevelStr is: 'critical', 'error', 'warn', 'info', 'debug'
    '''
    level = LogLevel.levelWithName(levelStr)
    logLevelFilterPredicate.setLogLevelForNamespace(namespace=namespace, level=level)

# ----------------------------------------------------------------------

# Convenient syslog functions for both Widndows and Linux

sysLogInfo  = None
sysLogError = None

if os.name == "nt":
    import servicemanager

    sysLogInfo  = servicemanager.LogInfoMsg
    sysLogError = servicemanager.LogErrorMsg
    
else:
    import syslog

    def sysLogError(*args):
        syslog.syslog(syslog.LOG_ERR, *args)

    def sysLogWarn(*args):
        syslog.syslog(syslog.LOG_WARNING, *args)    

    def sysLogInfo(*args):
        syslog.syslog(syslog.LOG_INFO, *args)


    sysLogInfo  = syslog.syslog
    sysLogError = syslog.syslog


__all__ = ["startLogging", "setLogLevel", "sysLogError", "sysLogInfo"]