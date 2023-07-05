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

    def exec(self, command: str, *data):
        # Execute a command
        data = (*data,)
        command.replace("'%s'", "%s")
        self.cur.execute(command, data)

    def select(self):
        # Query the database and obtain data as Python objects
        command = "SELECT * FROM test;"
        data = ()
        self.exec(command, *data)
        self.cur.fetchone()
