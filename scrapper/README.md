# Borgwarner ETL Tool

## Index

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Tests](#tests)
6. [Run](#run)

## <a name="overview">Overview</a>



## <a name="requirements">Requirements</a>

This project has been developed using [Setuptools](https://setuptools.readthedocs.io/en/latest/). 
So, `Python 3.6` and `pip3` are required.

You also need command line utility `ssconvert`, you can install it on Ubuntu using the following command:

```
apt-get install ssconvert
```

an alternative to install this package in the system is to install the following package 

```bash
apt-get install gnumeric
```

`ssconvert` version used for development was `1.12.35`

## <a name="installation">Installation</a>

All the other required python packages may be installed using the command:

```bash
pip3 install .

# or may be required

pip3 install . --user
```

A new requirement must be added to the `install_requires` property within the `setup.py` file.

## <a name="configuration">Configuration</a> 

All the configuration variables are included on **.env** files. For 
further information read the [related documentation](https://pypi.org/project/python-dotenv/). An example **.env** file is provided `.env.example` you can use it as a base **.env** file if you rename it to `.env`

## <a name="tests">Tests</a>

```bash
# All tests
pytest

# All tests verbose mode (not encouraged use logging module instead)
pytest -s

# Unit tests
pytest etl/tests/unit

# Integration tests
pytest etl/tests/integration

# Validation tests
pytest etl/tests/validation
```

## <a name="run">Run</a>

The package has a command-line entry point configured. This entry point is built using the library 
[Click](https://palletsprojects.com/p/click/). To get all the possible commands, use `borgwarner-etl --help`.

```bash
# starts a server with the HTTP ETL API
borgwarner-etl server
```

### Api documentation

Swagger generated API documentation for a running server, can be found at `http://ip:port/docs` or `http://ip:port/redocs`

![doc](./assets/doc.png)

![redoc](./assets/redoc.png)