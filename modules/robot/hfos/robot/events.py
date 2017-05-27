from circuits import Event


class machineroom_event(Event):
    """

    :param value:
    :param args:
    """

    def __init__(self, value, *args):
        super(machineroom_event, self).__init__(*args)
        self.controlvalue = value


class machine(machineroom_event):
    """Skipper wants us to change the engine speed/direction"""


class pump(machineroom_event):
    """Skipper wants us to turn on/off the coolant pump"""


class rudder(machineroom_event):
    """Skipper wants us to change the rudder angle"""


class control_update(Event):
    """A client wants to remote control a servo"""

    def __init__(self, controldata, *args):
        super(control_update, self).__init__(*args)
        self.controldata = controldata
