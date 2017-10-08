diffport
========

.. image:: https://img.shields.io/travis/reichlab/diffport.svg?style=flat-square
    :target: https://travis-ci.org/reichlab/diffport

.. image:: https://img.shields.io/pypi/v/diffport.svg?style=flat-square
    :target: https://pypi.python.org/pypi/diffport

Diffport is a database summary diff reporting tool. It helps in maintaining,
diffing and reporting summaries from a database based on a desired set of
*watchers*.

Usage
-----

Diffport works by using a set of *watchers* to take snapshots of database at
different times and then producing a difference report when asked for it.
It uses a config file specifying these watchers and their own specific
configuration. An example follows::

   # diffport.yaml
   - name: number-of-rows
     config:
       groupby:
         - <groupby-column>
         - <groupby-column>
       table: <table-name>

   - name: tables-in-schema
     config: <table-name>

Command line usage instruction can be found by using ``diffport --help``.

Diffport needs environment variable ``DATABASE_URL`` to be set for connecting to
a database. A sample value for postgres follows (see `here
<https://dataset.readthedocs.io/en/latest/quickstart.html#connecting-to-a-database>`_
for more)::

  postgresql://scott:tiger@localhost:5432/mydatabase
