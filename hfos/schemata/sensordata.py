"""
Schema: SensorData
====================

Contains
--------

SensorData:

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from pynmea2 import types
from pynmea2.types import proprietary
from pynmea2.nmea import NMEASentenceType, ProprietarySentence
from decimal import Decimal


def getSentence(name, module):
    return getattr(module, name)


def getSentencesFromModule(module):
    sentences = {}

    for sentence in dir(module):

        obj = getSentence(sentence, module)
        if type(obj) in (NMEASentenceType, ProprietarySentence):
            # print(sentence, type(obj))
            sentences[sentence] = obj

    return sentences


def getProprietarySentences():
    sentences = {}

    for module in dir(proprietary):
        sentences.update(getSentencesFromModule(getattr(proprietary, module)))

    return sentences


def getNMEASentences():
    return getSentencesFromModule(types)


sentences = {}
sentences.update(getNMEASentences())
sentences.update(getProprietarySentences())


def getFields(sentences):
    fields = {}

    for name in sentences:
        sen = sentences[name]
        fields[name] = sen.fields

    return fields


fields = getFields(sentences)


def getSensorData(fields):
    sensordata = {}
    for sen in fields:
        for no, field in enumerate(fields[sen]):
            # print(sen, no, field[1])

            if len(field) == 3:

                if field[2] in (Decimal, float):
                    valuetype = 'number'
                elif field[2] == int:
                    valuetype = 'integer'
                else:
                    valuetype = 'string'
            else:
                valuetype = 'string'

            sensordata[field[1]] = {'title': str(field[1]), 'description': str(field[0]), 'type': valuetype}

    return sensordata


sensordatatypes = getSensorData(fields)

Props = {
    'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
             'type': 'string',
             'title': 'Unique SensorData ID'
             },
    'Time_Created': {'title': 'Creation time', 'type': 'number', 'description': 'When this event was logged'},
}

Props.update(sensordatatypes)

SensorData = {
    'id': '#sensorData',
    'title': 'SensorData',
    'type': 'object',
    'name': 'sensordata',
    'properties': Props  # TODO: This doesn't work out. Too huge, too slow!
}



SensorValueTypes = []
for key in SensorData['properties']:
    if key not in ('uuid', 'Time_Created'):
        SensorValueTypes.append(key)

SensorDataForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [

                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [

                ]
            }
        ]
    },
    'description',
    {
        'type': 'submit',
        'title': 'Save Sensor Data configuration',
    }
]

__schema__ = SensorData
__form__ = SensorDataForm
