class remotecontrolcomponent {

    constructor(scope, objectproxy, $state, $rootScope, socket, user, $timeout) {
        this.scope = scope;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.socket = socket;
        this.user = user;
        this.timeout = $timeout;

        this.status = 'Initializing';

        this.controlActive = false;
        this.controlling = false;
        this.activeGamepad = 0;
        this.axes = '';
        this.status = 'Not connected';
        this.controldata = {};

        var self = this;

        function getcontroldata() {
            self.op.getList('controllable', {}, '*');
            self.op.getList('controller', {}, '*');
        }


        this.scope.$on('Profile.Update', getcontroldata);
        this.scope.$on('$destroy', function (e) {
            this.timeout.cancel(scangamepads);
        });

        if (this.user.signedin) {
            getcontroldata();
        }

        function handle_response(msg) {
            if (msg.action === 'takeControl') {
                self.controlling = msg.data === true;
                console.log('Toggled remote control to ', self.controlling);
                self.scope
            } else if ((msg.action === 'list')) {
                console.log('GRC:', msg.data);
                self.controldata = msg.data;
            } else {
                console.log('Weird message received for remotectrl: ', msg);
            }
            /*} else if (msg.component === 'camera') {
             if (msg.action === 'list') {
             console.log('Subscribing to first camera.');
             self.socket.send({'component': 'camera', 'action': 'subscribe', 'data': msg.data.Camera1});
             }
             }*/
        }


        // TODO: Move to service
        this.socket.listen('remotectrl', handle_response);

        var haveEvents = 'ongamepadconnected' in window;
        var controllers = {};
        var rAF = window.requestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.webkitRequestAnimationFrame;

        function connecthandler(e) {
            console.log('Gamepad connected: ', e.gamepad);
            addgamepad(e.gamepad);
        }

        function addgamepad(gamepad) {
            controllers[gamepad.index] = gamepad;

            var d = document.createElement('div');
            d.setAttribute('id', 'controller' + gamepad.index);

            var t = document.createElement('span');
            var lb = document.createTextNode('gamepad: ' + gamepad.id);
            t.appendChild(lb);

            d.appendChild(t);

            var b = document.createElement('div');
            b.className = 'buttons';
            for (var i = 0; i < gamepad.buttons.length; i++) {
                var e = document.createElement('span');
                e.className = 'button';
                //e.id = 'b' + i;
                e.innerHTML = i;
                b.appendChild(e);
            }

            d.appendChild(b);

            var a = document.createElement('div');
            a.className = 'axes';

            for (var j = 0; j < gamepad.axes.length; j++) {
                var p = document.createElement('progress');
                p.className = 'axis';
                //p.id = 'a' + i;
                p.setAttribute('max', '2');
                p.setAttribute('value', '1');
                p.innerHTML = j;
                a.appendChild(p);
            }

            d.appendChild(a);

            // See https://github.com/luser/gamepadtest/blob/master/index.html
            var start = document.getElementById('start');
            if (start) {
                start.style.display = 'none';
            }

            document.body.appendChild(d);
            self.status = 'Connected';
            rAF(updateStatus);
        }

        function disconnecthandler(e) {
            this.status = 'Disonnected';
            removegamepad(e.gamepad);
        }

        function removegamepad(gamepad) {
            var d = document.getElementById('controller' + gamepad.index);
            document.body.removeChild(d);
            delete controllers[gamepad.index];
        }

        function updateStatus() {
            if (!haveEvents) {
                scangamepads();
            }

            var i = 0;
            var j;

            for (j in controllers) {
                var controller = controllers[j];

                var d = document.getElementById('controller' + j);
                var buttons = d.getElementsByClassName('button');

                for (i = 0; i < controller.buttons.length; i++) {
                    var b = buttons[i];
                    var val = controller.buttons[i];
                    var pressed = val === 1.0;
                    if (typeof(val) === 'object') {
                        pressed = val.pressed;
                        val = val.value;
                    }

                    var pct = Math.round(val * 100) + '%';
                    b.style.backgroundSize = pct + ' ' + pct;

                    if (pressed) {
                        b.className = 'button pressed';
                    } else {
                        b.className = 'button';
                    }
                }

                var axes = d.getElementsByClassName('axis');
                for (i = 0; i < controller.axes.length; i++) {
                    var a = axes[i];
                    a.innerHTML = i + ': ' + controller.axes[i].toFixed(4);
                    a.setAttribute('value', controller.axes[i] + 1);
                }

                var c = document.getElementById('controllers');
                c.appendChild(d);
            }

            rAF(updateStatus);
        }

        function checkAxes(newaxes) {
            if (self.axes === '') {
                console.log('Setting up initial axes');
                return true;
            } else {
                var margin = 0.23;
                var oldaxes = self.axes;

                for (var i = 0; i < self.axes.length; i++) {
                    if ((oldaxes[i] > newaxes[i] + margin) || (oldaxes[i] < newaxes[i] - margin)) {
                        return true;
                    }
                }
                return false;
            }
        }

        function scangamepads() {
            var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
            for (var i = 0; i < gamepads.length; i++) {
                if (gamepads[i]) {
                    if (gamepads[i].index in controllers) {
                        controllers[gamepads[i].index] = gamepads[i];
                    } else {
                        addgamepad(gamepads[i]);
                    }
                }
            }
            if (self.controlling === true) {
                var newaxes = gamepads[self.activeGamepad].axes;
                if (checkAxes(newaxes) === true) {
                    console.log('Updating axes: ', newaxes);
                    self.axes = newaxes;
                    self.socket.send({'component': 'remotectrl', 'action': 'controlData', 'data': newaxes});
                }
            }
        }


        window.addEventListener('gamepadconnected', connecthandler);
        window.addEventListener('gamepaddisconnected', disconnecthandler);

        if (!haveEvents) {
            this.timeout(scangamepads, 1000);
            //setInterval(scangamepads, 1000);
            console.log('Gamepad control active');
        }

    }

    toggleControl() {
        console.log('Toggling remote control');
        if (this.controlActive === true) {
            this.socket.send({'component': 'remotectrl', 'action': 'takeControl', 'data': ''});
        } else {
            this.socket.send({'component': 'remotectrl', 'action': 'leaveControl', 'data': ''});
        }
    }
}

remotecontrolcomponent.$inject = ['$scope', 'objectproxy', '$state', '$rootScope', 'socket', 'user', '$timeout'];

export default remotecontrolcomponent;
