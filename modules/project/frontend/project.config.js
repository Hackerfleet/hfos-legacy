import taskgridicon from './assets/iconmonstr-clipboard-4.svg';
import todoicon from './assets/iconmonstr-clipboard-6.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.taskgrid-non-url', {
            url: '/taskgrid',
            template: '<taskgrid></taskgrid>',
            label: 'Taskgrid',
            icon: taskgridicon
        })
        .state('app.taskgrid', {
            url: '/taskgrid/{taskgrid}/{projects}/{tags}',
            template: '<taskgrid></taskgrid>',
        })
        .state('app.todo', {
            url: '/todo',
            template: '<todo></todo>',
            label: 'Todo',
            icon: todoicon
        });
}
