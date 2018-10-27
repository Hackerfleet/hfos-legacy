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
from pycountry import countries, currencies, languages, subdivisions

"""


Module defaultform
==================

A default form listing all object elements with submit button.


"""

savebutton = {
    'type': 'button',
    'title': 'Save Object',
    'condition': '$ctrl.readonly === false',
    'onClick': '$ctrl.submitObject()'
}

createnewbutton = {
    'type': 'button',
    'title': 'Save & Create new',
    'condition': '$ctrl.readonly === false',
    'onClick': '$ctrl.save_createObject()'
}

deletebutton = {
    'type': 'button',
    'title': 'Delete Object',
    'condition': '$ctrl.readonly === false',
    'onClick': '$ctrl.deleteObject()'
}

editbuttons = {
    'type': 'actions',
    'condition': '$ctrl.readonly === false',
    'items': [
        savebutton,
        createnewbutton,
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
        'condition': '$ctrl.readonly === false',
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


def lookup_object(key, lookup_type):
    """Returns a lookup button to inspect a selected object"""

    result = {
        'key': 'lookup_' + key,
        'type': 'template',
        'template': '<a href="/#!/editor/' + lookup_type + '/{{$ctrl.model.' + key + '}}/edit">Edit</a>',
    }

    return result


def create_object(key, lookup_type):
    """Returns a lookup button to inspect a selected object"""

    result = {
        'key': 'create_' + key,
        'type': 'template',
        'template': '<a href="/#!/editor/' + lookup_type + '//create">Create new</a>',
    }

    return result


def fieldset(title, items, options=None):
    """A field set with a title and sub items"""
    result = {
        'title': title,
        'type': 'fieldset',
        'items': items
    }
    if options is not None:
        result.update(options)

    return result


def section(rows, columns, items, label=None):
    """A section consisting of rows and columns"""

    # TODO: Integrate label

    sections = []

    column_class = "section-column col-sm-%i" % (12 / columns)

    for vertical in range(columns):
        column_items = []
        for horizontal in range(rows):
            try:
                item = items[horizontal][vertical]
                column_items.append(item)
            except IndexError:
                hfoslog('Field in', label, 'omitted, due to missing row/column:', vertical, horizontal,
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
    """An array that starts empty"""

    result = {
        'key': key,
        'startEmpty': True
    }
    if add_label is not None:
        result['add'] = add_label
        result['style'] = {'add': 'btn-success'}
    return result


def tabset(titles, contents):
    """A tabbed container widget"""

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


def rating_widget(key='rating', maximum=10):
    """A customizable star rating widget"""
    widget = {
        'key': 'rating',
        'type': 'template',
        'template':
            '<div class="rating">'
            '   <span class="fa fa-star-o" ng-repeat="rating in []|range: {1} - model.{0}"'
            '         ng-click="model.{0} = {1} - rating"></span>'
            '   <span class="fa fa-star" ng-repeat="rating in []|range: model.{0}"'
            '         ng-click="model.{0} = model.{0} - rating"></span>'
            '</div>'
            '<span>{{model.{0}}} out of 10</span>'.format(key, maximum)
    }

    return widget


# def collapsible(key, elements, label=None):
#     """Widget for a collapsible section"""
#
#     if not label:
#         label = key
#
#     result = {
#         'type': 'template',
#         'template': '<h3 ng-click="form.'+key+'_collapsed = !form.'+key+'_collapsed">' +
#                     label +
#                     '<span ng-class="{\'fa-chevron-up\': form.'+key+'_collapsed,'
#                     '                 \'fa-chevron-down\': !form.'+key+'_collapsed}" class="fa">'
#                     '</span>'
#                     '</h3>',
#     }
#
#     return result, {'type': 'section', 'condition': 'form.'+key+'_collapsed', 'items': elements}


def country_field(key='country'):
    """Provides a select box for country selection"""

    country_list = list(countries)
    title_map = []
    for item in country_list:
        title_map.append({'value': item.alpha_3, 'name': item.name})

    widget = {
        'key': key,
        'type': 'uiselect',
        'titleMap': title_map
    }

    return widget


def area_field(key='area'):
    """Provides a select box for country selection"""

    area_list = list(subdivisions)
    title_map = []
    for item in area_list:
        title_map.append({'value': item.code, 'name': item.name})

    widget = {
        'key': key,
        'type': 'uiselect',
        'titleMap': title_map
    }

    return widget


def test():
    """Development function to manually test all widgets"""
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
