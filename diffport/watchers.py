"""
Modules for watchers
"""

from abc import ABC, abstractmethod
from tabulate import tabulate
from typing import Dict, List
from .templates import *


class Watcher(ABC):

    @staticmethod
    @abstractmethod
    def take_snapshot(db, config: Dict):
        """
        Return a snapshot dictionary using the config and db.
        """
        ...

    @staticmethod
    @abstractmethod
    def diff(old, new):
        """
        Return a dictionary representing the diff between old and new snapshot.
        The output goes into report function for getting a markdown string.
        """
        ...

    @staticmethod
    @abstractmethod
    def report(diff) -> str:
        """
        Return a report in markdown format for given diff.
        """
        ...


class WatcherNumberOfRows(Watcher):
    """
    Watch for changes in number of rows in tables. Also provides grouped
    counts.
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Take snapshot for number of rows in given table grouped by asked fields

        config:
          [{groupby: [cols, ...]
            table: <string>},
           ...]
        """

        def get_table_hashes(table_config):
            if "groupby" in table_config:
                # group_fields = ", ".join(config["groupby"])
                # select_fields = f"{group_fields}, md5({config['table']}::text) as hash"
                # stmt = f"SELECT {select_fields} FROM {config['table']} ORDER BY {group_fields}"

                # # ORDER BY lets us switch rows on sequentially
                # grouped_data = []
                # hashes = [] # type: List[str]
                # prev_group_values = None
                # for res in db.query(stmt):
                #     group_values = [res[field] for field in config["groupby"]]

                #     if prev_group_values is None:
                #         prev_group_values = group_values

                #     if group_values != prev_group_values:
                #         grouped_data.append(group_values + list(hashes))
                #         prev_group_values = group_values
                #         hashes = []
                #     else:
                #         hashes.append(res["hash"])
                # return grouped_data
                pass
            else:
                stmt = f"SELECT md5({table_config['table']}::text) as hash FROM {table_config['table']}"
                return [r["hash"] for r in db.query(stmt)]

        return [[tc["table"], get_table_hashes(tc)] for tc in config]

    @staticmethod
    def diff(old, new):

        def _get_diff(old_hashes, new_hashes):
            """
            Get diff counts between list of hashes
            """

            return [len(set(old_hashes) - set(new_hashes)), len(set(new_hashes) - set(old_hashes))]

        output = []
        for table, hashes in old:
            if type(hashes[0]) == str:
                # This data is without grouping
                new_idx = [row[0] for row in new].index(table)
                if new_idx > -1:
                    diff = _get_diff(hashes, new[new_idx][1])
                    output.append([
                        table,
                        {
                            "removed": diff[0],
                            "added": diff[1]
                        },
                        "basic"
                    ])
            else:
                # Work with group values of the old snapshot
                # new_group_identifiers = [group_row[:-1] for group_row in new]
                # changes = []
                # for group_row in old:
                #     old_group_identifier = group_row[:-1]
                #     if old_group_identifier in new_group_identifiers:
                #         new_hashes = new[new_group_identifiers.index(old_group_identifier)][-1]
                #         old_hashes = group_row[-1]
                #         diff = _get_diff(old_hashes, new_hashes)
                #         if diff != [0, 0]:
                #             changes.append([*old_group_identifier, *diff])

                # return changes
                pass
        return output

    @staticmethod
    def report(diff) -> str:
        data = []
        for table_diff in diff:
            if table_diff[-1] == "basic":
                data.append([
                    table_diff[0],
                    f"{table_diff[1]['removed']} rows removed, {table_diff[1]['added']} added."
                ])
            else:
                # data.append([
                #     table_diff[0],
                #     tabulate(diff, headers=[*config["groupby"], "rows removed", "rows added"])
                # ])
                pass

        return tpl_number_of_rows.render(
            data=data,
        )


class WatcherTablesInSchema(Watcher):
    """
    Watch for tables added/removed in schema
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save list of tables in given schema

        config: [<schema>, ...]
        """

        def get_schema_tables(schema):
            res = db.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
            return [r["table_name"] for r in res]

        return [[schema, get_schema_tables(schema)] for schema in config]

    @staticmethod
    def diff(old, new):
        # Only using schemas which are available in old
        output = []
        for schema, tables in old:
            new_idx = [row[0] for row in new].index(schema)
            if new_idx > -1:
                removed_tbls = list(set(tables) - set(new[new_idx][1]))
                added_tbls = list(set(new[new_idx][1]) - set(tables))
                if not (len(removed_tbls) == len(added_tbls) == 0):
                    output.append([schema, {
                        "removed": removed_tbls,
                        "added": added_tbls,
                    }])
        return output

    @staticmethod
    def report(diff) -> str:

        return tpl_tables_in_schema.render(
            data=diff
        )


class WatcherColumnsInSchema(Watcher):
    """
    Watch for columns added/removed considering all tables of a schema at a time
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save all distinct table in given schema

        config: [<schema>, ...]
        """

        def get_schema_columns(schema):
            res = db.query(f"SELECT DISTINCT column_name FROM information_schema.columns WHERE table_schema = '{schema}'")
            return [r["column_name"] for r in res]

        return [[schema, get_schema_columns(schema)] for schema in config]

    @staticmethod
    def diff(old, new):
        # Only using schemas which are available in old
        output = []
        for schema, columns in old:
            new_idx = [row[0] for row in new].index(schema)
            if new_idx > -1:
                removed_cols = list(set(columns) - set(new[new_idx][1]))
                added_cols = list(set(new[new_idx][1]) - set(columns))
                if not (len(removed_cols) == len(added_cols) == 0):
                    output.append([schema, {
                        "removed": removed_cols,
                        "added": added_cols,
                    }])
        return output

    @staticmethod
    def report(diff) -> str:

        return tpl_columns_in_schema.render(
            data=diff
        )


class WatcherTableChange(Watcher):
    """
    Watch for table changes
    """

    @staticmethod
    def take_snapshot(db, config: Dict):
        """
        Save all table hashes in given schema

        config:
          schemas:
            - <schema-one>
            - <schema-two>
          tables:
            - <table-one>
            - <table-two>
        """

        # Create a list of tables to look for
        tables = [] # type: List[str]
        try:
            tables += config["tables"]
        except KeyError:
            pass

        if "schemas" in config:
            for schema in config["schemas"]:
                res = db.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
                tables += [f"{schema}.{r['table_name']}" for r in res]

        # Create hash of tables
        def _table_hash(table):
            res = db.query(f"""SELECT md5(array_agg(md5((t.*)::varchar))::varchar) as hash
              FROM (
                SELECT *
                  FROM {table}
                ORDER BY 1
              ) AS t""")
            return res.next()["hash"]

        return [[table, _table_hash(table)] for table in tables]

    @staticmethod
    def diff(old, new):
        changed = []
        for table, checksum in old:
            new_idx = [row[0] for row in new].index(table)
            if new_idx > -1:
                if new[new_idx][1] != checksum:
                    changed.append(table)

        return changed

    @staticmethod
    def report(diff) -> str:

        return tpl_table_change.render(
            changed_tables=diff
        )
