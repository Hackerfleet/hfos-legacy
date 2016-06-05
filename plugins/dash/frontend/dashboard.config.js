import icon from './assets/iconmonstr-compass-6-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.dashboard', {
            url: '/dashboard',
            template: '<dashboard></dashboard>',
            label: 'Dashboard',
            icon: icon
        });
}
