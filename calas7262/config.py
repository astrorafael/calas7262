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
import os
import os.path
import argparse
import errno

# Only Python 2
import ConfigParser

# ---------------
# Twisted imports
# ---------------

from twisted.logger import LogLevel

#--------------
# local imports
# -------------

from calas7262.utils import chop
from calas7262 import __version__

# ----------------
# Module constants
# ----------------


VERSION_STRING = "calas7262/{0}/Python {1}.{2}".format(__version__, sys.version_info.major, sys.version_info.minor)

# -----------------------
# Module global variables
# -----------------------


# ------------------------
# Module Utility Functions
# ------------------------

def cmdline():
    '''
    Create and parse the command line for the tess package.
    Minimal options are passed in the command line.
    The rest goes into the config file.
    '''
    parser = argparse.ArgumentParser(prog='calas7262')
    parser.add_argument('--version',        action='version', version='{0}'.format(VERSION_STRING))
    parser.add_argument('-k' , '--console', action='store_true', help='log to console')
    parser.add_argument('--log-file', type=str, default="calas7262.log", help='log file')
    parser.add_argument('--log-messages', action='store_true', help='log raw messages too')
    parser.add_argument('-s' , '--size',    type=int, default=25 , help='how many samples to take before computing statistics')
    parser.add_argument('-w' , '--wavelength', type=int, required=True, help='enter wavelength for CSV logging')
    parser.add_argument('-l' , '--log-level', type=str, default="info", choices=["info","debug"], help='enter wavelength for CSV logging')
    parser.add_argument('-c' , '--csv-file', type=str, default="calas7262.csv", help='statistics CSV file')
    parser.add_argument('-p' , '--port', type=str, default="/dev/ttyUSB0", help='Serial Port path')
    parser.add_argument('-b' , '--baud', type=int, default=115200, choices=[9600, 115200], help='Serial port baudrate')
    
    return parser.parse_args()

def cmdline_options():
    '''
    Load options from command line
    '''
   
    opts  = cmdline()
    
    options = {}
    options['as7262'] = {}
    options['as7262']['log_level']  = opts.log_level
    options['as7262']['csv_file']   = opts.csv_file
    
    options['serial'] = {}
    options['serial']['endpoint']      = "serial:" + opts.port + ":" + str(opts.baud)
    options['serial']['log_level']     = opts.log_level
    options['serial']['log_messages']  = opts.log_messages

    options['stats'] = {}
    options['stats']['log_level']   = opts.log_level
    options['stats']['size']        = opts.size
    options['stats']['wavelength']  = opts.wavelength
   
    return options, opts

def loadCfgFile(path):
    '''
    Load options from configuration file whose path is given
    Returns a dictionary
    '''

    if path is None or not (os.path.exists(path)):
        raise IOError(errno.ENOENT,"No such file or directory", path)

    options = {}
    parser  = ConfigParser.RawConfigParser()
    # str is for case sensitive options
    #parser.optionxform = str
    parser.read(path)

    options['as7262'] = {}
    options['as7262']['log_level']  = parser.get("as7262","log_level")
    options['as7262']['csv_file']   = parser.get("as7262","csv_file")
    
    options['serial'] = {}
    options['serial']['endpoint']      = parser.get("serial","endpoint")
    options['serial']['log_level']     = parser.get("serial","log_level")
   

    options['stats'] = {}
    options['stats']['log_level']     = parser.get("stats","log_level")
   
    return options


__all__ = ["VERSION_STRING", "loadCfgFile", "cmdline"]
