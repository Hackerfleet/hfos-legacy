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

.. image:: https://img.shields.io/badge/IRC-%23hackerfleet%20on%20freenode-blue.svg
    :target: http://webchat.freenode.net/?randomnick=1&channels=hackerfleet&uio=d4>
    :alt: IRC Channel

HFOS - The Hackerfleet Operating System
=======================================

**A collaborative and modular infrastructure for your data.**

* **Geo Information** Use a sophisticated map to annotate and review geographical information
* **Vehicle support** Attach a sailyacht, your camper or pack one in your backpack
* **Project planning** Issue tracking for collaborative teams
* **Modular** Expandable with integrated modules, build your own
* **Cloud independent** Run nodes on your own infrastructure

Installation
============

There is more than one way of installing HFOS, `see the quickstart instructions for those <http://hfos.readthedocs.io/en/latest/start/quick.html>`__.

The simplest way is to use the supplied installation script:

.. code-block:: sh

    sudo ./install

The installation produces a lot of output which is automatically piped into 'output.log'.
It installs all dependencies then sets up a user account and the system's services.
This assumes, that you're not running another web server on port 443 and that your firewall is
configured to allow communications on that port.
HFOS modules may require additional open ports, to find out about that, read their readme files.

If you run into trouble or get any unexpected errors, contact us or `try the complex installation procedure <http://hfos.readthedocs.io/en/latest/start/installing.html>`__.

Modules
=======

The system is modular, so you can install what you need and leave other things.

A lot of the included modules are still Work in Progress, so help out, if you're interested
in a powerful - **cloud independent** - collaboration tool suite.

General modules
---------------

These are 'official' Hackerfleet developed modules. If you'd like to contribute your own,
ping riot@c-base.org, to get it added to the list.

============== ==============================================================
  Name           Description
============== ==============================================================
sails          Web UI, compatible with all modern browsers
automat        Automation for non programmers
alert          User alerting and notification system
calc           Integrated EtherCalc
camera         Camera support
chat           Integrated chat
comms          Communication package
countables     Count arbitrary things
dash           Dashboard information system
enrol          Enrollment (new user) management
equipment      Equipment management
filemanager    File management
garden         Garden automation tools
ldap           LDAP user authorization
library        Library management
mesh           Mesh networking
nodestate      Node wide status system
polls          Tool for lightweight internet voting
project        Project management tools
protocols      Miscellaneous communication protocols
robot          RC remote control unit
shareables     Shared resource blocking tool
switchboard    Virtual switchboard
wiki           Etherpad + Wiki = awesomeness
============== ==============================================================

Many of these are not yet fully usable, so please help out and perhaps take ownership of one (or more) of them!

Navigation (Hackerfleet) modules
--------------------------------

We primarily focused on navigation tools, so these are currently the 'more usable' modules.
They are far from complete, see the WiP list below.

*Obligatory Warning*: **Do not use for navigational purposes!**
*Always have up to date paper maps and know how to use them!*

============== ==============================================================
  Name           Description
============== ==============================================================
anchor         Automatic anchor safety watcher
busrepeater    Tool to repeat navigation data bus frames to other media
logbook        Displaying and manual logging of important (nautical) events
maps           (Offline) moving maps with shareable views/layers
navdata        Navigational data module
nmea           NMEA-0183 Navigation data and AIS bus parser
webguides      Importer for skipperguide.de wiki content into the map
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

* `github.com/Hackerfleet <https://github.com/Hackerfleet>`__
* `reddit <https://reddit.com/r/hackerfleet>`__
* `Twitter <https://twitter.com/hackerfleet>`__
* `Facebook <https://www.facebook.com/Hackerfleet>`__
* `soup.io <http://hackerfleet.soup.io/>`__
* `G+ <https://plus.google.com/105528689027070271173>`__
* `irc #hackerfleet on freenode <http://webchat.freenode.net/?randomnick=1&channels=hackerfleet&uio=d4>`__

.. note:: Please be patient when using IRC, responses might take a few hours!

Contributors
============

Code
----

-  Heiko 'riot' Weinen riot@c-base.org
-  Johannes 'ijon' Rundfeldt ijon@c-base.org
-  Martin Ling
-  Sascha 'c_ascha' Behrendt c_ascha@c-base.org

Assets
------

-  Fabulous icons by iconmonstr.com and Hackerfleet contributors

Support
-------

-  `c-base e.V. <https://c-base.org>`__ our home base, the spacestation below Berlin Mitte
-  Lassulus for hosting and nix expertise
-  `Jetbrains s.r.o <https://jetbrains.com>`__ for the opensource license of their ultimate IDE
-  `Github <https://github.com>`__ for hosting our code
-  `Gitlab <https://gitlab.com>`__ for hosting our code ;)
-  `Travis.CI <https://travis-ci.org>`__ for continuous integration services
-  `BrowserStack <https://browserstack.com>`__ for cross device testing capabilities

License
=======

Copyright (C) 2011-2018 riot <riot@c-base.org> and others.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


-- :boat: :+1:
