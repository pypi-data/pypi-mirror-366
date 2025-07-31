from unittest.mock import MagicMock

class InfluxDBClientMock:
    def __init__(self, *args, **kwargs):
        # Use MagicMock to mock all methods
        self.write_points = MagicMock(return_value=True)
        self.query = MagicMock(return_value=MagicMock(raw={"series": [{"name": "mock_series", "values": [[1, "mock_value"]], "columns": ["time", "value"]}]}))
        self.switch_database = MagicMock()
        self.create_database = MagicMock()
        self.drop_database = MagicMock()
        self.close = MagicMock()

        # Mock connection attributes
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 8086)
        self.username = kwargs.get("username", "root")
        self.password = kwargs.get("password", "root")
        self.database = kwargs.get("database", "testdb")