.. diffport documentation master file, created by
   sphinx-quickstart on Thu Jan  4 00:34:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

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

.. toctree::
   :maxdepth: 2

   usage
   development
