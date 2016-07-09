import icon from './assets/iconmonstr-clipboard-4-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.taskgrid', {
            url: '/taskgrid',
            template: '<taskgrid></taskgrid>',
            label: 'Taskgrid',
            icon: icon
        });
}
