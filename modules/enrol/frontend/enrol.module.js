/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2018 riot <riot@c-base.org> and others.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

import './enrol/enrolmanagement.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './enrol.config.js';

import enrolcomponent from './enrol/enrol';
import enroltemplate from './enrol/enrol.tpl.html';

import invitationcomponent from './enrol/invitation';
import invitationtemplate from './enrol/invitation.tpl.html';

import passwordcomponent from './enrol/password';
import passwordtemplate from './enrol/password.tpl.html';

import enrolmentcomponent from './enrol/enrolment';
import enrolmenttemplate from './enrol/enrolment.tpl.html';

import resetcomponent from './enrol/reset';
import resettemplate from './enrol/reset.tpl.html';

import tostemplate from './enrol/tos.tpl.html';

export default angular
    .module('main.app.enrol', [uirouter])
    .config(routing)
    .component('enrol', {controller: enrolcomponent, template: enroltemplate})
    .component('invitation', {controller: invitationcomponent, template: invitationtemplate})
    .component('password', {controller: passwordcomponent, template: passwordtemplate})
    .component('enrolment', {controller: enrolmentcomponent, template: enrolmenttemplate})
    .component('resetaccount', {controller: resetcomponent, template: resettemplate})
    .component('tos', {template: tostemplate})
    .name;
