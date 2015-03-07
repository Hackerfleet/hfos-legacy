"""
Hackerfleet Operating System - Backend

Module: Database
================

Contains the underlying object model manager and generates object factories from Schemata.

Contains
========

userobject: User account factory
profileobject: User profile factory
mapviewobject: Mapview factory

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

#from circuits import Component, handler, Event, Worker, task
import warmongo

from hfos.schemata.profile import Profile
from hfos.schemata.user import User
from hfos.schemata.mapview import MapView


warmongo.connect("hfos")

userobject = warmongo.model_factory(User)
profileobject = warmongo.model_factory(Profile)
mapviewobject = warmongo.model_factory(MapView)

foo = mapviewobject({'uuid': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                     'name': 'schöner name',
                     'shared': True,
                     'color': 'RGB(0,0,255)',
                     'notes': 'Ahahaha, some notes',
                     'coords': {
                         'lat': 0,
                         'lon': 0,
                         'zoom': 5
                     }
})

foo.validate()
print(foo.serializablefields())