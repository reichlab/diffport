.. _usage:

Usage
=====

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
          :doc:`development`.

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

General command line usage instructions follow

.. automodule:: diffport.cli

.. _watchers:

Watchers
--------

Watchers are units with responsibility of saving a specific *kind* of
information about the database, like count of rows in a certain table. Along
with saving snapshot, they also provide way to find and report differences
between two of such snapshots.

As of now, diffport has the following set of watchers based on our specific
requirements. To develop new watchers or to modify existing, see the section on
:ref:`development`.

- :ref:`number_of_rows`
- :ref:`number_of_rows_hash`
- :ref:`schema_tables`
- :ref:`schema_columns`
- :ref:`table_change`

Next few sections describe the config options needed for each of these watchers.
To use a watcher, we need to put its config along with its identifier in the
main config file for diffport like this::

  # diffport.yaml
  - name: <watcher-id>
    config: <watcher-config>

.. _number_of_rows:

Number of rows
~~~~~~~~~~~~~~

This maintains row counts of tables. While diffing, the quantity it returns is a
number (positive or negative) depending on whether rows were added or removed.
Its watcher id is ``number-of-rows``.

Suppose we want to keep track of how many rows are added/removed from tables
``patients`` and ``doctors``. The required config for this would be a list as
shown::

  # <watcher-config> for number-of-rows
  - table: patients
  - table: doctors

We can also do counting by grouping the table on specific columns. For example,
in this case, if we want to know the changes in patients count based on
``region`` and ``sex``, we can add a key ``groupby`` like this::

  - table: patients
    groupby:
      - region
      - sex
  - table: doctors

.. _number_of_rows_hash:

Number of rows (hash version)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is similar to :ref:`number_of_rows` but returns two numbers, one for count
of removed rows and other for count of added rows, instead of just one *change*
number. For doing this, it maintains a list of hashes for each row of the table
and checks for added/removed rows while diffing with another snapshot. Its
watcher id is ``number-of-rows-hash``.

Its config options are similar to that of :ref:`number_of_rows_hash`.

.. _schema_tables:

Tables in Schema
~~~~~~~~~~~~~~~~

This saves the current tables in schema and reports added/removed tables on
diffing. Its watcher id is ``tables-in-schema``.

It needs a list of schema as config option::

  # <watcher-config> for tables-in-schema
  - raw_tables
  - processed_tables

.. _schema_columns:

Columns in Schema
~~~~~~~~~~~~~~~~~

This saves all the columns currently employed in certain schema across all the
tables involved. This is useful to know if a table with new set of columns is
(it doesn't look for removed columns as of yet) added to the schema. Its watcher
id is ``columns-in-schema``.

Like :ref:`schema_tables`, it needs the list of schema as config::

  # <watcher-config> for columns-in-schema
  - raw_tables
  - processed_tables

.. _table_change:

Table change
~~~~~~~~~~~~

This keeps hashes of certain tables, specified in config, and compares it with
other snapshot to give a list of tables which don't match with their older
versions. Its watcher id is ``table-change``.

It watches a list of tables based on the following config::

  # <watcher-config> for table-change
  schemas:
    - raw_tables
    - processed_tables
  tables:
    - core

Given the above config, it saves hashes of:

- All tables from the schema ``raw_tables`` and ``processed_tables``
- ``core`` table.

As of now, the config requires both the fields, ``schemas`` and ``tables``, so
you need to pass in ``[]`` to any of these if not using it. For example, if you
only need to watch for the schema ``raw_tables`` use the following config::

  schemas:
    - raw_tables
  tables: []
