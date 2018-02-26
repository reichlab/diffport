"""
Modules for watchers
"""

from abc import ABC, abstractmethod
from tabulate import tabulate
from typing import Dict, List, Any, Tuple, Union, Callable
from .templates import *
from functools import partial
from copy import deepcopy
from pydash import py_


# A snapshot with config and snaplist
SnapItem = Tuple[Union[str, List[str]], Any]
SnapList = List[SnapItem]
Snap = Dict[str, Any]


def items_common(a: SnapList, b: SnapList) -> Tuple[SnapList, SnapList]:
    """
    Return new [a, b] for SnapItems that are present in a AND b.
    The items are identified using the first element of each row and are returned
    ordered as in a.
    """

    n_a = []
    n_b = []
    for item_id, item_data in a:
        idx_b = py_.find_index(b, lambda x: x[0] == item_id)
        if idx_b > -1:
            n_a.append((item_id, item_data))
            n_b.append((item_id, b[idx_b][1]))

    return n_a, n_b


def items_sub(a: SnapList, b: SnapList) -> SnapList:
    """
    Return SnapItems from a which are not in b.
    """

    return py_.difference_by(a, b, lambda x: x[0])


def find_col_diff(col_data_old: SnapList, col_data_new: SnapList, diff_fn: Callable):
    """
    Return differences between columns using the diff_fn.

    Parameters
    ----------
    col_data_old : SnapList
        Tuple of two items. First is column grouping identifier, e.g. for a
        table with grouping ['city', 'team'], this value might be
        ['Sydney', 'Sydney Sixers']. Second item is (old) data for that grouping.
    col_data_new : SnapList
        Similar as col_data_old but from the new snapshot.
    diff_fn : Callable(old, new)
        Callable which returns an object representing difference between two
        data as defined in the SnapLists above. It should also handle `None` as
        parameter. It should return `None` for no diff.
    """

    output = [] # type: SnapList

    # First work on the common items
    common_old, common_new = items_common(col_data_old, col_data_new)
    for old_col_set, new_col_set in zip(common_old, common_new):
        diff = diff_fn(old_col_set[1], new_col_set[1])
        if diff is not None:
            output.append((old_col_set[0], diff))

    # Now do only items which are only present in old data
    only_removed = items_sub(col_data_old, col_data_new)
    for col_set in only_removed:
        diff = diff_fn(col_set[1], None)
        if diff is not None:
            output.append((col_set[0], diff))

    # Finally do items which are only in new data
    only_added = items_sub(col_data_new, col_data_old)
    for col_set in only_added:
        diff = diff_fn(None, col_set[1])
        if diff is not None:
            output.append((col_set[0], diff))

    return output


class Watcher(ABC):

    @staticmethod
    @abstractmethod
    def take_snapshot(db, config: Dict) -> Snap:
        """
        Return a snapshot dictionary using the config and db.
        """
        ...

    @staticmethod
    @abstractmethod
    def diff(old_snap: Snap, new_snap: Snap):
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


class NumberOfRowsHash(Watcher):
    """
    Watch for changes in number of rows in tables. Return the number of rows removed
    and added based on saved hash of each row.
    """

    @staticmethod
    def take_snapshot(db, config: Any) -> Snap:
        """
        Take snapshot for number of rows in given table grouped by asked fields

        config:
          [{groupby: [cols, ...]
            table: <string>},
           ...]
        """

        def _get_table_hashes(table_config):
            if "groupby" in table_config:
                group_fields = ", ".join(table_config["groupby"])
                select_fields = f"{group_fields}, md5({table_config['table']}::text) as hash"
                stmt = f"SELECT {select_fields} FROM {table_config['table']} ORDER BY {group_fields}"

                grouped_data = []
                for res in db.query(stmt):
                    group_values = [res[field] for field in table_config["groupby"]]

                    group_values_idx = py_.find_index(grouped_data, lambda x: x[0] == group_values)
                    if group_values_idx > -1:
                        grouped_data[group_values_idx][1].append(res["hash"])
                    else:
                        grouped_data.append([group_values, [res["hash"]]])

                return grouped_data
            else:
                stmt = f"SELECT md5({table_config['table']}::text) as hash FROM {table_config['table']}"
                return [r["hash"] for r in db.query(stmt)]

        return {
            "config": config,
            "data": [(tc["table"], _get_table_hashes(tc)) for tc in config]
        }

    @staticmethod
    def diff(old_snap: Snap, new_snap: Snap):
        old, new = old_snap["data"], new_snap["data"]
        old, new = items_common(old, new)

        def _get_diff(old_hashes, new_hashes, skip=False):
            if old_hashes is None:
                return { "removed": 0, "added": len(set(new_hashes)) }
            elif new_hashes is None:
                return { "removed": len(set(old_hashes)), "added": 0 }
            else:
                removed = len(set(old_hashes) - set(new_hashes))
                added = len(set(new_hashes) - set(old_hashes))
                if skip and (removed == added == 0):
                    return None
                else:
                    return { "removed": removed, "added": added }

        output = [] # type: Any
        for row_old, row_new in zip(old, new):
            if type(row_old[1][0]) == str:
                # This data is without grouping, each row_old/new[1] is like ["hash1", "hash2", ...]
                diff = _get_diff(row_old[1], row_new[1])
                output.append([row_old[0], diff, "basic"])
            else:
                # This is grouped data, each row_old/new[1] is like [[grouped-cols, ...], [hashes]]
                col_set_diff = find_col_diff(row_old[1], row_new[1], partial(_get_diff, skip=True))
                output.append([row_old[0], col_set_diff, "grouped"])

        return {
            "config": new_snap["config"],
            "data": output
        }

    @staticmethod
    def report(diff) -> str:
        data = []
        for table_diff in diff["data"]:
            if table_diff[-1] == "basic":
                data.append([
                    table_diff[0],
                    f"{table_diff[1]['removed']} rows removed, {table_diff[1]['added']} added."
                ])
            elif table_diff[-1] == "grouped":
                table_name = table_diff[0]
                headers = py_.find(diff["config"], lambda x: x["table"] == table_name)["groupby"]

                data.append([
                    table_name,
                    tabulate([[*row[0], row[1]["removed"], row[1]["added"]] for row in table_diff[1]],
                             headers=[*headers, "rows removed", "rows added"])
                ])

        return tpl_number_of_rows_hash.render(data=data)


class NumberOfRows(Watcher):
    """
    Watch for changes in number of rows in tables and return only the difference.
    """

    @staticmethod
    def take_snapshot(db, config: Any) -> Snap:
        """
        Take snapshot for number of rows in given table grouped by asked fields

        config:
          [{groupby: [cols, ...]
            table: <string>},
           ...]
        """

        def _get_table_counts(table_config):
            """
            For a table in config, if there is no groupby, return a tuple
            like (table_name: str, count: int)
            If there is a groupby field in config, return a the grouped counts in a list
            where each item is a pair of group by field values and count.
            """

            if "groupby" in table_config:
                group_fields = ", ".join(table_config["groupby"])
                select_fields = f"{group_fields}, count(*) as count"
                stmt = f"SELECT {select_fields} FROM {table_config['table']} GROUP BY {group_fields} ORDER BY {group_fields}"

                counts = []
                for res in db.query(stmt):
                    counts.append([[res[field] for field in table_config["groupby"]], res["count"]])
                return counts
            else:
                stmt = f"SELECT count(*) as count FROM {table_config['table']}"
                return db.query(stmt).next()["count"]

        return {
            "config": config,
            "data": [(tc["table"], _get_table_counts(tc)) for tc in config]
        }

    @staticmethod
    def diff(old_snap: Snap, new_snap: Snap):
        old, new = old_snap["data"], new_snap["data"]
        old, new = items_common(old, new)

        def _get_diff(old_counts, new_counts):
            if old_counts is None:
                return new_counts
            elif new_counts is None:
                return -old_counts
            else:
                diff = new_counts - old_counts
                return None if diff == 0 else diff

        output = [] # type: Any
        for row_old, row_new in zip(old, new):
            if type(row_old[1]) == int:
                # This data is without grouping, each row_old/new[1] is a direct count
                diff = _get_diff(row_old[1], row_new[1])
                output.append([row_old[0], diff, "basic"])
            else:
                # This is grouped data, each row_old/new[1] is like [[grouped-cols, ...], count]
                col_set_diff = find_col_diff(row_old[1], row_new[1], _get_diff)
                output.append([row_old[0], col_set_diff, "grouped"])

        return {
            "config": new_snap["config"],
            "data": output
        }

    @staticmethod
    def report(diff) -> str:
        data = []
        for table_diff in diff["data"]:
            if table_diff[-1] == "basic":
                data.append([table_diff[0], f"Changes: {table_diff[1]}"])
            elif table_diff[-1] == "grouped":
                table_name = table_diff[0]
                headers = py_.find(diff["config"], lambda x: x["table"] == table_name)["groupby"]

                data.append([
                    table_name,
                    tabulate([[*row[0], row[1]] for row in table_diff[1]],
                             headers=[*headers, "changes"])
                ])

        return tpl_number_of_rows.render(data=data)


class SchemaTables(Watcher):
    """
    Watch for tables added/removed in schema
    """

    @staticmethod
    def take_snapshot(db, config: Dict) -> Snap:
        """
        Save list of tables in given schema

        config: [<schema>, ...]
        """

        def get_schema_tables(schema):
            res = db.query(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
            return [r["table_name"] for r in res]

        return {
            "config": config,
            "data": [(schema, get_schema_tables(schema)) for schema in config]
        }

    @staticmethod
    def diff(old_snap: Snap, new_snap: Snap):
        old, new = old_snap["data"], new_snap["data"]
        old, new = items_common(old, new)
        output = []
        for row_old, row_new in zip(old, new):
            removed_tbls = list(set(row_old[1]) - set(row_new[1]))
            added_tbls = list(set(row_new[1]) - set(row_old[1]))
            if not (len(removed_tbls) == len(added_tbls) == 0):
                output.append([row_old[0], {
                    "removed": removed_tbls,
                    "added": added_tbls,
                }])

        return {
            "config": new_snap["config"],
            "data": output
        }

    @staticmethod
    def report(diff) -> str:
        return tpl_schema_tables.render(data=diff["data"])


class SchemaColumns(Watcher):
    """
    Watch for columns added/removed considering all tables of a schema at a time
    """

    @staticmethod
    def take_snapshot(db, config: Dict) -> Snap:
        """
        Save all distinct table in given schema

        config: [<schema>, ...]
        """

        def get_schema_columns(schema):
            res = db.query(f"SELECT DISTINCT column_name FROM information_schema.columns WHERE table_schema = '{schema}'")
            return [r["column_name"] for r in res]

        return {
            "config": config,
            "data": [(schema, get_schema_columns(schema)) for schema in config]
        }

    @staticmethod
    def diff(old_snap: Snap, new_snap: Snap):
        old, new = old_snap["data"], new_snap["data"]
        old, new = items_common(old, new)
        output = []
        for row_old, row_new in zip(old, new):
            removed_cols = list(set(row_old[1]) - set(row_new[1]))
            added_cols = list(set(row_new[1]) - set(row_old[1]))
            if not (len(removed_cols) == len(added_cols) == 0):
                output.append([row_old[0], {
                    "removed": removed_cols,
                    "added": added_cols,
                }])

        return {
            "config": new_snap["config"],
            "data": output
        }

    @staticmethod
    def report(diff) -> str:
        return tpl_schema_columns.render(data=diff["data"])


class TableChange(Watcher):
    """
    Watch for table changes
    """

    @staticmethod
    def take_snapshot(db, config: Dict) -> Snap:
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

        return {
            "config": config,
            "data": [(table, _table_hash(table)) for table in tables]
        }

    @staticmethod
    def diff(old_snap: Snap, new_snap: Snap):
        old, new = old_snap["data"], new_snap["data"]
        old, new = items_common(old, new)

        changed = []
        for row_old, row_new in zip(old, new):
            if row_new[1] != row_old[1]:
                changed.append(row_old[0])

        return {
            "config": new_snap["config"],
            "data": changed
        }

    @staticmethod
    def report(diff) -> str:
        return tpl_table_change.render(changed_tables=diff["data"])
