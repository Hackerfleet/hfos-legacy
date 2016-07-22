/**
 * Created by riot on 14.05.16.
 */

const widgettypes = ['digitalreadout', 'simplebarreadout'];

const widgettemplates = {};

for (var item of widgettypes) {
    widgettemplates[item] = require('../templates/' + item + '.tpl.html');
}

console.log('[NGDC] Dynamic widgets:', widgettemplates);

var ngDynamicController = function ($compile, $http, $parse) {
    console.log('[NGDC] Init.');
    return {
        restrict: 'A',
        transclude: true,
        terminal: true,
        priority: 100000,
        link: function (scope, elem, attrs) {
            console.log('[NGDC] SCOPE:', scope, attrs, elem);
            var ctrl = $parse(elem.attr('ng-dynamic-controller'))(scope);
            var valuetype = $parse(elem.attr('valuetype'))(scope);
            scope.valuetype = valuetype;
            console.log('[NGDC] Link creating to:', ctrl, valuetype);
            elem.removeAttr('ng-dynamic-controller');
            //elem.attr('ng-controller', ctrl);
            console.log('[NGDC] Appending template:', widgettemplates[ctrl]);
            elem.append(widgettemplates[ctrl]);
            $compile(elem)(scope);
            console.log('[NGDC] Done');
        }
    };
    /*
    console.log('[NGDC] Init.');
    return {
        scope: {
            name: '=ngDynamicController',
            valuetype: '='
        },
        restrict: 'A',
        transclude: true,
        terminal: true,
        priority: 100000,
        link: function (scope, elem, attrs) {
            console.log('[NGDC] SCOPE:', scope, scope.name, attrs);
            //var name = $parse(elem.attr('ng-dynamic-controller'))(scope);
            console.log('[NGDC] Link creating to:', scope.name);
            elem.removeAttr('ng-dynamic-controller');
            elem.attr('ng-controller', scope.name);
            console.log('[NGDC] Appending template:', widgettemplates[scope.name]);
            elem.append(widgettemplates[scope.name]);
            $compile(elem)(scope);
            console.log('[NGDC] Done');
        }
    };
    */
};

ngDynamicController.$inject = ['$compile', '$http', '$parse'];

export default ngDynamicController;