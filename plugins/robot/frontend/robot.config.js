import icon from './assets/iconmonstr-gamepad-2-icon.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.remotecontrol', {
            url: '/remotecontrol',
            template: '<remotecontrol></remotecontrol>',
            label: 'Remote Control',
            icon: icon
        });
}
