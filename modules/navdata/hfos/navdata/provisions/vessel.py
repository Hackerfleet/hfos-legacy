from hfos.logger import hfoslog
from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from uuid import uuid4

systemvessel = {
    'name': 'Default System Vessel',
    'uuid': str(uuid4())
}


def provision():
    # TODO: Handle the case with an already existing vessel (See also system-provision)
    provisionList([systemvessel], objectmodels['vessel'])

    sysconfig = objectmodels['systemconfig'].find_one({'active': True})
    hfoslog('Adapting system config for default vessel:', sysconfig)
    sysconfig.vesseluuid = systemvessel['uuid']
    sysconfig.save()

    hfoslog('Provisioning: Vessel: Done.', emitter='PROVISIONS')
