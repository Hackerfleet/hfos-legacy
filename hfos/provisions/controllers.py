__author__ = 'riot'

from hfos.provisions.base import *
from hfos.database import controllerobject

Controllers = [
    {'name': 'MS0x00 - Logitech Extreme 3D Pro',
     'description': 'Setup for MS0x00 and a Logitech Extreme 3D Pro Joystick',
     'uuid': '5caa7f56-d068-451c-9b69-4efe49d4d5b5',
     'mappings': [
         {
             'controltype': 'analog',
             'controlaxis': 0,
             'controluuid': '51358884-0d61-40a7-acd6-e1f35bbfa3c8'
         },
         {
             'controltype': 'analog',
             'controlaxis': 1,
             'controluuid': '9c4bccbf-17b0-4c8f-bceb-143006287cf7',
         },
         {
             'controltype': 'digital',
             'controlbutton': 0,
             'controluuid': '3136b068-06f5-48e3-9735-cfe77aff0517'
         },
         {
             'controltype': 'digital',
             'controlbutton': 1,
             'controluuid': '18b74670-f069-4ff4-b0e3-7bf812f5fc0e'
         },
         {
             'controltype': 'digital',
             'controlbutton': 2,
             'controluuid': '92968d37-e4a7-4088-b9e8-59787ad0b983'
         },
         {
             'controltype': 'digital',
             'controlbutton': 3,
             'controluuid': 'c85e391d-2586-4157-b386-6b583d5d1934'
         },
     ]}
]

provisionList(Controllers, controllerobject)
hfoslog('Provisioning: Controllers: Done.')