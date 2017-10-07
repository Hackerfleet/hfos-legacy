//import './chat/chat.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './chat.config.js';

import './chat/chat.scss';

import chatserviceclass from './chat/chatservice.js';
import chatcomponent from './chat/chatcomponent.js';
import chatbutton from './chat/chatbutton';

import template from './chat/chat.tpl.html';

export default angular
    .module('main.app.chat', [uirouter])
    .config(routing)
    .service('chatservice', chatserviceclass)
    .component('chat', {controller: chatcomponent, template: template})
    .directive('chatbutton', chatbutton)
    .run(function (chatservice) {})
    .name;
