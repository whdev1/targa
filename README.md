![banner](https://user-images.githubusercontent.com/90288849/151036869-f4f2b51e-e3c3-41fe-a0b6-9d8fc58c8a15.jpg)

<div align="center">
    <em>
        A lightweight async Python library for MySQL queries and modeling. 
    </em>
</div>

## Installation
The latest version of Targa can be downloaded and installed using `pip`.

```
pip install targa
```

Any requirements (including `aiomysql`) should be automatically installed for you.

## Usage
### Connecting to a database
The `targa.Database.connect` method may be used to connect to an existing MySQL database. This method returns a `targa.Database` instance that can be used to issue queries.

```Python
import asyncio
import targa

async def main():
    database = targa.Database.connect(
        host          = '', # hostname or IP of the database server
        username      = '', # username to connect with
        password      = '', # password to connect with
        database_name = ''  # name of the database instance to connect to
    )

if __name__ == '__main__':
    asyncio.run(main())
```

## Issuing a query
Once a `targa.Database` is initialized, the `query` method may be used to execute SQL queries. For example, consider a scenario where the rows in the following `persons` table need to be read:

| id | first_name | occupation |
|----|------------|------------|
| 1  | Will       | Developer  |
| 2  | John       | Accountant |
| 3  | Sue        | Engineer   |

Assuming a database connection has already been established, these rows could be accessed as follows:

```Python
import asyncio
import targa

async def main():
    # ... database connection already established

    persons = await database.query('SELECT * FROM persons')

    for person_dict in persons:
        print(person_dict)

if __name__ == '__main__':
    asyncio.run(main())
```

The `query` method returns each result row as a `dict` mapping the column names as keys to the row values. As a result, this program would output:

```Python
{'id': 1, 'first_name': 'Will', 'occupation': 'Developer'}
{'id': 2, 'first_name': 'John', 'occupation': 'Accountant'}
{'id': 3, 'first_name': 'Sue', 'occupation': 'Engineer'}
```

## Defining models
Object models in Targa are represented as annotated Python classes that inherit the `targa.Model` base class. For example, a `Person` model for the table previously discussed would look like this:

```Python
import targa

class Person(targa.Model):
    id: int
    first_name: str
    occupation: str
```

Once this model is defined, an individual dict returned from querying the `persons` table could be wrapped as follows:

```Python
import asyncio
import targa

async def main():
    # ... database connection already established

    persons = await database.query('SELECT * FROM persons')

    for person_dict in persons:
        print(Person(**person_dict))

if __name__ == '__main__':
    asyncio.run(main())
```

This program would output the following:

```Python
Person(id=1, name='Will', occupation='Developer')
Person(id=2, name='John', occupation='Accountant')
Person(id=3, name='Sue', occupation='Engineer')
```

The fields of each Targa model are type checked as they are instantiated and may be accessed just like the fields of any other Python class.