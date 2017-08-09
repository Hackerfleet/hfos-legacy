'use strict';

/**
 * @ngdoc service
 * @name hfosFrontendApp.chatservice
 * @description
 * # chatservice
 * Service in the hfosFrontendApp.
 */

class chatservice {
    
    constructor(user, interval, socket, rootscope, $timeout, objectproxy) {
        this.user = user;
        this.interval = interval;
        this.socket = socket;
        this.rootscope = rootscope;
        this.op = objectproxy;
        
        this.messages = {};
        this.channels = {};
        this.unjoined = {};
        this.unread = {};
        
        this.users = {};
        
        this.channel = '';
        
        this.joined_channels = [];
        
        this.blinkstate = 0;
        this.blinker = false;
        this.message_count = 0;
        
        let self = this;
        
        this.blinkfunc = function () {
            let state = self.blinkstate;
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
        
        socket.listen('hfos.chat.host', function (msg) {
            if (msg.action === 'say') {
                console.log('Incoming chat data: ', msg);
                let chat_message = msg.data;
                if (typeof self.messages[chat_message.recipient] === 'undefined') {
                    self.messages[chat_message.recipient] = {};
                }
                
                self.messages[chat_message.recipient][chat_message.timestamp] = chat_message;
                
                self.rootscope.$broadcast('Chat.Message');
                
                if (self.channel !== chat_message.recipient) {
                    self.blinkstate = 1;
                    self.blinker = self.interval(self.blinkfunc, 1500, 5);
                }
            } else if (msg.action === 'join') {
                console.log('[CHAT] Joined a channel:', msg.data);
                self.channel = msg.data;
                self.joined_channels.push(msg.data);
                self.sort_channels();
                self.change(msg.data);
            } else if (msg.action === 'history') {
                console.log('[CHAT] Got a history update', msg.data);
                let channel = msg.data.channel;
                if (typeof self.messages[channel] === 'undefined') {
                    self.messages[channel] = {};
                }
                for (let message of msg.data.history) {
                    self.messages[channel][message.timestamp] = message;
                }
            } else if (msg.action === 'status') {
                console.log('[CHAT] Got a status update', msg.data);
                
                self.joined_channels = msg.data.joined;
                self.unread = msg.data.unread;
                
                self.message_count = 0;
                for (let channel of Object.keys(self.unread)) {
                    self.message_count += self.unread[channel];
                }
                
                self.sort_channels();
            }
        });
        
        this.sort_channels = function () {
            console.log('[CHAT] Sorting channels', self.channels, self.joined_channels);
            self.joined = {};
            self.unjoined = {};
            if (Object.keys(self.channels).length === 0) {
                console.log('[CHAT] No channellist yet.');
                return
            }
            for (let uuid of Object.keys(self.channels)) {
                console.log('[CHAT] UUID:', uuid);
                
                let channel = self.channels[uuid];
                console.log('[CHAT] Channel:', channel);
                console.log('[CHAT] UUID indexof:', self.joined_channels.indexOf(uuid), uuid);
                if (self.joined_channels.indexOf(uuid) >= 0) {
                    console.log('[CHAT] Joined channel:', channel.name);
                    self.joined[uuid] = channel;
                } else {
                    console.log('[CHAT] Unjoined channel:', channel.name);
                    self.unjoined[uuid] = channel;
                }
            }
        };
        
        this.request_channels = function () {
            console.log('[CHAT] Getting channels');
            self.op.searchItems('chatchannel', '*', '*').then(function (msg) {
                for (let channel of msg.data) {
                    self.channels[channel.uuid] = channel;
                }
                self.sort_channels();
                console.log('[CHAT] Channels:', self.channels, self.joined, self.unjoined);
            })
        };
        
        this.request_profiles = function () {
            console.log('[CHAT] Getting current users ', self.channels[self.channel]);
            let filter = {
                    'owner': {'$in': self.channels[self.channel].users}
                },
                fields = ['owner', 'name', 'userdata'];
            console.log('[CHAT] Looking for users:', filter);
            self.op.searchItems('profile', filter, fields).then(function (msg) {
                self.users[self.channel] = {};
                console.log('[CHAT] Got user profiles:', msg.data);
                
                for (let profile of msg.data) {
                    console.log('PROFILE:', profile);
                    let user = {
                        profile: profile
                    };
                    if (profile.userdata !== null) {
                        if (profile.userdata.nick !== null) {
                            user.name = profile.userdata.nick;
                        } else if (profile.userdata.name !== null || profile.userdata.familyname !== null) {
                            user.name = profile.userdata.name + ' ' + profile.userdata.familyname;
                        }
    
                        self.users[self.channel][profile.owner] = user;
                    } else {
                        self.op.get('user', profile.owner).then(function (account) {
                            console.log('[CHAT] Got name from account:', account);
                            user.name = account.name;
                            self.users[self.channel][profile.owner] = user;
                        })
                    }
                }
                console.log('[CHAT] Userlist populated:', self.users[self.channel]);
            })
        };
        
        this.logonwatcher = this.rootscope.$on('User.Login', function () {
            self.request_channels();
        });
        
        if (this.user.signedin) {
            self.request_channels();
        }
        
        console.log('[CHAT] CHAT LOADED');
    }
    
    join(channel) {
        console.log('[CHAT] Joining channel ', channel);
        this.socket.send({component: 'hfos.chat.host', action: 'join', data: channel});
    }
    
    get_history() {
        console.log('[CHAT] Requesting history');
        let timestamp = new Date() / 1000;
        console.log(this.messages[this.channel]);
        if (typeof this.messages[this.channel] !== 'undefined') {
            console.log('[CHAT] There are old messages in the list:', this.messages[this.channel]);
            timestamp = Math.min.apply(Math, Object.keys(this.messages[this.channel]));
        }
        
        console.log('[CHAT] Earliest timestamp is:', timestamp);
        let packet = {
            component: 'hfos.chat.host',
            action: 'history',
            data: {
                end: timestamp,
                limit: 20,
                channel: this.channel
            }
        };
        this.socket.send(packet);
    }
    
    change(channel) {
        if (typeof channel === 'undefined') {
            // TODO: Remember last channel and restore that
            channel = Object.keys(this.channels)[0];
        }
        console.log('[CHAT] Changing to channel ', channel);
        this.channel = channel;
        let packet = {
            component: 'hfos.chat.host',
            action: 'change',
            data: channel
        };
        this.request_profiles();
        this.socket.send(packet);
        
        if (typeof this.messages[channel] === 'undefined' || this.messages[channel].length === 0) {
            this.get_history();
        }
    }
    
    getMessages(channel) {
        return this.messages[channel];
    }
    
    send(msg) {
        console.log('Transmitting chat message:', msg);
        let packet = {
            component: 'hfos.chat.host',
            action: 'say',
            data: {
                recipient: this.channel,
                content: msg
            }
        };
        this.socket.send(packet);
    }
    
}

chatservice.$inject = ['user', '$interval', 'socket', '$rootScope', '$timeout', 'objectproxy'];

export default chatservice;
