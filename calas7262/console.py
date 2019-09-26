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

# ----------
# Exceptions
# ----------




# -------
# Classes
# -------

# My Command Line Intefrace portocol
class CommandLineProtocol(basic.LineReceiver):

    delimiter = os.linesep

    def __init__(self):
     
        self._callbacks  = {
            'start' : set(),
            'quit'  : set()
        }

    def lineReceived(self, line):
        line = line.lower()
        if  line == "quit":
            for callback in self._callbacks['quit']:
                callback()
        elif line == "start":
            for callback in self._callbacks['start']:
                callback()
        else:
            self.transport.write("ca7262> ")

    def addStartCallback(self, callback):
        '''
        API Entry Point
        '''
        self._callbacks['start'].add(callback)

    def addQuitCallback(self, callback):
        '''
        API Entry Point
        '''
        self._callbacks['quit'].add(callback)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class ConsoleService(Service):

    # Service name
    NAME = 'Console Service'


    def __init__(self, options):
        Service.__init__(self)
        self.options    = options
        self.protocol   = CommandLineProtocol()
        
    def startService(self):
        '''
        Starts the Console Service that listens to a TESS
        By exception, this returns a deferred that is handled by emaservice
        '''
        log.info("starting Console Service")
        self.protocol.addStartCallback(self.onCalibrationStart)
        self.protocol.addQuitCallback(self.onCalibrationQuit)
        self.stdio = stdio.StandardIO(self.protocol)  
        

    # ----------------------------
    # Helpers
    # -----------------------------

    def displayPrompt(self):
        self.stdio.write("ca7262> ")

    def displayTables(self, tables):
        for table in tables:
            self.stdio.write(str(table) + '\n')


    # ----------------------------
    # Event Handlers from Protocol
    # -----------------------------

    def onCalibrationStart(self):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onCalibrationStart()


    def onCalibrationQuit(self):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onCalibrationQuit()
       

    

__all__ = [
    "ConsoleService",
]