'use strict';

class importercomponent {
    
    constructor(scope, objectproxy, $state, $rootScope, socket, user, schemata, menu, alert, clipboard) {
        this.scope = scope;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.socket = socket;
        this.user = user;
        this.schemata = schemata;
        this.menu = menu;
        this.alert = alert;
        this.clipboard = clipboard;
        
        this.scope.$on('Profile.Update', function () {
            console.log('Profile update - fetching map data');
        });
    
        if (this.user.signedin === true) {
            console.log('Logged in - fetching map data');
        }
    
    }
    upload() {
        console.log('Uploading new map file.');
        
        var file = document.getElementById('filename').files[0];
        console.log('file: ', file);
        this.socket.sendFile(file, 'mapimport', 'upload');
        
    }
    
    rescan() {
        console.log('Triggering rastertile path rescan.');
    
        this.socket.send({
            component: 'maprescan',
            action:'rescan'
        });
    
    }
}

importercomponent.$inject = ['$scope', 'objectproxy', '$state', '$rootScope', 'socket', 'user', 'schemata', 'menu', 'alert', 'clipboard'];

export default importercomponent;
