# ./app/postgresql_hdr
import psycopg2 as pg2


class PostgresConnectionParameters:

    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port


class PostgresqlHdr:

    def __init__(
            self,
            pcp: PostgresConnectionParameters = None,
            dbname: str = None,
            user: str = None,
            password: str = None,
            host: str = None,
            port: str = None
    ):
        self.cur = None
        self.conn = None
        self._pcp = pcp

        if (
            self._pcp is None and
            (
                dbname is not None or
                user is not None or
                password is not None or
                host is not None or
                port is not None
            )
        ):
            self._pcp = PostgresConnectionParameters(dbname, user, password, host, port)

        # Connect to db and create cursor
        if self._pcp is not None:
            self.connect_db()
            self.create_cursor()

    def connect_db(self):
        # Connect to an existing database
        self.conn = pg2.connect(
            dbname=self._pcp.dbname,
            user=self._pcp.user,
            password=self._pcp.password,
            host=self._pcp.host,
            port=self._pcp.port
        )

    def create_cursor(self):
        # Open a cursor to perform database operations
        self.cur = self.conn.cursor()

    def close(self):
        # Close communication with the database
        self.cur.close()
        self.conn.close()

    def commit(self):
        # Make the changes to the database persistent
        self.conn.commit()

    def exec(self, command: str, *data, commit=False):
        # Execute a command
        data = (*data,)
        command.replace("'%s'", "%s")
        try:
            self.cur.execute(command, data)
            if commit:
                self.commit()
            status = True
        except pg2.errors.UniqueViolation:
            self.conn.rollback()
            status = "UNIQUE"

        return status

    def select(self, table, columns=None, sql_conditions=""):
        # Query the database
        if columns is None:
            columns_str = "*"
        else:
            columns_str = f"{', '.join(columns)}"

        command = f"SELECT {columns_str} FROM {table} {sql_conditions};"
        data = ()
        self.exec(command, *data)
        selected_data = self.cur.fetchall()

        # Get table column names
        if columns in ["*", "", None, " "]:
            command = f"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{table}';"
            data = ()
            self.exec(command, *data)
            columns = [x[0] for x in self.cur.fetchall()]

        # result as Json
        return [{col: row_val for col, row_val in zip(columns, row)} for row in selected_data]

    def insert_one(self, table, data_dict: dict):
        """

        :param table:           | table_name
        :param data_dict:       | {"column_name": "value", ...}
        :return:
        """

        columns_str = f"({', '.join([*data_dict.keys()])})"
        values_placeholders = f"({', '.join(['%s' for _ in data_dict.keys()])})"
        command = f"INSERT INTO {table} {columns_str} VALUES {values_placeholders};"

        data = [*data_dict.values()]
        self.exec(command, *data, commit=True)

    def update(self, table, data_dict, sql_conditions):
        """
        :param table: str
        :param data_dict:           | {"column_name": "value", ...}
        :param sql_conditions: str
        :return:
        """
        if len([*data_dict.keys()]) > 1:
            columns_str = f"({', '.join([*data_dict.keys()])})"
            values_placeholders = f"({', '.join(['%s' for _ in data_dict.keys()])})"
        else:
            columns_str = [*data_dict.keys()][0]
            values_placeholders = '%s'

        command = f"UPDATE {table} " \
                  f"SET {columns_str} = {values_placeholders} " \
                  f"{sql_conditions};"

        data = [*data_dict.values()]
        self.exec(command, *data, commit=True)

    def delete_rows(self, table, sql_conditions):
        command = f"DELETE FROM {table} " \
                  f"{sql_conditions};"
        self.exec(command, commit=True)

