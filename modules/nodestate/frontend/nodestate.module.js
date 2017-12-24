/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2017 riot <riot@c-base.org> and others.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

import './nodestate/nodestate.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './nodestate.config.js';

import nodestatecomponent from './nodestate/nodestate';
import template from './nodestate/nodestate.tpl.html';

export default angular
    .module('main.app.nodestate', [uirouter])
    .config(routing)
    .component('nodestate', {controller: nodestatecomponent, template: template, bindings: {uuid: '@', hideui: '@'}})
    .name;
