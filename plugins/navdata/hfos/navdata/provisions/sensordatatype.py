from hfos.provisions.base import provisionList
from hfos.database import objectmodels
# TODO: This needs to be independent of the datasource.
# We should not expect only NMEA0183 sentences but should also make sure
# to catch everything else, like nmea2k, seatalk etc

from pynmea2 import types
from pynmea2.types import proprietary
from pynmea2.nmea import NMEASentenceType, ProprietarySentence
from decimal import Decimal
from uuid import uuid4
from pprint import pprint


def getSentence(name, module):
    return getattr(module, name)


def getSentencesFromModule(module):
    sentences = {}

    for sentence in dir(module):

        obj = getSentence(sentence, module)
        if type(obj) in (NMEASentenceType, ProprietarySentence):
            print(sentence, type(obj))
            pprint(obj)
            doc = obj.__doc__
            if doc == None:
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


sentences = {}
sentences.update(getNMEASentences())
sentences.update(getProprietarySentences())


# pprint(sentences)

def getFields(sentences):
    fields = {}

    for name in sentences:
        sen, doc = sentences[name]
        if len(sen.fields) > 0:
            fields[name] = sen.fields, doc

    return fields


fields = getFields(sentences)


# pprint(fields)


def getSensorData(fields):
    sensordata = {}
    for sentype in fields:
        sen, doc = sentences[sentype]
        print(sen, doc)
        for field in sen.fields:
            print(sen, doc, field[1])

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


sensordatatypes = getSensorData(fields)

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

provisionList(provisionitems, objectmodels['sensordatatype'], clear=True)
