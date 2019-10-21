# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import datetime
import os.path
import csv

from collections   import OrderedDict
from pkg_resources import resource_filename

# ---------------
# Twisted imports
# ---------------

from twisted.logger   import Logger, LogLevel
from twisted.internet import task, reactor, defer
from twisted.internet.defer  import inlineCallbacks, returnValue, DeferredList
from twisted.internet.threads import deferToThread
from twisted.application.service  import Service

#--------------
# local imports
# -------------

from calas7262.logger   import setLogLevel
from calas7262.protocol import AS7262_KEYS


# ----------------
# Module constants
# ----------------

TSTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='storag')

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------    
# -----------------------------------------------------------------------------  


class StorageService(Service):

    # Service name
    NAME = 'Storage Service'


    def __init__(self, options):
        Service.__init__(self)
        setLogLevel(namespace='stats', levelStr=options['log_level'])
        self.started    = False
        self.options    = options
        self.qe_data    = {}
        

    def startService(self):
        '''
        Starts Stats service
        '''
        log.info("starting Storage Service")
        Service.startService(self)
        log.info("before calling resource_string()")
        path = resource_filename(__name__, 'data/QE_photodiode.csv')
        log.info("Calling resource_string() returns {ret}",ret=str(path))
        self.loadQE(path)
        log.info("QE data is {qe}",qe=self.qe_data)

       
    def stopService(self):
        log.info("stopping Stats Service")
        return Service.stopService(self)


    def onCalibrationSave(self, stats, samples):
        d = deferToThread(self.saveSamples, samples).addCallback(self._done, self.options['csv_samples'])
        d = deferToThread(self.saveCSV, stats).addCallback(self._done, self.options['csv_file'])

    # ----------------------
    # Other Helper functions
    # ----------------------

    def loadQE(self, path):
        with open(path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    key   = int(row['WL'])
                    value = row['QE']
                    self.qe_data[key] = value
                line_count += 1

        

    def _done(self, *args):
        log.info("CSV file {file} saved",file=args[1])


    def saveSamples(self, samples):
        '''Exports summary statistics to a common CSV file'''
        log.debug("Appending to CSV file {file}",file=self.options['csv_samples'])
        w = self.options['wavelength']
        if not w in self.qe_data.keys():
            log.error("No available QE for the selected wavelength !!")
            reactor.stop()
       
        # Adding metadata to the estimation
        for sample in samples:
            sample['tstamp'] = (sample['tstamp'] + datetime.timedelta(seconds=0.5)).strftime(TSTAMP_FORMAT)
            sample['wavelength']  = self.options['wavelength']
            sample['current']     = self.options['photodiode']
            sample['quantum_eff'] = self.qe_data[w]
        
        keys = ['tstamp', 'wavelength', 'current', 'quantum_eff'] + AS7262_KEYS

        # CSV file generation
        writeheader = not os.path.exists(self.options['csv_samples'])
        with open(self.options['csv_samples'], mode='a+') as csv_samples:
            writer = csv.DictWriter(csv_samples, fieldnames=keys, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if writeheader:
                writer.writeheader()
            writer.writerows(samples)
        log.info("updated CSV file {file}",file=self.options['csv_samples'])



    def saveCSV(self, stats):
        '''Exports summary statistics to a common CSV file'''
        log.debug("Appending to CSV file {file}",file=self.options['csv_file'])
        # Adding metadata to the estimation
       
        stats['tstamp']  = (datetime.datetime.utcnow() + datetime.timedelta(seconds=0.5)).strftime(TSTAMP_FORMAT)
        #stats['author']  = self.author
        w = stats['wavelength']
        if not w in self.qe_data.keys():
            log.error("No available QE for the selected wavelength !!")
            reactor.stop()
        stats['quantum_eff'] = self.qe_data[w]
        
        # transform dictionary into readable header columns for CSV export
        oldkeys = ['tstamp', 'N', 'wavelength', 'photodiode', 'quantum_eff',
            'violet', 'violet stddev', 'raw_violet', 'raw_violet stddev',
            'blue',   'blue stddev',   'raw_blue',   'raw_blue stddev',
            'green',  'green stddev',  'raw_green',  'raw_green stddev', 
            'yellow', 'yellow stddev', 'raw_yellow', 'raw_yellow stddev',
            'orange', 'orange stddev', 'raw_orange', 'raw_orange stddev',
            'red',    'red stddev',    'raw_red',    'raw_red stddev'
        ]
        newkeys = ['Timestamp', '# Samples', 'Wavelength', 'Photod. I (A)', 'Photod. QE',
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

    
    

__all__ = [ "StorageService" ]