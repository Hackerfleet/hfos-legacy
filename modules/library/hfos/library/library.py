"""


Module Library
==============

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical
from datetime import datetime
from hfos.events.system import updatesubscriptions, AuthorizedEvents, authorizedevent
from hfos.events.client import send

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

try:
    from isbntools.app import meta as isbnmeta
except:
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


class libraryrequest(authorizedevent):
    pass


class Library(ConfigurableComponent):
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

        super(Library, self).__init__("LIB", *args)
        self.config.creator = "Hackerfleet"

        AuthorizedEvents['library'] = libraryrequest

        self.log("Started")

    def libraryrequest(self, event):
        self.log("Someone interacts with the library! Yay!", lvl=warn)
        try:
            book = None

            if event.action == "lend":
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
            elif event.action == "return":
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
            elif event.action == "augment":
                self._augmentBook('book', event.data, event.client)

            if book:
                self.fireEvent(
                    updatesubscriptions(uuid=book.uuid, schema='book',
                                        data=book))
        except Exception as e:
            self.log("Error during library handling: ", type(e), e,
                     lvl=critical, exc=True)

    def objectcreation(self, event):
        if event.schema == 'book':
            self.log("Augmenting book.")
            self._augmentBook(event.schema, event.uuid, event.client)

    def _augmentBook(self, schema, uuid, client):
        """
        Checks if the newly created object is a book and only has an ISBN.
        If so, tries to fetch the book data off the internet.

        :param schema: must be 'book'
        :param uuid: uuid of book to augment
        """
        try:
            if schema == 'book':
                if not isbnmeta:
                    self.log(
                        "No isbntools found! Install it to get full "
                        "functionality!",
                        lvl=warn)
                    return

                newbook = objectmodels['book'].find_one({'uuid': uuid})
                try:
                    if len(newbook.isbn) != 0:

                        self.log('Got a lookup candidate: ', newbook._fields)

                        try:
                            meta = isbnmeta(newbook.isbn,
                                            service=self.config.isbnservice)

                            mapping = libraryfieldmapping[
                                self.config.isbnservice]
                            for key in meta.keys():
                                if key in mapping:
                                    if isinstance(mapping[key], tuple):
                                        name, conv = mapping[key]
                                        meta[name] = conv(meta.pop(key))
                                    else:
                                        meta[mapping[key]] = meta.pop(key)

                            newbook.update(meta)
                            newbook.save()
                            self.log("Book successfully augmented from ",
                                     self.config.isbnservice)
                        except Exception as e:
                            self.log("Error during meta lookup: ", e, type(e),
                                     newbook.isbn, lvl=error, exc=True)
                            self.fireEvent(send(client.uuid,
                                                {'component': 'alert',
                                                 'action': 'error',
                                                 'data': 'Could not look up metadata, sorry:' + str(
                                                     e)}))
                    else:
                        self.log(
                            'Saw something, but it is not to be looked up: ',
                            newbook._fields)
                except Exception as e:
                    self.log("Error during book update.")

        except Exception as e:
            self.log("Book creation notification error: ", uuid, e, type(e),
                     lvl=error, exc=True)
