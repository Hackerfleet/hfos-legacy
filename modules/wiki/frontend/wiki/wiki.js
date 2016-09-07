'use strict';

class wikicomponent {

    constructor($scope, objectproxy, $state, $rootScope, stateparams, user) {
        this.$scope = $scope;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;

        this.pagename = stateparams.name;

        this.title = 'NO PAGE';
        this.html = '<h1>Missing!</h1>';

        var self = this;
        console.log('WIKI RUNNING');

        this.getData = function() {
            console.log('[WIKI] Getting wikipage');
            self.op.getObject('wikipage', null, true, {'name': self.pagename});
        }

        if (user.signedin) {
            this.getData();
        }

        this.$scope.$on('User.Login', this.getData);

        this.$scope.$on('Op.Get', function(uuid, obj, schema) {
            if (schema === 'wikipage' && obj.name == self.pagename) {
                console.log('[WIKI] Got a wikipage!');
                console.log('Wikicomponent got a wikipage!');
                self.html = obj.html;
                self.title = obj.title;
            }
        })
    }
}

wikicomponent.$inject = ['$scope', 'objectproxy', '$state', '$rootScope', '$stateParams', 'user'];

export default wikicomponent;
