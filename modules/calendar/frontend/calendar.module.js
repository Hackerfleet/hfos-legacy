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

import angular from 'angular';
import uirouter from 'angular-ui-router';

import './calendar/calendar.scss';

import { routing } from './calendar.config.js';

import calendarcomponent from './calendar/calendar.js';
import template from './calendar/calendar.tpl.html';

import upcomingcomponent from './calendar/upcoming.js';
import upcomingtemplate from './calendar/upcoming.tpl.html';

import 'fullcalendar/dist/fullcalendar.min.css';
require('fullcalendar');
import 'angular-ui-calendar';

export default angular
    .module('main.app.calendar', [uirouter, 'ui.calendar', 'ngAnimate'])
    .config(routing)
    .component('calendar', {controller: calendarcomponent, template: template})
    .component('upcoming', {controller: upcomingcomponent, template: upcomingtemplate})
    .name;
