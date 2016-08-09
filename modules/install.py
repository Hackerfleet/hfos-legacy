import argparse
from subprocess import Popen, PIPE
import sys
from tempfile import mktemp

try:
    import urwid
except ImportError:
    urwid = None

# TODO:
# * Automatically find local modules
# * Grab module list from pypi
# * Add installation location / venv info somewhere (permanent)
# * Redirect install log for archival and review purposes
# * Provisions (Installable via HFOS Sails' setup.py)
# * Migrations?
# * Dependencies?!

Modules = {
    'alert': True,
    'busrepeater': False,
    'camera': False,
    'chat': False,
    'comms': False,
    'countables': False,
    'crew': False,
    'dash': False,
    'garden': False,
    'ldap': False,
    'library': False,
    'logbook': False,
    'maps': False,
    'navdata': False,
    'nmea': False,
    'project': False,
    'protocols': False,
    'robot': False,
    'shareables': False,
    'switchboard': False,
    'wiki': False,
}


def gui():
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

            self.SFLW = None
            self.body = None

            self.populate()
            urwid.ListBox.__init__(self, self.SFLW)

        def populate(self):
            options = []
            for item in sorted(Modules.keys()):
                state = Modules[item]
                option = urwid.CheckBox(item, state,
                                        on_state_change=self.state_change)
                options.append(option)

            self.SFLW = urwid.SimpleFocusListWalker(options)
            self.body = self.SFLW
            self._invalidate()

        def state_change(self, option, state):
            # footer.set_text(('banner', u"HELLO!!! %s %s " % (
            # option._label.text, state)))
            Modules[option._label.text] = state

    class Installer(urwid.Frame):
        def __init__(self):
            self.body = None

            self.header = urwid.Text(('title', u" HFOS Modules "), align='center')
            self.headermap = urwid.AttrMap(self.header, 'streak')
            self.footer = urwid.Text(('banner', u" Select plugins to install! "),
                                     align='center')
            self.footermap = urwid.AttrWrap(self.footer, 'streak')

            self.allbutton = urwid.Button(u"Select All", self.on_all_button)
            self.nonebutton = urwid.Button(u"Select None", self.on_none_button)

            self.okbutton = urwid.Button(u"Ok", self.on_ok_button)
            self.exitbutton = urwid.Button(u"Cancel", self.on_cancel_button)

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

        def on_all_button(self):
            for plugin in Modules:
                Modules[plugin] = True

            self.selector.populate()

        def on_none_button(self):
            for plugin in Modules:
                Modules[plugin] = False

            self.selector.populate()

        def on_ok_button(self):
            self.footer.set_text(('banner', u" Installing plugins. "))
            self.install_modules()

        def on_cancel_button(self):
            print("Quit")
            exit_on_q('q')

        # def installPlugin(self, plugin):

        def install_modules(self):
            plugins = []

            for plugin in Modules:
                if Modules[plugin]:
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

            mode = "install" if self.installrbutton.state is True else "develop"

            for plugin in plugins:
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

            def writelog(fileobject, block):
                for line in block:
                    fileobject.write(line)

            header = "#" * 5

            def writeheader(fileobject, text):
                fileobject.write(header + " " + str(text) + " " + header +
                                 "\n")

            with open(filename, "w") as f:
                for plugin in log:
                    writeheader(f, "Install log for %s" % plugin)

                    writeheader(f, "Info output")
                    writelog(f, str(log[plugin][0]))
                    writeheader(f, "Error output")
                    writelog(f, str(log[plugin][1]))

            print("Done. Logfile written to %s " % filename)

            sys.exit()

    return Installer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui",
                        help="Launch (console-) GUI to install modules",
                        action="store_true")

    parser.add_argument("--all",
                        help="Install all found modules",
                        action="store_true")

    parser.add_argument("--dev",
                        help="Invoke setup.py with develop instead of install",
                        action="store_true")

    args = parser.parse_args()

    if args.all:

        for module in Modules.keys():
            try:
                setup = Popen([
                    'python',
                    'setup.py',
                    'develop' if args.dev else 'install'
                ],
                    cwd=module + "/")
                setup.wait()
            except Exception as e:
                print("Problematic module encountered, could not install: ",
                      module, e, type(e))

        sys.exit(0)

    if args.gui and urwid is not None:
        gui()
    elif urwid is None:
        print("No GUI available. Maybe install python3-urwid to use this or"
              "use install --all to just install everything")

if __name__ == "__main__":
    main()
