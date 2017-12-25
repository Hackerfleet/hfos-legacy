import icon from './assets/iconmonstr-id-card-22.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.contact', {
            url: '/contact',
            template: '<contact></contact>',
            label: 'Contacts',
            icon: icon
        });
}
