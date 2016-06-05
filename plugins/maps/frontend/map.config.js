import icon from './assets/iconmonstr-map-2-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.map', {
            url: '/map',
            template: '<map></map>',
            label: 'Map',
            icon: icon
        });
}
