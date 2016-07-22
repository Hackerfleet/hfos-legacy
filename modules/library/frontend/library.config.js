import icon from './assets/iconmonstr-mediamashup-icon.svg';

export function routing($stateProvider) {

    $stateProvider
        .state('app.library', {
            url: '/library',
            template: '<library></library>',
            label: 'Library',
            icon: icon
        });
}
