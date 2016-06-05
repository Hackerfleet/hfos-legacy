import icon from './assets/iconmonstr-speech-bubble-26.svg';


export function routing($stateProvider) {

    $stateProvider
        .state('app.chat', {
            url: '/chat',
            template: '<chat></chat>',
            label: 'Chat',
            icon: icon
        });
}
