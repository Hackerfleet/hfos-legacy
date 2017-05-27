'use strict';

class librarycomponent {

    constructor(objectproxy, $state, $rootScope) {
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.searchISBN = '';
        this.searchMeta = '';

        this.searching = false;

        let self = this;

        this.searchByISBN = function () {
            self.searching = true;

            console.log('Searching for book by ISBN:', self.searchISBN);
            self.op.getList('book', {'isbn': self.searchISBN}, ['*']);
        };


        this.searchByMeta = function () {
            console.log('Searching for book by Metadata:', self.searchMeta);

        };
    }
}

librarycomponent.$inject = ['objectproxy', '$state', '$rootScope'];

export default librarycomponent;
