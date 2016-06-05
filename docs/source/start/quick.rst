Quick Start Guide
=================
.. DANGER::
   These instructions are not up to date and may cause problems! The build system has been
   changed slightly and these manual parts will soon be updated.

Docker
------

We're preparing a Docker image for installation and another one for development, which is already pretty
mature.

The command to get the current testing release is:

  ``$ docker run -i -t hackerfleet/hfos hfos_launcher.py``


Manual Installation
-------------------

If you don't want or cannot run the docker image, you can set HFOS up manually.


Preparation
^^^^^^^^^^^

Before doing anything with HFOS, be sure you have all the dependencies installed via your distribution's
package manager.

For Debian Unstable use this::

    sudo apt-get install mongodb python3.4 python3-pip python3-grib \
                         python3-bson python3-pymongo python3-serial

If you want (and can), install the mongo and bson extensions::

    sudo apt-get install python3-pymongo-ext python3-bson-ext

You will need to set up a bunch of more dependencies via npm to set up the frontend::

    sudo apt-get install npm

Backend
^^^^^^^

No installation/daemon yet. Just set up a virtual env and install it.
You may want to create a path in /var/cache for hfos' tilecache and other stuff::

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
^^^^^^^^

To install the frontend, update and pull the submodule, then change into it and either install or develop::

    git submodule init
    git submodule update
    cd frontend
    npm install
    bower install
    grunt serve

Point your browser to localhost:9000 to observe the magic. Don't forget to start the backend!

Development
-----------

You can also install the package in development mode, so you don't have to deploy everytime you changed something::

    cd hfos
    virtualenv -p /usr/bin/python3.4 --system-site-packages

Activate venv and run setup.py::

    source venv/bin/activate
    python setup.py develop

Run hfos::

    python hfos_launcher.py

You should see some info/debug output and the web engine as well as other components starting up.
Currently it is set up to serve only on http://localhost:8055 - so point your browser there and explore HFOS.

