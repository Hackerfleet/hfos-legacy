[![Build Status](https://travis-ci.org/Hackerfleet/hfos.svg)](https://travis-ci.org/Hackerfleet/hfos)
[![Stories in Ready](https://badge.waffle.io/Hackerfleet/hfos.png?label=ready&title=Ready)](https://waffle.io/Hackerfleet/hfos)
[![Requirements Status](https://requires.io/github/Hackerfleet/hfos/requirements.svg?branch=master)](https://requires.io/github/Hackerfleet/hfos/requirements/?branch=master)
HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to maritime navigation.

This software package is supposed to run on your ship/car/plane/ufo's board computer.

_Obligatory Warning_: **Do not use for navigational purposes!**

_Always have up to date paper maps and know how to use them!_

Included modules
----------------

Note: the frontend is now included as submodule!

* webui (compatible with all modern browsers)
* nmea bus parser
* offline (cached) moving seamap incl.
 * openseamap
 * openstreetmap
 * openweathermap
 * and lots of other useful layers

Work in progress (1.0)
----------------------

* Navigation, GRIB data (in charts)
* Navigation aides, planning
* Datalog, automated navigational data exchange
* Crew management, safety tools
* wireless crew network and general communications

Bugs & Discussion
=================

Please research any bugs you find via our [Github issue tracker for HFOS](https://github.com/hackerfleet/hfos/issues)
and report them if they're still unknown.

If you want to discuss (opensource) maritime technology in general incl. where we're heading, head over to our
[Github discussion forum](https://github.com/hackerfleet/discussion/issues)
...which is cleverly disguised as a Github issue tracker.

Installation
============

Preparation
-----------

Before doing anything with HFOS, be sure you have all the dependencies installed via your distribution's package manager.
For Debian Unstable use this:

    sudo apt-get install mongodb python3.4 python3-pip python3-grib \
                         python3-bson python3-pymongo python3-serial

If you want (and can), install the mongo and bson extensions:

    sudo apt-get install python3-pymongo-ext python3-bson-ext

You will need to set up a bunch of more dependencies via npm to set up the frontend:

    sudo apt-get install npm

Backend
-------

No installation/daemon yet. Just set up a virtual env and install it.
You may want to create a path in /var/cache for hfos' tilecache and other stuff:

    sudo mkdir -p /var/cache/hfos/tilecache
    git clone https://github.com/hackerfleet/hfos
    cd hfos
    virtualenv -p /usr/bin/python3.4 --system-site-packages venv
    source venv/bin/activate
    python setup.py install
    python hfos.py


You may need to adapt permissions for that folder to accomodate the user you let hfos run with, until we re-
add the daemon and package support foam, that does that automatically.

Frontend
--------

To install the frontend, update and pull the submodule, then change into it and either install or develop.

    git submodule init
    git submodule update
    cd frontend
    npm install
    bower install
    grunt serve

Point your browser to localhost:9000 to observe the magic. Don't forget to start the backend!

Development
-----------

    cd hfos
    virtualenv -p /usr/bin/python3.4 --system-site-packages

Activate venv and run setup.py:

    source venv/bin/activate
    python setup.py develop

Run hfos:

    python hfos.py

You should see some info/debug output and the web engine as well as other components starting up.
Currently it is set up to serve only on http://localhost:8055 - so point your browser there and explore HFOS.

Debian PKG Generation
---------------------

*Outdated - these do not work without some additional work* Debian instructions:

If you're using Debian, we provide a skeleton to build a cleanly installable dpkg package:

    sudo apt-get install dpkg-dev
    dpkg-buildpackage

Run buildpackage in the top source directory to generate a debian package.


Configuration
-------------

Lives in `/etc/hfos/config.json` after installation, but is currently not used.


Contributors
============

We like to hang out on irc, if you want to chat or help out, 
join irc://freenode.org/hackerfleet :)


Code
----

* Heiko 'riot' Weinen <riot@hackerfleet.org>
* Johannes 'ijon' Rundfeldt <ijon@hackerfleet.org>

Assets
------

This is migrating over to hfos-frontend submodule.

* Fabulous icons by iconmonstr.com and Hackerfleet contributors
* Tumbeasts from http://theoatmeal.com/pl/state_web_winter/tumblr for the error page (CC-BY)

Missing? Add yourself or ping us ;)

:boat: :+1:
