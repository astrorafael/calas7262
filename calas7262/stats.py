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
import random
import os
import math
import statistics

from collections import deque


import tabulate

# ---------------
# Twisted imports
# ---------------

from twisted          import __version__ as __twisted_version__
from twisted.logger   import Logger, LogLevel
from twisted.internet import task, reactor, defer
from twisted.internet.defer  import inlineCallbacks, returnValue, DeferredList, DeferredQueue
from twisted.internet.threads import deferToThread
from twisted.application.service  import Service

#--------------
# local imports
# -------------

from calas7262 import __version__
from calas7262.config import VERSION_STRING, loadCfgFile
from calas7262.logger import setLogLevel
from calas7262.config import cmdline
from calas7262.protocol   import COLOUR_KEYS


# ----------------
# Module constants
# ----------------


# ----------
# Exceptions
# ----------

class TESSEstimatorError(ValueError):
    '''Estimator is not median or mean'''
    def __str__(self):
        s = self.__doc__
        if self.args:
            s = "{0}: '{1}'".format(s, self.args[0])
        s = '{0}.'.format(s)
        return s

# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='stats')

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------    
# -----------------------------------------------------------------------------  


class StatsService(Service):

    # Service name
    NAME = 'Statistics Service'


    def __init__(self, options):
        Service.__init__(self)
        setLogLevel(namespace='stats', levelStr=options['log_level'])
        self.started    = False
        self.options    = options
        self.qsize      = options['size']
        self.wavelength = options['wavelength']
        self.photodiode = options['photodiode']
        if self.photodiode is not None:
            self.photodiode = '{:.6e}'.format(self.photodiode)
        

    def startService(self):
        '''
        Starts Stats service
        '''
        log.info("starting Stats Service: Window Size= {w} samples", 
            w=self.options['size'])
        Service.startService(self)
        reactor.callLater(0, self.accumulate)
        self.nsamples = 0
        self.started = True
        self.queue      = { 
            'violet'     : deque([], self.qsize),
            'blue'       : deque([], self.qsize),
            'green'      : deque([], self.qsize),
            'yellow'     : deque([], self.qsize),
            'orange'     : deque([], self.qsize),
            'red'        : deque([], self.qsize),
            'raw_violet' : deque([], self.qsize),
            'raw_blue'   : deque([], self.qsize),
            'raw_green'  : deque([], self.qsize),
            'raw_yellow' : deque([], self.qsize),
            'raw_orange' : deque([], self.qsize),
            'raw_red'    : deque([], self.qsize),
        } 
        log.info("photodiode current (A) = {current}", current= self.photodiode)
       
    def stopService(self):
        log.info("stopping Stats Service")
        self.started = False
        return Service.stopService(self)


    def onPhotodiodeInput(self, current):
        '''
        Takee note
        '''
        self.photodiode = '{:.6e}'.format(float(current[0]))
        log.info("photodiode current (A) = {current}", current= self.photodiode)
    
    # --------------
    # Main task
    # ---------------

    @inlineCallbacks
    def accumulate(self):
        '''
        Task driven by deferred readings
        '''
        log.debug("starting statistics loop")
        while self.started:
            sample = yield self.parent.queue['AS7262'].get()
            self.nsamples += 1
            log.info("received AS7262 sample {n}/{N}", n=self.nsamples, N=self.qsize)
            self.exptime = sample['exptime']
            self.gain    = sample['gain']
            self.accum   = sample['accum']
            self.queue['violet'].append(sample['violet'])
            self.queue['blue'].append(sample['blue'])
            self.queue['green'].append(sample['green'])
            self.queue['yellow'].append(sample['yellow'])
            self.queue['orange'].append(sample['orange'])
            self.queue['red'].append(sample['red'])
            self.queue['raw_violet'].append(sample['raw_violet'])
            self.queue['raw_blue'].append(sample['raw_blue'])
            self.queue['raw_green'].append(sample['raw_green'])
            self.queue['raw_yellow'].append(sample['raw_yellow'])
            self.queue['raw_orange'].append(sample['raw_orange'])
            self.queue['raw_red'].append(sample['raw_red'])
            if len(self.queue['red']) == self.qsize:
                masterEntry, detailEntry, statsEntry = self.computeStats()
                tables = self.formatStats(masterEntry, detailEntry)
                yield self.parent.onStatsComplete(statsEntry, tables)
                yield self.stopService()
               
    # --------------
    # Main task
    # ---------------

    def computeStats(self):
        masterEntry = []
        masterEntry.append([self.qsize, self.wavelength, self.exptime, self.gain, self.accum])
        detailEntry = []
        statsEntry = {}
        statsEntry['N'] = self.qsize
        statsEntry['wavelength'] = self.wavelength
        statsEntry['photodiode'] = self.photodiode
        for key in COLOUR_KEYS:   #['violet'.'blue','green','yellow','orange','red']:
            central = statistics.mean(self.queue[key])
            stddev  = round(statistics.stdev(self.queue[key], central), 2)
            central = round(central,2)
            detailEntry.append([key, central, stddev])
            statsEntry[key] = central
            statsEntry[key + ' stddev'] = stddev
        return masterEntry, detailEntry, statsEntry

    def formatStats(self, masterEntry, detailEntry):
        headMas=["Samples","Wavelength (nm)","Exp. Time (ms)", "Gain", "Accumulated"]
        table1 = tabulate.tabulate(masterEntry, headers=headMas, tablefmt='grid')
        headDet=["Band","Average Flux","Std. Deviation"]
        table2 = tabulate.tabulate(detailEntry, headers=headDet, tablefmt='grid')
        return (table1, table2)
       
        

__all__ = [ "StatsService" ]