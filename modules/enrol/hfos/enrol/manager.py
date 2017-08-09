#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""


Module: Enrolmanager
===================


"""

from hfos.component import ConfigurableComponent, handler
from hfos.events.system import authorizedevent, anonymousevent
from hfos.events.client import send
from hfos.database import objectmodels
from hfos.logger import warn, debug, verbose
from hfos.tools import std_uuid, std_now
from pystache import render
from email.mime.text import MIMEText
from smtplib import SMTP


# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


class change(authorizedevent):
    pass


class invite(authorizedevent):
    pass


class accept(anonymousevent):
    pass


class Manager(ConfigurableComponent):
    """
    The Enrol-Manager handles enrollment requests, invitations and user
    verification.
    """
    channel = "hfosweb"

    configprops = {
        'mail_server': {
            'type': 'string',
            'title': 'Mail server',
            'description': 'Mail server to use for sending invitations and '
                           'password resets',
            'default': 'localhost'
        },
        'registration': {
            'type': 'boolean',
            'title': 'Open registration',
            'description': 'Offer registration for new users',
            'default': True
        },
        'auto_accept': {
            'type': 'boolean',
            'title': 'Auto accept invited',
            'description': 'Automatically accept invited users after they '
                           'verify',
            'default': True
        },
        'mail_from': {
            'type': 'string',
            'title': 'Mail from address',
            'description': 'From mail address to send to new invitees',
            # TODO: Get a better default here:
            'default': 'enrol@localhost'
        },
        'invitation_subject': {
            'type': 'string',
            'title': 'Invitation mail subject',
            'description': 'Mail subject to send to new invitees',
            'default': 'Invitation to join {{node_name}}'
        },
        'invitation_mail': {
            'type': 'string',
            'title': 'Invitation mail text',
            'description': 'Mail body to send to new invitees',
            'default': '''Hello {{name}}!
You are being invited to join the HFOS crew at {{node_name}}!
Click this link to join the crew: 
{{invitation_url}}{{uuid}}

Have fun,
the friendly robot of {{node_name}}
'''
        }
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the Enrol Manager component.

        :param args:
        """

        super(Manager, self).__init__("ENROL", *args, **kwargs)

        # TODO: Get those from Systemconfig:
        self.node_name = 'HFOS DEFAULT NODENAME'
        protocol = 'https'
        hostname = 'localhost:443'
        self.invitation_url = protocol + '://' + hostname + '/#!/invitation/'

        self.send_mail = True

        self.log("Started")

    @handler(accept)
    def accept(self, event):
        def fail(uuid):
            self.log('Sending failure feedback to', uuid, lvl=debug)
            fail_msg = {
                'component': 'hfos.enrol.manager',
                'action': 'accept',
                'data': False
            }
            self.fireEvent(send(uuid, fail_msg))

        self.log('Invitation accepted:', event.__dict__, lvl=debug)
        try:
            enrollment = objectmodels['enrollment'].find_one({
                'uuid': event.data
            })

            if enrollment is not None:
                self.log('Enrollment found', lvl=debug)
                if enrollment.status == 'Open':
                    self.log('Enrollment is still open', lvl=debug)
                    if enrollment.method in ('Invited', 'Manual') and \
                            self.config.auto_accept:
                        enrollment.status = 'Accepted'
                        data = 'You can now log in to the system and start to use it.'
                        # TODO: Actually create account
                    else:
                        enrollment.status = 'Pending'
                        data = 'Someone has to confirm your registration ' \
                               'first. Thank you, for your patience.'
                        # TODO: Alert admin users

                    enrollment.save()
                    packet = {
                        'component': 'hfos.enrol.manager',
                        'action': 'accept',
                        'data': {True: data}
                    }
                    self.fireEvent(send(event.client.uuid, packet))
                else:
                    self.log('Enrollment has been closed already!', lvl=warn)
                    fail(event.client.uuid)
            else:
                self.log('No enrollment available.', lvl=warn)
                fail(event.client.uuid)
        except Exception as e:
            self.log('Error during invitation accept handling:', e, type(e),
                     lvl=warn, exc=True)

    @handler(change)
    def change(self, event):
        uuid = event.data['uuid']
        status = event.data['status']

        if status not in ['Open', 'Pending', 'Accepted', 'Denied', 'Resend']:
            self.log('Erroneous status for enrollment requested!', lvl=warn)
            return

        self.log('Changing status of an enrollment', uuid, 'to', status)

        enrollment = objectmodels['enrollment'].find_one({'uuid': uuid})
        if enrollment is not None:
            self.log('Enrollment found', lvl=debug)
        else:
            return

        if status == 'Resend':
            enrollment.timestamp = std_now()
            enrollment.save()
            self._send_mail(enrollment)
            reply = {True: 'Resent'}
        else:
            enrollment.status = status
            enrollment.save()
            reply = {True: enrollment.serializablefields()}

        packet = {
            'component': 'hfos.enrol.manager',
            'action': 'change',
            'data': reply
        }
        self.log('packet:', packet, lvl=verbose)
        self.fireEvent(send(event.client.uuid, packet))
        self.log('Enrollment changed', lvl=debug)

    @handler(invite)
    def invite(self, event):
        self.log('Inviting new user to enrol')
        name = event.data['name']
        email = event.data['email']
        method = event.data['method']

        props = {
            'uuid': std_uuid(),
            'status': 'Open',
            'name': name,
            'method': method,
            'email': email,
            'timestamp': std_now()
        }
        enrollment = objectmodels['enrollment'](props)
        enrollment.save()

        self.log('Enrollment stored', lvl=debug)

        if method == 'Invited':
            self._send_mail(enrollment)

        packet = {
            'component': 'hfos.enrol.manager',
            'action': 'invite',
            'data': {True: enrollment.serializablefields()}
        }
        self.fireEvent(send(event.client.uuid, packet))

    def _send_mail(self, enrollment):
        self.log('Sending enrollment status mail to user')

        context = {
            'name': enrollment.name,
            'invitation_url': self.invitation_url,
            'node_name': self.node_name,
            'uuid': enrollment.uuid
        }
        mail = render(self.config.invitation_mail, context)
        self.log('Mail:', mail, lvl=verbose)
        mime_mail = MIMEText(mail)
        mime_mail['Subject'] = render(self.config.invitation_subject, context)
        mime_mail['From'] = self.config.mail_from
        mime_mail['To'] = enrollment.email

        self.log('MimeMail:', mime_mail, lvl=verbose)
        if self.send_mail:
            self.log('Sending mail to', enrollment.email)
            server = SMTP(self.config.mail_server)
            server.send_message(mime_mail)
            server.quit()
