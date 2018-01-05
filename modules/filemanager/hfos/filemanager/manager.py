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

from hfos.tools import std_uuid

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
from hfos.logger import error, warn

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
    """A client requires a schema to validate data or display a form"""


class get_directory(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class get_volumes(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class put(authorizedevent):
    """A client requires a schema to validate data or display a form"""


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

        for item in objectmodels['volume'].find():
            self.volumes[item.uuid] = item

        self.worker = Worker(process=False, workers=1,
                             channel="filemanagerworkers").register(self)

        self._scan_filesystem('/tmp/foo')
        # self._get_directory('/mnt/cx3/MUSIC/PLAID')

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
        response = {
            'component': 'hfos.filemanager.manager',
            'action': 'get_volumes',
            'data': []
        }
        for item in self.volumes.values():
            response['data'].append(item.serializablefields())

        self.log('Transmitting list of volumes:', response, pretty=True)
        self.fireEvent(send(event.client.uuid, response))

    @handler(get_directory)
    def get_directory(self, event):
        uuid = event.data
        if uuid in self.volumes:
            path = self.volumes[uuid].path
        else:
            node = objectmodels['file'].find_one({'uuid': uuid})
            path = node.path

        response = {
            'component': 'hfos.filemanager.manager',
            'action': 'get_directory',
            'data': self._get_directory(path)
        }

        self.fireEvent(send(event.client.uuid, response))

    def _get_directory(self, path):
        items = []
        top = time.time()
        self.log('Getting files for directory', path)
        self.log("Files in directory:", self.file_object.count({'path': {'$regex': '^' + path + '$'}}))
        count = time.time() - top
        for item in self.file_object.find({'path': {'$regex': '^' + path + '$'}}):
            self.log(item)
            items.append(item.serializablefields())

        find = time.time() - top

        self.log('Count', count, 'find', find)

        # self.log(items, pretty=True)
