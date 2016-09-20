'use strict';

class wikicomponent {
    
    constructor($scope, objectproxy, $state, $rootScope, stateparams, user, alert) {
        this.$scope = $scope;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.alert = alert;
        
        this.pagename = stateparams.name;
        this.pageuuid = "";
        
        this.title = 'No page';
        this.html = '<h1>Page not found</h1>';
        this.note = '';
        
        this.selectedtemplate = "Empty";
        
        var self = this;
        console.log('WIKI RUNNING');
        
        this.getData = function () {
            console.log('[WIKI] Getting wikipage');
            self.op.getObject('wikipage', null, true, {'name': self.pagename});
            self.op.getList('wikitemplate');
        };
        
        if (user.signedin) {
            console.log('[WIKI] Logged in, fetching page.')
            this.getData();
        }
        
        this.$scope.$on('User.Login', self.getData);
        
        this.$scope.$on('OP.List', function (ev, schema) {
            if (schema === 'wikitemplate') {
                self.templatelist = self.op.lists.wikitemplate;
                console.log('self.templatelist', self.templatelist);
            }
        });
        
        this.$scope.$on('OP.Update', function (ev, uuid, obj, schema) {
            if (schema === "wikipage" && uuid == self.pageuuid) {
                console.log('[WIKI] Page update received');
                self.updatePage(obj);
            }
        });
        
        this.updatePage = function (obj) {
            console.log('[WIKI] Rendering a wikipage!');
            self.html = obj.html;
            self.title = obj.title;
            self.pageuuid = obj.uuid;
            
            // TODO: Extend this to make it work with external links and handle link titles
            var brackets = /\[([^\]]+)]/g;
            self.html = self.html.replace(brackets, '<a href="#/wiki/$1">$1</a>');
        };
        
        this.$scope.$on('OP.Get', function (ev, uuid, obj, schema) {
            console.log('[WIKI] UUID, OBJ, SCH', uuid, obj, schema);
            if (schema === 'wikipage') {
                console.log('[WIKI] Got a wikipage: ', obj, 'looking for:', self.pagename);
                if (obj.name == self.pagename) {
                    if (obj.title.startsWith('#redirect')) {
                        console.log('[WIKI] Redirect hit, fetching new page.');
                        
                        self.note = 'Redirected from <a href="#/editor/wikipage/' +
                            self.pagename + '/edit">' +
                            self.pagename + '</a>';
                        var newslug = obj.title.split('#redirect ')[1];
                        self.pagename = newslug;
                        self.getData();
                    } else {
                        self.updatePage(obj);
                    }
                } else {
                    console.log('[WIKI] Not our page.');
                }
            } else if (schema === 'wikitemplate') {
                self.templates[obj.name] = obj;
            }
        })
    }
    
    createPage() {
        console.log('Creating empty page with name:', this.pagename, this.selectedtemplate);
        if (this.selectedtemplate == 'Empty') {
            this.state.go('app.editor', {schema: 'wikipage', action: 'create'})
        } else {
            this.alert.add('warning', 'WiP', 'Sorry, this is Work in Progress.', 2);
        }
    }
    
    editpage() {
        this.state.go('app.editor', {schema: 'wikipage', action: 'edit', uuid: this.pageuuid})
    }
}

wikicomponent.$inject = ['$scope', 'objectproxy', '$state', '$rootScope', '$stateParams', 'user', 'alert'];

export default wikicomponent;
