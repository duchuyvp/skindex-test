from typing import Any

import sqlalchemy


class SqlDatabase:
    """A class representing a SQL database.

    Args:
        engine (sqlalchemy.engine.Engine, optional): The SQLAlchemy engine to use for database connections.
        uri (str, optional): The URI string to create a SQLAlchemy engine if `engine` is not provided.

    Attributes:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used for database connections.
        cached (dict): A dictionary to cache retrieved models.

    Methods:
        get(table: str, id: str) -> Any:
            Retrieves a model from the specified table by its id.

        remove(table: str, id: str):
            Removes a model from the specified table by its id.

        clear():
            Clears the cached models.

    Note:
        At least provide `engine` or `uri` when creating an instance of `SqlDatabase`.

    Usage:
        database = SqlDatabase(engine=my_engine)
        model = database.get('my_table', 'my_id')
        database.remove('my_table', 'my_id')
        database.clear()
    """

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine | None = None,
        uri: str | None = None,
    ):
        super().__init__()

        if engine is None and uri is None:
            raise ValueError("At least provide engine or uri")

        if engine is None:
            assert uri
            engine = sqlalchemy.create_engine(uri)

        self.engine = engine
        self.cached: dict[str, set[str]] = {}

    def get(self, table: str, id: str) -> Any:
        """Retrieves a model from the specified table by its id.

        Args:
            table (str): The name of the table.
            id (str): The id of the model to retrieve.

        Returns:
            Any: The retrieved model.

        Raises:
            sqlalchemy.exc.ResourceClosedError: If the execution of the SQL statement fails.
        """
        with self.engine.connect() as conn:
            self.cached[table] = set()
            self.cached[table].add(id)
            stm = sqlalchemy.text(f"SELECT * FROM \"{table}\" WHERE id = '{id}';")
            model = conn.execute(stm).mappings().fetchone()
            return model

    def remove(self, table: str, id: str):
        """Removes a model from the specified table by its id.

        Args:
            table (str): The name of the table.
            id (str): The id of the model to remove.

        Raises:
            sqlalchemy.exc.ResourceClosedError: If the execution of the SQL statement fails.
        """
        with self.engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"DELETE FROM {table} WHERE id = '{id}';"))

    def clear(self):
        """Clears the cached models."""
        for table, models in self.cached.items():
            for id in models:
                self.remove(table, id)
