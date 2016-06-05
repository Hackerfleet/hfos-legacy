import angular from 'angular';

import NavDataService from './navdata/navdata.js';

export default angular
    .module('main.app.navdata', [])
    .service('navdata', NavDataService)
    .name;
