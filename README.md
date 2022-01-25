![banner](https://user-images.githubusercontent.com/90288849/151036869-f4f2b51e-e3c3-41fe-a0b6-9d8fc58c8a15.jpg)

<div align="center">
    <em>
        A lightweight async library for MySQL queries and modelling. 
    </em>
</div>

## Introduction

## Installation
The latest version of Targa can be downloaded and installed using `pip`.

```
pip install targa
```

Any requirements (including `aiomysql`) should be automatically installed for you.

## Usage
### Connecting to a database
The `targa.Database.connect` method may be used to connect to an existing MySQL database.

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