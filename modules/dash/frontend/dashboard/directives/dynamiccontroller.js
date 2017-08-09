/**
 * Created by riot on 14.05.16.
 */

const widgettypes = ['digitalreadout', 'simplebarreadout', 'historybarreadout', 'simplecompass', 'linechart'];

const widgettemplates = {};

for (let item of widgettypes) {
    widgettemplates[item] = require('../templates/' + item + '.tpl.html');
}

console.log('[NGDC] Dynamic widgets:', widgettemplates);

let ngDynamicController = function ($compile, $http, $parse) {
    console.log('[NGDC] Init.');
    return {
        restrict: 'A',
        transclude: true,
        terminal: true,
        priority: 100000,
        link: function (scope, elem, attrs) {
            console.log('[NGDC] SCOPE:', scope, attrs, elem);
            let ctrl = $parse(elem.attr('ng-dynamic-controller'))(scope),
                valuetype = $parse(elem.attr('valuetype'))(scope);
            scope.valuetype = valuetype;
            console.log('[NGDC] Link creating to:', ctrl, valuetype);
            elem.removeAttr('ng-dynamic-controller');
            //elem.attr('ng-controller', ctrl);
            console.log('[NGDC] Appending template:', widgettemplates[ctrl]);
            elem.append(widgettemplates[ctrl]);
            $compile(elem)(scope);

            scope.$watch(
                function () {
                    return [scope.gridsterItem.sizeX, scope.gridsterItem.sizeY].join('x');
                },
                function (value) {
                    let split = value.split('x');
                    split[0] = split[0] * scope.gridster.colWidth - 15;
                    split[1] = split[1] * scope.gridster.rowHeight - 50;
                    console.log('directive got resized:', split);
                    scope.$broadcast('resize', split);
                    scope.width = split[0];
                    scope.height = split[1];
                }
            );
            scope.width = scope.gridsterItem.sizeX * scope.gridster.colWidth - 15;
            scope.height = scope.gridsterItem.sizeY * scope.gridster.rowHeight - 50;
    
            console.log('SCOPE:', scope);

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
            //let name = $parse(elem.attr('ng-dynamic-controller'))(scope);
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