import pymysql

from ars.data_sources import DataSource


class TestUnitDataSource(object):

    def test_database_connection(self):
        data_source = DataSource()
        data_source.connect()

        assert (data_source.cursor is not None)
        assert (type(data_source.cursor) is pymysql.cursors.Cursor)

    def test_database_disconnection(self):
        data_source = DataSource()
        data_source.connect()
        data_source.disconnect()

        assert (data_source.cursor is None)
