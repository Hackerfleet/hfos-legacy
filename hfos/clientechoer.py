from circuits import Component

class ClientEchoer(Component):

    channel="wsserver"

    def init(self):
        pass


    def connect(self, *args):
        print("CE: Connect ")

    def read(self, *args):
        print("CE:" + str(args))

