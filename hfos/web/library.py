"""


Module Library
==============

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component
from hfos.database import objectmodels, ValidationError
from hfos.logger import hfoslog, error, warn

try:
    from isbntools.app import meta as isbnmeta
except:
    isbnmeta = None
    hfoslog("[LIB] No isbntools found! Install it to get full functionality!", lvl=warn)


class Library(Component):
    """
    The Library manages stored media objects


    """
    channel = "hfosweb"

    def __init__(self, *args):
        """
        Initialize the Library component.

        :param args:
        """
        super(Library, self).__init__(*args)
        self.isbnservice = 'wcat'

        hfoslog("[LIB] Started")

    def objectcreation(self, event):
        """
        Checks if the newly created object is a book and only has an ISBN.
        If so, tries to fetch the book data off the internet.

        :param event: objectcreation event
        """
        try:
            if event.schema == 'book':
                if not isbnmeta:
                    hfoslog("[LIB] No isbntools found! Install it to get full functionality!", lvl=warn)
                    return

                newbook = objectmodels['book'].find_one({'uuid': event.uuid})
                try:
                    if len(newbook.isbn) != 0:

                        hfoslog('[LIB] Got a lookup candidate: ', newbook._fields)

                        try:
                            meta = isbnmeta(newbook.isbn, service=self.isbnservice)
                            newbook.update(meta)
                            newbook.save()
                            hfoslog("[LIB] Book successfully augmented from ", self.isbnservice)
                        except Exception as e:
                            hfoslog("[LIB] Error during meta lookup: ", e, type(e), newbook.isbn, lvl=error)
                    else:
                        hfoslog('[LIB] Saw something, but it is not to be looked up: ', newbook._fields)
                except Exception as e:
                    hfoslog("[LIB] Error during book update.")

        except Exception as e:
            hfoslog("[LIB] Book creation notification error: ", event, e, type(e), lvl=error)
