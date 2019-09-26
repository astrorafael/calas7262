# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# Some parts:
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import os
import signal

# ---------------
# Twisted imports
# ---------------

from zope.interface import implementer, Interface

from twisted.persisted import sob
from twisted.python    import components
from twisted.internet  import defer, task
from twisted.application.service import IService, Process

#--------------
# local imports
# -------------

import zptess.service.reloadable as reloadable
import zptess.service.pausable   as pausable

# ----------------
# Global functions
# -----------------


# --------------------------------------------------------------
# --------------------------------------------------------------
# --------------------------------------------------------------

class Service(reloadable.Service, pausable.Service):
    '''
    Pausable & Reloadable service
    '''

    def __init__(self):
        super(Service, self).__init__()

    def __getstate__(self):
        '''I don't know if this makes sense'''
        reloadable.Service.__getstate__(self)
        return pausable.Service.__getstate__(self)
       
        
# --------------------------------------------------------------
# --------------------------------------------------------------
# --------------------------------------------------------------

class MultiService(reloadable.MultiService, pausable.MultiService): 
    '''
    Container for pausable & reloadable services
    '''

    def __init__(self):
        super(MultiService, self).__init__()
   

        
# --------------------------------------------------------------
# --------------------------------------------------------------
# --------------------------------------------------------------     

class TopLevelService(reloadable.TopLevelService, pausable.TopLevelService):    
    '''
    Top level container for pausable & reloadable services.
    Handles the signals for pasue/resume & reload.
    '''

    def __init__(self):
        super(TopLevelService, self).__init__()
       
    def __getstate__(self):
        '''I don't know if this makes sense'''
        reloadable.TopLevelService.__getstate__(self)
        return pausable.TopLevelService.__getstate__(self)
        
    def _sighandler(self):
        '''
        Periodic task to check for signal events
        '''
        reloadable.TopLevelService._sighandler(self)
        pausable.TopLevelService._sighandler(self)
    
        
 

# --------------------------------------------------------------
# --------------------------------------------------------------
# --------------------------------------------------------------


def Application(name, uid=None, gid=None):
    """
    Return a compound class.
    Return an object supporting the L{IService}, L{IPausable}, L{IReloadable}, L{IServiceCollection},
    L{IProcess} and L{sob.IPersistable} interfaces, with the given
    parameters. Always access the return value by explicit casting to
    one of the interfaces.
    """
    ret = components.Componentized()
    availableComponents = [TopLevelService(), Process(uid, gid),
                           sob.Persistent(ret, name)]

    for comp in availableComponents:
        ret.addComponent(comp, ignoreClass=1)
    IService(ret).setName(name)
    return ret  

__all__ = [
    "Service",
    "MultiService",
    "TopLevelService",
    "Application",
]