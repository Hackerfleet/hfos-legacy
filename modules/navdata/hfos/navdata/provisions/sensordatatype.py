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

from hfos.logger import hfoslog
from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from pynmea2 import types
from pynmea2.types import proprietary
from pynmea2.nmea import NMEASentenceType, ProprietarySentence
from decimal import Decimal
from uuid import uuid4
from pprint import pprint


# TODO: This needs to be independent of the datasource.
# We should not expect only NMEA0183 sentences but should also make sure
# to catch everything else, like nmea2k, seatalk etc


def getSentence(name, module):
    return getattr(module, name)


def getSentencesFromModule(module):
    sentences = {}

    for sentence in dir(module):

        obj = getSentence(sentence, module)
        if type(obj) in (NMEASentenceType, ProprietarySentence):
            # print(sentence, type(obj))
            # pprint(obj)
            doc = obj.__doc__
            if doc is None:
                doc = 'UNDOCUMENTED'
            else:
                doc = doc.lstrip().rstrip()

            sentences[sentence] = obj, doc

    return sentences


def getProprietarySentences():
    sentences = {}

    for module in dir(proprietary):
        sentences.update(getSentencesFromModule(getattr(proprietary, module)))

    return sentences


def getNMEASentences():
    return getSentencesFromModule(types)


def getFields(sentences):
    fields = {}

    for name in sentences:
        sen, doc = sentences[name]
        if len(sen.fields) > 0:
            fields[name] = sen.fields, doc

    return fields


def getSensorData(fields, sentences):
    sensordata = {}
    for sentype in fields:
        sen, doc = sentences[sentype]
        # print(sen, doc)
        for field in sen.fields:
            # print(sen, doc, field[1])

            if len(field) == 3:

                if field[2] in (Decimal, float):
                    valuetype = 'number'
                elif field[2] == int:
                    valuetype = 'integer'
                else:
                    valuetype = 'string'
            else:
                valuetype = 'string'

            if field[1] in sensordata:
                print("WARNING: DUPLICATE FIELD FOUND:", field[1])
            SensorDataTypeTemplate = {
                'uuid': str(uuid4()),
                'sentence': sentype,
                'name': sentype + "_" + str(field[1]),
                'title': str(field[0]),
                'timestamp': 0,
                'lastvalue': '',
                'description': doc,
                'record': False,
                'bus': '',
                'type': valuetype
            }
            sensordata[sentype + '_' + field[1]] = SensorDataTypeTemplate

    return sensordata


def provision(**kwargs):
    sentences = {}
    sentences.update(getNMEASentences())
    sentences.update(getProprietarySentences())

    # pprint(sentences)

    fields = getFields(sentences)

    # pprint(fields)

    sensordatatypes = getSensorData(fields, sentences)

    # pprint(sensordatatypes)

    provisionitems = []

    # datatypes = {
    #    'string': [],
    #    'number': [],
    #    'integer': [],
    #    'unknown': []
    # }

    for datatype in sensordatatypes.values():
        provisionitems.append(datatype)
        # datatypes[datatype['type']].append(datatype['description'])

        # pprint(provisionitems)
        # print(len(provisionitems))

        # pprint(datatypes)

        # for name, typeitems in datatypes.items():
        #    print('%s has %i elements' % (name, len(typeitems)))

    provisionList(provisionitems, objectmodels['sensordatatype'], **kwargs)
    hfoslog('Provisioning: Sensordatatypes: Done.', emitter='PROVISIONS')
