"""


Module defaultform
==================

A default form listing all object elements with submit button.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

__license__ = """
Hackerfleet Technology Demonstrator
=====================================================================
Copyright (C) 2011-2016 riot <riot@c-base.org> and others.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

savebutton = {
    'type': 'button',
    'title': 'Save Object',
    'onClick': '$ctrl.submitObject()'
}

deletebutton = {
    'type': 'button',
    'title': 'Delete Object',
    'onClick': '$ctrl.deleteObject()'
}

editbuttons = {
    'type': 'actions',
    'items': [
        savebutton,
        deletebutton
    ]
}

defaultform = [
    '*',
    editbuttons
]

changeonlyform = [
    '*',
    {
        'type': 'actions',
        'items': [
            savebutton
        ]
    }
]

readonlyform = [
    '*'
]

noform = []


def lookup_field(key, lookup_type, placeholder=None, html_class="",
                 select_type="strapselect", mapping="uuid"):
    if placeholder is None:
        placeholder = "Select a " + lookup_type
    result = {
        'key': key,
        'htmlClass': html_class,
        'type': select_type,
        'placeholder': placeholder,
        'options': {
            "type": lookup_type,
            "asyncCallback": "$ctrl.getFormData",
            "map": {'valueProperty': mapping, 'nameProperty': 'name'}
        }
    }

    return result
