"""
Module for helping with database connections
"""

import json
import os
import sys


def env_connection():
    """
    Return connection string from environment variable
    """

    try:
        return os.environ["DATABASE_URL"]
    except KeyError:
        print("DATABASE_URL environment variable not set")
        sys.exit(1)


def json_connection(json_path: str, dialect: str) -> str:
    """
    Return connection string using the json path
    """

    with open(json_path) as fp:
        c = json.load(fp)

    return f"{dialect}://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['dbname']}"


def get_connection_string(source: str, dialect: str):
    """
    Return connection string for dataset.
    The format is dialect://user:password@host/dbname
    """

    if source == "env":
        return env_connection()
    elif source.endswith(".json"):
        return json_connection(source, dialect)
