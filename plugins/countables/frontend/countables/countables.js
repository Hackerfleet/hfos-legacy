'use strict';

class countablescomponent {

    constructor(objectproxy, user, $state, $scope, socket) {
        this.op = objectproxy;
        this.user = user;
        this.state = $state;
        this.scope = $scope;
        this.socket = socket;

        var self = this;

        self.words = [
            /*{word: 'Hallo', size: 1, id: '1f37637c-20b6-4073-b4a0-ae72426a5783'},
            {word: 'Another', size: 5, id: '80311540-5dc7-4dfa-9374-2c75984c7e26'},
            {word: 'Welt!', size: 3, id: 'ce9bef68-e548-4fa4-be1f-27917eb5a00c'}*/
        ];

        this.getCountables = function () {
            console.log('Getting countables')
            self.op.getList('countable', {}, ['amount'])
        };

        this.fillCountables = function (ev, schema) {
            console.log('Countable LISTUPDATE:', ev, schema);
            if (schema === 'countable') {
                var list = self.op.lists['countable'];
                var tags = [];
                var max = 0;
                for (var item of list) {
                    tags.push({word: item.name + '(' + item.amount + ')', size: item.amount, id: item.uuid});
                    max = Math.max(max, item.amount);
                }
                for (var item of tags) {
                    item.size = Math.round((item.size / max) * 10);
                    console.log(item)
                }
                self.words = tags;
            }

            //self.scope.$apply();
        };

        if (this.user.signedin === true) {
            console.log('User signed in. Getting data.');
            this.getCountables();
        } else {
            console.log('Not logged in apparently, heres this:', this.user);
        }

        $scope.$on('User.Login', this.getCountables);
        $scope.$on('OP.ListUpdate', this.fillCountables)

    }

    count(data) {
        var packet = {
            component: 'countablewatcher',
            action: 'count',
            data: data
        };

        console.log('Sending countable packet:', packet);
        this.socket.send(packet);
        this.getCountables();
    }
}

countablescomponent.$inject = ['objectproxy', 'user', '$state', '$scope', 'socket'];

export default countablescomponent;
