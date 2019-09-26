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
        self.options    = options
        self.qsize      = options['size']
        self.wavelength = options['wavelength']
        self.queue       = { 
            'violet' : deque([], self.qsize),
            'blue'   : deque([], self.qsize),
            'green'  : deque([], self.qsize),
            'yellow' : deque([], self.qsize),
            'orange' : deque([], self.qsize),
            'red'    : deque([], self.qsize),
        } 
            

    def startService(self):
        '''
        Starts Stats service
        '''
        log.info("starting Stats Service: Window Size= {w} samples", 
            w=self.options['size'])
        Service.startService(self)
        reactor.callLater(0, self.accumulate)
        self.nsamples = 0

       
    def stopService(self):
        log.info("stopping Stats Service")
        return Service.stopService(self)
    
    
    # --------------
    # Main task
    # ---------------

    @inlineCallbacks
    def accumulate(self):
        '''
        Task driven by deferred readings
        '''
        log.debug("starting statistics loop")
        while True:
            sample = yield self.parent.queue['AS7262'].get()
            self.nsamples += 1
            log.info("AS7262 sample {n}/{N}", n=self.nsamples, N=self.qsize)
            self.exptime = sample['exptime']
            self.gain    = sample['gain']
            self.queue['violet'].append(sample['violet'])
            self.queue['blue'].append(sample['blue'])
            self.queue['green'].append(sample['green'])
            self.queue['yellow'].append(sample['yellow'])
            self.queue['orange'].append(sample['orange'])
            self.queue['red'].append(sample['red'])
            if len(self.queue['red']) == self.qsize:
                self.computeStats()
                tables = self.formatStats()
                self.parent.onStatsComplete(self.stats, tables)
               
    # --------------
    # Main task
    # ---------------

    def computeStats(self):
        self.master = []
        self.master.append([self.qsize, self.wavelength, self.exptime, self.gain])
        self.detail = []
        self.stats = {}
        self.stats['N'] = self.qsize
        self.stats['wavelength'] = self.wavelength
        for key in self.queue.keys():   #['violet'.'blue','green','yellow','orange','red']:
            central = statistics.mean(self.queue[key])
            stddev  = round(statistics.stdev(self.queue[key], central), 2)
            central = round(central,2)
            self.detail.append([key, central, stddev])
            self.stats[key] = central
            self.stats[key + ' stddev'] = stddev

    def formatStats(self):
        #msg = []
        #msg.append(["Please adjust AS7262 Gain and Exposure Time"])
        #print(tabulate.tabulate(msg, tablefmt='grid'))
        headMas=["Samples","Wavelenth (nm)","Exp. Time (ms)", "Gain"]
        msg1 = tabulate.tabulate(self.master, headers=headMas, tablefmt='grid')
        headDet=["Band","Average Flux","Std. Deviation"]
        msg2 = tabulate.tabulate(self.detail, headers=headDet, tablefmt='grid')
        return (msg1, msg2)
       
        

__all__ = [ "StatsService" ]