.. image:: https://travis-ci.org/Hackerfleet/hfos.svg?branch=master
:target: https://travis-ci.org/Hackerfleet/hfos
    :alt: Build Status

.. image:: https://landscape.io/github/Hackerfleet/hfos/master/landscape.svg?style=flat
:target: https://landscape.io/github/Hackerfleet/hfos/master
    :alt: Quality

.. image:: https://coveralls.io/repos/Hackerfleet/hfos/badge.svg
:target: https://coveralls.io/r/Hackerfleet/hfos
    :alt: Coverage

.. image:: https://requires.io/github/Hackerfleet/hfos/requirements.svg?branch=master
:target: https://requires.io/github/Hackerfleet/hfos/requirements/?branch=master
    :alt: Requirements Status


HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to collaborative tasks.

This software package is supposed to run on your home/office/ship/plane/ufo/*space's
board computer.

It initially grew out of frustration with existing navigation solutions for sailors,
as none of these are really oriented towards sailing crews (i.e. multi-user setups), but
we saw the potential for other 'classic' areas of collaboration and started extending
it towards a more general application framework.

A lot of the included modules are still Work in Progress, so help out, if you're interested
in a powerful - cloud independent - collaboration tool suite.

Modules
=======

The system is modular, so you can install what you need and leave other things.

General modules
---------------

These are 'official' Hackerfleet developed modules. If you'd like to contribute your own,
ping riot@c-base.org, to get it added to the list.

============== ==============================================================
  Name           Description
============== ==============================================================
sails          Web UI, compatible with all modern browsers
alert          User alerting and notification system
camera         Camera support
chat           Integrated chat
comms          Communication package
countables     Count arbitrary things
dash           Dashboard information system
garden         Garden automation tools
ldap           LDAP user authorization
library        Library management
mesh           Mesh networking
polls          Tool for lightweight internet voting
project        Project management tools
protocols      Miscellaneous communication protocols
robot          RC remote control unit
shareables     Shared resource blocking tool
switchboard    Virtual switchboard
wiki           Etherpad + Wiki = awesomeness
============== ==============================================================

Most of these are not yet fully usable, so please help out and perhaps take ownership of one (or more) of them!

Navigation (Hackerfleet) modules
--------------------------------

We primarily focused on navigation tools, so these are currently the 'more usable' modules.
They are far from complete, see the WiP list below.

*Obligatory Warning*: **Do not use for navigational purposes!**
*Always have up to date paper maps and know how to use them!*

============== ==============================================================
  Name           Description
============== ==============================================================
busrepeater    Tool to repeat navigation data bus frames to other media
logbook        Displaying and manual logging of important (nautical) events
maps           (Offline) moving maps with shareable views/layers
navdata        Navigational data module
nmea           NMEA-0183 Navigation data bus parser
============== ==============================================================

Work in progress
----------------

-  Full GDAL based vector chart support (Currently only raster charts)
-  Dynamic Logbook
-  GRIB data (in charts)
-  Navigation aides, planning
-  Datalog, automated navigational data exchange
-  Crew management, more safety tools
-  wireless crew network and general communications

Bugs & Discussion
=================

Please research any bugs you find via our `Github issue tracker for
HFOS <https://github.com/hackerfleet/hfos/issues>`__ and report them,
if they're still unknown.

If you want to discuss distributed, opensource (or maritime) technology
in general incl. where we're heading, head over to our `Github discussion
forum <https://github.com/hackerfleet/discussion/issues>`__
...which is cleverly disguised as a Github issue tracker.

You can also find us here:

* `irc #hackerfleet on freenode <http://webchat.freenode.net/?randomnick=1&channels=hackerfleet&uio=d4>`__
* `github.com/Hackerfleet <https://github.com/Hackerfleet>`__
* `Waffle.io <https://waffle.io/hackerfleet/hfos>`__
* `reddit <https://reddit.com/r/hackerfleet>`__
* `Twitter <https://twitter.com/hackerfleet>`__
* `Facebook <https://www.facebook.com/Hackerfleet>`__
* `soup.io <http://hackerfleet.soup.io/>`__
* `G+ <https://plus.google.com/105528689027070271173>`__

Installation
============

First of all: The installation procedure is rather complex right now.
We're trying to simplify the process, but in the meantime, if you encounter
any trouble/problems, just contact us via irc or email and we'll happily try to
help you get your installation running.

This is very important for us, since the system has not yet been deployed
very often and we're not yet aware of most of the pitfalls and traps on that
route.

We encourage you to use Python >= 3.4 for HFOS, but the system is
built (and checked against) 2.7, too.

Warning: **HFOS is not compatible with Python 3.2!**

Preparation
-----------

Before doing anything with HFOS, be sure you have all the dependencies
installed via your distribution's package manager.

For Debian Unstable use this:

.. code-block:: bash

    $ sudo apt-get install mongodb python3.4 python3-pip python3-grib \
                           python3-bson python3-pymongo python3-serial

If you want (and can), install the mongo and bson extensions for
speedups:

.. code-block:: bash

    $ sudo apt-get install python3-pymongo-ext python3-bson-ext

You will need to set up a bunch of more dependencies via npm to set up
the frontend, so install npm and if necessary the nodejs-legacy-symlink
package:

.. code-block:: bash

    $ sudo apt-get install npm nodejs-legacy

If you want to install the full development dependencies to write
documentation as well, you need to install the enchant package:

.. code-block:: bash

    $ sudo apt-get install enchant

In case you want to use raster (or in future: vector) charts, you'll
need to install libgdal and its binaries:

.. code-block:: bash

    $ sudo apt-get install gdal-bin python-gdal

Note, that it is necessary to install python-gdal 2.7 - not the python3 variant,
as the scripts are not included in that.

Backend
-------

The manage tool usually can install everything you need. It starts by adding
a new system user for HFOS and generating a (currently only self signed)
certificate.

The process also involves getting the frontend dependencies, installing the
supplied modules, building and installing the documentation, etc.

It also installs and activates a systemd service script to launch HFOS on
bootup.

We also create two folders in /var (lib/hfos and cache/hfos) for hfos' tile-
cache and other stuff as well as install basic default provisions into the
database:

.. code-block:: bash

    $ git clone https://github.com/hackerfleet/hfos
    $ git submodule init
    $ git submodule update
    $ cd hfos
    $ virtualenv -p /usr/bin/python3.4 --system-site-packages venv
    $ source venv/bin/activate
    $ pip install -Ur requirements.txt
    $ python setup.py develop
    $ sudo venv/bin/python hfos_manage.py install all
    $ python hfos_launcher.py

If you want to develop (documentation) as well, you'll need to use the
`requirements-dev.txt` instead of the normal one.

If you want to manually start HFOS, invoke the launcher thus:

.. code-block:: bash

    $ sudo ./venv/bin/python hfos_launcher.py --cert /etc/ssl/certs/hfos/selfsigned.pem --port 443

Running the launcher as root to be able to open ports below 1024 should be
safe, as it drops its root privileges, unless you specify --insecure,
which is strongly discouraged and only meant for development purposes.

Documentation
-------------

The documentation is available online on `ReadTheDocs.org
<https://hfos.readthedocs.org>`__.
If you wish to build and install the included documentation for offline use,
run these commands:

.. code-block:: bash

    $ sudo ./venv/bin/python hfos_manage.py -install-doc

This installs all necessary documentation tools and copies the files to the
expected HFOS web data folder.

You can also build the PDF file (and various other formats) by using the
Makefile inside the docs directory.

.. code-block:: bash

    $ cd docs
    $ make pdf

Just running make without arguments gives you a list of the other available
documentation formats.

Docker-Install
--------------

There is a Docker image available. This is usually the quickest
way to install HFOS, but it is only updated occasionally (for now):

.. code-block:: bash

    $ docker run -i -t -p 127.0.0.1:8055:8055 --name hfos-test-live \
       -t hackerfleet/hfos

Contributors
============

We like to hang out on irc, if you want to chat or help out,
join irc://freenode.org/hackerfleet :)

Please be patient or even better use screen/tmux or something to irc.
Most of us are there 24/7 but not always in front of our machines.

Missing in the list below? Add yourself or ping us ;)

Code
----

-  Heiko 'riot' Weinen riot@c-base.org
-  Johannes 'ijon' Rundfeldt ijon@c-base.org
-  Martin Ling

Assets
------

-  Fabulous icons by iconmonstr.com and Hackerfleet contributors

License
=======

Copyright (C) 2011-2017 riot <riot@c-base.org> and others.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


-- :boat: :+1:
