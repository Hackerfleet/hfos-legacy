'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:ChatCtrl
 * @description
 * # ChatCtrl
 * Controller of the hfosFrontendApp
 */

import sidebar from './chatsidebar.tpl.html';


class chatcomponent {
    constructor(chat, scope, $aside) {
        this.chat = chat;
        this.scope = scope;
        this.messages = [];
        this.input = '';
        this.messages = chat.messages;
        
        let self = this;
        this.chatsidebar = $aside({scope: this.scope, template: sidebar, backdrop: false, show: false});
        
        this.showSidebar = function (event) {
            console.log('[CHAT] Opening sidebar: ', self.chatsidebar);
            
            self.chatsidebar.$promise.then(function () {
                console.log("[CHAT] Sidebar:", self.chatsidebar);
                self.chatsidebar.show();
            });
        };
        
        this.messagewatcher = this.scope.$on('Chat.Message', function () {
            console.log('Chat controller received new message: ');
            self.messages = self.chat.messages;
        });
        
        this.scope.$on('$destroy', function () {
            console.log('[CHAT] Destroying controller');
            console.log(self.chatsidebar);
            self.messagewatcher();
            self.chatsidebar.hide();
        });
    
        console.log('Chat component started.');
        this.chat.change();
    }
    
    chatsend() {
        console.log('Transmitting current message.');
        this.chat.send(this.input);
        this.input = '';
    }
}

chatcomponent.$inject = ['chatservice', '$scope', '$aside'];

export default chatcomponent;