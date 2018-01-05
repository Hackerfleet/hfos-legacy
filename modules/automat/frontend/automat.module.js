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

import './automat/automat.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './automat.config.js';

import automatcomponent from './automat/automat';
import template from './automat/automat.tpl.html';
import automattoolcontroller from './automat/logic/directives/dynamiccontroller';

import comparecontroller from './automat/logic/controllers/compare_int';

export default angular
    .module('main.app.automat', [uirouter])
    .config(routing)
    .component('automat', {controller: automatcomponent, template: template})
    .controller('automat-compare_int', comparecontroller)
    .directive('ngAutomatTool', automattoolcontroller)
    .name;
