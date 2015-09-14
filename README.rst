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

.. image:: https://badge.fury.io/py/hfos.svg
    :target: http://badge.fury.io/py/hfos
    :alt: Pypi Package

.. image:: https://badge.waffle.io/hackerfleet/hfos.svg?label=ready&title=Ready
    :target: https://waffle.io/hackerfleet/hfos
    :alt: Stories Ready


HFOS - The Hackerfleet Operating System
=======================================

    A modern, opensource approach to maritime navigation.

    This software package is supposed to run on your ship/car/plane/ufo's
    board computer.

*Obligatory Warning*: **Do not use for navigational purposes!**

*Always have up to date paper maps and know how to use them!*

Included modules
----------------

-  webui (compatible with all modern browsers)
-  nmea bus parser
-  dashboard
-  offline (cached) moving maps
-  openseamap
-  openstreetmap
-  openweathermap
-  ship info wiki
-  man over board alert system
-  and lots of other useful layers

Work in progress (1.1)
----------------------

-  Full GDAL based raster chart support
-  Dynamic Logbook
-  GRIB data (in charts)
-  Navigation aides, planning
-  Datalog, automated navigational data exchange
-  Crew management, more safety tools
-  wireless crew network and general communications

License
=======

Copyright (C) 2011-2015 riot <riot@hackerfleet.org> and others.

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

Bugs & Discussion
=================

Please research any bugs you find via our `Github issue tracker for
HFOS <https://github.com/hackerfleet/hfos/issues>`__ and report them,
if they're still unknown.

If you want to discuss (opensource) maritime technology in general
incl. where we're heading, head over to our `Github discussion
forum <https://github.com/hackerfleet/discussion/issues>`__
...which is cleverly disguised as a Github issue tracker.

You can also find us here:

* `irc #hackerfleet on freenode <http://webchat.freenode.net/?randomnick=1&channels=hackerfleet&uio=d4>`__
* `hackerfleet.org <http://hackerfleet.org/>`__
* `github.com/Hackerfleet <https://github.com/Hackerfleet>`__
* `Waffle.io <https://waffle.io/hackerfleet/hfos>`__
* `Twitter <https://twitter.com/hackerfleet>`__
* `Facebook <https://www.facebook.com/Hackerfleet>`__
* `soup.io <http://hackerfleet.soup.io/>`__
* `G+ <https://plus.google.com/105528689027070271173>`__

Installation
============

We encourage you to use Python 3.4 for HFOS, but the system is
built (and checked against) 2.7, too.

Warning: **HFOS is not compatible with Python 3.2!**

Quickie-Install
---------------

There is a Docker image available. This is usually the quickest
way to install HFOS:

.. code-block:: bash
    $ docker run -i -t -p 127.0.0.1:8055:8055 --name hfos-test-live \
       -t hackerfleet/hfos

Preparation
-----------

Before doing anything with HFOS, be sure you have all the dependencies
installed via your distribution's package manager.

For Debian Unstable use this:

.. code-block:: bash

    $ sudo apt-get install mongodb python3.4 python3-pip python3-grib \
                           python3-bson python3-pymongo python3-serial

If you want (and can), install the mongo and bson extensions:

.. code-block:: bash

    $ sudo apt-get install python3-pymongo-ext python3-bson-ext

You will need to set up a bunch of more dependencies via npm to set up
the frontend, so install npm and if necessary the nodejs-legacy-symlink
package:

.. code-block:: bash

    $ sudo apt-get install npm nodejs-legacy

Backend
-------

There is no fully automatic installation/daemon yet. Just set up a virtual
environment and install HFOS into it.

We also create two folders in /var (lib/hfos and cache/hfos) for hfos' tile-
cache and other stuff as well as install basic default provisions into the
database:

.. code-block:: bash

    $ sudo mkdir -p /var/cache/hfos/tilecache
    $ git clone https://github.com/hackerfleet/hfos
    $ cd hfos
    $ virtualenv -p /usr/bin/python3.4 --system-site-packages venv
    $ source venv/bin/activate
    $ python setup.py install
    $ python setup.py install_provisions
    $ sudo python setup.py install_var
    $ python hfos_launcher.py

You may need to adapt permissions for the /var folders to accomodate the
user you let hfos run with, until we re-add the daemon and package support
foam, that does that automatically.

Frontend
--------

To install the frontend, update and pull the submodule, then change into
it and either install or develop.

.. code-block:: bash

    $ git submodule init
    $ git submodule update
    $ cd frontend
    $ npm install
    $ sudo npm install -g bower grunt grunt-cli
    $ bower install
    $ grunt serve

Point your browser to localhost:9000 to observe the magic. Don't forget
to start the backend!

You can also copy a static version of the frontend by instructing grunt to:

.. code-block:: bash

    $ sudo grunt copy:dev

Using this method is not meant for live editing, but for the final production 
installation.

Documentation
-------------

The documentation is available online on `ReadTheDocs.org 
<https://hfos.readthedocs.org>`__.
If you wish to build and install the included documentation for offline use,
run these commands:

.. code-block:: bash

    $ pip install -r requirements-dev.txt
    $ python setup.py build_sphinx
    $ sudo python setup.py install_doc

This installs all necessary documentation tools and copies the files to the
expected HFOS web data folder.

You can also build the PDF file (and various other formats) by using the 
Makefile inside the docs directory.

.. code-block:: bash

    $ cd docs
    $ make pdf

Just running make without arguments gives you a list of the other available
documentation formats.

Development
-----------

.. code-block:: bash

    $ cd hfos
    $ virtualenv -p /usr/bin/python3.4 --system-site-packages

Activate venv and run setup.py:

.. code-block:: bash

    $ source venv/bin/activate
    $ python setup.py develop

Run hfos:

.. code-block:: bash

    $ python hfos_launcher.py

You should see some info/debug output and the web engine as well as
other components starting up.
Currently it is set up to serve only on http://localhost:8055 - so
point your browser there and explore HFOS.

Contributors
============

We like to hang out on irc, if you want to chat or help out,
join irc://freenode.org/hackerfleet :)

Missing in the list below? Add yourself or ping us ;)

Code
----

-  Heiko 'riot' Weinen riot@hackerfleet.org
-  Johannes 'ijon' Rundfeldt ijon@hackerfleet.org
-  Martin Ling

Assets
------

This is migrating over to hfos-frontend submodule.

-  Fabulous icons by iconmonstr.com and Hackerfleet contributors
-  Tumbeasts from http://theoatmeal.com/pl/state_web_winter/tumblr for
   the error page (CC-BY)


-- :boat: :+1:
