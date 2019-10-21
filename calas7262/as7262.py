# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

# -------------
# Other modules
# -------------


# ---------------
# Twisted imports
# ---------------

from twisted                   import __version__ as __twisted_version__
from twisted.logger            import Logger, LogLevel
from twisted.internet          import task, reactor, defer
from twisted.internet.defer    import Deferred, inlineCallbacks, returnValue, DeferredQueue

#--------------
# local imports
# -------------

from calas7262        import __version__
from calas7262.logger import setLogLevel

from calas7262.service.reloadable import MultiService
from calas7262.protocol import AS7262ProtocolFactory
from calas7262.serial   import SerialService
from calas7262.stats    import StatsService    
from calas7262.console  import ConsoleService    

# ----------------
# Module constants
# ----------------


# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='as7262')

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------    
# -----------------------------------------------------------------------------  


class AS7262Service(MultiService):

    # Service name
    NAME = 'AS7262'

    # Queue names, by priority
    QNAMES = ['AS7262','OPT3001']
  
    # Queue sizes
    QSIZES = [ 15, 15, 10, 10*24*60, 10*24*60]


    def __init__(self, options):
        MultiService.__init__(self)
        setLogLevel(namespace='as7262', levelStr=options['log_level'])
        self.options        = options
        self.serialService  = None
        self.statsService   = None
        self.consoService   = None
        self.storageService = None
        self.factory        = AS7262ProtocolFactory()
        self.queue          = { 
            'AS7262'  : DeferredQueue(),
            'OPT3001' : DeferredQueue(), 
        }
        self.stats = {}  

    def startService(self):
        '''
        Starts only two services (serial & probe) and see if we can continue.
        '''
        log.info('starting {name} {version} using Twisted {tw_version}', 
            name=self.name,
            version=__version__, 
            tw_version=__twisted_version__)
        self.serialService  = self.getServiceNamed(SerialService.NAME)
        self.serialService.setFactory(self.factory) 
        self.statsService   = self.getServiceNamed(StatsService.NAME)
        self.consoService   = self.getServiceNamed(ConsoleService.NAME)
        self.storageService = self.getServiceNamed(StorageService.NAME)
        try:
            self.storageService.startService()
            self.serialService.startService()
            self.consoService.startService()
        except Exception as e:
            log.failure("{excp!s}", excp=e)
            log.critical("Problems initializing {name}. Exiting gracefully", 
                name=self.serialService.name)
            reactor.callLater(0,reactor.stop)   # reactor is no yet running here ...

    @inlineCallbacks
    def stopService(self):
        log.info("Stopping other services")
        yield self.serialService.stopService()
        reactor.stop()

    # ----------------------------------
    # Event Handlers from child services
    # ----------------------------------

    def onReading(self, reading, who):
        '''
        Enqueues to the proper service
        '''
        qname = reading['type']
        self.queue[qname].put(reading)
        if reading['type'] == 'AS7262':
            self.samples.append(reading)

    def onDeviceReady(self):
        '''
        Disaplay a prompt
        '''
        self.consoService.displayPrompt()

    def onCalibrationStart(self):
        '''
        Pass it onwards when a new reading is made
        '''
        self.stats = {}
        self.samples = []
        self.statsService.startService()
        self.serialService.enableMessages()

    def onPhotodiodeInput(self, current):
        '''
        Pass it onwards when a new reading is made
        '''
        self.statsService.onPhotodiodeInput(current)
        

    def onCalibrationQuit(self):
        '''
        Pass it onwards when a new reading is made
        '''
        reactor.stop()


    def onStatsComplete(self, stats, tables):
        self.serialService.disableMessages()
        self.stats.update(stats)   # Merge dictionaries
        self.consoService.displayTables(tables)


    def onCalibrationSave(self):
        if len(self.stats) == 0:
            self.consoService.writeln("Sorry!, no stats to save.")
            return
        if not 'photodiode' in self.stats.keys():
            self.consoService.writeln("Enter photodiode current first!")
            return
        self.storageService.onCalibrationSave(self.stats, self.samples)
           

    # ----------------------
    # Other Helper functions
    # ----------------------

        

__all__ = [ "AS7262Service" ]