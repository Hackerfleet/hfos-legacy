.. HFOS documentation master file, created by
sphinx-quickstart on Fri Jun 12 16:27:08 2015.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive.

==================
HFOS Documentation
==================

:Version: |version|
:Release: |release|
:Date: |today|


.. _documentation-index:

Sailor's Manual
===============

.. toctree::
:maxdepth: 2
       manual/index
       manual/

Developer Documentation
=======================


.. toctree::
:maxdepth: 1

       start/index
       tutorials/index
       man/index
       api/index
       dev/index
       changes
       roadmap
       contributors
       faq

.. toctree::
:hidden:

       glossary

.. ifconfig:: devel

   .. toctree::
:hidden:

          todo
          readme

Indices and tables
==================

* :ref:`Index <genindex>`
* :ref:`modindex`
* :ref:`search`
* :doc:`glossary`

.. ifconfig:: devel

   * :doc:`todo`
   * :doc:`readme`
