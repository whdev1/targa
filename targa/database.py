from operator import sub
import aiomysql
from .errors import InitializationError, MySQLErrors, SubstError
from typing import Dict, List, Union

class Database:
    _connection: aiomysql.Connection = None

    def __init__(
        self,
        _connection: aiomysql.Connection
    ) -> None:
        self._connection = _connection
    
    async def connect(
        host: str,
        username: str,
        password: str,
        database_name: str,
        port: int = 3306,
        autocommit: bool = True
    ):
        """
        Initiates a new async MySQL connection based on the provided credentials.

        Parameters:
            host: str
                The hostname or IP of the database server to connect to.
            
            username: str
                The username to log into the database with.
            
            password: str
                The password associated with the provided username.
            
            database_name: str
                The name of the database instance to connect to.
            
            port: int = 3306
                The port to connect to. (3306 by default)
            
            autocommit: bool = True
                Represents whether or not this database connection should lock or
                autocommit queries.
        
        Returns:
            A new targa.Database instance representing the established connection.
        """

        # initialize an aiomysql connection and wrap a new Targa database instance around it
        return Database(
            await aiomysql.connect(
                host       = host,
                user       = username,
                password   = password,
                db         = database_name,
                autocommit = autocommit
            )
        )

    def _ensure_connection(self) -> None:
        if not self._connection:
            raise InitializationError("Database connection was never initialized")
    
    async def query(self, query: str, *substitutions) -> Union[List[Dict], None]:
        """
        Issues the specified query to the remote database and gets a list of dicts
        representing the rows that were returned. If no rows were received, None is
        returned.

        Performs escaped substitutions for "?" using the provided values.

        Parameters:
            query: str
                The SQL query to send to the remote database.
            
            *substitutions
                (Optional) A list of values to substitute for "?"
        
        Returns:
            Either a list of dicts representing the returned rows or None if no rows
            were returned.
        """

        # ensure that a connection is established
        self._ensure_connection()

        # perform any substitutions as necessary
        substitutions = [str(x) for x in substitutions]
        if len(substitutions) > 0:
            for n in range(len(substitutions)):
                # locate a '?' character
                index: int
                try:
                    index = query.index('?')
                except ValueError:
                    raise SubstError('Not enough value to substitute for in provided query')
                
                # perform a substitution for the '?' ensuring that any input strings are escaped
                query = query[:index] + self._connection.escape_string(substitutions[n]) + query[index + 1:]
        
        column_names: List
        rows: List
        async with self._connection.cursor() as cursor:
            # execute the query and get the response columns and rows from the datrabase. the response
            # will be provided as a tuple of tuples so it's converted to a list of dicts
            #
            # this statement is wrapped in a try so that the database client will ping and reconnect
            # if the connection has been lost for some reason (i.e. inactivity)
            runtime_error_occured: bool = False
            try:
                await cursor.execute(query)
            except Exception as outer_ex:
                await self._connection.ping()

                # sometimes when this point is reached the query will have been executed but
                # a RuntimeError was thrown. if a duplicate primary key error is raised and a 
                # RuntimeError already occured previously, this is the case. (this appears to
                # be brought on by a bug in aiomysql)
                try:
                    await cursor.execute(query)
                except Exception as e:
                    if isinstance(outer_ex, RuntimeError) and len(e.args) > 0 and e.args[0] == MySQLErrors.duplicate_primary_key:
                        pass
                    else:
                        raise e
            
            # check if data was actually returned
            if cursor.description:
                column_names = [x[0] for x in list(cursor.description)]
                rows = list(await cursor.fetchall())
            else:
                return None

        # zip each of the returned rows into a dict along with the returned column names.
        return [
            dict(
                zip(column_names, row)
            ) for row in rows
        ]