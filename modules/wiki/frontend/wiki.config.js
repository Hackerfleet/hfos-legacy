import icon from './assets/iconmonstr-clipboard-2.svg';

export function routing($stateProvider) {

    $stateProvider
        .state('app.wiki', {
            url: '/wiki',
            template: '<wiki></wiki>',
            label: 'Wiki',
            icon: icon
        });
}
