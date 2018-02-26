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
diffing and reporting summaries from a database based on a set of *watchers*.

.. note:: Diffport should be considered a beta software. It hasn't been tried
          with databases other than postgres.

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

.. note:: More details about these watchers is given in the section on
          :ref:`watchers`. Details on how to add new watchers is in
          :ref:`development`.

Then to take snapshots, run the following in a directory where you want to store
the snapshots (the saves go in a subdirectory ``store``)::

  diffport save --config=/path/to/diffport.yaml

Each snapshot is identified by a unique id (a hash) which is then used to do the
diff::

  # This displays the list of snapshots with hashes
  diffport list --config=/path/to/diffport.yaml

  # To see diff between two hashes
  diffport diff <hash-old> <hash-new> --config=/path/to/diffport.yaml

  # Without giving hashes, diffport reports diff between the last two snapshots
  diffport diff --config=/path/to/diffport.yaml

General command line usage instructions follow::

  Usage:
    diffport save [--identifier=ID] [--config=CFG] [--source=CON] [--dialect=DIA]
    diffport (rm | remove) <snap-hash> [--config=CFG]
    diffport (ls | list) [--json] [--config=CFG]
    diffport diff [<snap-old> <snap-new>] [--config=CFG]

  Arguments:
    save                 Save a snapshot at current time
    rm, remove           Remove a snapshot
    ls, list             List all the summary snapshots
    diff                 Return diff summary for the two snapshots
                         (or the two latest ones if hashes not provided)

  Options:
    --json               Output for machines
    --config=CFG         Configuration file [default: ./diffport.yaml]
    --source=CON         Database source [default: env]
    --dialect=DIA        Database type [default: postgresql]
    -h, --help           Open help
    -v, --version        Show version


.. _watchers:

Watchers
--------

.. _development:

Development
-----------
