""" Module providing function to read data from database
"""

import urllib.parse
from sqlalchemy import create_engine, text, types, Engine


def get_postgres_engine(
    host: str, user: str, pwd: str, port: int, database: str
) -> Engine:

    user = urllib.parse.quote_plus(user)
    pwd = urllib.parse.quote_plus(pwd)
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{database}"
    )

    return engine


def get_engine(
    server,
    database,
    driver,
    trusted_connection="yes",
    autocommit=True,
    fast_executemany=True,
    user="",
    pwd="",
    **kwargs,
):
    """Create a connection to a sql server via sqlalchemy
    Arguments:
    server -- The server name (str). e.g.: 'SQL2012PROD03'
    database -- The specific database within the server (str). e.g.: 'LowFlows'
    driver -- The driver to use for the connection (str). e.g.: SQL Server
    trusted_conn -- Is the connection to be trusted. Values are 'yes' or 'No' (str).
    """

    if driver == "SQL Server":
        engine = create_engine(
            f"mssql+pyodbc://{server}/{database}"
            f"?driver={driver}"
            f"&Trusted_Connection={trusted_connection}"
            f"&autocommit={autocommit}",
            fast_executemany=fast_executemany,
        )
    elif driver == "postgresql":
        user = urllib.parse.quote_plus(user)
        pwd = urllib.parse.quote_plus(pwd)
        port = kwargs.get("port", 5432)
        engine = create_engine(
            f"postgresql+psycopg2://{user}:{pwd}@{server}:{port}/{database}"
        )
    else:
        raise NotImplementedError("No other connections supported")
    return engine


def checkTableExists(dbcon, tablename):
    # dbcur = dbcon.cursor()
    dbcur = dbcon.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(
            tablename.replace("'", "''")
        )
    )
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def create_table(dbcon, tablename, tablesql):
    # dbcur = dbcon.cursor()
    dbcur = dbcon.execute(
        """
    CREATE TABLE [dbo].[{0}](
		{1}
	)
    """.format(
            tablename.replace("'", "''"), tablesql
        )
    )
    dbcur.close()


def truncate_table(dbcon, tablename):
    # dbcur = dbcon.cursor()
    dbcur = dbcon.execute(
        f"""
        TRUNCATE TABLE [dbo].[{tablename}]
    """
    )
    dbcur.close()


def createWktElement(geom):
    """Transform byte geometry to text WKT"""
    return geom.wkt


class Geometry(types.UserDefinedType):
    """Class to specify the geometry type to sqlalchimy for SQLServer"""

    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        # Note that this does *not* format the value to the expression text, but
        # the bind value key.
        return text(f"GEOMETRY::STGeomFromText(:{bindvalue.key}, 4326)").bindparams(
            bindvalue
        )
