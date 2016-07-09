"""

Configurable Component
======================

Contains
--------

Systemwide configurable component definition. Stores configuration either in database or as json files.
Enables editing of configuration through frontend.

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.component import ComponentBaseConfigSchema
from hfos.logger import hfoslog, warn, critical, error, debug, verbose

from circuits import Component
from jsonschema import ValidationError
from warmongo import model_factory

from random import randint

from uuid import uuid4

from copy import deepcopy
import inspect
from sys import exc_info

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


from pprint import pprint

class ConfigurableComponent(Component):
    names = []
    configprops = {}

    def __init__(self, uniquename=None, *args, **kwargs):


        super(ConfigurableComponent, self).__init__(*args, **kwargs)



        self.uniquename = ""

        if uniquename:
            if uniquename not in self.names:
                self.uniquename = uniquename
                self.names.append(uniquename)
            else:
                hfoslog("Unique component added twice: ", uniquename, lvl=critical)
        else:
            while True:
                uniquename = "%s%s" % (self.name, randint(0, 32768))
                if uniquename not in self.names:
                    self.uniquename = uniquename
                    self.names.append(uniquename)

                    break

        ## self.configform = deepcopy(ComponentConfigForm)
        self.configschema = deepcopy(ComponentBaseConfigSchema)

        configprops = self.configprops
        #configprops['default'] = {}

        self.configschema['schema']['properties'].update(self.configprops)

        #self.configschema['schema']['properties']['settings'] = {
        #    'type': 'object',
        #    'id': '#client',
        #    'name': self.uniquename,
        #    'properties': self.configprops,
        #    'default': {}
        #}
        #self.log("[UNIQUECOMPONENT] Config Schema: ", self.configschema,
        #         lvl=critical)
        #pprint(self.configschema)

        #self.configschema['name'] = self.uniquename
        #self.configschema['id'] = "#" + self.uniquename

        #schemastore[self.uniquename] = {'schema': self.configschema, 'form': self.configform}

        self.componentmodel = model_factory(self.configschema['schema'])
        #self.log("Component model: ", lvl=critical)
        #pprint(self.componentmodel._schema)


        self._readConfig()
        if not self.config:
            self.log("Creating initial default configuration.")
            try:
                self._setConfig()
                self._writeConfig()
            except ValidationError as e:
                self.log("Error during configuration reading: ", e, type(e), exc=True)

    def unregister(self):
        self.names.remove(self.uniquename)
        super(ConfigurableComponent, self).unregister()

    def _readConfig(self):
        self.config = self.componentmodel.find_one({'name': self.uniquename})
        if self.config:
            self.log("Configuration read.", lvl=debug)
        else:
            self.log("No configuration found.", lvl=warn)
        #self.log(self.config)

    def _writeConfig(self):
        if not self.config:
            self.log("Unable to write non existing configuration", lvl=error)
            return

        try:
            self.config.validate()
            self.config.save()
            self.log("Configuration stored.")
        except ValidationError as e:
            self.log("Not storing invalid configuration: ", e, type(e), exc=True, lvl=error)

    def _setConfig(self, config={}):
        try:
            #pprint(self.configschema)
            self.config = self.componentmodel(config)
            #self.log("Config schema:", lvl=critical)
            #pprint(self.config.__dict__)

            #pprint(self.config._fields)

            try:
                name = self.config.name
            except Exception as e:
                self.log("Has no name.", lvl=verbose)

            try:
                self.config.name = self.uniquename
            except Exception as e:
                self.log("Cannot set component name for configuration: ", e, type(e), self.name, exc=True, lvl=critical)

            try:
                uuid = self.config.uuid
            except:
                self.log("Has no UUID", lvl=verbose)
                self.config.uuid = str(uuid4())

            try:
                notes = self.config.notes
            except:
                self.log("Has no notes", lvl=verbose)

                notes = self.__doc__.lstrip().rstrip()
                if not notes:
                    notes = "No notes."
                self.log(notes)
                self.config.notes = notes

            try:
                componentclass = self.config.componentclass
            except:
                self.log("Has no component class", lvl=verbose)
                self.config.componentclass = self.name

        except ValidationError as e:
            self.log("Not setting invalid component configuration: ", e, type(e), exc=True, lvl=error)

        self.log("Fields:", self.config._fields, lvl=verbose)

    def log(self, *args, **kwargs):
        func = inspect.currentframe().f_back.f_code
        # Dump the message + the name of this function to the log.

        if 'exc' in kwargs and kwargs['exc'] == True:
            exc_type, exc_obj, exc_tb = exc_info()
            line_no = exc_tb.tb_lineno
        else:
            line_no = func.co_firstlineno

        sourceloc = "[%.10s@%s:%i]" % (
            func.co_name,
            func.co_filename,
            line_no
        )
        hfoslog(sourceloc=sourceloc, emitter=self.uniquename, *args, **kwargs)


class ExampleComponent(ConfigurableComponent):
    configprops = {
        'setting': {'type': 'string', 'title': 'Some Setting',
                    'description': 'Some string setting.', 'default': 'Yay'},
    }

    def __init__(self, *args, **kwargs):

        super(ExampleComponent, self).__init__("EXAMPLE", *args, **kwargs)

        self.log("Example component started.")
        #self.log(self.config)
