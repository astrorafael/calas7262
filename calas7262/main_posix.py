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

from twisted.internet import reactor
from twisted.application.service import IService

#--------------
# local imports
# -------------

from calas7262             import __version__
from calas7262.application import application
from calas7262.logger      import sysLogInfo

# ----------------
# Module constants
# ----------------

# -----------------------
# Module global variables
# -----------------------


# ------------------------
# Module Utility Functions
# ------------------------

sysLogInfo("Starting {0} {1} Linux service".format(IService(application).name, __version__ ))
IService(application).startService()
reactor.run()
sysLogInfo("{0} {1} Linux service stopped".format(IService(application).name, __version__ ))
