'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:ChatCtrl
 * @description
 * # ChatCtrl
 * Controller of the hfosFrontendApp
 */

class ChatComponent {
    constructor(Chat) {

        this.messages = [];
        this.input = '';
        this.messages = Chat.messages;

        var self = this;

        this.$watch('Chat.messages', function (newVal, oldVal) {
            console.log('Chat controller received new message: ', newVal);
            if (newVal) {
                self.messages = newVal;
            }
        });

    }

    chatsend() {
        console.log('Transmitting current message.');
        Chat.send(this.input);
        this.input = '';
    }

}
