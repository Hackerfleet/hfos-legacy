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

    constructor(rootscope, $modal, navdata, user, objectproxy) {
        this.rootscope = rootscope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.objectproxy = objectproxy;

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

        this.referenceframe = {};
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


        this.objectproxy.getObject('dashboardconfig', this.dashboarduuid);

        var self = this;

        this.rootscope.$on('hfos.NavdataUpdate', function () {
            var framedata = navdata.frame();
            var frameages = navdata.ages();
            var now = new Date().getTime();
            console.log('Updating Dashboard');
            var data;

            for (var property of framedata) {
                data = {
                    value: framedata[property],
                    birth: frameages[property],
                    age: humanizeDuration(((now / 1000) - frameages[property]) * 1000, {round: true}),
                    observed: self.observed.indexOf(property) >= 0
                };
                self.referenceframe[property] = data;
            }


        });

        rootscope.$on('OP.Get', function (ev, uuid) {
            if (uuid === self.dashboarduuid) {
                console.log('[DASH] Received dashboard configuration');
                self.resetDashboard();
            }
        });

        rootscope.$on('Clientconfig.Update', function () {
            console.log('[DASH] New dashboard configured, adapting');
            self.dashboarduuid = user.clientconfig.dashboarduuid;
            self.objectproxy.getObject('dashboardconfig', self.dashboarduuid);
        });

    }

    updateObserved() {
        console.log('[DASH] Updating observed values from ', this.dashboard.cards);
        this.observed = [];
        for (var card of this.dashboard.cards) {
            console.log('[DASH]', this.dashboard.cards[card]);
            this.observed.push(this.dashboard.cards[card].valuetype);
        }
        console.log(this.observed);
    }

    resetDashboard() {
        console.log('[DASH] Resetting dashboard to ', this.dashboarduuid);
        this.dashboard = this.objectproxy.objects[this.dashboarduuid];
        console.log(this.dashboard);
        //console.log(decksterConfig);
        this.updateObserved();
    }

    opentab(tabname) {
        console.log('[DASH] Switching tab to ', tabname);
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
        this.objectproxy.putObject('dashboardconfig', this.dashboard);
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

Dashboard.$inject = ['$rootScope', '$modal', 'navdata', 'user', 'objectproxy'];

export default Dashboard;

/*directive('ngDynamicController', ['$compile', '$http', function ($compile, $http) {
 return {
 scope: {
 widgettype: '=ngDynamicController',
 valuetype: '='
 },
 restrict: 'A',
 transclude: true,
 //            terminal: true,
 //            priority: 100000,
 link: function (scope, elem, attrs) {
 console.log('[NGDC] SCOPE:', scope, attrs);
 elem.attr('ng-controller', scope.widgettype);
 elem.removeAttr('ng-dynamic-controller');

 $http.get('/views/cards/' + scope.widgettype + '.html')
 .then(function (response) {
 console.log('[NGDC] Html Response:', response.data);
 elem.append(response.data);
 $compile(elem)(scope);
 });
 /*var build = function (html) {
 element.empty().append($compile(html)(scope));
 };
 scope.$watch('widget.template', function (newValue, oldValue){
 if (newValue) {
 build(newValue);
 }
 });

 /*
 var build = function (html) {
 //    $http.get('/views/cards/' + html + '.html')
 .then(function(response){
 //var linkFn = $compile(response.data)(scope);
 //elem.html(linkFn(scope));
 console.log(elem);
 elem.attr('ng-controller', scope.widgettype);
 console.log(elem);
 elem.removeAttr('ng-dynamic-controller');
 console.log(elem);
 elem.append($compile(response.data)(scope));
 console.log(elem);
 });
 //elem.empty().append($compile(html)(scope));
 };
 scope.$watch('widgettype', function (newValue, oldValue) {
 console.log('[NGDC] Adding html for widgettype: ', scope.widgettype);
 if (newValue) {
 build(newValue);
 }
 });*//*

 // $compile(elem)(scope);
 }
 };
 }]);*/

