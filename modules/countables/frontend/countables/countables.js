'use strict';

class countablescomponent {

    constructor(objectproxy, user, $state, $scope, socket) {
        this.op = objectproxy;
        this.user = user;
        this.state = $state;
        this.scope = $scope;
        this.socket = socket;

        let self = this;

        self.words = [
            /*{word: 'Hallo', size: 1, id: '1f37637c-20b6-4073-b4a0-ae72426a5783'},
            {word: 'Another', size: 5, id: '80311540-5dc7-4dfa-9374-2c75984c7e26'},
            {word: 'Welt!', size: 3, id: 'ce9bef68-e548-4fa4-be1f-27917eb5a00c'}*/
        ];
        
        this.getCountables = function () {
            self.op.searchItems('countable', '', ['amount']).then(function(result){
                let tags = [];
                let max = 0;
                let item=null;
                for (item of result.data) {
                    tags.push({name: item.name + '(' + item.amount + ')', size: item.amount, uuid: item.uuid});
                    max = Math.max(max, item.amount);
                }
                for (item of tags) {
                    item.size = Math.max(8, Math.round((item.size / max) * 42));
                    console.log(item)
                }
                self.words = tags;
            });
                
            //self.scope.$apply();
        };

        if (this.user.signedin === true) {
            console.log('User signed in. Getting data.');
            this.getCountables();
        } else {
            console.log('Not logged in apparently, heres this:', this.user);
        }

        $scope.$on('User.Login', this.getCountables);
    }

    count(uuid) {
        let packet = {
            component: 'hfos.countables.counter',
            action: 'increment',
            data: uuid
        };

        console.log('Sending countable packet:', packet);
        this.socket.send(packet);
        this.getCountables();
    }
}

countablescomponent.$inject = ['objectproxy', 'user', '$state', '$scope', 'socket'];

export default countablescomponent;
