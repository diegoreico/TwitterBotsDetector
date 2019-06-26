import os


# DATABASE CONFIGURATION
def mysql_host() -> str:
    return os.getenv('MYSQL_HOST')


def mysql_port() -> int:
    return int(os.getenv('MYSQL_PORT'))


def mysql_user() -> str:
    return os.getenv('MYSQL_USER')


def mysql_password() -> str:
    return os.getenv('MYSQL_PASSWORD')


def mysql_database() -> str:
    return os.getenv('MYSQL_DATABASE')
