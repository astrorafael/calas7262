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
import re
import csv
import datetime
import os.path

# -------------
# Other modules
# -------------

import requests

# ---------------
# Twisted imports
# ---------------

from twisted                   import __version__ as __twisted_version__
from twisted.logger            import Logger, LogLevel
from twisted.internet          import task, reactor, defer
from twisted.internet.defer    import Deferred, inlineCallbacks, returnValue, DeferredQueue
from twisted.internet.threads  import deferToThread


#--------------
# local imports
# -------------

from calas7262 import __version__
from calas7262.config import VERSION_STRING, loadCfgFile
from calas7262.logger import setLogLevel

from calas7262.service.reloadable import MultiService
from calas7262.config   import cmdline
from calas7262.protocol import AS7262ProtocolFactory, AS7262_KEYS
from calas7262.serial   import SerialService
from calas7262.stats    import StatsService    
from calas7262.console  import ConsoleService    



# ----------------
# Module constants
# ----------------

TSTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


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
        self.options     = options
        self.serialService = None
        self.statsService  = None
        self.consoService  = None
        self.factory       = AS7262ProtocolFactory()
        self.queue         = { 
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
        self.statsService = self.getServiceNamed(StatsService.NAME)
        self.consoService = self.getServiceNamed(ConsoleService.NAME)
        try:
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
        else:
            d = deferToThread(self._exportCSV, self.stats).addCallback(self._done, self.options['csv_file'])
            d = deferToThread(self._exportSamples).addCallback(self._done, self.options['csv_samples'])
           

    # ----------------------
    # Other Helper functions
    # ----------------------

    def _done(self, *args):
        log.info("CSV file {file} saved",file=args[1])


    def _exportSamples(self):
        '''Exports summary statistics to a common CSV file'''
        log.debug("Appending to CSV file {file}",file=self.options['csv_samples'])
        # Adding metadata to the estimation
        for sample in self.samples:
            sample['tstamp'] = (sample['tstamp'] + datetime.timedelta(seconds=0.5)).strftime(TSTAMP_FORMAT)
        
        keys = ['tstamp'] + AS7262_KEYS

        # CSV file generation
        writeheader = not os.path.exists(self.options['csv_samples'])
        with open(self.options['csv_samples'], mode='a+') as csv_samples:
            writer = csv.DictWriter(csv_samples, fieldnames=keys, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if writeheader:
                writer.writeheader()
            writer.writerows(self.samples)
        log.info("updated CSV file {file}",file=self.options['csv_samples'])


    def _exportCSV(self, stats):
        '''Exports summary statistics to a common CSV file'''
        log.debug("Appending to CSV file {file}",file=self.options['csv_file'])
        # Adding metadata to the estimation
       
        stats['tstamp']  = (datetime.datetime.utcnow() + datetime.timedelta(seconds=0.5)).strftime(TSTAMP_FORMAT)
        #stats['author']  = self.author
        
        # transform dictionary into readable header columns for CSV export
        oldkeys = ['tstamp', 'N', 'wavelength', 'photodiode',
            'violet', 'violet stddev', 'raw_violet', 'raw_violet stddev',
            'blue',   'blue stddev',   'raw_blue',   'raw_blue stddev',
            'green',  'green stddev',  'raw_green',  'raw_green stddev', 
            'yellow', 'yellow stddev', 'raw_yellow', 'raw_yellow stddev',
            'orange', 'orange stddev', 'raw_orange', 'raw_orange stddev',
            'red',    'red stddev',    'raw_red',    'raw_red stddev'
        ]
        newkeys = ['Timestamp', '# Samples', 'Wavelength', 'Photodiode (nA)',
            'Violet', 'StdDev', 'Violet (raw)', 'StdDev',
            'Blue',   'StdDev',   'Blue (raw)', 'StdDev',
            'Green',  'StdDev',  'Green (raw)', 'StdDev',
            'Yellow', 'StdDev', 'Yellow (raw)', 'StdDev',
            'Orange', 'StdDev', 'Orange (raw)', 'StdDev',
            'Red',    'StdDev',    'Red (raw)', 'StdDev'
        ]
        for old,new in zip(oldkeys,newkeys):
            stats[new] = stats.pop(old)
        # CSV file generation
        writeheader = not os.path.exists(self.options['csv_file'])
        with open(self.options['csv_file'], mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=newkeys, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if writeheader:
                writer.writeheader()
            writer.writerow(stats)
        log.info("updated CSV file {file}",file=self.options['csv_file'])


        

__all__ = [ "AS7262Service" ]