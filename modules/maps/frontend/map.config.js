import mapicon from './assets/iconmonstr-map-view-icon.svg';
import importicon from './assets/iconmonstr-map-import-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.map', {
            url: '/map',
            template: '<map></map>',
            label: 'Map',
            icon: mapicon
        })
        .state('app.mapimport', {
            url: '/mapimport',
            template: '<mapimport></mapimport>',
            label: 'Map Import',
            icon: importicon
        });
}
