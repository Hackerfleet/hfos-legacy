#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

from hfos.logger import hfoslog, warn

"""


Module defaultform
==================

A default form listing all object elements with submit button.


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


def lookup_field(key, lookup_type=None, placeholder=None, html_class="div",
                 select_type="strapselect", mapping="uuid"):
    """Generates a lookup field for form definitions"""

    if lookup_type is None:
        lookup_type = key

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


def fieldset(title, items):
    result = {
        'title': title,
        'type': 'fieldset',
        'items': items
    }
    return result


def section(rows, columns, items):
    sections = []

    column_class = "col-sm-%i" % (12 / columns)

    for vertical in range(columns):
        column_items = []
        for horizontal in range(rows):
            try:
                item = items[horizontal][vertical]
                column_items.append(item)
            except IndexError:
                hfoslog('Field omitted, due to missing row/column:', vertical, horizontal,
                        lvl=warn, emitter='FORMS', tb=True, frame=2)

        column = {
            'type': 'section',
            'htmlClass': column_class,
            'items': column_items
        }
        sections.append(column)

    result = {
        'type': 'section',
        'htmlClass': 'row',
        'items': sections
    }
    return result


def emptyArray(key, add_label=None):
    result = {
        'key': key,
        'startEmpty': True
    }
    if add_label is not None:
        result['add'] = add_label
        result['style'] = {'add': 'btn-success'}
    return result


def tabset(titles, contents):
    tabs = []
    for no, title in enumerate(titles):
        tab = {
            'title': title,
        }
        content = contents[no]
        if isinstance(content, list):
            tab['items'] = content
        else:
            tab['items'] = [content]
        tabs.append(tab)

    result = {
        'type': 'tabs',
        'tabs': tabs
    }

    return result


def test():
    print('Hello')
    from pprint import pprint

    section_thing = section(2, 3, [['first', 'second', 'third'], ['fourth', 'fifth']])

    pprint(section_thing)

    fieldset_thing = fieldset('Fieldset', ['1', '2', '3'])

    pprint(fieldset_thing)

    thing = tabset(
        ['First', 'Second'],
        [
            section_thing,
            fieldset_thing
        ]
    )

    pprint(thing)


if __name__ == '__main__':
    test()
