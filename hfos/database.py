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

from .logger import hfoslog

warmongo.connect("hfos")

userobject = warmongo.model_factory(User)
profileobject = warmongo.model_factory(Profile)
mapviewobject = warmongo.model_factory(MapView)