"""

Module: Wiki
============

Wiki manager

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, error, warn
from hfos.events.client import send
from hfos.database import ValidationError, objectmodels
import pymongo


# TODO: Currently unused:
# try:
#     from docutils.core import publish_parts
# except ImportError:
#     publish_parts = None
#     hfoslog("No docutils found! Install it to get full functionality!",
#             lvl=warn, emitter="WIKI")

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class Wiki(ConfigurableComponent):
    """
    Wiki manager

    Handles
    * incoming page requests and updates
    * a list of registered pagenames
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(Wiki, self).__init__('WIKI', *args)

        self.log("Started")

    def objectcreation(self, event):
        self._page_update(event)

    def objectchange(self, event):
        self._page_update(event)

    def _page_update(self, event):
        """
        Checks if the newly created object is a wikipage..
        If so, rerenders the automatic index.

        :param event: objectchange or objectcreation event
        """
        try:
            if event.schema == 'wikipage':
                self._update_index()

        except Exception as e:
            self.log("Page creation notification error: ", event, e,
                     type(e), lvl=error)

    def _update_index(self):
        self.log('Updating page index')
        wikipage = objectmodels['wikipage']
        index = wikipage.find_one({'name': 'Index'})
        index.html = "<ul>"
        for item in wikipage.find(sort=[("name", pymongo.DESCENDING)]):
            index.html += '<li><a href="#/wiki/' + item.name + '">' + \
                          item.title + '</a></li>'
        index.save()
