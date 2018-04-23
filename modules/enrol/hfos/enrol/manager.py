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

"""


Module: Enrolmanager
===================


"""

from socket import timeout
from base64 import b64encode
from time import time
from captcha.image import ImageCaptcha
from validate_email import validate_email
from circuits import Timer, Event

from hfos.component import ConfigurableComponent, handler
from hfos.events.system import authorizedevent, anonymousevent
from hfos.events.client import send
from hfos.database import objectmodels
from hfos.logger import warn, debug, verbose, error, hilight
from hfos.tools import std_uuid, std_now, std_hash, std_salt, _
from pystache import render
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL


# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


class change(authorizedevent):
    roles = ['admin']


class invite(authorizedevent):
    roles = ['admin']


class accept(anonymousevent):
    pass


class changepassword(authorizedevent):
    pass


class enrol(anonymousevent):
    pass


class captcha(anonymousevent):
    pass


class status(anonymousevent):
    pass


class request_reset(anonymousevent):
    pass


class Manager(ConfigurableComponent):
    """
    The Enrol-Manager handles enrollment requests, invitations and user
    verification.
    """
    channel = "hfosweb"

    configprops = {
        'mail_send': {
            'type': 'boolean',
            'title': 'Send emails',
            'description': 'Generally toggle email sending (for Debugging)',
            'default': True
        },
        'mail_server': {
            'type': 'string',
            'title': 'Mail server',
            'description': 'Mail server to use for sending invitations and '
                           'password resets',
            'default': 'localhost'
        },
        'mail_server_port': {
            'type': 'integer',
            'title': 'Mail server port',
            'description': 'Mail server port to connect to',
            'default': 25
        },
        'mail_ssl': {
            'type': 'boolean',
            'title': 'Use SSL',
            'description': 'Use SSL to secure the mail server connection',
            'default': True
        },
        'mail_tls': {
            'type': 'boolean',
            'title': 'Use TLS',
            'description': 'Use TLS to secure the mail server connection',
            'default': False
        },
        'mail_from': {
            'type': 'string',
            'title': 'Mail from address',
            'description': 'From mail address to send to new invitees',
            # TODO: Get a better default here:
            'default': 'enrol@{{hostname}}'
        },
        'mail_username': {
            'type': 'string',
            'title': 'SMTP Username',
            'default': ''
        },
        'mail_password': {
            'type': 'string',
            'title': 'SMTP Password',
            'x-schema-form': {
                'type': 'password'
            }
        },
        'allow_registration': {
            'type': 'boolean',
            'title': 'Open registration',
            'description': 'Offer registration for new users',
            'default': True
        },
        'auto_accept_invited': {
            'type': 'boolean',
            'title': 'Auto accept invited',
            'description': 'Automatically accept invited users after they '
                           'verify',
            'default': True
        },
        'auto_accept_enrolled': {
            'type': 'boolean',
            'title': 'Auto accept self enrolled',
            'description': 'Automatically accept users that enrolled themselves after they '
                           'verify',
            'default': False
        },
        'group_accept_invited': {
            'type': 'string',
            'description': 'Group to add invited and accepted users to - use commas to specify more than one',
            'title': 'Group Invited',
            'default': 'crew'
        },
        'group_accept_enrolled': {
            'type': 'string',
            'description': 'Group to add self enrolled and accepted users to - use commas to specify more than one',
            'title': 'Group Enrolled',
            'default': 'crew'
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
        },
        'acceptance_subject': {
            'type': 'string',
            'title': 'Acceptance mail subject',
            'description': 'Mail subject to send to accepted invitees',
            'default': 'Your account on {{node_name}} is now active'
        },

        'acceptance_mail': {
            'type': 'string',
            'title': 'Acceptance mail text',
            'description': 'Mail body to send to accepted invitees',
            'default': '''Hello {{name}}!
You can now use the HFOS node at {{node_name}}!
Click this link to login: 
{{node_url}}

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

        self.image_captcha = ImageCaptcha(fonts=['/usr/share/fonts/truetype/freefont/FreeSerif.ttf'])

        self.captchas = {}

        self.send_mail = True

        systemconfig = objectmodels['systemconfig'].find_one({'active': True})

        try:
            salt = systemconfig.salt.encode('ascii')
            self.log('Using active systemconfig salt')
        except (KeyError, AttributeError):
            self.log('No system salt found! Check your configuration. This can happen upon first start.', lvl=error)
            self.unregister()
            return

        protocol = "https"
        hostname = systemconfig.hostname

        self.hostname = hostname
        self.node_name = systemconfig.name
        self.node_url = protocol + '://' + hostname
        self.invitation_url = self.node_url + '/#!/invitation/'

        self.salt = salt
        self.systemconfig = systemconfig

        self.log("Started")

    @handler(change)
    def change(self, event):
        """An admin user requests a change to an enrolment"""

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
            self._send_invitation(enrollment)
            reply = {True: 'Resent'}
        else:
            enrollment.status = status
            enrollment.save()
            reply = {True: enrollment.serializablefields()}

        if status == 'Accepted':
            self._create_user(enrollment.name, enrollment.password, enrollment.email, 'Invited')
            self._send_acceptance(enrollment)

        packet = {
            'component': 'hfos.enrol.manager',
            'action': 'change',
            'data': reply
        }
        self.log('packet:', packet, lvl=verbose)
        self.fireEvent(send(event.client.uuid, packet))
        self.log('Enrollment changed', lvl=debug)

    @handler(changepassword)
    def changepassword(self, event):
        """An enrolled user wants to change their password"""

        old = event.data['old']
        new = event.data['new']
        uuid = event.user.uuid

        # TODO: Write email to notify user of password change

        user = objectmodels['user'].find_one({'uuid': uuid})
        if std_hash(old, self.salt) == user.passhash:
            user.passhash = std_hash(new, self.salt)
            user.save()

            packet = {
                'component': 'hfos.enrol.manager',
                'action': 'changepassword',
                'data': True
            }
            self.fireEvent(send(event.client.uuid, packet))
            self.log('Successfully changed password for user', uuid)
        else:
            packet = {
                'component': 'hfos.enrol.manager',
                'action': 'changepassword',
                'data': False
            }
            self.fireEvent(send(event.client.uuid, packet))
            self.log('User tried to change password without supplying old one', lvl=warn)

    @handler(invite)
    def invite(self, event):
        """A new user has been invited to enrol by an admin user"""

        self.log('Inviting new user to enrol')
        name = event.data['name']
        email = event.data['email']
        method = event.data['method']

        self._invite(name, method, email, event.client.uuid)

    @handler(enrol)
    def enrol(self, event):
        """A user tries to self-enrol with the enrolment form"""

        if self.systemconfig.allowregister is False:
            self.log('Someone tried to register although enrolment is closed.')
            return

        self.log('Client trying to register a new account:', event, pretty=True)
        # self.log(event.data, pretty=True)

        uuid = event.client.uuid

        def fail(reason):
            """Reports failure to the enrol form module"""

            self.log('Enrolment request failed:', reason)

            response = {
                'component': 'hfos.enrol.manager',
                'action': 'enrol',
                'data': (False, reason)
            }
            self.fire(send(uuid, response))

        if uuid in self.captchas and event.data.get('captcha', None) == self.captchas[uuid]['text']:
            self.log('Captcha solved!')
        else:
            self.log('Captcha failed!')
            fail('You did not solve the captcha correctly.')
            self._generate_captcha(event)

            return

        mail = event.data.get('mail', None)
        if mail is None:
            fail(_('You have to supply all required fields.'))
            return
        elif not validate_email(mail):
            fail(_('The supplied email address seems invalid'))
            return

        if objectmodels['user'].count({'mail': mail}) > 0:
            fail(_('Your mail address cannot be used.'))
            return

        password = event.data.get('password', None)
        if password is None or len(password) < 5:
            fail(_('Your password is not long enough.'))
            return

        username = event.data.get('username', None)
        if username is None or len(username) < 4:
            fail(_('Your username is not long enough.'))
            return
        elif objectmodels['user'].count({'name': username}) > 0:
            fail(_('The username you supplied is not available.'))
            return

        self.log('Provided data is good to enrol.')
        if self.config.auto_accept_enrolled:
            self._create_user(username, password, mail, 'Enrolled')
        else:
            self._invite(username, 'Enrolled', mail, uuid)

    @handler(accept)
    def accept(self, event):
        """A challenge/response for an enrolment has been accepted"""

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
                        self.config.auto_accept_invited:
                        enrollment.status = 'Accepted'
                        data = 'You can now log in to the system and start to use it.'
                        self._create_user(enrollment.name, enrollment.password, enrollment.email, enrollment.method)
                        self._send_acceptance(enrollment)
                        # TODO: add account to self.config.group_accept group
                    else:
                        enrollment.status = 'Pending'
                        data = 'Someone has to confirm your enrollment ' \
                               'first. Thank you, for your patience.'
                        # TODO: Alert admin users
                    enrollment.save()

                # Reaffirm acceptance to end user, when clicking on the link multiple times
                elif enrollment.status == 'Accepted':
                    data = 'You can now log in to the system and start to use it.'
                elif enrollment.status == 'Pending':
                    data = 'Someone has to confirm your enrollment ' \
                           'first. Thank you, for your patience.'
                else:
                    self.log('Enrollment has been closed already!', lvl=warn)
                    fail(event.client.uuid)
                    return
                packet = {
                    'component': 'hfos.enrol.manager',
                    'action': 'accept',
                    'data': {True: data}
                }
                self.fireEvent(send(event.client.uuid, packet))
            else:
                self.log('No enrollment available.', lvl=warn)
                fail(event.client.uuid)
        except Exception as e:
            self.log('Error during invitation accept handling:', e, type(e),
                     lvl=warn, exc=True)

    @handler(status)
    def status(self, event):
        """An anonymous client wants to know if we're open for enrollment"""

        self.log('Registration status requested')

        response = {
            'component': 'hfos.enrol.manager',
            'action': 'status',
            'data': self.config.allow_registration
        }

        self.fire(send(event.client.uuid, response))

    @handler(captcha)
    def captcha(self, event):
        """An anonymous client requests a captcha challenge"""

        self._generate_captcha(event)

    @handler(request_reset)
    def request_reset(self, event):
        """An anonymous client requests a password reset"""

        self.log('Password reset request received:', event.__dict__, lvl=hilight)

        user_object = objectmodels['user']

        username = event.data.get('username', None)
        email = event.data.get('email', None)

        if email is not None and user_object.count({'mail': email}) > 0:
            email_user = user_object.find_one({'mail': email})
        if username is not None and user_object.count({'name': username}) > 0:
            named_user = user_object.find_one({'name': username})

    def _generate_captcha(self, event):
        self.log('Generating requested captcha')

        text = std_salt(length=6, lowercase=False)
        now = time()

        captcha = {
            'text': text,
            'image': self.image_captcha.generate(text),
            'time': now
        }
        # self.image_captcha.write(text, '/tmp/captcha.png')
        self.captchas[event.client.uuid] = captcha

        Timer(3, Event.create('captcha_transmit', captcha, event.client.uuid)).register(self)

    def captcha_transmit(self, captcha, uuid):
        """Delayed transmission of a requested captcha"""

        self.log('Transmitting captcha')

        response = {
            'component': 'hfos.enrol.manager',
            'action': 'captcha',
            'data': b64encode(captcha['image'].getvalue()).decode('utf-8')
        }
        self.fire(send(uuid, response))

    def _invite(self, name, method, email, uuid):
        """Actually invite a given user"""

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

        self._send_invitation(enrollment)

        packet = {
            'component': 'hfos.enrol.manager',
            'action': 'invite',
            'data': [True, email]
        }
        self.fireEvent(send(uuid, packet))

    def _create_user(self, username, password, mail, method):
        """Create a new user and all initial data"""

        try:
            if method == 'Invited':
                config_role = self.config.group_accept_invited
            else:
                config_role = self.config.group_accept_enrolled

            roles = []
            if ',' in config_role:
                for item in config_role.split(','):
                    roles.append(item.lstrip().rstrip())
            else:
                roles = [config_role]

            newuser = objectmodels['user']({
                'name': username,
                'passhash': std_hash(password, self.salt),
                'mail': mail,
                'uuid': std_uuid(),
                'roles': roles
            })
            if password == '':
                newuser.needs_password_change = True
                newuser.passhash = ''
            newuser.save()
        except Exception as e:
            self.log("Problem creating new user: ", type(e), e,
                     lvl=error)
            return

        try:
            newprofile = objectmodels['profile']({
                'uuid': std_uuid(),
                'owner': newuser.uuid
            })
            self.log("New profile uuid: ", newprofile.uuid,
                     lvl=verbose)

            newprofile.save()

            # TODO: Notify new owner
            # TODO: Notify crew-admins
        except Exception as e:
            self.log("Problem creating new profile: ", type(e),
                     e, lvl=error)

    def _send_invitation(self, enrollment):
        """Send an invitation mail to an open enrolment"""

        self.log('Sending enrollment status mail to user')

        self._send_mail(self.config.invitation_subject, self.config.invitation_mail, enrollment)

    def _send_acceptance(self, enrollment):
        """Send an acceptance mail to an open enrolment"""

        self.log('Sending acceptance status mail to user')

        self._send_mail(self.config.acceptance_subject, self.config.acceptance_mail, enrollment)

    def _send_mail(self, subject, template, enrollment):
        """Connect to mail server and send actual email"""

        context = {
            'name': enrollment.name,
            'invitation_url': self.invitation_url,
            'node_name': self.node_name,
            'node_url': self.node_url,
            'uuid': enrollment.uuid
        }

        mail = render(template, context)
        self.log('Mail:', mail, lvl=verbose)
        mime_mail = MIMEText(mail)
        mime_mail['Subject'] = render(subject, context)
        mime_mail['From'] = render(self.config.mail_from, {'hostname': self.hostname})
        mime_mail['To'] = enrollment.email

        self.log('MimeMail:', mime_mail, lvl=verbose)
        if self.send_mail:
            self.log('Sending mail to', enrollment.email)
            try:
                if self.config.mail_ssl:
                    server = SMTP_SSL(self.config.mail_server, port=self.config.mail_server_port, timeout=5)
                else:
                    server = SMTP(self.config.mail_server, port=self.config.mail_server_port, timeout=5)

                if self.config.mail_tls:
                    self.log('Starting TLS', lvl=debug)
                    server.starttls()

                if self.config.mail_username != '':
                    self.log('Logging in with', self.config.mail_username, lvl=debug)
                    server.login(self.config.mail_username, self.config.mail_password)
                else:
                    self.log('No username, trying anonymous access', lvl=debug)

                self.log('Sending Mail', lvl=debug)
                response_send = server.send_message(mime_mail)
                server.quit()

            except timeout as e:
                self.log('Could not send email to enrollee, mailserver timeout:', e, lvl=error)
                return
            self.log('Server response:',response_send)
