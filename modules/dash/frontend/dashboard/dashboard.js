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
    
    constructor($scope, $rootscope, $stateParams, $modal, navdata, user, objectproxy, socket, menu, $timeout) {
        this.scope = $scope;
        this.rootscope = $rootscope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
        this.timeout = $timeout;
        
    
        this.humanize = humanizeDuration;
        
        this.now = new Date() / 1000;
        
        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 75,
            rowHeight: 75,
            colWidth: 75,
            floating: false
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
    
        if (typeof this.dashboarduuid === 'undefined') {
            this.dashboarduuid = user.clientconfig.dashboarduuid;
        }
    
        this.dashboard = {};
        
        this.sensed = [];
        
        this.referencedata = {};
        this.referenceages = {};
        this.observed = [];
        
        this.op.getObject('dashboardconfig', this.dashboarduuid);
        
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
                if (toState != 'Dashboard') {
                    self.stopSubscriptions();
                }
            });
        
        this.switchDashboard = function (uuid) {
            self.dashboarduuid = uuid;
            self.op.getObject('dashboardconfig', uuid);
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
        });
    
        this.clientconfigupdate = this.rootscope.$on('Clientconfig.Update', function () {
            self.getDashboard();
        });
        
        if (typeof user.clientconfig.dashboarduuid !== 'undefined') {
            this.getDashboard();
        }
    
        self.scope.$on('$destroy', function() {
            self.stopSubscriptions();
            self.dashboardupdate();
            self.clientconfigupdate();
            self.loginupdate();
            self.statechange();
        });
        
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
        
        this.storeMenuConfig = function () {
            console.log('[MENU] Pushing menu to profile:', menu);
            for (let card of self.dashboard.cards) {
                delete card['$$hashKey'];
            }
            self.op.putObject('dashboardconfig', self.dashboard);
            
            self.changetimeout = null;
        };
        
        $scope.$watch('$ctrl.dashboard.cards', function (items) {
            if (self.changetimeout !== null) {
                $timeout.cancel(self.changetimeout);
            }
            self.changetimeout = $timeout(self.storeMenuConfig, 2000);
        }, true);
        
        this.requestDashboards = function () {
            console.log('[DASH] Getting list of dashboards');
            self.op.getList('dashboardconfig');
        };
        
        if (this.user.signedin === true) {
            console.log('[DASH] Logged in - fetching dashboard data');
            this.requestDashboards();
        }
        
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
            if (this.observed.indexOf(card.valuetype) == -1) {
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

Dashboard.$inject = ['$scope', '$rootScope', '$stateParams', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu', '$timeout'];

export default Dashboard;
