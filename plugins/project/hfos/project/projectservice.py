"""

Module: ProjectService
======================

Doing rather not much except serve as module component entrypoint.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class ProjectService(ConfigurableComponent):
    """
    Empty hull component to store settings etc.
    """

    configprops = {}

    def __init__(self, **kwargs):
        super(ProjectService, self).__init__('PROJECT', **kwargs)
