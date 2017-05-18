"""


Module: Events.Schemamanager
============================

Major HFOS event declarations

:copyright: (C) 2011-2017 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.events.system import authorizedevent

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


# Schema client services

class config(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class all(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class get(authorizedevent):
    """A client requires a schema to validate data or display a form"""
