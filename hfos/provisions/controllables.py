from hfos.provisions.base import *
from hfos.database import controllableobject

Controllables = [
    {
        "uuid": "51358884-0d61-40a7-acd6-e1f35bbfa3c8",
        "name": "engine_power",
        "description": "Engine power setting",
        "type": "analog",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "23cd1b85-e7b5-4c70-a072-8bca5ede4d92",
        "name": "engine_reverse",
        "description": "Engine reverse setting",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "9c4bccbf-17b0-4c8f-bceb-143006287cf7",
        "name": "rudder",
        "description": "Rudder setting",
        "type": "analog",
        "min": 0,
        "center": 127,
        "max": 255
    },
    {
        "uuid": "3136b068-06f5-48e3-9735-cfe77aff0517",
        "name": "light_stb",
        "description": "Light Starboard",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "18b74670-f069-4ff4-b0e3-7bf812f5fc0e",
        "name": "light_pt",
        "description": "Light Port",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "92968d37-e4a7-4088-b9e8-59787ad0b983",
        "name": "pump_on",
        "description": "Activate coolant pump",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "c85e391d-2586-4157-b386-6b583d5d1934",
        "name": "pump_off",
        "description": "Deactivate coolant pump",
        "type": "digital",
        "min": 0,
        "max": 255
    },
]

provisionList(Controllables, controllableobject)
hfoslog('Provisioning: Controllables: Done.')