import logging
from pathlib import Path
from sqlite3 import Connection

from django.db.backends.sqlite3 import base
from django.utils.asyncio import async_unsafe

logger = logging.getLogger(__name__)

try:
    LIBRARY_NAME = list(Path(__file__).parent.glob("_lib*")).pop()
except Exception:
    LIBRARY_NAME = None


class DatabaseClient(base.DatabaseClient):
    library_name = LIBRARY_NAME

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        # MacOS's build of sqlite does not support loading modules by default
        # so on MacOS we want to allow users to override the sqlite path if needed
        args = [
            settings_dict.get("CLIENT", cls.executable_name),
            settings_dict["NAME"],
            "-cmd",
            f".load {cls.library_name}",
            *parameters,
        ]
        return args, None


class DatabaseWrapper(base.DatabaseWrapper):
    vendor = "markdowndb"
    display_name = "SQLite with Markdown virtual table"

    client_class = DatabaseClient

    @async_unsafe
    def get_new_connection(self, conn_params):
        conn: Connection = super().get_new_connection(conn_params)
        conn.enable_load_extension(True)
        conn.load_extension(str(self.client_class.library_name))

        return conn

    def init_connection_state(self):
        """
        Define our tables when connecting to a database

        When Django updates a connection to our Database, we want to loop through
        all applicable models and pass along our schema and file paths using the
        CREATE VIRTUAL TABLE statement.

        We use the underlying schema_editor.table_sql method which can give us a
        valid CREATE TABLE statement for each of our Model classes.

        See also: https://sqlite.org/vtab.html#usage
        """
        super().init_connection_state()
        from django.apps import apps

        with self.schema_editor() as schema_editor:
            for app_model in apps.get_models():
                if app_model._meta.required_db_vendor == self.vendor:
                    sql, _params = schema_editor.table_sql(app_model)
                    model_path = self.settings_dict["ROOT"] / app_model._meta.label
                    create_table = f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS temp.{app_model._meta.db_table}
            USING {self.vendor}(schema='{sql}', path='{model_path}');
            """.strip()
                    schema_editor.execute(create_table)
