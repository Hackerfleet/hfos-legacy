import icon from './assets/iconmonstr-drop-29.svg';

export function routing($stateProvider) {

    $stateProvider
        .state('app.garden', {
            url: '/garden',
            template: '<garden></garden>',
            label: 'Garden',
            icon: icon
        });
}
