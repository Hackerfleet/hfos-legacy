'use strict';

/**
 * @ngdoc service
 * @name hfosFrontendApp.Chat
 * @description
 * # Chat
 * Service in the hfosFrontendApp.
 */
angular.module('hfosFrontendApp')
    .service('Chat', function ($interval, socket) {
        // AngularJS will instantiate a singleton by calling "new" on this function

        var chatmessages = [];
        var blinkstate = 0;
        var blinker = false;


        socket.onMessage(function (message) {
            // Chat Handler
            var msg = JSON.parse(message.data);

            console.log(msg);

            if (msg.component === 'chat') {
                console.log('Incoming chat data: ', msg);
                chatmessages.push(msg.data);

                //if($scope.chat.open === false) {
                blinkstate = 1;
                blinker = $interval(blinkfunc, 1500, 5);
                //}
            }
        });

        var getMessages = function () {
            return chatmessages;
        };

        var send = function (msg) {
            console.log('Transmitting chat message:', msg);
            socket.send({'component': 'chat', 'action': 'say', 'data': msg});
        };

        var blinkfunc = function () {
            console.log('Blinkstate:', blinkstate);
            if (blinkstate === 0) {
                //if($scope.chat.open === true) {
                $('#btnchat').css('color', '#0f0');
                /*
                 } else {
                 $('#btnchat').css('color', '');
                 } */
                return;
            } else if (blinkstate === 1) {
                $('#btnchat').css('color', '#ff0');
                blinkstate++;
            } else if (blinkstate === 2) {
                $('#btnchat').css('color', '');
                blinkstate = 1;
            }
        };

        return {
            messages: chatmessages,
            send: send
        };
    });
