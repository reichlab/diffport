.. diffport documentation master file, created by
   sphinx-quickstart on Thu Jan  4 00:34:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to diffport's documentation!
====================================

.. image:: https://img.shields.io/travis/reichlab/diffport.svg?style=flat-square
    :target: https://travis-ci.org/reichlab/diffport

.. image:: https://img.shields.io/pypi/v/diffport.svg?style=flat-square
    :target: https://pypi.python.org/pypi/diffport

Diffport is a database *summary diff* reporting tool. It helps in maintaining,
diffing and reporting summaries from a database based on a set of *watchers*. It
currently works (and is tested) under postgres.

It works by using a set of *watchers* to take snapshots of database at different
times and then producing a difference report when asked for it. These watchers
define what information (summary) to take snapshot of.

.. _usage:

Usage
-----

Install diffport::

  pip install diffport

Setup a config file specifying the watchers you need with their own
configurations. An example follows::

   # diffport.yaml
   - name: number-of-rows
     config:
       groupby:
         - <groupby-column-one>
         - <groupby-column-two>
       table: <table-name>

   - name: tables-in-schema
     config:
       - <schema-one>
       - <schema-two>

The first watcher (``number-of-rows``) keeps the count of rows in table
``<table-name``, grouped by columns ``<groupby-column-one>`` and
``<groupby-column-two>``. The second watcher ``tables-in-schema`` keeps the list
of tables in each of the schema provided in *its* config.

More details about these watchers is given in the section on :ref:`watchers`.

.. _watchers:

Watchers
--------

.. _development:

Development
-----------
