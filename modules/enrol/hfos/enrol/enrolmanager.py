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


Module: EnrolManager
===================


"""

from socket import timeout
from base64 import b64encode
from time import time
from captcha.image import ImageCaptcha
from validate_email import validate_email
from circuits import Timer, Event, Worker, task

from hfos.component import ConfigurableComponent, handler
from hfos.events.system import authorizedevent, anonymousevent
from hfos.events.client import send
from hfos.database import objectmodels
from hfos.logger import warn, debug, verbose, error, hilight, hfoslog
from hfos.misc import std_uuid, std_now, std_hash, std_salt, i18n as _, std_human_uid
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


class delete(authorizedevent):
    roles = ['admin']


class addrole(authorizedevent):
    roles = ['admin']


class delrole(authorizedevent):
    roles = ['admin']


class toggle(authorizedevent):
    roles = ['admin']


class changepassword(authorizedevent):
    pass


class accept(anonymousevent):
    pass


class enrol(anonymousevent):
    pass


class captcha(anonymousevent):
    pass


class status(anonymousevent):
    pass


class request_reset(anonymousevent):
    pass


class EnrolManager(ConfigurableComponent):
    """
    The Enrol-EnrolManager handles enrollment requests, invitations and user
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
        'no_verify': {
            'type': 'boolean',
            'title': 'Skip verification',
            'description': 'Automatically accept all users immediately',
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
            'x-schema-form': {
                'type': 'textarea'
            },
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
            'x-schema-form': {
                'type': 'textarea'
            },
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

        super(EnrolManager, self).__init__("ENROL", *args, **kwargs)

        self.worker = Worker(process=False, workers=2, channel="enrolworkers").register(self)

        self.log("Started")
        self._setup()

    def reload_configuration(self, event):
        """Reload the current configuration and set up everything depending on it"""

        super(EnrolManager, self).reload_configuration(event)
        self.log('Reloaded configuration.')
        self._setup()

    def _setup(self):
        self.image_captcha = ImageCaptcha(fonts=['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'])

        self.captchas = {}

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

        self.log("Set up done", lvl=verbose)

    def _fail(self, event, msg="Error"):
        self.log('Sending failure feedback to', event.client.uuid, lvl=debug)
        fail_msg = {
            'component': 'hfos.enrol.enrolmanager',
            'action': event.action,
            'data': (False, msg)
        }
        self.fireEvent(send(event.client.uuid, fail_msg))

    def _acknowledge(self, event, msg="Done"):
        self.log('Sending success feedback to', event.client.uuid, lvl=debug)
        success_msg = {
            'component': 'hfos.enrol.enrolmanager',
            'action': event.action,
            'data': (True, msg)
        }
        self.fireEvent(send(event.client.uuid, success_msg))

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
            self._send_invitation(enrollment, event)
            reply = {True: 'Resent'}
        else:
            enrollment.status = status
            enrollment.save()
            reply = {True: enrollment.serializablefields()}

        if status == 'Accepted' and enrollment.method == 'Enrolled':
            self._create_user(enrollment.name, enrollment.password, enrollment.email, 'Invited', event.client.uuid)
            self._send_acceptance(enrollment, None, event)

        packet = {
            'component': 'hfos.enrol.enrolmanager',
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
                'component': 'hfos.enrol.enrolmanager',
                'action': 'changepassword',
                'data': True
            }
            self.fireEvent(send(event.client.uuid, packet))
            self.log('Successfully changed password for user', uuid)
        else:
            packet = {
                'component': 'hfos.enrol.enrolmanager',
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

        self._invite(name, method, email, event.client.uuid, event)

    @handler(enrol)
    def enrol(self, event):
        """A user tries to self-enrol with the enrolment form"""

        if self.config.allow_registration is False:
            self.log('Someone tried to register although enrolment is closed.')
            return

        self.log('Client trying to register a new account:', event, pretty=True)
        # self.log(event.data, pretty=True)

        uuid = event.client.uuid

        if uuid in self.captchas and event.data.get('captcha', None) == self.captchas[uuid]['text']:
            self.log('Captcha solved!')
        else:
            self.log('Captcha failed!')
            self._fail(event, _('You did not solve the captcha correctly.', event))
            self._generate_captcha(event)

            return

        mail = event.data.get('mail', None)
        if mail is None:
            self._fail(event, _('You have to supply all required fields.', event))
            return
        elif not validate_email(mail):
            self._fail(event, _('The supplied email address seems invalid', event))
            return

        if objectmodels['user'].count({'mail': mail}) > 0:
            self._fail(event, _('Your mail address cannot be used.', event))
            return

        password = event.data.get('password', None)
        if password is None or len(password) < 5:
            self._fail(event, _('Your password is not long enough.', event))
            return

        username = event.data.get('username', None)
        if username is None or len(username) < 1:
            self._fail(event, _('Your username is not long enough.', event))
            return
        elif (objectmodels['user'].count({'name': username}) > 0) or \
            (objectmodels['enrollment'].count({'name': username}) > 0):
            self._fail(event, _('The username you supplied is not available.', event))
            return

        self.log('Provided data is good to enrol.')
        if self.config.no_verify:
            self._create_user(username, password, mail, 'Enrolled', uuid)
        else:
            self._invite(username, 'Enrolled', mail, uuid, event, password)

    @handler(accept)
    def accept(self, event):
        """A challenge/response for an enrolment has been accepted"""

        self.log('Invitation accepted:', event.__dict__, lvl=debug)
        try:
            uuid = event.data
            enrollment = objectmodels['enrollment'].find_one({
                'uuid': uuid
            })

            if enrollment is not None:
                self.log('Enrollment found', lvl=debug)
                if enrollment.status == 'Open':
                    self.log('Enrollment is still open', lvl=debug)
                    if enrollment.method == 'Invited' and self.config.auto_accept_invited:
                        enrollment.status = 'Accepted'

                        data = 'You should have received an email with your new password ' \
                               'and can now log in to the system and start to use it. <br/>' \
                               'Please change your password immediately after logging in'
                        password = std_human_uid().replace(" ", '')

                        self._create_user(enrollment.name, password, enrollment.email, enrollment.method, uuid)
                        self._send_acceptance(enrollment, password, event)
                    elif enrollment.method == 'Enrolled' and self.config.auto_accept_enrolled:
                        enrollment.status = 'Accepted'
                        data = 'Your account is now activated.'

                        self._create_user(enrollment.name, enrollment.password, enrollment.email, enrollment.method,
                                          uuid)

                        # TODO: Evaluate if sending an acceptance mail makes sense
                        # self._send_acceptance(enrollment, "", event)
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
                    self._fail(event)
                    return
                packet = {
                    'component': 'hfos.enrol.enrolmanager',
                    'action': 'accept',
                    'data': {True: data}
                }
                self.fireEvent(send(event.client.uuid, packet))
            else:
                self.log('No enrollment available.', lvl=warn)
                self._fail(event)
        except Exception as e:
            self.log('Error during invitation accept handling:', e, type(e),
                     lvl=warn, exc=True)

    @handler(status)
    def status(self, event):
        """An anonymous client wants to know if we're open for enrollment"""

        self.log('Registration status requested')

        response = {
            'component': 'hfos.enrol.enrolmanager',
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

        email = event.data.get('email', None)
        email_user = None

        if email is not None and user_object.count({'mail': email}) > 0:
            email_user = user_object.find_one({'mail': email})

        if email_user is None:
            self._fail(event, msg="Mail address unknown")
            return

    @handler(delete)
    def delete(self, event):
        self.log('Deleting user')

        user_object = objectmodels['user'].find_one({'uuid': event.data})
        profile_object = objectmodels['profile'].find_one({'owner': event.data})

        user_object.delete()
        profile_object.delete()

        self.log('User deleted:', user_object.name)
        self._acknowledge(event, event.data)

    @handler(delrole)
    def delrole(self, event):
        self.log('Deleting user role')
        role = event.data.get('role', None)
        uuid = event.data.get('uuid', None)

        if role is None or uuid is None:
            self._fail(event, 'Bad Arguments')
            return

        user_object = objectmodels['user'].find_one({'uuid': uuid})
        user_object.roles.remove(role)
        user_object.save()

        self.log('User role deleted:', user_object.name, role)
        self._acknowledge(event)

    @handler(addrole)
    def addrole(self, event):
        self.log('Adding user role')
        role = event.data.get('role', None)
        uuid = event.data.get('uuid', None)

        if role is None or uuid is None:
            self._fail(event, 'Bad Arguments')
            return

        user_object = objectmodels['user'].find_one({'uuid': uuid})

        if role in user_object.roles:
            self._fail(event, 'Role already assigned')
            return

        user_object.roles.append(role)
        user_object.save()

        self.log('User role added:', user_object.name, role)
        self._acknowledge(event)

    @handler(toggle)
    def toggle(self, event):
        self.log('Toggling user activation')
        status = event.data.get('status', None)
        uuid = event.data.get('uuid', None)

        if status is None or uuid is None:
            self._fail(event, 'Bad Arguments')
            return

        user_object = objectmodels['user'].find_one({'uuid': uuid})
        user_object.active = status
        user_object.save()

        self.log('Toggled user:', user_object.name, ', activated:', status)
        self._acknowledge(event)

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
            'component': 'hfos.enrol.enrolmanager',
            'action': 'captcha',
            'data': b64encode(captcha['image'].getvalue()).decode('utf-8')
        }
        self.fire(send(uuid, response))

    def _invite(self, name, method, email, uuid, event, password=""):
        """Actually invite a given user"""

        props = {
            'uuid': std_uuid(),
            'status': 'Open',
            'name': name,
            'method': method,
            'email': email,
            'password': password,
            'timestamp': std_now()
        }
        enrollment = objectmodels['enrollment'](props)
        enrollment.save()

        self.log('Enrollment stored', lvl=debug)

        self._send_invitation(enrollment, event)

        packet = {
            'component': 'hfos.enrol.enrolmanager',
            'action': 'invite',
            'data': [True, email]
        }
        self.fireEvent(send(uuid, packet))

    def _create_user(self, username, password, mail, method, uuid):
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
                'roles': roles,
                'created': std_now()
            })

            if method == 'Invited':
                newuser.needs_password_change = True

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

            packet = {
                'component': 'hfos.enrol.enrolmanager',
                'action': 'enrol',
                'data': [True, mail]
            }
            self.fireEvent(send(uuid, packet))

            # TODO: Notify crew-admins
        except Exception as e:
            self.log("Problem creating new profile: ", type(e),
                     e, lvl=error)

    def _send_invitation(self, enrollment, event):
        """Send an invitation mail to an open enrolment"""

        self.log('Sending enrollment status mail to user')

        self._send_mail(self.config.invitation_subject, self.config.invitation_mail, enrollment, event)

    def _send_acceptance(self, enrollment, password, event):
        """Send an acceptance mail to an open enrolment"""

        self.log('Sending acceptance status mail to user')

        if password is not "":
            password_hint = '\n\nPS: Your new password is ' + password + ' - please change it after your first login!'

            acceptance_text = self.config.acceptance_mail + password_hint
        else:
            acceptance_text = self.config.acceptance_mail

        self._send_mail(self.config.acceptance_subject, acceptance_text, enrollment, event)

    def _send_mail(self, subject, template, enrollment, event):
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
        if self.config.mail_send is True:
            self.log('Sending mail to', enrollment.email)

            self.fireEvent(task(send_mail_worker, self.config, mime_mail, event), "enrolworkers")
        else:
            self.log('Not sending mail, here it is for debugging info:', mail, pretty=True)

    @handler('task_success', channel="enrolworkers")
    def task_success(self, event, call, result):
        success, log, originating_event = result

        if success is True:
            self.log('Sent mail successfully.')
        else:
            self.log('Sending mail failed:', event, call, log, lvl=error)
            self._fail(originating_event,
                       _('Sorry, sending that email apparently failed. Please contact a node maintainer.'))


def send_mail_worker(config, mail, event):
    """Worker task to send out an email, which blocks the process unless it is threaded"""
    log = ""

    try:
        if config.mail_ssl:
            server = SMTP_SSL(config.mail_server, port=config.mail_server_port, timeout=30)
        else:
            server = SMTP(config.mail_server, port=config.mail_server_port, timeout=30)

        if config.mail_tls:
            log += 'Starting TLS\n'
            server.starttls()

        if config.mail_username != '':
            log += 'Logging in with ' + str(config.mail_username) + "\n"
            server.login(config.mail_username, config.mail_password)
        else:
            log += 'No username, trying anonymous access\n'

        log += 'Sending Mail\n'
        response_send = server.send_message(mail)
        server.quit()

    except timeout as e:
        log += 'Could not send email to enrollee, mailserver timeout: ' + str(e) + "\n"
        return False, log, event

    log += 'Server response:' + str(response_send)
    return True, log, event
