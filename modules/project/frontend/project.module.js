import './taskgrid/taskgrid.scss';
import './todo/todo.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './project.config.js';

import taskgridcomponent from './taskgrid/taskgrid.js';
import taskgridtemplate from './taskgrid/taskgrid.tpl.html';

import todocomponent from './todo/todo.js';
import todotemplate from './todo/todo.tpl.html';

export default angular
    .module('main.app.taskgrid', [uirouter])
    .config(routing)
    .component('taskgrid', {controller: taskgridcomponent, template: taskgridtemplate})
    .component('todo', {controller: todocomponent, template: todotemplate})
    .name;
