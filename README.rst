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
automat        Automation for non programmers
alert          User alerting and notification system
calc           Integrated EtherCalc
camera         Camera support
chat           Integrated chat
comms          Communication package
countables     Count arbitrary things
dash           Dashboard information system
enrol          Enrollment (new user) management
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

* `github.com/Hackerfleet <https://github.com/Hackerfleet>`__
* `Waffle.io <https://waffle.io/hackerfleet/hfos>`__
* `reddit <https://reddit.com/r/hackerfleet>`__
* `Twitter <https://twitter.com/hackerfleet>`__
* `Facebook <https://www.facebook.com/Hackerfleet>`__
* `soup.io <http://hackerfleet.soup.io/>`__
* `G+ <https://plus.google.com/105528689027070271173>`__
* `irc #hackerfleet on freenode <http://webchat.freenode.net/?randomnick=1&channels=hackerfleet&uio=d4>`__

.. note:: Please be patient when using IRC, responses might take a few hours!

Installation
============

There is more than one way of installing HFOS, :ref:`see the quickstart instructions for those <quick_install>`.

The simplest way is to use the new install script:

.. code-block:: sh

    $ sudo ./install

If you run into trouble or get any unexpected errors, :ref:`try the complex installation procedure <complex_install>`.


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
