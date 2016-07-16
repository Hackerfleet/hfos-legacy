import urwid
from subprocess import Popen, PIPE
import sys
from pprint import pprint
from tempfile import mktemp

# TODO:
# * Add installation location / venv info somewhere (permanent)
# * Redirect install log for archival and review purposes
# * Provisions
# * Migrations?
# * Dependencies?!

Plugins = {
    'alert': True,
    'camera': False,
    'chat': False,
    'comms': False,
    'dash': False,
    'ldap': False,
    'library': False,
    'maps': False,
    'navdata': False,
    'nmea': False,
    'project': False,
    'robot': False,
    'shareables': False,
    'wiki': False
}

palette = [
    ('title', 'light cyan', 'dark blue'),
    ('banner', 'black', 'light gray'),
    ('streak', 'black', 'light cyan'),
    ('button normal', 'light gray', 'dark blue', 'standout'),
    ('button select', 'white', 'dark green'),
    ('list normal', 'light cyan', 'dark blue', 'standout'),
    ('list select', 'white', 'dark blue'),
    ('bg', 'black', 'dark blue'),
]

blank = urwid.Divider()


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


class PluginSelector(urwid.ListBox):
    def __init__(self):
        self.populate()
        urwid.ListBox.__init__(self, self.SFLW)

    def populate(self):
        options = []
        for item in sorted(Plugins.keys()):
            state = Plugins[item]
            option = urwid.CheckBox(item, state,
                                    on_state_change=self.stateChange)
            options.append(option)

        self.SFLW = urwid.SimpleFocusListWalker(options)
        self.body = self.SFLW
        self._invalidate()

    def stateChange(self, option, state):
        # footer.set_text(('banner', u"HELLO!!! %s %s " % (
        # option._label.text, state)))
        Plugins[option._label.text] = state


class Installer(urwid.Frame):
    def __init__(self):
        self.header = urwid.Text(('title', u" HFOS Plugins "), align='center')
        self.headermap = urwid.AttrMap(self.header, 'streak')
        self.footer = urwid.Text(('banner', u" Select plugins to install! "),
                                 align='center')
        self.footermap = urwid.AttrWrap(self.footer, 'streak')

        self.allbutton = urwid.Button(u"Select All", self.onAllButton)
        self.nonebutton = urwid.Button(u"Select None", self.onNoneButton)

        self.okbutton = urwid.Button(u"Ok", self.onOkButton)
        self.exitbutton = urwid.Button(u"Cancel", self.onCancelButton)

        self.radiogroup = []
        self.developrbutton = urwid.RadioButton(self.radiogroup, 'Develop')
        self.installrbutton = urwid.RadioButton(self.radiogroup, 'Install')

        self.modepile = urwid.Pile([self.developrbutton, self.installrbutton])

        self.buttons = [
            blank,
            self.allbutton,
            self.nonebutton,
            blank,
            self.modepile,
            blank,
            self.okbutton,
            self.exitbutton
        ]

        self.wraps = []
        for button in self.buttons:
            self.wraps.append(
                urwid.AttrWrap(button, 'button normal', 'button select'))

        self.buttonlb = urwid.ListBox(urwid.SimpleListWalker(self.wraps))

        self.selector = PluginSelector()
        self.pluginwrap = urwid.AttrWrap(self.selector, 'list normal',
                                         'list select')

        self.contentframe = urwid.Pile([self.pluginwrap, self.buttonlb])

        self.padding = urwid.Padding(self.contentframe, align='center',
                                     width=('relative', 50))
        self.filler = urwid.Filler(self.padding, height=('relative', 50))

        urwid.Frame.__init__(self, body=self.filler, header=self.headermap,
                             footer=self.footermap)

        self.loop = urwid.MainLoop(self, palette, unhandled_input=exit_on_q)
        self.loop.run()

    def onAllButton(self, ev):
        for plugin in Plugins:
            Plugins[plugin] = True

        self.selector.populate()

    def onNoneButton(self, ev):
        for plugin in Plugins:
            Plugins[plugin] = False

        self.selector.populate()

    def onOkButton(self, ev):
        self.footer.set_text(('banner', u" Installing plugins. "))
        self.installPlugins()

    def onCancelButton(self, ev):
        print("Quit")
        exit_on_q('q')

    # def installPlugin(self, plugin):

    def installPlugins(self):
        plugins = []

        for plugin in Plugins:
            if Plugins[plugin]:
                plugins.append(plugin)

        installtext = urwid.Text(('title', u"Installing"), align='center')
        installinfo = urwid.Text(('title', u"Preparing installation"),
                                 align='center')
        installwrap = urwid.AttrMap(
            urwid.Pile([installtext, blank, installinfo, blank]), 'bg')
        installprogressbar = urwid.ProgressBar('title', 'streak',
                                               done=len(plugins))

        installlb = urwid.AttrMap(urwid.ListBox(
            urwid.SimpleListWalker([
                installwrap,
                installprogressbar,
                blank
            ])
        ), 'bg')

        installlbfill = urwid.Filler(installlb, height=('relative', 50))

        self.body = installlbfill

        done = 0

        log = {}

        mode = "install" if self.installrbutton.state == True else "develop"

        for plugin in plugins:
            pluginlog = {'out': [], 'err': []}
            self.footer.set_text(('banner',
                                  u" Using %s as installation mode to "
                                  u"install %s " % (
                                  mode, plugin)))
            setup = Popen(['python', 'setup.py', mode], cwd=plugin + "/",
                          stderr=PIPE, stdout=PIPE)
            setup.wait()
            pluginlog = setup.communicate()

            log[plugin] = pluginlog

            # self.installPlugin(plugin)
            installinfo.set_text((u"Installing package 'hfos-%s'" % plugin))
            done += 1
            installprogressbar.set_completion(done)
            self.loop.draw_screen()

        self.loop.stop()

        filename = mktemp("log", "hfos_plugin_installer")

        def writelog(f, block):
            for line in block:
                f.write(line)

        header = "#" * 5

        def writeheader(f, text):
            f.write(header + " " + str(text) + " " + header + "\n")

        with open(filename, "w") as f:
            for plugin in log:
                writeheader(f, "Install log for %s" % plugin)

                writeheader(f, "Info output")
                writelog(f, str(log[plugin][0]))
                writeheader(f, "Error output")
                writelog(f, str(log[plugin][1]))

        print("Done. Logfile written to %s " % filename)

        sys.exit()


installer = Installer()
