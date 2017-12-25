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
Schema: Contact
===============
Contains
--------
Contact: vCard (jCard) based structure to store information about contacts

"""

from hfos.schemata.defaultform import defaultform, tabset, fieldset, section, emptyArray, editbuttons
from hfos.schemata.base import base_object

ContactSchema = base_object('contact')
ContactSchema.update({
    # "$schemaTransformation": "http://buzzword.org.uk/2008/jCard/transformation.js",
    "id": "jCard",
    "version": "0.1.0",
    "title": "jCard",
    "description": "This document defines the jCard data format for representing and exchanging a variety of information about an individual (e.g., formatted and structured name and delivery addresses, email address, multiple telephone numbers, photograph, logo, audio clips, etc.).",
    "type": "object",
    "seeAlso": [
        "http://microformats.org/wiki/jcard",
        "http://microformats.org/wiki/hcard",
        "http://www.ietf.org/internet-drafts/draft-ietf-vcarddav-vcardrev-05.txt",
        "http://www.ietf.org/rfc/rfc2426.txt"
    ],
})
ContactSchema['properties'].update({
    "adr": {
        "optional": True,
        "type": "array",
        "items": {
            "type": "object",
            "description": "To specify the components of the delivery address for the jCard object.",
            "properties": {
                "post-office-box": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The post office box."
                },
                "extended-address": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The extended address (e.g. apartment or suite number)."
                },
                "street-address": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The street address."
                },
                "locality": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The locality (e.g., city)."
                },
                "region": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The region (e.g., state or province)."
                },
                "postal-code": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The postal code."
                },
                "country-name": {
                    "optional": True,
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "The country name."
                },
                "type": {
                    "optional": True,
                    "type": ["array"],
                    "items": {"type": "string"},
                    "description": "The type can include the type parameter \"TYPE\" to specify the delivery address type."
                }
            }
        }
    },
    "agent": {
        "optional": True,
        "type": "array",
        "items": {
            "type": "string",
            "description": "To specify information about another person who will act on behalf of the individual or resource associated with the jCard. [May be the person's name, URI, or a nested jCard object.]"
        }
    },
    "bday": {
        "optional": True,
        "type": "string",
        "description": "To specify the birth date of the object the jCard represents.",
        "format": "datepicker"
    },
    "birth": {
        "optional": True,
        "type": ["string", "object"],
        "status": "experimental",
        "description": "To specify the place of birth of the object the jCard represents. [This is usually a string, but may be a nested jCard or an adr or geo structure.]"
    },
    "caladruri": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "items": {
            "type": "string",
            "description": "To specify the location to which an event request should be sent for the user.",
            "format": "uri"
        }
    },
    "caluri": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "items": {
            "type": "string",
            "description": "To specify the URI for a user's calendar in a jCard object.",
            "format": "uri"
        }
    },
    "categories": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify application category information about the jCard."
        }
    },
    "class": {
        "optional": True,
        "type": "string",
        "description": "To specify the access classification for a jCard object."
    },
    "dday": {
        "optional": True,
        "type": "string",
        "description": "To specify the date of death of the object the jCard represents.",
        "status": "experimental",
        "format": "datepicker"
    },
    "death": {
        "optional": True,
        "type": ["string", "object"],
        "status": "experimental",
        "description": "To specify the place of death of the object the jCard represents. [This is usually a string, but may be a nested jCard or an adr or geo structure.]"
    },
    "email": {
        "optional": True,
        "type": "array",
        "default": [],
        "description": "To specify the electronic mail address for communication with the object the jCard represents.",
        "items": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "A single text value.",
                    "format": "email"
                },
                "type": {
                    "optional": True,
                    "type": "array",
                    "description": "The type can include the type parameter \"TYPE\" to specify the format or preference of the electronic mail address.",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "fburl": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "items": {
            "type": "string",
            "description": "To specify the URI for a user's busy time in a jCard object.",
            "format": "uri"
        }
    },
    "fn": {
        "type": "string",
        "description": "To specify the formatted text corresponding to the name of the object the jCard represents."
    },
    "gender": {
        "optional": True,
        "type": "string",
        "status": "experimental",
        "description": "To specify the gender of the object the jCard represents."
    },
    "geo": {
        "optional": True,
        "type": "object",
        "description": "To specify information related to the global positioning of the object the jCard represents.",
        "properties": {
            "longitude": {
                "type": "number",
                "description": "The longitude represents the location east and west of the prime meridian as a positive or negative real number, respectively."
            },
            "latitude": {
                "type": "number",
                "description": "The latitude represents the location north and south of the equator as a positive or negative real number, respectively."
            },
            "altitude": {
                "optional": True,
                "type": "number",
                "status": "experimental",
                "description": "In metres above sea level."
            }
        }
    },
    "impp": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "description": "To specify the URI for instant messaging and presence protocol communications with the object the vCard represents.",
        "items": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "A single text value.",
                    "format": "uri"
                },
                "type": {
                    "optional": True,
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "key": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify a public key or authentication certificate associated with the object that the jCard represents."
        }
    },
    "kind": {
        "optional": True,
        "type": "string",
        "status": "experimental",
        "description": "To specify the kind of object the jCard represents.",
        "default": "individual"
    },
    "label": {
        "optional": True,
        "type": "array",
        "default": [],
        "description": "To specify the formatted text corresponding to delivery address of the object the jCard represents.",
        "items": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "A single text value."
                },
                "type": {
                    "optional": True,
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "lang": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "items": {
            "type": "string",
            "description": "To specify the language(s) that may be used for contacting the individual associated with the jCard."
        }
    },
    "logo": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify a graphic image of a logo associated with the object the jCard represents.",
            "format": "image"
        }
    },
    "mailer": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify the type of electronic mail software that is used by the individual associated with the jCard."
        }
    },
    "n": {
        "optional": True,
        "type": "object",
        "description": "To specify the components of the name of the object the jCard represents.",
        "properties": {
            "family-name": {
                "optional": True,
                "type": "array",
                "items": {"type": "string"}
            },
            "given-name": {
                "optional": True,
                "type": "array",
                "items": {"type": "string"}
            },
            "additional-name": {
                "optional": True,
                "type": "array",
                "items": {"type": "string"}
            },
            "honorific-prefix": {
                "optional": True,
                "type": "array",
                "items": {"type": "string"}
            },
            "honorific-suffix": {
                "optional": True,
                "type": "array",
                "items": {"type": "string"}
            }
        }
    },
    "nickname": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify the text corresponding to the nickname of the object the jCard represents."
        }
    },
    "note": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify supplemental information or a comment that is associated with the jCard."
        }
    },
    "org": {
        "optional": True,
        "type": "array",
        "default": [],
        "description": "To specify the organizational name and units associated with the jCard.",
        "items": {
            "type": "object",
            "properties": {
                "organization-name": {"type": "string"},
                "organization-unit": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "photo": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify an image or photograph information that annotates some aspect of the object the jCard represents.",
            "format": "image"
        }
    },
    "related": {
        "optional": True,
        "type": "array",
        "default": [],
        "status": "experimental",
        "items": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string"
                },
                "type": {
                    "optional": True,
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "rev": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify revision information about the current jCard.",
            "format": "datepicker"
        }
    },
    "role": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify information concerning the role, occupation, or business category of the object the jCard represents."
        }
    },
    "sort-string": {
        "optional": True,
        "type": "string",
        "description": "To specify the family name or given name text to be used for national-language-specific sorting of the FN and N types."
    },
    "sound": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify a digital sound content information that annotates some aspect of the jCard.  By default this property is used to specify the proper pronunciation of the name property value of the jCard.",
            "format": "uri"
        }
    },
    "source": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To identify the source of directory information contained in the content type.",
            "format": "uri"
        }
    },
    "tel": {
        "optional": True,
        "type": "array",
        "default": [],
        "description": "To specify the telephone number for telephony communication with the object the jCard represents.",
        "items": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "A single phone-number value.",
                    "format": "phone"
                },
                "type": {
                    "optional": True,
                    "type": "array",
                    "description": "The property can include the parameter \"TYPE\" to specify intended use for the telephone number.",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "title": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify the job title, functional position or function of the object the jCard represents."
        }
    },
    "tz": {
        "optional": True,
        "type": "string",
        "description": "To specify information related to the time zone of the object the jCard represents."
    },
    "uid": {
        "optional": True,
        "type": "string",
        "description": "To specify a value that represents a globally unique identifier corresponding to the individual or resource associated with the jCard."
    },
    "url": {
        "optional": True,
        "type": "array",
        "default": [],
        "items": {
            "type": "string",
            "description": "To specify a uniform resource locator associated with the object that the jCard refers to.",
            "format": "uri"
        }
    }
})

ContactForm = [
    tabset(
        ['General', 'Communication', 'Locations', 'Misc'],
        [
            [
                {
                    'key': 'fn',
                    'readonly': True
                },
                section(2, 3, [
                    [
                        'n.given-name',
                        emptyArray('n.additional-name'),
                        'n.family-name'],
                    [emptyArray('n.honorific-prefix'), emptyArray('n.honorific-suffix')]
                ]),
                section(3, 4, [
                    [emptyArray('title'), emptyArray('photo'), emptyArray('label')],
                    [emptyArray('note'), 'bday', 'birth'],
                    [emptyArray('categories'), 'gender', emptyArray('nickname'), 'tz']
                ])
            ],
            [emptyArray('email'), emptyArray('tel'), emptyArray('mailer'), emptyArray('url'), emptyArray('impp')],
            [emptyArray('adr'), 'geo'],
            [emptyArray('org'), emptyArray('agent'), emptyArray('logo'), 'kind', emptyArray('sound'),
             emptyArray('caladruri'),
             emptyArray('caluri'), emptyArray('related'), 'dday', emptyArray('source')]
        ]
    ),
    editbuttons
]

Contact = {'schema': ContactSchema, 'form': ContactForm}
