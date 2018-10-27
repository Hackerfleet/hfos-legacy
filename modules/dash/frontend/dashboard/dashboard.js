'use strict';

let humanizeDuration = require('humanize-duration');

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the hfosFrontendApp
 */
class Dashboard {

    constructor($scope, $rootscope, $stateParams, $modal, navdata, user, systemconfig, objectproxy, socket, menu, $timeout) {
        this.scope = $scope;
        this.rootscope = $rootscope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.systemconfig = systemconfig;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
        this.timeout = $timeout;


        this.humanize = humanizeDuration;

        this.now = new Date() / 1000;
        this.lockState = false;
        this.showBoxes = true;

        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 75,
            rowHeight: 75,
            colWidth: 75,
            mobileModeEnabled: false,
            floating: false,
            draggable: {
                enabled: false
            },
            resizable: {
                enabled: false
            }
        };

        this.changetimeout = null;

        if (typeof this.uuid === 'undefined') {
            this.dashboarduuid = $stateParams.uuid;
        } else {
            this.dashboarduuid = this.uuid;
        }

        if (typeof this.hideui === 'undefined') {
            this.hideui = false;
        }

        this.dashboard = {};

        this.sensed = [];

        this.referencedata = {};
        this.referenceages = {};
        this.observed = [];

        if (this.user.signedIn === true) {
            if (typeof this.dashboarduuid === 'undefined') this.getDefaultDashboard();
            this.op.getObject('dashboardconfig', this.dashboarduuid);
        }

        let self = this;

        this.handleNavdata = function (msg) {
            console.log('DASHBOARD HANDLING NAVDATA');
            if (msg.action === 'sensed') {
                console.log('[DASH] Got a navdata list:', msg.data);
                if ('sensed' in msg.data) {
                    console.log('[DASH] Updating sensed list.');
                    self.now = new Date() / 1000;
                    self.sensed = msg.data.sensed;
                }
            }
        };

        self.socket.listen('hfos.navdata.sensors', self.handleNavdata);

        this.stopSubscriptions = function () {
            console.log('[DASH] Finally destroying all subscriptions');
            self.stopObserved();
            self.socket.unlisten('hfos.navdata.sensors', self.handleNavdata);
        };

        this.statechange = self.rootscope.$on('$stateChangeStart',
            function (event, toState, toParams, fromState, fromParams, options) {
                console.log('DASH] States: ', toState, fromState);
                if (toState !== 'Dashboard') {
                    self.stopSubscriptions();
                }
            });

        this.switchDashboard = function (uuid) {
            self.dashboarduuid = uuid;
            self.op.get('dashboardconfig', uuid).then(function(msg) {
                if (msg.action === 'get') {
                    self.resetDashboard();
                }
            });
        };

        this.dashboardupdate = this.rootscope.$on('OP.Get', function (ev, uuid) {
            if (uuid === self.dashboarduuid) {
                console.log('[DASH] Received dashboard configuration');
                self.resetDashboard();
            }
        });

        this.loginupdate = this.rootscope.$on('User.Login', function () {
            console.log('[DASH] Login successful - fetching dashboard data');
            self.requestDashboards();
            self.getDefaultDashboard();
        });

        this.profileupdate = this.rootscope.$on('Profile.Update', function() {
            console.log('[DASH] Profile updated');
            self.getDefaultDashboard();
        });

        this.clientconfigupdate = this.rootscope.$on('Clientconfig.Update', function () {
            // TODO: Is this handling smart? Maybe it overrides a manually selected one.
            console.log('[DASH] Clientconfig updated');
            self.getDefaultDashboard();
        });

        if (typeof user.clientconfig.dashboarduuid !== 'undefined') {
            this.getDashboard();
        }

        this.scope.$on('OP.ListUpdate', function (event, schema) {
            if (schema === 'dashboardconfig') {
                let dashboardlist = self.op.lists.dashboardconfig,
                    dashboardmenu = [];
                for (let dashboard of dashboardlist) {
                    dashboardmenu.push({
                        type: 'func',
                        name: dashboard.uuid,
                        text: dashboard.name,
                        callback: self.switchDashboard,
                        args: dashboard.uuid
                    });
                }
                self.menu.removeMenu('Dashboards');
                self.menu.addMenu('Dashboards', dashboardmenu);
            }
        });

        this.handleGridChange = function (newVal, oldVal) {
            if (newVal === oldVal) {
                console.log('No actual change');
                return;
            }
            if (self.changetimeout !== null) {
                self.timeout.cancel(self.changetimeout);
            }
            self.changetimeout = self.timeout(self.storeMenuConfig, 2000);
        };

        this.storeMenuConfig = function () {
            console.log('[DASH] Pushing dashboard');
            for (let card of self.dashboard.cards) {
                delete card['$$hashKey'];
            }
            self.op.putObject('dashboardconfig', self.dashboard);

            self.changetimeout = null;
        };

        this.requestDashboards = function () {
            console.log('[DASH] Getting list of dashboards');
            self.op.getList('dashboardconfig');
        };

        if (this.user.signedin === true) {
            console.log('[DASH] Logged in - fetching dashboard data');
            this.requestDashboards();
        }

        this.store_listener = this.scope.$on('Dash.Store', function(ev, data) {
            console.log('[DASH] Storing widget data:', data);
            let modified = false;

            self.dashboard.cards.forEach(function(item) {
                if (item.position.x === data.x && item.position.y === data.y) {
                    item.valuetype = data.valuetype;
                    modified = true;
                }
            });
            if (modified === true) self.storeMenuConfig();
        });

        self.scope.$on('$destroy', function() {
            self.stopSubscriptions();
            self.dashboardupdate();
            self.clientconfigupdate();
            self.loginupdate();
            self.profileupdate();
            self.statechange();
            self.store_listener();
        });

        console.log('[DASH] Starting');
    }

    stopObserved() {
        if (this.observed.length > 0) {
            console.log('[DASH] Stopping current navdata subscriptions');
            let request = {
                component: 'hfos.navdata.sensors',
                action: 'unsubscribe',
                data: this.observed
            };
            this.socket.send(request);
        } else {
            console.log('[DASH] No subscriptions to remove');
        }
    }

    updateObserved() {
        this.stopObserved();
        console.log('[DASH] Updating observed values from ', this.dashboard.cards);
        this.observed = [];
        for (let card of this.dashboard.cards) {
            console.log('[DASH] Inspecting card:', this.observed, card.valuetype, this.observed.indexOf(card.valuetype));
            if (this.observed.indexOf(card.valuetype) === -1) {
                console.log('[DASH] Adding: ', card.valuetype);
                this.observed.push(card.valuetype);
            }
        }
        console.log(this.observed);
        let request = {
            component: 'hfos.navdata.sensors',
            action: 'subscribe',
            data: this.observed
        };
        this.socket.send(request);
    }

    resetDashboard() {
        console.log('[DASH] Resetting dashboard to ', this.dashboarduuid);
        this.dashboard = this.op.objects[this.dashboarduuid];
        console.log(this.dashboard);
        this.updateObserved();
    }

    getDefaultDashboard() {
        this.dashboardconfiguuid = this.user.getModuleDefault('dashboarduuid');

        this.getDashboard();
    }

    getDashboard() {
        console.log('[DASH] Getting newly configured dashboard');
        this.switchDashboard(this.user.clientconfig.dashboarduuid);
    }
    
    opentab(tabname) {
        console.log('[DASH] Switching tab to ', tabname);
        if (tabname === 'sensed') {
            let req = {
                component: 'hfos.navdata.sensors',
                action: 'sensed'
            };
            
            console.log('[DASH] Requesting sensed list.');
            this.socket.send(req);
        }
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
    }

    toggleLock() {
        this.lockState = !this.lockState;
        this.gridsterOptions.draggable.enabled = this.lockState;
        this.gridsterOptions.resizable.enabled = this.lockState;
        if (this.lockState) {
            console.log('Enabling gridwatcher');
            this.gridChangeWatcher = this.scope.$watch('$ctrl.dashboard.cards', this.handleGridChange, true);
        } else {
            this.gridChangeWatcher();
        }
    }

    toggleDashboardItem(key) {
        let card;
        if (this.observed.indexOf(key) >= 0) {
            console.log('[DASH] Removing ', key, ' from dashboard.');
            for (let item of this.dashboard.cards) {
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
}

Dashboard.$inject = ['$scope', '$rootScope', '$stateParams', '$modal', 'navdata', 'user', 'systemconfig', 'objectproxy', 'socket', 'menu', '$timeout'];

export default Dashboard;
