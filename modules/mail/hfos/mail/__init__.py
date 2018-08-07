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
Package: Mail 
=============

Defines a "send_mail" event and contains mail receiver as well as transmitter.

"""

from circuits import Event


class send_mail(Event):
    """Request to send an email"""

    def __init__(self, to_address, subject, text, account='default', *args, **kwargs):
        """

        :param to_address:
        :param subject:
        :param text:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.to_address = to_address
        self.subject = subject
        self.text = text
        self.account = account
