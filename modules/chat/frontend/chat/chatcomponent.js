'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:ChatCtrl
 * @description
 * # ChatCtrl
 * Controller of the hfosFrontendApp
 */

class chatcomponent {
    constructor(chat, scope) {
        this.chat = chat;
        this.scope = scope;
        this.messages = [];
        this.input = '';
        this.messages = chat.messages;

        var self = this;

        this.scope.$on('Chat.Message', function () {
            console.log('Chat controller received new message: ');
            self.messages = self.chat.messages;
        });
        console.log('Chat component started.');
    };

    chatsend() {
        console.log('Transmitting current message.');
        this.chat.send(this.input);
        this.input = '';
    }
}

chatcomponent.$inject = ['chatservice', '$scope'];

export default chatcomponent;