import icon from './assets/iconmonstr-info-8.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.notifications', {
            url: '/notifications',
            template: '<notifications></notifications>',
            label: 'Notifications',
            icon: icon
        });
}
