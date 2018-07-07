import icon from './assets/nodestate-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.nodestate', {
            url: '/nodestate',
            template: '<nodestate></nodestate>',
            label: 'Nodestate',
            icon: icon
        });
}
