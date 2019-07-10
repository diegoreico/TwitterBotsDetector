import logging

import pymysql

from botdetector.config import twitter_config as config


class DataSource(object):
    def __init__(self):
        self.__connection = None
        self.cursor = None

        self.__host = config.mysql_host()
        self.__port = config.mysql_port()
        self.__user = config.mysql_user()
        self.__password = config.mysql_password()
        self.__database = config.mysql_database()

    def connect(self):
        try:
            self.__connection = pymysql.connect(host=self.__host, port=self.__port, user=self.__user,
                                                passwd=self.__password,
                                                db=self.__database)

            self.cursor = self.__connection.cursor()
        except pymysql.MySQLError:
            logging.error("Cannot connect to MySQL database")

    def disconnect(self):
        self.cursor = None
        self.__connection.close()

    @property
    def cursor(self):
        return self.__cursor

    @cursor.setter
    def cursor(self, cursor):
        self.__cursor = cursor
