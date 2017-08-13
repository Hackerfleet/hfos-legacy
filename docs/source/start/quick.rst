Quick Start Guide
=================

.. _quick_install:

Install script
--------------

The script currently only supports Debian based systems.

.. note::
   Feel free to contribute installation steps for other distros - that is mostly adapting the package manager
   and package names

To use the install script, get the source code (see :ref:`Getting the source <getting_source>`) if you
don't have it already, then invoke the script with root permissions:

.. code-block:: sh

    $ sudo ./install

If you run into trouble or get any unexpected errors, :ref:`try the complex installation procedure <complex_install>`.

Docker
------

We're providing a Docker image for installation.

The command to get the current testing release is:

  ``$ docker run -i -t hackerfleet/hfos hfos_launcher.py``


Planned Installations
---------------------

* We're planning to offer ready-made SD card images for various embedded systems.
* A custom NixOS system is planned as well.
