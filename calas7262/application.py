# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import os.path

# ---------------
# Twisted imports
# ---------------

from twisted.internet import reactor

#--------------
# local imports
# -------------

from calas7262.service.reloadable import Application
from calas7262.logger import sysLogInfo,  startLogging
from calas7262.config import VERSION_STRING, cmdline_options


from calas7262.as7262    import AS7262Service
from calas7262.serial    import SerialService 
from calas7262.stats     import StatsService    

# Read the command line arguments
options, cmd_opts  = cmdline_options()

startLogging(console=cmd_opts.console, filepath=cmd_opts.log_file)

# ------------------------------------------------
# Assemble application from its service components
# ------------------------------------------------

application = Application("as7262")

as7262Service  = AS7262Service(options['as7262'])
as7262Service.setName(AS7262Service.NAME)
as7262Service.setServiceParent(application)

serialService = SerialService(options['serial'])
serialService.setName(SerialService.NAME)
serialService.setServiceParent(as7262Service)

statsService = StatsService(options['stats'])
statsService.setName(StatsService.NAME)
statsService.setServiceParent(as7262Service)

# --------------------------------------------------------
# Store direct links to subservices in our manager service
# --------------------------------------------------------

__all__ = [ "application" ]
