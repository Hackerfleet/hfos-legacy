import icon from './assets/iconmonstr-compass-6-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.nodestate', {
            url: '/nodestate',
            template: '<nodestate></nodestate>',
            label: 'Nodestate',
            icon: icon
        });
}
