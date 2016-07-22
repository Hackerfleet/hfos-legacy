/**
 * Created by riot on 03.05.16.
 */

class DashboardConfigCtrl {

    constructor(rootscope, user, objectproxy) {
        this.rootscope = rootscope;
        this.objectproxy = objectproxy;
        this.user = user;
        console.log('DashboardConfigController init');

        this.dashboardlist = objectproxy.getList('dashboardconfig', {
            '$or': [
                {'useruuid': user.user.uuid},
                {'shared': true}]
        }, ['name', 'description']);

        var self = this;

        this.rootscope.$on('OP.ListUpdate', function (ev, schema) {
            console.log('[DASHBOARDCONFIG] List update:', schema);

            if (schema === 'dashboard') {
                console.log('[DASHBOARDCONFIG] Dashboardconfig list updating');
                self.dashboardlist = self.objectproxy.lists.dashboardconfig;
                //$scope.$apply();
            }
        });
    }

    selectDashboard(uuid) {
        console.log('[DASHBOARDCONFIG] Updating dashboard selection');
        var origconf = this.user.clientconfig;
        console.log(origconf);
        origconf.dashboarduuid = uuid;
        this.user.updateclientconfig(origconf);
    }
}

DashboardConfigCtrl.$inject = ['$rootScope', 'user', 'objectproxy'];

export default DashboardConfigCtrl;
