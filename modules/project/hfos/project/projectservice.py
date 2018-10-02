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
from datetime import datetime, timezone
import dateutil.parser
from circuits.core.events import Event
from circuits.core.handlers import handler
from circuits.core.timers import Timer
from hfos.mail import send_mail

from hfos.database import objectmodels
from hfos.misc import std_now

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

Module: ProjectService
======================

Doing rather not much except serve as module component entrypoint.


"""

from hfos.component import ConfigurableComponent


class check_alerts(Event):
    pass


def get_time():
    return datetime.now(timezone.utc)


class ProjectService(ConfigurableComponent):
    """
    Empty hull component to store settings etc.
    """

    configprops = {}

    def __init__(self, **kwargs):
        super(ProjectService, self).__init__('PROJECT', **kwargs)

        self.alerts = {}

        self._get_future_tasks()
        self.alert_timer = Timer(5, check_alerts(), persist=True).register(self)

    def _get_future_tasks(self):
        """Assemble a list of future alerts"""

        self.alerts = {}
        now = std_now()

        for task in objectmodels['task'].find({'alert_time': {'$gt': now}}):
            self.alerts[task.alert_time] = task

        self.log('Found', len(self.alerts), 'future tasks')

    def objectcreation(self, event):
        if event.schema == 'task':
            self._handle_task_change(event.uuid)

    def objectchange(self, event):
        if event.schema == 'task':
            self._handle_task_change(event.uuid)

    def objectdeletion(self, event):
        if event.schema == 'task':
            task = objectmodels['task'].find_one({'uuid', event.uuid})
            if task in self.alerts.values():
                self.log('Deleting future task from alerts')
                del self.alerts[task.alert_time]

    def _handle_task_change(self, uuid):
        self.log('Inspecting task change/creation')
        task = objectmodels['task'].find_one({'uuid': uuid})
        self.log('Task:', task.serializablefields())
        if dateutil.parser.parse(task.alert_time) >= get_time():
            self.log('Adding future task')
            self.alerts[task.alert_time] = task

    def check_alerts(self):
        """Periodical check to issue due alerts"""

        alerted = []

        for alert_time, task in self.alerts.items():
            task_time = dateutil.parser.parse(alert_time)
            if task_time < get_time():
                self.log('Alerting about task now:', task)

                address = objectmodels['user'].find_one({'uuid': task.owner}).mail
                subject = "Task alert: %s" % task.name
                text = """Task alert is due:\n%s""" % task.notes

                self.fireEvent(send_mail(address, subject, text))

                alerted.append(task.alert_time)

        for item in alerted:
            del self.alerts[item]
