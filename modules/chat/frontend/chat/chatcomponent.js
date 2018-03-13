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
    constructor(chat, user, rootscope, scope, $aside) {
        this.chat = chat;
        this.user = user;
        this.rootscope = rootscope;
        this.scope = scope;
        this.messages = [];
        this.input = '';
        this.messages = chat.messages;

        this.send_history = {};
        this.send_history_counter = 0;

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
    }

    keyup($event) {
        console.log('KEYCODE', $event.keyCode);
        if ($event.keyCode === 13 && !$event.shiftKey) {
            this.chatsend()
        }
        else if ($event.keyCode === 38 || $event.keyCode === 40) {
            if ($event.keyCode === 38) {
                this.send_history_counter--;
            }
            if ($event.keyCode === 40) {
                this.send_history_counter++;
            }

            this.send_history_counter = Math.min(this.send_history[this.chat.channel].length, this.send_history_counter);
            this.send_history_counter = Math.max(0, this.send_history_counter);

            if (this.send_history[this.chat.channel].indexOf(this.input) < 0) {
                this.save_history(this.input);
            }
            this.input = this.send_history[this.send_history_counter];
            console.log('HISTORY:', this.send_history_counter);
        }

    }

    save_history(msg) {
        if (typeof this.send_history[this.chat.channel] === 'undefined') {
            this.send_history[this.chat.channel] = [msg];
        }
        this.send_history[this.chat.channel].push(msg);
    }

    chatsend() {
        console.log('Transmitting current message.');
        this.send_history_counter++;
        this.save_history(this.input);

        this.chat.send(this.input);
        this.input = '';
    }
}

chatcomponent.$inject = ['chatservice', 'user', '$rootScope', '$scope', '$aside'];

export default chatcomponent;
