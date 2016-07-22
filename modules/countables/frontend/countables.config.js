import icon from './assets/iconmonstr-cursor-31.svg';

export function routing($stateProvider) {

    $stateProvider
        .state('app.countables', {
            url: '/countables',
            template: '<countables></countables>',
            label: 'Countables',
            icon: icon
        });
}
