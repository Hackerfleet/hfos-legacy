'use strict';

class wikicomponent {

    constructor(objectproxy, $state, $rootScope) {
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;

        this.title = 'NO PAGE';
        this.html = '<h1>Missing!</h1>';
    }
}

wikicomponent.$inject = ['objectproxy', '$state', '$rootScope'];

export default wikicomponent;
