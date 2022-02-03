from .keys import _PK
from .model import Model
import aiomysql
from .errors import InitializationError, MySQLErrors, SubstError
from typing import Dict, List, Union

class Database:
    _connection: aiomysql.Connection = None

    def __init__(
        self,
        _connection: aiomysql.Connection
    ) -> None:
        """
        Synchronous initialization method. Accepts an established aiomysql connection
        and returns a targa.Database wrapping it. Not intended to be called by user code.

        Parameters:
            _connection: aiomysql.Connection
                The established aiomysql connection to wrap
        
        Returns:
            Nothing
        """
        
        self._connection = _connection
    
    @staticmethod
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

    async def _ensure_connection(self) -> None:
        """
        Ensures that a connection to the remote database is both established and
        active.

        Parameters:
            None
        
        Returns:
            Nothing
        """

        if not self._connection:
            raise InitializationError("Database connection was never initialized")
        else:
            await self._connection.ping()
    
    async def insert(self, model_inst: Model) -> None:
        """
        Inserts the specified Targa model instance into the remote database as a new record.

        Parameters:
            model_inst: Model
                The Model instance to insert into the remote database.
        
        Returns:
            Nothing
        """

        # ensure that a connection is established
        await self._ensure_connection()

        # get the expected table name
        table_name: str = model_inst._get_table_name()

        # build up an INSERT INTO query making sure the escape any input data
        query: str = f"INSERT INTO {table_name} ({', '.join(model_inst.__annotations__.keys())})\n" + \
                     f"VALUES ("
        for field in model_inst.__annotations__:
            if model_inst.__dict__[field] is not None:
                query += f"'{self._connection.escape_string(str(model_inst.__dict__[field]))}', "
            else:
                query += 'NULL, '
        query = query[:-2] + ')'

        # execute the query then commit the result
        await self.query(query, _ensure_conn = False)
        await self._connection.commit()
    
    async def query(self, query: str, *substitutions, _ensure_conn: bool = True) -> Union[List[Dict], None]:
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
        if _ensure_conn:
            await self._ensure_connection()

        # perform any substitutions as necessary
        substitutions = [str(x) for x in substitutions]
        if len(substitutions) > 0:
            for n in range(len(substitutions)):
                # locate a '?' character
                index: int
                try:
                    index = query.index('?')
                except ValueError:
                    raise SubstError('Not enough values to substitute for in provided query')
                
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

    async def update(self, model_inst: Model, where_clause: str = None) -> None:
        """
        Updates the specified model in the remote database using an UPDATE statement
        which includes the specified WHERE clause.

        Parameters:
            model_inst: Model
                The model instance that should be updated in the remote database.

            where_clause: str = None
                The WHERE clause to include in the SQL statement. Optional if a primary key
                was annotated in this model.
        
        Returns:
            Nothing
        """

        # if no WHERE clause was provided, generate one based on a provided primary key annotation
        if not where_clause:
            # derive a list of annotation types
            annotation_types: List[type] = [type(x[1]) for x in model_inst.__annotations__.items()]

            # get the index of the first primary key annotation
            pk_field_index: int = annotation_types.index(_PK)

            # check that a primary key annotation was actually found
            pk_field: str
            if pk_field_index >= 0:
                pk_field = list(model_inst.__annotations__.keys())[pk_field_index]
            else:
                raise KeyError('A WHERE clause is required if a primary key was not annotated')

            # if it was, generate the WHERE clause
            where_clause = f"WHERE {pk_field} = '{self._connection.escape_string(model_inst.__dict__[pk_field])}'"

        # ensure that a connection is established
        await self._ensure_connection()

        # get the table name for this model instance
        table_name: str = model_inst._get_table_name()

        # build up an update query making sure to escape any input
        query: str = f"UPDATE {table_name}\nSET "
        for field in model_inst.__annotations__.keys():
            if model_inst.__dict__[field] is not None:
                query += f"{field} = '{self._connection.escape_string(str(model_inst.__dict__[field]))}', "
            else:
                query += f"{field} = NULL, "
        query = query[:-2] + '\n' + where_clause + ';'
    
        # execute the query then commit the result
        await self.query(query, _ensure_conn = False)
        await self._connection.commit()