/**
 * Created by riot on 14.05.16.
 */

const widgettypes = ['digitalreadout'];

const widgettemplates = {};

for (var item of widgettypes) {
    widgettemplates[item] = require('../templates/' + item + '.tpl.html');
}

console.log(widgettemplates);

class ngDynamicController {
    constructor($compile, $http) {
        this.scope = {
            widgettype: '=ngDynamicController',
            valuetype: '='
        };
        this.restrict = 'A';
        this.transclude = true;
//            terminal: true,
//            priority: 100000,
        this.link = function (scope, elem, attrs) {
            console.log('[NGDC] SCOPE:', scope, attrs);
            elem.attr('ng-controller', scope.widgettype);
            elem.removeAttr('ng-dynamic-controller');

            $http.get('/views/cards/' + scope.widgettype + '.tpl.html')
                .then(function (response) {
                    console.log('[NGDC] Html Response:', response.data);
                    elem.append(response.data);
                    $compile(elem)(scope);
                });
        };
    }
}

ngDynamicController.$inject = ['$compile', '$http'];

export default ngDynamicController;