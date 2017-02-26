
import os
from glob import glob
from shutil import copy

from hfos.logger import hfoslog, debug, verbose, warn, error, critical, hilight

try:
    from subprocess import Popen
except ImportError:
    from subprocess32 import Popen  # NOQA


def copytree(root_src_dir, root_dst_dir, hardlink=True):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                if hardlink:
                    hfoslog('Removing frontend link:', dst_file,
                            emitter='MANAGE', lvl=verbose)
                    os.remove(dst_file)
                else:
                    hfoslog('Overwriting frontend file:', dst_file,
                            emitter='MANAGE', lvl=verbose)

            hfoslog('Hardlinking ', src_file, dst_dir, emitter='MANAGE',
                    lvl=verbose)
            try:
                if hardlink:
                    os.link(src_file, dst_file)
                else:
                    copy(src_file, dst_dir)
            except PermissionError as e:
                hfoslog(
                    " No permission to create target %s for frontend:" % (
                        'link' if hardlink else 'copy'),
                    dst_dir, e, emitter='MANAGE', lvl=error)
            except Exception as e:
                hfoslog("Error during", 'link' if hardlink else 'copy',
                        "creation:", type(e), e, emitter='MANAGE',
                        lvl=error)

            hfoslog('Done linking', root_dst_dir, emitter='MANAGE',
                    lvl=verbose)


# TODO: Installation of frontend requirements is currently disabled
def install_frontend(forcereload=False, forcerebuild=False,
                     forcecopy=True, install=True, development=False):
    hfoslog("Updating frontend components", emitter='MANAGE')
    components = {}
    loadable_components = {}
    # TODO: Fix this up, it is probably not a sane way to get at the real root
    if development:
        frontendroot = os.path.abspath(os.path.dirname(os.path.realpath(
            __file__)) + "../../../frontend")
    else:
        frontendroot = '/opt/hfos/frontend'
    frontendtarget = '/var/lib/hfos/frontend'

    if install:
        cmdline = ["npm", "install"]

        hfoslog("Running", cmdline, lvl=verbose,
                emitter='MANAGE')
        npminstall = Popen(cmdline, cwd=frontendroot)
        out, err = npminstall.communicate()

        npminstall.wait()

        hfoslog("Frontend dependency installing done: ", out,
                err, lvl=debug, emitter='MANAGE')


    if True:  # try:
        from pkg_resources import iter_entry_points

        entry_point_tuple = (
            iter_entry_points(group='hfos.base', name=None),
            iter_entry_points(group='hfos.sails', name=None),
            iter_entry_points(group='hfos.components', name=None)
        )

        for iterator in entry_point_tuple:
            for entry_point in iterator:
                try:
                    name = entry_point.name
                    location = entry_point.dist.location
                    loaded = entry_point.load()

                    hfoslog("Entry point: ", entry_point,
                            name,
                            entry_point.resolve(), lvl=verbose,
                            emitter='MANAGE')

                    hfoslog("Loaded: ", loaded, lvl=verbose, emitter='MANAGE')
                    comp = {
                        'location': location,
                        'version': str(entry_point.dist.parsed_version),
                        'description': loaded.__doc__
                    }

                    frontend = os.path.join(location, 'frontend')
                    hfoslog("Checking component frontend parts: ",
                            frontend, lvl=verbose, emitter='MANAGE')
                    if os.path.isdir(
                            frontend) and frontend != frontendroot:
                        comp['frontend'] = frontend
                    else:
                        hfoslog("Component without frontend "
                                "directory:", comp, lvl=debug,
                                emitter='MANAGE')

                    components[name] = comp
                    loadable_components[name] = loaded

                    hfoslog("Loaded component:", comp, lvl=verbose,
                            emitter='MANAGE')

                except Exception as e:
                    hfoslog("Could not inspect entrypoint: ", e,
                            type(e), entry_point, iterator, lvl=error,
                            exc=True, emitter='MANAGE')

    # except Exception as e:
    #    hfoslog("Error: ", e, type(e), lvl=error, exc=True, emitter='MANAGE')
    #    return

    hfoslog('COMPONENTS AFTER LOOKUP:', components.keys(), lvl=hilight)

    def _update_frontends(install=True):
        hfoslog("Checking unique frontend locations: ",
                loadable_components, lvl=debug, emitter='MANAGE')

        importlines = []
        modules = []

        for name, component in components.items():
            if 'frontend' in component:
                origin = component['frontend']

                target = os.path.join(frontendroot, 'src', 'components',
                                      name)
                target = os.path.normpath(target)

                if install:
                    reqfile = os.path.join(origin, 'requirements.txt')

                    if os.path.exists(reqfile):
                        hfoslog("Installing package dependencies", lvl=debug,
                                emitter='MANAGE')
                        with open(reqfile, 'r') as f:
                            cmdline = ["npm", "install"]
                            for line in f.readlines():
                                cmdline.append(line.replace("\n", ""))

                            hfoslog("Running", cmdline, lvl=verbose,
                                    emitter='MANAGE')
                            npminstall = Popen(cmdline, cwd=frontendroot)
                            out, err = npminstall.communicate()

                            npminstall.wait()

                            hfoslog("Frontend installing done: ", out,
                                    err, lvl=debug, emitter='MANAGE')

                # if target in ('/', '/boot', '/usr', '/home', '/root',
                # '/var'):
                #    hfoslog("Unsafe frontend deletion target path, "
                #            "NOT proceeding! ", target, lvl=critical,
                #            emitter='MANAGE')

                hfoslog("Copying:", origin, target, lvl=debug,
                        emitter='MANAGE')

                copytree(origin, target)

                for modulefilename in glob(target + '/*.module.js'):
                    modulename = os.path.basename(modulefilename).split(
                        ".module.js")[0]
                    line = u"import {s} from './components/{p}/{" \
                           u"s}.module';\n" \
                           u"modules.push({s});\n".format(s=modulename, p=name)
                    if not modulename in modules:
                        importlines += line
                        modules.append(modulename)
            else:
                hfoslog("Module without frontend:", name, component,
                        lvl=debug, emitter='MANAGE')

        with open(os.path.join(frontendroot, 'src', 'main.tpl.js'),
                  "r") as f:
            main = "".join(f.readlines())

        parts = main.split("/* COMPONENT SECTION */")
        if len(parts) != 3:
            hfoslog("Frontend loader seems damaged! Please check!",
                    lvl=critical, emitter='MANAGE')
            return

        try:
            with open(os.path.join(frontendroot, 'src', 'main.js'),
                      "w") as f:
                f.write(parts[0])
                f.write("/* COMPONENT SECTION:BEGIN */\n")
                for line in importlines:
                    f.write(line)
                f.write("/* COMPONENT SECTION:END */\n")
                f.write(parts[2])
        except Exception as e:
            hfoslog("Error during frontend package info writing. Check "
                    "permissions! ", e, lvl=error, emitter='MANAGE')

    def _rebuild_frontend():
        hfoslog("Starting frontend build.", lvl=warn, emitter='MANAGE')
        npmbuild = Popen(["npm", "run", "build"], cwd=frontendroot)
        out, err = npmbuild.communicate()
        try:
            npmbuild.wait()
        except Exception as e:
            hfoslog("Error during frontend build", e, type(e),
                    exc=True, lvl=error, emitter='MANAGE')
            return

        hfoslog("Frontend build done: ", out, err, lvl=debug, emitter='MANAGE')
        copytree(os.path.join(frontendroot, 'build'),
                 frontendtarget, hardlink=False)
        copytree(os.path.join(frontendroot, 'assets'),
                 os.path.join(frontendtarget, 'assets'),
                 hardlink=False)

        hfoslog("Frontend deployed", emitter='MANAGE')

    hfoslog("Checking component frontend bits in ", frontendroot,
            lvl=verbose, emitter='MANAGE')

    _update_frontends(install=install)
    if forcerebuild:
        _rebuild_frontend()

    hfoslog("Done: Install Frontend", emitter='MANAGE')

    # We have to find a way to detect if we need to rebuild (and
    # possibly wipe) stuff. This maybe the case, when a frontend
    # module has been updated/added/removed.
