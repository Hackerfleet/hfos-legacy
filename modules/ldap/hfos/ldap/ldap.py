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

from circuits import handler, Event

from hfos.component import ConfigurableComponent
from hfos.ui.auth import add_auth_hook
from hfos.logger import hfoslog, debug, warn, critical, error

try:
    import ldap
except ImportError:
    ldap = None
    hfoslog("No python-ldap library found, install "
            "requirements-optional.txt", lvl=warn, emitter="LDAP")

cbaseldap = {
    'URI': 'ldap://127.0.0.1:389/',
    'BASE': 'dc=c-base,dc=org',
    'USERBASE': 'ou=crew',
    'BINDDN': 'cn=password,ou=bind,dc=c-base,dc=org',
    'PINFIELD': 'c-labPIN',
    'UIDFIELD': 'uid',
    'ACCESS_FILTER': '(&(uidNumber={})(memberof=cn=cey-c-lab,ou=groups,'
                     'dc=c-base,dc=org)(memberof=cn=crew,ou=groups,'
                     'dc=c-base,dc=org))'
}

defaultcomponentconfig = {
    'URI': 'ldap://127.0.0.1:389/',
    'BASE': 'dc=example,dc=org',
    'USERBASE': 'ou=crew',
    'BINDDN': 'cn=password,ou=bind,dc=example,dc=org',
    'BINDPW': 'ENTER BIND-PASSWORD HERE',
    'PINFIELD': 'c-labPIN',
    'UIDFIELD': 'uid',
    'ACCESS_FILTER': '(&(uidNumber={})(memberof=cn=cey-c-lab,ou=groups,'
                     'dc=c-base,dc=org)(memberof=cn=crew,ou=groups,'
                     'dc=c-base,dc=org))'
}


class lmap_authenticate(Event):
    def __init__(self, username, password, *args, **kwargs):
        super(lmap_authenticate, self).__init__(*args, **kwargs)

        self.uid = username
        self.pin = password


class LDAPAdaptor(ConfigurableComponent):
    configprops = {
        'URI': {'type': 'string', 'title': 'URI',
                'description': 'Uniform Resource Identifier (e.g. '
                               'ldap://127.0.0.1:389/)',
                'default': 'ldap://127.0.0.1:389/'},
        'BASE': {'type': 'string', 'title': 'Base',
                 'description': 'CN (e.g. dc=example,dc=org)',
                 'default': 'dc=example,dc=org'},
        'USERBASE': {'type': 'string', 'title': 'Userbase',
                     'description': 'OU (e.g. ou=users)',
                     'default': 'ou=users'},
        'BINDDN': {'type': 'string', 'title': 'Bind Domain',
                   'description': 'CN to bind (e.g. cn=password,ou=bind,'
                                  'dc=example,dc=org)',
                   'default': 'cn=password,ou=bind,dc=example,dc=org'},
        'BINDPW': {
            'type': 'string', 'title': 'Bind Password',
            'description': 'Bind password', 'default': '',
            'x-schema-form': {
                'type': 'password'
            }
        },
        'PINFIELD': {'type': 'string', 'title': 'Pin field',
                     'description': 'Pin Field in LDAP',
                     'default': 'pinfield'},
        'UIDFIELD': {'type': 'string', 'title': 'UID field',
                     'description': 'User ID field in LDAP', 'default': 'uid'},
        'ACCESS_FILTER': {'type': 'string', 'title': 'Access Filter',
                          'description': 'E.g. (&(uidNumber={})('
                                         'memberof=cn=users,ou=groups,'
                                         'dc=example,dc=org)('
                                         'memberof=cn=otherusers,ou=groups,'
                                         'dc=example,dc=org))',
                          'default': '(&(uidNumber={})(memberof=cn=users,'
                                     'ou=groups,dc=example,dc=org)('
                                     'memberof=cn=otherusers,ou=groups,'
                                     'dc=example,dc=org))'}
    }

    def __init__(self, *args, **kwargs):
        super(LDAPAdaptor, self).__init__("LDAP", *args, **kwargs)
        if ldap is None:
            self.log("NOT started, no python-lmap found", lvl=warn)
            return
        self.log("Started")

        # self.ldap = ldap.Server(self.config.URI)

        self.log('Adding authentication hook', lvl=debug)
        self.fireEvent(add_auth_hook(self.uniquename, lmap_authenticate))

    def _get_ldap_details(self, username, password):
        self.log('Connecting to LDAP')
        dn = 'uid=' + username + ',' + self.config.BINDDN
        session = ldap.Connection(self.server, dn, password, auto_bind=True)

        search_filter = "(uid=%s)" % username

        result = session.search(self.config.BINDDN, search_filter)

        session.unbind()
        return result

    @handler('ldap_authenticate')
    def ldap_authenticate(self, event):
        try:
            username = event.username
            password = event.password

            user_data = self._get_ldap_details(username, password)
            self.log('LDAP details:', user_data)

        except Exception as e:
            self.log('Invalid user/pin:', username, '(' + str(e) + ')',
                     lvl=warn)
            return False
