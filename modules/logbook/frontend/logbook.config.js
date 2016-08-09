import icon from './assets/iconmonstr-book-2-log.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.logbook', {
            url: '/logbook',
            template: '<logbook></logbook>',
            label: 'Logbook',
            icon: icon
        });
}
