'use strict';

var humanizeDuration = require('humanize-duration');

import configcomponent from './config';
import configtemplate from './config.tpl.html';
/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the hfosFrontendApp
 */
class Dashboard {

    constructor(scope, $modal, navdata, user, objectproxy, socket, menu) {
        this.scope = scope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;

        this.humanize = humanizeDuration;

        this.now = new Date() / 1000;

        this.deckOptions = {
            id: 'Dashboard',
            gridsterOpts: { // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
                columns: 3,
                rowHeight: 150,
                margins: [10, 10]
            }
        };

        this.dashboarduuid = user.clientconfig.dashboarduuid;
        this.dashboard = {};

        this.sensed = [];

        this.referencedata = {};
        this.referenceages = {};
        this.observed = [];

        this.configmodal = this.$modal({
            template: configtemplate,
            controller: configcomponent,
            controllerAs: '$ctrl',
            title: 'Dashboard configuration',
            backdrop: false,
            id: 'DashboardConfig',
            show: false
        });


        this.op.getObject('dashboardconfig', this.dashboarduuid);

        var self = this;

        /*
        this.handleNavdata = function (msg) {
            console.log('Updating Dashboard');
            self.referencedata[msg.data.type] = msg.data.value;
            self.referenceages[msg.data.type] = msg.data.timestamp;
        };

        self.socket.listen('navdata', this.handleNavdata);
        */

        this.handleNavdata = function (msg) {
            if (msg.action === 'list') {
                console.log('Got a navdata list:', msg.data);
                if ('sensed' in msg.data) {
                    console.log('Updating sensed list.');
                    self.now = new Date() / 1000;
                    self.sensed = msg.data.sensed;
                }
            }
        };

        self.socket.listen('navdata', this.handleNavdata);

        this.switchDashboard = function (uuid) {
            self.dashboarduuid = uuid;
            self.op.getObject('dashboardconfig', uuid);
        };

        this.scope.$on('OP.Get', function (ev, uuid) {
            if (uuid === self.dashboarduuid) {
                console.log('[DASH] Received dashboard configuration');
                self.resetDashboard();
            }
        });

        this.scope.$on('Clientconfig.Update', function () {
            self.getDashboard();
        });

        if (typeof user.clientconfig.dashboarduuid !== 'undefined')  {
            this.getDashboard();
        }

        this.scope.$on('OP.ListUpdate', function (event, schema) {
            if (schema === 'dashboardconfig') {
                var dashboardlist = self.op.lists.dashboardconfig;
                var dashboardmenu = [];
                for (var dashboard of dashboardlist) {
                    dashboardmenu.push({
                        type: 'func',
                        name: dashboard.uuid,
                        text: dashboard.name,
                        callback: self.switchDashboard,
                        args: dashboard.uuid
                    });
                }
                self.menu.addMenu('Dashboards', dashboardmenu);
            }
        });

        this.requestDashboards = function() {
            self.op.getList('dashboardconfig');
        };

        this.scope.$on('User.Login', function (ev) {
            console.log('Login successful - fetching dashboard data');
            self.requestDashboards();
        });

        if (this.user.signedin === true) {
            console.log('Logged in - fetching dashboard data');
            this.requestDashboards();
        }
    }

    updateObserved() {
        console.log('[DASH] Updating observed values from ', this.dashboard.cards);
        this.observed = [];
        for (var card of this.dashboard.cards) {
            console.log('[DASH]', card);
            this.observed.push(card.valuetype);
        }
        console.log(this.observed);
        var request = {
            component: 'navdata',
            action: 'subscribe',
            data: this.observed
        };
        this.socket.send(request);
    }

    resetDashboard() {
        console.log('[DASH] Resetting dashboard to ', this.dashboarduuid);
        this.dashboard = this.op.objects[this.dashboarduuid];
        console.log(this.dashboard);
        //console.log(decksterConfig);
        this.updateObserved();
    }

    getDashboard() {
        console.log('[DASH] Getting newly configured dashboard');
        this.dashboarduuid = this.user.clientconfig.dashboarduuid;
        this.op.getObject('dashboardconfig', this.dashboarduuid);
    }

    opentab(tabname) {
        console.log('[DASH] Switching tab to ', tabname);
        if (tabname === 'sensed') {
            var req = {
                component: 'navdata',
                action: 'list',
                data: 'sensed'
            };

            console.log('Requesting sensed list.');
            this.socket.send(req);
        }
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
    }

    toggleDashboardItem(key) {
        var card;
        if (this.observed.indexOf(key) >= 0) {
            console.log('[DASH] Removing ', key, ' from dashboard.');
            for (var item of this.dashboard.cards) {
                if (item.valuetype === key) {
                    this.dashboard.cards.pop(item);
                }
            }
        } else {
            console.log('[DASH] Adding ', key, ' to dashboard.');
            card = {
                'widgettype': 'DigitalReadout',
                'valuetype': key,
                'title': key
            };
            this.dashboard.cards.push(card);
        }
        console.log('[DASH] Putting new dashboard: ', this.dashboard);
        this.op.putObject('dashboardconfig', this.dashboard);
        this.updateObserved();
    }

    configureCards() {
        console.log('[DASH] Opening configuration:', configcomponent, configtemplate);

        // Pre-fetch an external template populated with a custom scope
        // Show when some event occurs (use $promise property to ensure the template has been loaded)
        this.configmodal.$promise.then(this.configmodal.show);


        console.log('I am done with this stuff..');
    }
}

Dashboard.$inject = ['$scope', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu'];

export default Dashboard;