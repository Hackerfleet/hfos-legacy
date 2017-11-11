import mapicon from './assets/iconmonstr-map-view-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.map', {
            url: '/map',
            template: '<map></map>',
            label: 'Map',
            icon: mapicon
        });
}
