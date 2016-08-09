/**
 * Created by riot on 03.05.16.
 */

class LogbookConfigCtrl {

    constructor(rootscope, user, objectproxy) {
        this.rootscope = rootscope;
        this.objectproxy = objectproxy;
        this.user = user;
        console.log('LogbookConfigController init');

        this.logbooklist = objectproxy.getList('logbookconfig', {
            '$or': [
                {'useruuid': user.user.uuid},
                {'shared': true}]
        }, ['name', 'description']);

        var self = this;

        this.rootscope.$on('OP.ListUpdate', function (ev, schema) {
            console.log('[LOGBOOKCONFIG] List update:', schema);

            if (schema === 'logbook') {
                console.log('[LOGBOOKCONFIG] Logbookconfig list updating');
                self.logbooklist = self.objectproxy.lists.logbookconfig;
                //$scope.$apply();
            }
        });
    }

    selectLogbook(uuid) {
        console.log('[LOGBOOKCONFIG] Updating logbook selection');
        var origconf = this.user.clientconfig;
        console.log(origconf);
        origconf.logbookuuid = uuid;
        this.user.updateclientconfig(origconf);
    }
}

LogbookConfigCtrl.$inject = ['$rootScope', 'user', 'objectproxy'];

export default LogbookConfigCtrl;
