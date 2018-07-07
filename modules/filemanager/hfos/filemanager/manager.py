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

from hfos.misc import std_uuid

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

Module: FileManager
===================


"""

import os
import time
import sys
from hashlib import md5

from circuits import Worker, task, Event, Timer

from hfos.events.client import send
from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.database import ValidationError, objectmodels
from hfos.logger import error, warn, verbose, hilight

try:
    PermissionError
except NameError:  # pragma: no cover
    class PermissionError(Exception):
        """Not enough Permissions (2to3 substitute)"""
        pass


class status_update(Event):
    def __init__(self, count, *args, **kwargs):
        super(status_update, self).__init__(*args, **kwargs)
        self.count = count


def filewalk(top, component, links=None):
    data = []
    log = []
    count = 0
    handled = 0
    log.append('Started scan of %s' % top)

    file_object = objectmodels['file']

    for root, dirs, files in os.walk(top, topdown=False):
        for name in files + dirs:
            filename = os.path.join(root, name)
            try:
                stat = os.stat(filename)
            except (FileNotFoundError, PermissionError) as e:
                log.append('Access error on %s' % filename)
                continue

            hash = md5(filename.encode('utf-8')).hexdigest()

            count += 1
            if count % 1000 == 0:
                component.fireEvent(status_update(count))

            if file_object.count({'hash': hash}) > 0:
                continue

            try:
                if os.path.islink(filename):
                    if links:
                        # TODO: Handle symlinks in a nice manner
                        pass
                else:
                    # TODO: new levelled verbose
                    # TODO: allow hashing of files in a smart way
                    entry = {
                        'uuid': std_uuid(),
                        'path': root,
                        'name': name,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'hash': hash,
                        'type': 'file'
                    }
                    if os.path.isdir(filename):
                        entry['type'] = 'folder'
                    new_file = file_object(entry)

                    data.append(new_file)
                    handled += 1
            except EnvironmentError as e:
                log.append('Error during file inspection: %s' % e)

    return data, log


class get(authorizedevent):
    """FileManager Event"""


class get_directory(authorizedevent):
    """FileManager Event"""


class get_volumes(authorizedevent):
    """FileManager Event"""


class put(authorizedevent):
    """FileManager Event"""


class FileManager(ConfigurableComponent):
    """
    Provides a common configuration interface for connected and configured filesystems.

    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(FileManager, self).__init__('FILES', *args)

        self.file_object = objectmodels['file']

        self.volumes = {}
        self.volumes_lookup = {}

        for item in objectmodels['volume'].find():
            self.volumes[item.uuid] = item
            self.volumes_lookup[item.name] = item

            if not os.path.exists(item.path):
                self.log('Target volume does not exist. Creating path', item.path, lvl=warn)
                try:
                    os.makedirs(item.path)
                except Exception as e:
                    self.log('Could not create volume path:', e, type(e), exc=True, lvl=error)

        self.worker = Worker(process=False, workers=1,
                             channel="filemanagerworkers").register(self)

        # self._scan_filesystem('/tmp/foo')

    def _scan_filesystem(self, path):
        self.log('Scanning path:', path)
        new_volume = objectmodels['volume']({'uuid': std_uuid()})
        new_volume.name = path.split('/')[-1]
        new_volume.path = path
        new_volume.save()
        self.volumes[new_volume.uuid] = new_volume
        self.fireEvent(task(filewalk, path, self), 'filemanagerworkers')

    @handler('scan_filesystem')
    def scan_filesystem(self, event):
        self._scan_filesystem(event.data)

    @handler('status_update')
    def status_update(self, event):
        self.log('Scanner update:', event.count)

    @handler('task_success', channel="filemanagerworkers")
    def task_success(self, event, call, result):
        files, log = result
        self.log('Path %s scanned, %i files found' % (call, len(files)))
        if len(log) > 0:
            for item in log:
                self.log(item)

        if len(files) > 0:
            self.log('Size is', sys.getsizeof(files))

            begin = time.time()
            self.file_object.bulk_create(files)

            self.log('Storing', len(files), "files' metadata took", round(time.time() - begin, 2), 's')
        else:
            self.log('No new files found.')

    @handler(get_volumes)
    def get_volumes(self, event):

        req = event.data.get('req', None)

        if req is None:
            self.log('Request without request id!', lvl=warn)

        response = {
            'component': 'hfos.filemanager.manager',
            'action': 'get_volumes',
            'data': {
                'req': req,
                'volumes': []
            }
        }

        for item in self.volumes.values():
            response['data']['volumes'].append(item.serializablefields())

        self.log('Transmitting list of volumes:', response, pretty=True, lvl=verbose)
        self.fireEvent(send(event.client.uuid, response))

    @handler(get_directory)
    def get_directory(self, event):
        uuid = event.data.get('uuid', None)
        path = event.data.get('path', "")
        if uuid is None:
            self.log('No directory uuid given!', lvl=warn)
            self._notify_failure(event, 'No directory specified')
            return

        if uuid in self.volumes:
            volume = self.volumes[uuid]
            self.log(volume.__dict__, pretty=True)
        else:
            node = objectmodels['file'].find_one({'uuid': uuid})
            volume = objectmodels['volume'].find_one({'uuid': node.volume})

        if 'uservolume' in volume.flags:
            self.log('Volume is user based', lvl=verbose)
            path = os.path.join(event.user.uuid, path)

        self.log('User requests directory content:', path)

        req = event.data.get('req', None)

        if req is None:
            self.log('Request without request id!', lvl=warn)

        response = {
            'component': 'hfos.filemanager.manager',
            'action': 'get_directory',
            'data': {
                'directory': self._get_directory(volume, path),
                'volume': volume.uuid,
                'path': path,
                'req': req
            }
        }

        self.fireEvent(send(event.client.uuid, response))

    def _get_directory(self, volume, path):
        self.log('Getting files for directory', path)

        items = []
        top = time.time()

        file_filter = {
            'volume': volume.uuid,
            'path': {'$regex': '^' + path + '.*$'}
        }

        self.log("Files in directory:", self.file_object.count(file_filter))
        count = time.time() - top

        for item in self.file_object.find({'path': {'$regex': '^' + path + '.*$'}}):
            self.log(item)
            items.append(item.serializablefields())

        find = time.time() - top

        self.log('Count', count, 'find', find)

        return items

    def _check_permissions(self, user, permissions):
        for role in user.account.roles:
            if role in permissions:
                return True

        return False

    def _notify_failure(self, event, reason='Internal Error'):
        self.log('Cancelling request', event.action, 'for user', event.user.uuid, ', reason:', reason)

        result = {
            'component': 'hfos.filemanager.manager',
            'action': event.action,
            'data': {
                'req': event.data.get('req', None),
                'success': False,
                'reason': reason
            }
        }

        self.fireEvent(send(event.client.uuid, result))

    @handler(put)
    def put_file(self, event):
        self.log('File put event received:', event.__dict__.keys())

        volume_id = event.data.get('volume')
        raw = event.data.get('raw')
        filename = os.path.normpath(event.data.get('name'))
        path = os.path.normpath(event.data.get('path', ''))
        req = event.data.get('req', None)

        if req is None:
            self.log('Request without request id!', lvl=warn)

        if not volume_id or not raw or not filename:
            self.log('Erroneous put file request:', event.__dict__, lvl=error)
            self._notify_failure(event)
            return

        if volume_id in self.volumes:
            volume = self.volumes[volume_id]
        elif volume_id in self.volumes_lookup:
            volume = self.volumes_lookup[volume_id]
        else:
            self.log('Unknown volume for put file request specified:', volume_id, lvl=error)
            self._notify_failure(event)
            return

        if not self._check_permissions(event.user, volume.default_permissions['write']):
            self._notify_failure(event,
                                 'User ' + event.user.account.name + ' is not allowed to write to ' + volume.name)
            return

        if 'uservolume' in volume.flags:
            path = os.path.join(event.user.uuid, path)
            user_path = os.path.join(volume.path, path)
            if not os.path.exists(user_path):
                os.makedirs(user_path)

        destination = os.path.normpath(os.path.join(volume.path, path, filename))

        if not destination.startswith(volume.path):
            self.log('Client tried to write outside of volume:',
                     path, filename,
                     ' - resulting in:', destination, lvl=warn)
            self._notify_failure(event)
            return

        self.log('Writing to', destination)

        try:
            with open(destination, 'wb') as f:
                f.write(raw)
        except Exception as e:
            self.log('Error during writing:', e, type(e), lvl=error, exc=True)
            self._notify_failure(event)
            return

        uuid = std_uuid()

        fileobject = objectmodels['file']({'uuid': uuid})
        fileobject.owner = event.user.uuid
        fileobject.name = filename
        fileobject.volume = volume.uuid
        fileobject.path = path
        fileobject.type = 'file'
        fileobject.hash = md5(filename.encode('utf-8')).hexdigest()
        fileobject.size = len(raw)
        fileobject.mtime = time.time()

        fileobject.save()

        response = {
            'component': 'hfos.filemanager.manager',
            'action': 'put',
            'data': {
                'success': True,
                'req': event.data.get('req'),
                'uuid': uuid,
                'filename': filename
            }
        }

        self.fireEvent(send(event.client.uuid, response))
