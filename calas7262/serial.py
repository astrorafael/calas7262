# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

# ---------------
# Twisted imports
# ---------------

from twisted.logger               import Logger
from twisted.internet             import reactor
from twisted.internet.defer       import inlineCallbacks, returnValue
from twisted.internet.serialport  import SerialPort
from twisted.application.service  import Service

#--------------
# local imports
# -------------

from calas7262.logger   import setLogLevel
from calas7262.utils    import chop


# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='serial')

# ----------
# Exceptions
# ----------




# -------
# Classes
# -------



# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class SerialService(Service):

    # Service name
    NAME = 'Serial Service'


    def __init__(self, options):
        Service.__init__(self)
        self.options    = options   
        protocol_level  = 'info' if self.options['log_messages'] else 'warn'
        setLogLevel(namespace='proto', levelStr=protocol_level)
        setLogLevel(namespace='serial', levelStr=self.options['log_level'])
        self.serport   = None
        self.protocol  = None
        self.endpoint  = None
        self.factory   = None
    
    def startService(self):
        '''
        Starts the Serial Service that listens to a TESS
        By exception, this returns a deferred that is handled by emaservice
        '''
        log.info("starting Serial Service")
        parts = chop(self.options['endpoint'], sep=':')
        if parts[0] == 'serial':
            self.endpoint = parts[1:]
            if self.serport is None:
                self.protocol = self.factory.buildProtocol(0)
                self.serport  = SerialPort(self.protocol, self.endpoint[0], reactor, baudrate=self.endpoint[1])
            self.gotProtocol(self.protocol)
            log.info("Using serial port {tty} at {baud} bps", tty=self.endpoint[0], baud=self.endpoint[1])
        else:
            raise

    
    def enableMessages(self):
        log.info("enabling messages from hardware")
        self.protocol.enableMessages()
      
    def disableMessages(self):
        log.info("disabling messages from hardware")
        self.protocol.disableMessages()

            

    # --------------
    # Helper methods
    # ---------------

    def setFactory(self, factory):
        self.factory = factory


    def gotProtocol(self, protocol):
        log.debug("Serial: Got Protocol")
        self.protocol  = protocol
        self.protocol.addReadingCallback(self.onReading)
        self.protocol.addDeviceReadyCallback(self.onDeviceReady)

    # ----------------------------
    # Event Handlers from Protocol
    # -----------------------------

    def onReading(self, reading):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onReading(reading, self)
       

    def onDeviceReady(self):
        '''
        Pass it onwards when a new reading is made
        '''
        self.parent.onDeviceReady()
       

__all__ = [
    "SerialService",
]