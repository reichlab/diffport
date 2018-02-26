diffport
========

.. image:: https://img.shields.io/travis/reichlab/diffport.svg?style=flat-square
    :target: https://travis-ci.org/reichlab/diffport

.. image:: https://img.shields.io/pypi/v/diffport.svg?style=flat-square
    :target: https://pypi.python.org/pypi/diffport

Diffport is a database *summary diff* reporting tool. It helps in maintaining,
diffing and reporting summaries from a database based on a set of *watchers*. It
currently works (and is tested) under postgres.

Usage
-----

Diffport works by using a set of *watchers* to take snapshots of database at
different times and then producing a difference report when asked for it.
It uses a config file specifying these watchers and their own specific
configuration needs. An example follows::

   # diffport.yaml
   - name: number-of-rows
     config:
       - groupby:
           - disease
           - date_sick_year
         table: unique_case_data

   - name: tables-in-schema
     config:
       - original_data

   - name: columns-in-schema
     config:
       - original_data

   - name: table-change
     config:
       schemas:
         - original_data
       tables: []

For more details and usage instructions, head over to the project's
documentation `here <http://reichlab.io/diffport>`_.
