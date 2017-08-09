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

/**
 * Created by riot on 03.05.16.
 */

class CalcConfigCtrl {

    constructor(rootscope, user, objectproxy) {
        this.rootscope = rootscope;
        this.objectproxy = objectproxy;
        this.user = user;
    
        let self = this;
        console.log('CalcConfigController init');
    
        this.update_list = function(msg) {
            console.log('[CALCCONFIG] List update:', msg);
        
            self.calclist = self.objectproxy.lists.calcconfig;
        };
        
        this.objectproxy.searchItems('calcconfig', {
            '$or': [
                {'useruuid': user.user.uuid},
                {'shared': true}]
        }, ['name', 'description']).then(self.updateList);


        this.rootscope.$on('OP.ListUpdate', function (ev, schema) {
            if (schema === 'she'
        });
    }

    selectCalc(uuid) {
        console.log('[CALCCONFIG] Updating calc selection');
        let origconf = this.user.clientconfig;
        console.log(origconf);
        origconf.calcuuid = uuid;
        this.user.updateclientconfig(origconf);
    }
}

CalcConfigCtrl.$inject = ['$rootScope', 'user', 'objectproxy'];

export default CalcConfigCtrl;
