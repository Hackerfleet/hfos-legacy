#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""


Module Library
==============


"""

from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn
from datetime import datetime
from hfos.events.objectmanager import updatesubscriptions
from hfos.events.client import send

try:
    from isbntools.app import meta as isbnmeta
except ImportError:
    isbnmeta = None
    hfoslog("No isbntools found, install requirements-optional.txt",
            lvl=warn, emitter="LIB")

libraryfieldmapping = {
    'wcat': {
        'Title': 'name',
        'ISBN-13': 'isbn-alt',
        'Authors': 'authors',
        'Language': 'language',
        'Publisher': 'publisher',
        'Year': ('year', int)
    }
}


class book_lend(authorizedevent):
    """Requests lending status of a book"""


class book_return(authorizedevent):
    """Requests lending status of a book"""


class book_augment(authorizedevent):
    """Requests lending status of a book"""


class Manager(ConfigurableComponent):
    """
    The Library manages stored media objects
    """
    channel = "hfosweb"

    configprops = {
        'isbnservice': {'type': 'string', 'title': 'Some Setting',
                        'description': 'Some string setting.',
                        'default': 'wcat'},
    }

    def __init__(self, *args):
        """
        Initialize the Library component.

        :param args:
        """

        super(Manager, self).__init__("LIB", *args)
        self.config.creator = "Hackerfleet"

        self.log("Started")

    @handler(book_lend)
    def book_lend(self, event):
        book = objectmodels['book'].find_one({'uuid': event.data})
        if book.available:
            book.available = False
            book.status = "Lent"
            book.statuschange = datetime.now().isoformat()
            book.statusowner = str(event.user.uuid)
            book.save()
            self.log("Book successfully lent.")
        else:
            self.log("Book can't be lent, it is not available!",
                     lvl=warn)

        self._notify_result(event, book)

    @handler(book_return)
    def book_return(self, event):
        book = objectmodels['book'].find_one({'uuid': event.data})
        if not book.available:
            book.available = True
            book.status = "Available"
            book.statuschange = datetime.now().isoformat()
            book.statusowner = str(event.user.uuid)
            book.save()
            self.log("Book successfully returned.")
        else:
            self.log("Book can't be lent, it is not available!",
                     lvl=warn)

        self._notify_result(event, book)

    @handler(book_augment)
    def book_augment(self, event):
        self.log("Manually augmenting book")
        self._augment_book(event.data, event)

    def objectcreation(self, event):
        if event.schema == 'book':
            self.log("Augmenting book.")
            self._augment_book(event.uuid, event)

    def _notify_result(self, event, book):
        if book:
            self.fireEvent(updatesubscriptions('book', book))

    def _augment_book(self, uuid, event):
        """
        Checks if the newly created object is a book and only has an ISBN.
        If so, tries to fetch the book data off the internet.

        :param uuid: uuid of book to augment
        :param client: requesting client
        """
        try:
            if not isbnmeta:
                self.log(
                    "No isbntools found! Install it to get full "
                    "functionality!",
                    lvl=warn)
                return

            new_book = objectmodels['book'].find_one({'uuid': uuid})
            try:
                if len(new_book.isbn) != 0:

                    self.log('Got a lookup candidate: ', new_book._fields)

                    try:
                        meta = isbnmeta(
                            new_book.isbn,
                            service=self.config.isbnservice
                        )

                        mapping = libraryfieldmapping[
                            self.config.isbnservice
                        ]

                        new_meta = {}

                        for key in meta.keys():
                            if key in mapping:
                                if isinstance(mapping[key], tuple):
                                    name, conv = mapping[key]
                                    try:
                                        new_meta[name] = conv(meta[key])
                                    except ValueError:
                                        self.log(
                                            'Bad value from lookup:',
                                            name, conv, key
                                        )
                                else:
                                    new_meta[mapping[key]] = meta[key]

                        new_book.update(new_meta)
                        new_book.save()

                        self._notify_result(event, new_book)
                        self.log("Book successfully augmented from ",
                                 self.config.isbnservice)
                    except Exception as e:
                        self.log("Error during meta lookup: ", e, type(e),
                                 new_book.isbn, lvl=error, exc=True)
                        error_response = {
                            'component': 'hfos.alert.manager',
                            'action': 'notify',
                            'data': {
                                'type': 'error',
                                'message': 'Could not look up metadata, sorry:' + str(e)
                            }
                        }
                        self.log(event, event.client, pretty=True)
                        self.fireEvent(send(event.client.uuid, error_response))

            except Exception as e:
                self.log("Error during book update.", e, type(e),
                         exc=True, lvl=error)

        except Exception as e:
            self.log("Book creation notification error: ", uuid, e, type(e),
                     lvl=error, exc=True)
