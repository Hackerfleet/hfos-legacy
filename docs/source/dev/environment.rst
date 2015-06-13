.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _pip: https://pypi.python.org/pypi/pip
.. _Fabric: http://www.fabfile.org/
.. _Python: https://www.python.org/
.. _Git: https://git-scm.com/


Setting up a HFOS Development Environment
=========================================

This is the recommended way to setup a development enviornment
for developing the backend and frontend of HFOS .

.. note:: This document *assumes* you already have a working `Python`_
environment with a minimum `Python`_ version of 2.7 as well
          as mongodb and `pip`_ already installed.


Prerequisites
-------------

It is highly recommended that you install and use `virtualenv`_ for all your
`Python`_ development and production deployments (*not just HFOS*).

It is also convenient to install and use the accompanying shell scripts
and tools `virtualenvwrapper`_ which adds a nice set of workflows
and functions useful for both development and deployments.

.. code-block:: bash
    
    $ pip install -U virtualenvwrapper
    $ source $(which virtualenvwrapper.sh)

.. note:: You should put ``source $(which virtualenvwrapper.sh)`` in either
your ``$HOME/.bashrc`` or ``$HOME/.profile`` depending on how you
          login and interact with your terminals.

In addition to the above recommendations you must also have a `Git`_ client
installed and ready to use as well as your Editor/IDE of choice ready to use.


Getting Started
---------------

1. `Fork HFOS <https://github.com/hackerfleet/hfos#fork-destination-box>`_
   (*if you haven't done so already*)
2. Clone your forked repository using `Git`_
3. Create a new virtual environment using `virtualenvwrapper`_
4. Install the `Development Requirements <https://github.com/hackerfleet/hfos/blob/master/requirements-dev.txt>`_
5. Install HFOS in "develop" mode

And you're done!

Example:

.. code-block:: bash
    
    $ git clone git@github.com:yourgithubaccount/hfos.git
    $ cd hfos
    $ mkvirtualenv hfos
    $ pip install -r requirements-dev.txt
    $ python setup.py develop

Alternatively if you already have `Fabric`_ installed:

.. code-block:: bash
    
    $ git clone git@github.com:yourgithubaccount/hfos.git
    $ cd hfos
    $ mkvirtualenv hfos
    $ fab develop
