/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2017 riot <riot@c-base.org> and others.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

'use strict';

class automatcompare_int {
    constructor($scope) {
        this.scope = $scope;
        /*this.value = this.scope.$parent.value;
        this.function = this.scope.$parent.function;*/
        console.log('[AT-CI] compare_int loaded, controller scope:', this, $scope);
        this.argument = $scope.$parent.argument;
        this.function = $scope.$parent.function;
        
        console.log('[AT-CI] Scope:', $scope);

        var self = this;
    }
    
    update() {
        console.log('[AT-CI] Changed values:', this.argument, this.function, this.scope);
        this.scope.$parent.argument = this.argument;
        this.scope.$parent.function = this.function;
    }
}

automatcompare_int.$inject = ['$scope', 'socket', '$interval'];

export default automatcompare_int;
