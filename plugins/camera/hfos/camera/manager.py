"""


Module: CameraManager
=====================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4
from circuits import handler, Timer, Event
from circuits.tools import tryimport
import six
from hfos.component import ConfigurableComponent
from hfos.events import send
from hfos.logger import error, debug

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

opencv = tryimport("cv2")


class CameraManager(ConfigurableComponent):
    """
    Handles camera updates, subscriptions and broadcasts
    """

    channel = "cam"

    def __init__(self, maxcams=16, *args):
        super(CameraManager, self).__init__("CAM", *args)

        self._cameras = {}
        self._subscribers = {}
        self._filming = True
        self._framecount = 0
        self._frames = {}

        if opencv is not None:
            self.log("Checking opencv for cameras.", lvl=debug)

            for cam in range(maxcams):
                video = opencv.VideoCapture(cam)
                if video.isOpened():
                    camera = {'uuid': str(uuid4()),
                              'name': 'Camera' + str(cam),
                              'cam': video
                              }
                    self._cameras[cam] = camera
                    self.log("Found camera [", cam, "]: ", camera)

            self.log("Starting timer")
            self.timer = Timer(0.05, Event.create("rec"),
                               persist=True).register(self)

            self.log("Found cameras: ", self._cameras, lvl=debug)
        else:
            self.log("No opencv, no cameras.")
        self.log("Started")

    def rec(self):
        """Records a single snapshot"""

        try:
            self._snapshot()
        except Exception as e:
            self.log("Timer error: ", e, type(e), lvl=error)

    def _snapshot(self):
        self._framecount += 1

        try:
            for camid, cam in self._cameras.items():
                if cam['uuid'] in self._subscribers:
                    # self.log("Taking input of ", cam)
                    success, cvresult = cam['cam'].read()
                    # self.log("Result: ", cvresult)
                    if success:

                        campacketheader = {'component': 'camera' + str(camid),
                                           'action': 'update',
                                           }
                        if six.PY3:
                            # noinspection PyArgumentList
                            campacket = bytes(str(campacketheader),
                                              encoding="UTF8") + \
                                        cvresult.tostring()
                        else:
                            campacket = bytes(
                                str(campacketheader)) + cvresult.tostring()

                        self._broadcast(campacket, cam['uuid'])
                    else:
                        self.log("Failed to get an image.", success, cvresult)

        except Exception as e:
            self.log("Error: ", e, type(e), lvl=error)
        if self._framecount % 100 == 0:
            self.log("", self._framecount, " frames taken.", lvl=debug)

    def toggleFilming(self):
        """Toggles the camera system recording state"""

        if self._filming:
            self.log("Stopping operation")
            self._filming = False
            self.timer.stop()
        else:
            self.log("Starting operation")
            self._filming = True
            self.timer.start()

    def _broadcast(self, camerapacket, camerauuid):
        try:
            for recipient in self._subscribers[camerauuid]:
                self.fireEvent(send(recipient, camerapacket, raw=True),
                               "hfosweb")
        except Exception as e:
            self.log("Failed broadcast: ", e, type(e), lvl=error)

    def _generatecameralist(self):
        try:
            result = {}
            for item in self._cameras.values():
                result[item['name']] = item['uuid']
            return result
        except Exception as e:
            self.log("Error during list retrieval:", e, type(e), lvl=error)

    def _unsubscribe(self, clientuuid, camerauuid=None):
        # TODO: Verify everything and send a response
        if not camerauuid:
            for subscribers in self._subscribers.values():
                if clientuuid in subscribers:
                    subscribers.remove(clientuuid)
                    self.log("Subscription removed: ", clientuuid, lvl=debug)
        else:
            self._subscribers[camerauuid].remove(clientuuid)
            if len(self._subscribers[camerauuid]) == 0:
                del (self._subscribers[camerauuid])
                self.log("Subscription deleted: ", camerauuid, clientuuid)

    def client_disconnect(self, event):
        """
        A client has disconnected, update possible subscriptions accordingly.

        :param event:
        """
        self.log("Removing disconnected client from subscriptions", lvl=debug)
        clientuuid = event.clientuuid
        self._unsubscribe(clientuuid)

    @handler("camerarequest", channel="hfosweb")
    def camerarequest(self, event):
        """
        Handles new camera category requests

        :param event: CameraRequest with actions
        * subscribe
        * unsubscribe
        * update
        """

        self.log("Event: '%s'" % event.__dict__)

        try:
            try:
                action = event.action
                data = event.data

                clientuuid = event.client.uuid
            except Exception as e:
                raise ValueError("[CAM] Problem during event unpacking:", e,
                                 type(e))

            if action == 'list':
                try:
                    dblist = self._generatecameralist()
                    self.fireEvent(send(clientuuid, {'component': 'camera',
                                                     'action': 'list',
                                                     'data': dblist}),
                                   "hfosweb")
                except Exception as e:
                    self.log("Listing error: ", e, type(e), lvl=error)
                return
            elif action == 'get':
                return
            elif action == 'subscribe':
                # TODO: Verify everything and send a response
                if data in self._subscribers:
                    if clientuuid not in self._subscribers[data]:
                        self._subscribers[data].append(clientuuid)
                else:
                    self._subscribers[data] = [clientuuid]
                self.log("Subscription registered: ", data, clientuuid)
                return
            elif action == 'unsubscribe':
                self._unsubscribe(clientuuid, data)
                return

        except Exception as e:
            self.log("Global Error: '%s' %s" % (e, type(e)), lvl=error)
