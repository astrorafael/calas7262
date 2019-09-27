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
import re

# ---------------
# Twisted imports
# ---------------

from twisted.logger               import Logger
from twisted.protocols            import basic
from twisted.internet             import reactor, stdio
from twisted.internet.defer       import inlineCallbacks, returnValue
from twisted.application.service  import Service


#--------------
# local imports
# -------------

from calas7262.logger   import setLogLevel
from calas7262.utils    import chop


# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='conso')

PROMPT = "cal7262> "

COMMANDS = {
    'start':
        {
            'help' : 'start recording AS7262 data',
            'syntax' : r'^start',
            'callbacks' : set()       
        },
    'quit':
        {
            'help' : 'exit program',
            'syntax' : r'^quit',
            'callbacks' : set()        
        },
    'photodiode':
        {
            'help' : 'record photodiode current in nA',
            'syntax' : r'^photo\w\s+([-+]?[0-9]*\.?[0-9]+)',
            'callbacks' : set()        
        },
    'save':
        {
            'help' : 'save statistics to CSV file',
            'syntax' : r'^save',
            'callbacks' : set()        
        },
    'help':
        {
            'help' : 'display available commands',
            'syntax' : r'^help',
            'callbacks' : set()        
        },
    '<CR>':
        {
            'help' : '',
            'syntax' : r'^$',
            'callbacks' : set()        
        },
    
}

COMMANDS_PAT = { key: re.compile(val['syntax']) for key,val in COMMANDS.items() }

# ----------
# Exceptions
# ----------


# -------
# Classes
# -------

# My Command Line Intefrace portocol
class CommandLineProtocol(basic.LineReceiver):

    delimiter = os.linesep
      
    def lineReceived(self, line):
        line = line.lower()
        anymatched = False
        for key,regexp in COMMANDS_PAT.items():
            matchobj = regexp.search(line)
            if matchobj:
                anymatched = True
                callbacks = COMMANDS[key]['callbacks']
                N = range(1,regexp.groups+1)
                params = matchobj.group(*N)
                for callback in callbacks:
                    callback(params)
        if not anymatched:
            self.transport.write("Error> " + line +'\n')
            self.transport.write(PROMPT)

    def addCallback(self, key, callback):
        COMMANDS[key]['callbacks'].add(callback)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class ConsoleService(Service):

    # Service name
    NAME = 'Console Service'


    def __init__(self, options):
        Service.__init__(self)
        setLogLevel(namespace='as7262', levelStr=options['log_level'])
        self.options    = options
        self.protocol   = CommandLineProtocol()
       
        
    def startService(self):
        '''
        Starts the Console Service that listens to a TESS
        '''
        log.info("starting Console Service")
        self.stdio = stdio.StandardIO(self.protocol)
        self.protocol.addCallback('start', self.calibrationStart)
        self.protocol.addCallback('quit', self.calibrationQuit)
        self.protocol.addCallback('photodiode', self.calibrationPhotodiode)
        self.protocol.addCallback('help', self.displayHelp)
        self.protocol.addCallback('save', self.calibrationSave)
        self.protocol.addCallback('<CR>', self.calibrationCR)
          

    # ----------------------------
    # Helpers
    # -----------------------------

    def displayPrompt(self):
        self.stdio.write(PROMPT)

    def displayTables(self, tables):
        for table in tables:
            self.stdio.write(str(table) + '\n')

    # ----------------------------
    # Event Handlers from Protocol
    # -----------------------------

    def displayHelp(self, *args):
        msg = ""
        for key,entry in COMMANDS.items():
            if key != '':
                msg += '\t' + key + '\t' + entry['help'] + '\n'
        self.stdio.write(msg)
        self.displayPrompt()

    def calibrationStart(self, *args):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onCalibrationStart()


    def calibrationQuit(self, *args):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onCalibrationQuit()

    def calibrationPhotodiode(self, *args):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onPhotodiodeInput(args[0])
      
    def calibrationSave(self, *args):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onCalibrationSave()
      
    def calibrationCR(self, *args):
        '''
        Pass it onwards when a new reading is made
        '''
        self.displayPrompt()
       

    

__all__ = [
    "ConsoleService",
]