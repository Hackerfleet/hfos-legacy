"""
Hackerfleet Operating System - Backend

Module: CameraManager
=====================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from uuid import uuid4

from circuits import Component, handler, Timer, Event
from circuits.tools import tryimport

from hfos.events import send
from hfos.logger import hfoslog, error, debug


opencv = tryimport("cv2")


class CameraManager(Component):
    """
    Handles camera updates, subscriptions and broadcasts
    """

    channel = "cam"

    def __init__(self, maxcams=16, *args):
        super(CameraManager, self).__init__(*args)

        self._cameras = {}
        self._subscribers = {}
        self._filming = True
        self._framecount = 0
        self._frames = {}

        hfoslog("CAM: Checking opencv for cameras.", lvl=debug)
        for cam in range(maxcams):
            video = opencv.VideoCapture(cam)
            if video.isOpened():
                camera = {'uuid': str(uuid4()),
                          'name': 'Camera' + str(cam),
                          'cam': video
                          }
                self._cameras[cam] = camera
                hfoslog("CAM: Found camera [", cam, "]: ", camera)

        hfoslog("CAM: Starting timer")
        self.timer = Timer(0.05, Event.create("rec"), persist=True).register(self)

        hfoslog(self._cameras)
        hfoslog("CAM: Started")

    def rec(self):

        try:
            self._snapshot()
        except Exception as e:
            hfoslog("CAM: Timer error: ", e, type(e), lvl=error)

    def _snapshot(self):
        self._framecount += 1

        try:
            for camid, cam in self._cameras.items():
                if cam['uuid'] in self._subscribers:
                    # hfoslog("CAM: Taking input of ", cam)
                    success, cvresult = cam['cam'].read()
                    # hfoslog("CAM: Result: ", cvresult)
                    if success:

                        campacketheader = {'component': 'camera',
                                           'action': 'update',
                                           }
                        campacket = bytes(str(campacketheader), encoding="UTF8") + cvresult.tostring()

                        self._broadcast(campacket, cam['uuid'])
                    else:
                        hfoslog("CAM: Failed to get an image.", success, cvresult)

        except Exception as e:
            hfoslog("CAM: Error: ", e, type(e), lvl=error)
        if self._framecount % 100 == 0:
            hfoslog("CAM: ", self._framecount, " frames taken.", lvl=debug)


    def toggleFilming(self):
        if self._filming:
            hfoslog("CAM: Stopping operation")
            self._filming = False
            self.timer.stop()
        else:
            hfoslog("CAM: Starting operation")
            self._filming = True
            self.timer.start()


    def _broadcast(self, camerapacket, camerauuid):
        try:
            for recipient in self._subscribers[camerauuid]:
                self.fireEvent(send(recipient, camerapacket, raw=True), "hfosweb")
        except Exception as e:
            hfoslog("CAM: Failed broadcast: ", e, type(e), lvl=error)

    def _generatecameralist(self):
        try:
            result = {}
            for item in self._cameras.values():
                result[item['name']] = item['uuid']
            return result
        except Exception as e:
            hfoslog("Error during list retrieval:", e, type(e), lvl=error)


    def _unsubscribe(self, clientuuid, camerauuid=None):
        # TODO: Verify everything and send a response
        if not camerauuid:
            for subscribers in self._subscribers.values():
                if clientuuid in subscribers:
                    subscribers.remove(clientuuid)
                    hfoslog("CAM: Subscription removed: ", clientuuid, lvl=debug)
        else:
            self._subscribers[camerauuid].remove(clientuuid)
            if len(self._subscribers[camerauuid]) == 0:
                del (self._subscribers[camerauuid])
                hfoslog("CAM: Subscription deleted: ", camerauuid, clientuuid)

    def client_disconnect(self, event):
        hfoslog("CAM: Removing disconnected client from subscriptions", lvl=debug)
        clientuuid = event.clientuuid
        self._unsubscribe(clientuuid)

    @handler("camerarequest", channel="hfosweb")
    def camerarequest(self, event):
        """
        Handles new camera category requests

        Types:
        * subscribe
        * unsubscribe
        * update
        """

        hfoslog("CAM: Event: '%s'" % event.__dict__)

        try:
            try:
                userobj = event.user
                action = event.action
                data = event.data

                useruuid = userobj.useruuid
                clientuuid = event.client.clientuuid
            except Exception as e:
                raise ValueError("CAM: Problem during event unpacking:", e, type(e))

            if action == 'list':
                try:
                    dblist = self._generatecameralist()
                    self.fireEvent(send(clientuuid, {'component': 'camera', 'action': 'list', 'data': dblist}),
                                   "hfosweb")
                except Exception as e:
                    hfoslog("CAM: Listing error: ", e, type(e), lvl=error)
                return
            elif action == 'get':
                return
            elif action == 'subscribe':
                # TODO: Verify everything and send a response
                if data in self._subscribers:
                    if not clientuuid in self._subscribers[data]:
                        self._subscribers[data].append(clientuuid)
                else:
                    self._subscribers[data] = [clientuuid]
                hfoslog("CAM: Subscription registered: ", data, clientuuid)
                return
            elif action == 'unsubscribe':
                self._unsubscribe(clientuuid, data)
                return


        except Exception as e:
            hfoslog("CAM: Global Error: '%s' %s" % (e, type(e)), lvl=error)