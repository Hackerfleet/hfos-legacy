"""


Module: Shareables
==================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hilight, error
from hfos.events.system import authorizedevent, AuthorizedEvents
# from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class shareablerequest(authorizedevent):
    pass


class ShareableWatcher(ConfigurableComponent):
    """
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the ShareableWatcher component.

        :param args:
        """

        super(ShareableWatcher, self).__init__("SHAREABLE", *args)

        AuthorizedEvents['shareable'] = shareablerequest

        self.log("Started")

    def objectcreation(self, event):
        if event.schema == 'shareable':
            self.log("Updating shareables")


    def shareablerequest(self, event):
        self.log('Reservation request:', event)
        try:
            if event.action == 'reserve':
                uuid = event.data['uuid']
                reserve_from = event.data['from']
                reserve_to = event.data['to']
                reserve_title = None if 'title' not in event.data else \
                    event.data['title']
                reserve_description = "" if 'description' not in event.data \
                    else event.data['description']

                shareable_model = objectmodels['shareable']
                shareable = shareable_model().find_one({'uuid': uuid})


                early = shareable_model().find_one({
                    'uuid': uuid,
                    'reservations': {
                        '$elemMatch': {
                            'starttime': {'$lte': reserve_from},
                            'endtime': {'$gte': reserve_from}
                        }
                    }
                })

                self.log('Any early reservation:', early, lvl=hilight)

                late = shareable_model().find_one({
                    'uuid': uuid,
                    'reservations': {
                        '$elemMatch': {
                            'starttime': {'$lte': reserve_to},
                            'endtime': {'$gte': reserve_to}
                        }
                    }
                })

                self.log('Any late reservation:', late, lvl=hilight)

                if not late and not early:
                    reservation = {
                        'useruuid': event.user.uuid,
                        'starttime': reserve_from,
                        'endtime': reserve_to,
                        'title': reserve_title if reserve_title else
                        "Reserved by " + event.user.account.name,
                        'description': reserve_description
                    }
                    shareable.reservations.append(reservation)
                    shareable.save()
                    self.log('Successfully stored reservation!', lvl=hilight)
                else:
                    self.log('Not able to store reservation due to '
                             'overlapping reservations.', lvl=error)
        except Exception as e:
            self.log('Unknown failure:', e, type(e), exc=True)
