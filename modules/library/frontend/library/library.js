'use strict';

class librarycomponent {

    constructor(objectproxy, $state, $rootScope, socket) {
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.socket = socket;

        this.searchISBN = '';
        this.searchMeta = '';

        this.searching = false;
        this.unknown_book = false;

        let self = this;

        this.searchByISBN = function () {
            self.searching = true;

            console.log('Searching for book by ISBN:', self.searchISBN);
            self.op.search('book', {'isbn': self.searchISBN}, ['*']).then(function (msg) {
                let books = msg.data.list;
                console.log('[LIB] Received a search result:', books);
                if (msg.data.size === 0) {
                    console.log('[LIB] No results.');
                    self.unknown_book = true;
                } else {
                    console.log('[LIB] Found ', msg.data.size, ' books:', books);
                    self.books = books;
                }
            });
        };


        this.searchByMeta = function () {
            console.log('Searching for book by Metadata:', self.searchMeta);

        };
    }

    registerByISBN() {
        console.log('[LIB] Looking up new book by ISBN');
        let book = {
            uuid: 'create',
            isbn: this.searchISBN
        };
        let self = this;
        this.op.put('book', book).then(function(msg) {
            if (msg.action !== 'fail') {
                let data = msg.data;
                let packet = {
                    component: 'hfos.library.manager',
                    action: 'book_augment',
                    uuid: data.uuid
                };
                console.log('Augmenting new ISBN book:', data);
                self.socket.send(packet);
            }
        })
    }

}

librarycomponent.$inject = ['objectproxy', '$state', '$rootScope', 'socket'];

export default librarycomponent;
