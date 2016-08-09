import icon from './assets/iconmonstr-user-14-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.crew', {
            url: '/crew',
            template: '<crew></crew>',
            label: 'Crew',
            icon: icon
        });
}
