.. _complex_install:

Installing
==========

First of all: The manual installation procedure is rather complex right now.

We've :ref:`simplified the process by supplying an install script <quick_install>`,
but if you encounter any trouble/problems, checkout these detailed installation steps.

If you still can't get it to install, :ref:`contact us via irc or email <communication>`
and we'll happily try to help you get your installation running.

This is very important for us, since the system has not yet been deployed
very often and we're not yet aware of all of the pitfalls and traps on that
route.

We encourage you to use Python >= 3.5 for HFOS, but the system is
built (and checked against) 2.7, too.

Warning: **HFOS is not compatible with Python 3.2!**

Preparation
-----------

These instructions are for Debian or Ubuntu based systems. Installation
on other distributions is possible.

Before doing anything with HFOS, be sure you have all the dependencies
installed via your distribution's package manager.

For Debian Unstable use this:

.. code-block:: sh

    $ sudo apt-get install nginx mongodb python3.5 python3-pip python3-grib \
                           python3-bson python3-pymongo python3-serial

If you want (and can, depending on your platform/distribution), install the
mongo and bson extensions for speedups:

.. code-block:: sh

    $ sudo apt-get install python3-pymongo-ext python3-bson-ext

The system will need to get a bunch of more dependencies via npm to set up
the frontend, so install npm and if necessary the nodejs-legacy-symlink
package:

.. code-block:: sh

    $ sudo apt-get install npm nodejs
    $ sudo npm install npm@4.2.0 -g

If you want to install the full development dependencies to write
documentation as well, you need to install the enchant package:

.. code-block:: sh

    $ sudo apt-get install enchant

In case you want to use raster (or in future: vector) charts in HFOS' map module,
you'll need to install libgdal and its binaries:

.. code-block:: sh

    $ sudo apt-get install gdal-bin python-gdal

Note, that it is necessary to install python-gdal 2.7 - not the python3 variant,
as the scripts are not included in that.

.. _getting_source:

Getting the source
------------------

To initially obtain the development source code if you don't have it already,
use git thus:

.. code-block:: sh

    $ mkdir ~/src
    $ cd ~/src
    $ git clone https://github.com/hackerfleet/hfos
    $ cd hfos
    $ git submodule init
    $ git submodule update
    $ git pull
    $ cd frontend
    $ git pull


Backend
-------

The manage tool usually can install everything you need. It starts by adding
a new system user for HFOS and generating a (currently only self signed)
certificate.

The process also involves installing the supplied modules, getting the frontend
dependencies, building and installing the documentation, etc.

It also creates two folders in /var (lib/hfos and cache/hfos) for hfos' tile-
cache and other stuff as well as install basic default provisions into the
database.

Finally, it installs and activates a systemd and nginx service script to launch
HFOS on bootup and make it available to users.

.. code-block:: sh

    $ virtualenv -p /usr/bin/python3.5 --system-site-packages venv
    $ source venv/bin/activate
    $ pip install -Ur requirements.txt
    $ python setup.py develop
    $ sudo venv/bin/python hfos_manage.py install all

If you want to develop (documentation) as well, you'll need to use the
`requirements-dev.txt` instead of the normal one.

If you want to manually start HFOS, invoke the launcher thus:

.. code-block:: sh

    $ sudo ./venv/bin/python hfos_launcher.py

Running the launcher as root to be able to open ports below 1024 should be
safe, as it drops its root privileges, unless you specify --insecure,
which is strongly discouraged and only meant for development purposes.
The default is to use port 8055 and relay that with the supplied nginx
site definition

Documentation
-------------

The documentation is available online on `ReadTheDocs.org
<https://hfos.readthedocs.org>`__.
If you wish to build and install the included documentation for offline use,
run these commands:

.. code-block:: sh

    $ sudo ./venv/bin/python hfos_manage.py install docs

This installs all necessary documentation tools and copies the files to the
expected HFOS web data folder.

You can also build the PDF file (and various other formats) by using the
Makefile inside the docs directory.

.. code-block:: sh

    $ cd docs
    $ make pdf

Just running make without arguments gives you a list of the other available
documentation formats.

Installing from a Source Package
--------------------------------
*If you have downloaded a source archive, this applies to you.*

.. code-block:: sh

   $ python setup.py install

For other installation options see:

.. code-block:: sh

   $ python setup.py --help install


Installing from the Development Repository
------------------------------------------
*If you have cloned the source code repository, this applies to you.*

If you have cloned the development repository, it is recommended that you
use setuptools and use the following command:

.. code-block:: sh

   $ python setup.py develop

This will allow you to regularly update your copy of the hfos development
repository by simply performing the following in the hfos working directory:

.. code-block:: sh

   $ git pull -u
   $ cd frontend
   $ git pull -u

.. note::
   You do not need to reinstall if you have installed with setuptools via
   the hfos repository and used setuptools to install in "develop" mode.

Windows & OS X installation notes
---------------------------------
*These instructions are WiP. The easiest way to get HFOS on Win7 or newer
is to install and user Docker or a virtual machine*

To install on Windows, you'll need to install these packages first:

 * Python 3.5 https://www.python.org/downloads/windows/
 * MongoDB https://www.mongodb.org/downloads#production
 * pymongo
 * numpy

Platform specific
-----------------

There are some collected instructions for various hardware platforms:

.. toctree::
    :maxdepth: 1
    :glob:

    platforms/*