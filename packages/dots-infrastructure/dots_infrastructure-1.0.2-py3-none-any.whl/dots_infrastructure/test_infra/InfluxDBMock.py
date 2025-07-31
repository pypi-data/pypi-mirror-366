#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO

import typing, numpy

from datetime import datetime
from dots_infrastructure.DataClasses import EsdlId, SimulaitonDataPoint
from dots_infrastructure.Logger import LOGGER
from influxdb import InfluxDBClient

from esdl import esdl

from dots_infrastructure.influxdb_connector import InfluxDBConnector



class InfluxDBMock(InfluxDBConnector):
    """A connector writes data to an InfluxDB database."""

    def __init__(self):
        super().__init__("test//test", "test", "test", "test", "test")
        self.data_points : typing.List[SimulaitonDataPoint] = []

    def connect(self) -> InfluxDBClient:
        LOGGER.info("Connecting to influxdb")

    def query(self, query):
        LOGGER.info("Query influxdb")

    def create_database(self):
        LOGGER.info("Create DB")

    def write(self, msgs):
        LOGGER.info("Writing to DB")

    def close(self):
        LOGGER.info("Close")

    def init_profile_output_data(
        self,
        simulation_id: str,
        model_id: str,
        esdl_type: str,
        esdl_objects: dict[EsdlId, esdl],
    ):
        self.simulation_id = simulation_id
        self.esdl_type = esdl_type
        self.model_id = model_id
        self.esdl_objects = esdl_objects

    def set_time_step_data_point(
        self, esdl_id: EsdlId, output_name: str, simulation_datetime: datetime, value: float
    ):
        self.data_points.append(SimulaitonDataPoint(output_name, simulation_datetime, value, esdl_id))

    def write_output(self):
        LOGGER.info("write output")

    def add_measurement(self, points, esdl_id, timestamp, fields):
        LOGGER.info("add measurement")
