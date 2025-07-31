from datetime import datetime
import unittest
from unittest.mock import MagicMock, call
import uuid

from esdl import Battery
from influxdb import InfluxDBClient
from dots_infrastructure.test_infra.InfluxDBClientMock import InfluxDBClientMock

from dots_infrastructure.influxdb_connector import InfluxDBConnector

class TestInfluxDBWriterLogic(unittest.TestCase):

    def setUp(self):
        self.influx_connector = InfluxDBConnector("test-host", "test-port", "test-user", "test-pwd", "test-db-name")
        self.influx_connector.connect = MagicMock(return_value=InfluxDBClientMock())

    def test_writing_to_influx_happens_in_chunks(self):
        # Arrange
        test_battery_id = str(uuid.uuid4())
        battery = Battery(name='battery_test', id=test_battery_id, capacity=5.0*3.6e6 ,
                              chargeEfficiency=1.0, dischargeEfficiency=1.0, fillLevel=0.3,
                              maxChargeRate=2.5, maxDischargeRate=2.5, powerFactor=1.0)

        self.influx_connector.init_profile_output_data("test-sim-id", "test-model-id", "Battery", {test_battery_id : battery})
        data_items = []
        for i in range(0,200100):
            self.influx_connector.set_time_step_data_point(test_battery_id, "test-output", datetime(2024,1,1), i)
            data_items.append({
                "measurement": "Battery",
                "tags": {
                    "simulation_id": "test-sim-id",
                    "model_id": "test-model-id",
                    "esdl_id": test_battery_id,
                    "esdl_name": 'battery_test',
                },
                "time": datetime(2024,1,1),
                "fields": {"test-output" : i},
            })

        # Execute
        self.influx_connector.write_output()

        # Assert
        calls = [call(data_items[0:100000], database="test-db-name", time_precision="s"), call(data_items[100000:200000], database="test-db-name", time_precision="s"), call(data_items[200000:200100], database="test-db-name", time_precision="s")]
        self.influx_connector.client.write_points.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()