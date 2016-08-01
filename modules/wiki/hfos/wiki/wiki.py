"""

Module: Wiki
============

Wiki manager

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, error, warn
from hfos.events import send
from hfos.database import ValidationError, objectmodels
import pymongo

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None
    hfoslog("No docutils found! Install it to get full functionality!",
            lvl=warn, emitter="WIKI")

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


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

    def _update_index(self):
        wikipage = objectmodels['wikipage']
        index = wikipage.find_one({'name': 'Index'})
        index.text = "<ul>"
        for item in wikipage.find(sort=[("name", pymongo.DESCENDING)]):
            index.text += '<li><a href="#/wiki/' + item.name + '">' + \
                          item.title + '</a></li>'
        index.save()

    def objectchange(self, event):
        """
        Checks if the newly updated object is a wikipage..
        If so, renders the new html.

        :param event: objectchange event
        """
        try:
            if event.schema == 'wikipage':
                newpage = objectmodels['wikipage'].find_one(
                    {'uuid': event.uuid})
                try:
                    hfoslog('[WIKI] Got a rendering candidate: ',
                            newpage._fields)

                    try:
                        if not publish_parts:
                            html = newpage.text
                        else:
                            html = publish_parts(
                                newpage.text,
                                writer_name='html')['html_body']

                        newpage.html = html
                        newpage.save()
                        self.log("Page successfully rendered")
                    except Exception as e:
                        self.log("Error during html rendering: ", e,
                                 type(e), newpage.isbn, lvl=error)
                except Exception as e:
                    self.log("Error during page update: ", e)

        except Exception as e:
            self.log("Page rendering notification error: ", event, e,
                     type(e), lvl=error)

    def wikirequest(self, event):
        """Wiki event handler for incoming events
        :param event: WikiRequest with incoming wiki pagename and pagedata
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data

            model = objectmodels['wikipage']

            if action == "get":
                wikipage = model.find_one({'name': data})

                if not wikipage:
                    self.log("Page not found: ", data)
                    wikipage = model({'uuid': str(uuid4()),
                                      'name': data,
                                      })
                else:
                    self.log("Page found, delivering: ", data)

                wikipacket = {'component': 'wiki',
                              'action': 'get',
                              'data': wikipage.serializablefields()
                              }
            elif action == "put":
                if data['uuid']:
                    wikipage = model.find_one({'uuid': data['uuid']})

                    if wikipage:
                        self.log("Updating old page.")
                        wikipage.update(data)
                    else:
                        wikipage = model(data)
                        self.log("Storing a new page:", wikipage._fields)
                        try:
                            wikipage.validate()
                            wikipage.save()
                        except ValidationError:
                            self.log("Validation of new page failed!",
                                     data, lvl=warn)

                        self.log("Page stored. Reindexing.")
                        self._update_index()
                        self.log("Reindexing done.")

                    wikipacket = {'component': 'wiki',
                                  'action': 'put',
                                  'data': (True, wikipage.name),
                                  }
                else:
                    hfoslog(
                        "[WIKI] Weird request without uuid! Trying to create "
                        "completely new page.",
                        lvl=warn)
                    wikipage = model(data)
                    wikipage.uuid = str(uuid4())
                    if wikipage.validate():
                        wikipage.save()

                    wikipacket = {'component': 'wiki',
                                  'action': 'put',
                                  'data': (True, wikipage.name),
                                  }

            else:
                self.log("Unsupported action: ", action, event,
                         event.__dict__, lvl=warn)
                return

            try:
                self.fireEvent(send(event.client.uuid, wikipacket))
            except Exception as e:
                self.log("Transmission error before broadcast: %s" % e,
                         lvl=error)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)
