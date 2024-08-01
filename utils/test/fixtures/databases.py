import os

import pytest

from utils import configuration
from utils.test import databases


@pytest.fixture
def load_config(config_path: str):
    """Pytest fixture that loads the configuration object into the environment.

    This fixture loads the configuration object into the environment by calling `configuration.inject_config_to_env()` and yields the configuration object.

    Returns:
        dict[str, Any]: The configuration object.

    Usage:
        This fixture can be used in pytest tests by including it as an argument in the test function.

        Example:
        def test_something(load_config):
    """
    config = configuration.load_config(config_path=config_path)
    yield config


@pytest.fixture
def config():
    """Pytest fixture that provides the configuration object.

    This fixture retrieves the configuration object from the environment variable "CONFIG" and yields it.

    Returns:
        dict[str, Any]: The configuration object.

    Usage:
        This fixture can be used in pytest tests by including it as an argument in the test function.

        Example:
        def test_something(config):
            # Use the configuration object within the test
            ...
    """
    config = configuration.get_config()
    yield config


@pytest.fixture
def sql_database_uri(load_config: None):
    """Pytest fixture that provides the SQL database URI.

    This fixture retrieves the SQL database URI from the environment variable "DATABASE_URI" and yields it.

    Returns:
        str: The SQL database URI.

    Usage:
        This fixture can be used in pytest tests by including it as an argument in the test function.

        Example:
        def test_something(sql_database_uri):
            # Use the SQL database URI within the test
            ...
    """
    config = configuration.get_config()
    uri = config.get("database", {}).get("connection").get("uri")
    if uri is None:
        uri = os.environ.get("DATABASE_URI")
    yield uri


@pytest.fixture
def sql_database(sql_database_uri: str, load_config: None):
    """Pytest fixture that provides a SQL database object.

    This fixture takes the SQL database URI as an argument and creates a `SqlDatabase` object using the provided URI. It yields the `SqlDatabase` object, allowing it to be used in pytest tests.

    Args:
        sql_database_uri (str): The SQL database URI.

    Returns:
        SqlDatabase: The SQL database object.

    Usage:
        This fixture can be used in pytest tests by including it as an argument in the test function.

        Example:
        def test_something(sql_database):
            # Use the SQL database object within the test
            ...
    """
    database = databases.SqlDatabase(uri=sql_database_uri)
    yield database
