# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import re
import datetime
import json

# ---------------
# Twisted imports
# ---------------

from twisted.logger               import Logger
from twisted.internet             import reactor
from twisted.internet.protocol    import ClientFactory
from twisted.protocols.basic      import LineOnlyReceiver

#--------------
# local imports
# -------------


# ----------------
# Module constants
# ----------------

# -----------------------

log = Logger(namespace='proto')

# ----------------
# Module functions
# ----------------



# ----------
# Exceptions
# ----------


class AS7262Error(Exception):
    '''Base class for all exceptions below'''
    pass



# -------
# Classes
# -------



# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

class AS7262ProtocolFactory(ClientFactory):

    def startedConnecting(self, connector):
        log.debug('Factory: Started to connect.')

    def buildProtocol(self, addr):
        log.debug('Factory: Connected.')
        return AS7262Protocol()

    def clientConnectionLost(self, connector, reason):
        log.debug('Factory: Lost connection. Reason: {reason}', reason=reason)

    def clientConnectionFailed(self, connector, reason):
        log.febug('Factory: Connection failed. Reason: {reason}', reason=reason)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

class AS7262Protocol(LineOnlyReceiver):


    # So that we can patch it in tests with Clock.callLater ...
    callLater = reactor.callLater

    # -------------------------
    # Twisted Line Receiver API
    # -------------------------

    def __init__(self):
        '''Sets the delimiter to the closihg parenthesis'''
        # LineOnlyReceiver.delimiter = b'\n'
        self._onReading     = set()                # callback sets
      
    def connectionMade(self):
        log.debug("connectionMade()")
        self._error_passes = 0


    def lineReceived(self, line):
        try:
            now = datetime.datetime.utcnow()
            line = line.decode('utf-8')  # from bytearray to string
            log.info("raw line => {line}", line=line)
            contents = json.loads(line)
        except Exception as e:
            self._error_passes += 1
            log.error('#{i}, Invalid JSON in line (ignoring) => {line}', i=self._error_passes, line=line)
            if self._error_passes == 6:
                self.enableSerialMsgs()
        else:
            contents[0] = "AS7262" if contents[0] == "A" else "OPT3001"
            if contents[0] == "AS7262":
                contents = zip(["type","seq","millis","exptime","gain","temp","violet","blue","green","yellow","orange","red"], contents)
            else:
                contents = zip(["type","seq","millis","exptime","lux"], contents)
            contents.append(('tstamp', now))
            contents = dict(contents)
            log.debug("decoded {dictionary}", dictionary=contents)
            for callback in self._onReading:
                callback(contents)

    def enableSerialMsgs(self):
        self.transport.write('x')
        self.transport.flushOutput()


    # ================
    # TESS Protocol API
    # ================


    def addReadingCallback(self, callback):
        '''
        API Entry Point
        '''
        self._onReading.add(callback)


    # --------------
    # Helper methods
    # --------------
        
        
#---------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------



__all__ = [
    "AS7262Error",
    "AS7262Protocol",
    "AS7262ProtocolFactory",
]