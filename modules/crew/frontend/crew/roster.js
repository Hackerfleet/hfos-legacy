'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:CrewCtrl
 * @description
 * # CrewCtrl
 * Controller of the hfosFrontendApp
 */
class Crew {
    
    constructor(scope, rootscope, $modal, navdata, user, objectproxy, socket, menu) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
        
        this.usermenu = {};
        this.fieldnames = ['name', 'fullname', 'location', 'text', 'image'];
        
        let self = this;
        
        this.requestusers = function () {
            console.log('[CREW] Login successful - fetching user data');
            this.op.searchItems('user', '*', ['name', 'description']).then(function (users) {
                console.log("[CREW] Users: ", users);
                for (let user of users.data) {
                    let user_entry = {
                        name: user.name,
                        uuid: user.uuid,
                        dropdown: false
                    };
                    self.op.searchItems('profile', {owner: user.uuid}, '*').then(function (data) {
                        let profile = data.data[0];
                        console.log('[CREW] Profile:', profile);
                        if (typeof profile !== 'undefined') {
                            user_entry.fullname = profile.userdata.name + ' ' + profile.userdata.familyname;
                            user_entry.location = profile.userdata.location;
                            user_entry.text = profile.userdata.notes;
                            user_entry.image = profile.userdata.image;
                        } else {
                            user_entry.text = 'No profile';
                        }
                    });
                    self.usermenu[user.uuid] = user_entry;
                }
            });
        };
        
        self.socket.listen('hfos.auth.login', self.handleNavdata);
        
        this.loginupdate = this.rootscope.$on('User.Login', function () {
            self.requestusers();
        });
        
        if (this.user.signedin === true) {
            self.requestusers();
        }
        
        
        self.scope.$on('$destroy', function () {
        });
    }
}

Crew.$inject = ['$scope', '$rootScope', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu'];

export default Crew;