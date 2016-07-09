'use strict';

/**
 * @ngdoc service
 * @name hfosFrontendApp.chatservice
 * @description
 * # chatservice
 * Service in the hfosFrontendApp.
 */

class chatservice {
    
    constructor(interval, socket, rootscope) {
        this.interval = interval;
        this.socket = socket;
        this.rootscope = rootscope;
        
        this.messages = [];
        this.blinkstate = 0;
        this.blinker = false;

        var self = this;
    
        this.blinkfunc = function() {
            var state = self.blinkstate;
            console.log('Blinkstate:', state);
        
            if (state === 0) {
                //if($scope.chat.open === true) {
                $('#btnchat').css('color', '#0f0');
                /*
                 } else {
                 $('#btnchat').css('color', '');
                 } */
                return;
            } else if (state === 1) {
                $('#btnchat').css('color', '#ff0');
                self.blinkstate++;
            } else if (state === 2) {
                $('#btnchat').css('color', '');
                self.blinkstate = 1;
            }
        };
        
        socket.listen('chat', function (msg) {
            console.log('Incoming chat data: ', msg);
            self.messages.push(msg.data);
            self.rootscope.$broadcast('Chat.Message');

            //if($scope.chat.open === false) {
            self.blinkstate = 1;
            self.blinker = self.interval(self.blinkfunc, 1500, 5);
            //}
        });
    }
    
    getMessages() {
        return this.messages;
    }
    
    send(msg) {
        console.log('Transmitting chat message:', msg);
        this.socket.send({'component': 'chat', 'action': 'say', 'data': msg});
    }
    

}

chatservice.$inject = ['$interval', 'socket', '$rootScope'];

export default chatservice;