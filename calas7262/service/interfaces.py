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

from zope.interface import implementer, Interface

class IPausable(Interface):
    """
    A pausable interface for services.
    Run pause/resume code at the appropriate times.
    @type paused:         C{boolean}
    @ivar paused:         Whether the service is paused.
    """


    def pauseService():
        """
        Pauses the service. It can take a while, so it returns a Deferred
        @rtype: L{Deferred<defer.Deferred>}
        @return: a L{Deferred<defer.Deferred>} which is triggered when the
            service has finished shutting down. If shutting down is immediate,
            a value can be returned (usually, C{None}).
        """

    def resumeService():
        """
        Resumes the service. It can take a while, so it returns a Deferred
        @rtype: L{Deferred<defer.Deferred>}
        @return: a L{Deferred<defer.Deferred>} which is triggered when the
            service has finished shutting down. If shutting down is immediate,
            a value can be returned (usually, C{None}).
        """


class IReloadable(Interface):
    """
    A reloadable interface for services.
    Run reload code at the appropriate times.
    """


    def reloadService(config=None):
        """
        Reloads the service by reading on the fly its service configuration.
        Configuration can be stored be a file (more likely) or a database.
        If C{config} is C{None}, then the service must find out what changed
        may be reading a configuration file (most likely) or a database.
        Otherwise, C{config} as an object or data type meaningful for the
        service itself passeb by a container I{IReloadable} C{MultiCervice}.
        @type config: any meaningful datatype or object.
        @rtype: L{Deferred<defer.Deferred>}
        @return: a L{Deferred<defer.Deferred>} which is triggered when the
            service has finished reloading. If reloading is immediate,
            a value can be returned (usually, C{None}).
        """


__all__ = [ "IReloadable", "IPausable" ]