import icon from './assets/iconmonstr-share-6.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.shareables', {
            url: '/shareables',
            template: '<shareables></shareables>',
            label: 'Shareables',
            icon: icon
        });
}
