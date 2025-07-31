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

import typing

from datetime import datetime
from dots_infrastructure.DataClasses import EsdlId
from dots_infrastructure.Logger import LOGGER
from influxdb import InfluxDBClient

from esdl import esdl



class InfluxDBConnector:
    """A connector writes data to an InfluxDB database."""

    def __init__(
        self,
        influx_host: str,
        influx_port: str,
        influx_user: str,
        influx_password: str,
        influx_database_name: str,
    ):
        self.influx_host: str = influx_host.split("//")[-1]
        self.influx_port: str = influx_port
        self.influx_database_name: str = influx_database_name
        self.influx_user: str = influx_user
        self.influx_password: str = influx_password

        LOGGER.debug("influx server: {}".format(self.influx_host))
        LOGGER.debug("influx port: {}".format(self.influx_port))
        LOGGER.debug("influx database: {}".format(self.influx_database_name))

        self.client: typing.Optional[InfluxDBClient] = None
        self.simulation_id: typing.Optional[str] = None
        self.model_id: typing.Optional[str] = None
        self.esdl_type: typing.Optional[str] = None
        self.esdl_objects: typing.Optional[dict[EsdlId, esdl]] = None

    def connect(self) -> InfluxDBClient:
        client = None
        try:
            LOGGER.debug("Connecting InfluxDBClient")
            client = InfluxDBClient(
                host=self.influx_host,
                port=self.influx_port,
                database=self.influx_database_name,
                username=self.influx_user,
                password=self.influx_password,
            )
            LOGGER.debug("InfluxDBClient ping: {}".format(client.ping()))
        except Exception as e:
            LOGGER.debug("Failed to connect to influx db: {}".format(e))
            if client:
                client.close()
        return client

    def query(self, query):
        if self.client is None:
            self.client = self.connect()

        return self.client.query(query)

    def create_database(self):
        if self.client is None:
            self.client = self.connect()
        self.client.create_database(self.influx_database_name)

    def write(self, msgs):
        if self.client is None:
            self.client = self.connect()

        # Send message to database.
        chunk_size = 100000
        for i in range(0, len(msgs), chunk_size):
            chunk = msgs[i:i + chunk_size]
            self.client.write_points(chunk, database=self.influx_database_name, time_precision="s")
        

    def close(self):
        if self.client:
            self.client.close()
        self.client = None

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
        self.data_points : typing.List[dict] = []
        self.esdl_objects = esdl_objects

    def set_time_step_data_point(
        self, esdl_id: EsdlId, output_name: str, simulation_datetime: datetime, value: float
    ):
        fields = {
            output_name : value
        }
        self.data_points.append(self.add_measurement(esdl_id, simulation_datetime, fields))
        MAX_AMOUNT_OF_DB_POINTS = 100000
        if len(self.data_points) >= MAX_AMOUNT_OF_DB_POINTS:
            LOGGER.debug(f"Writing {len(self.data_points)} data points to InfluxDB")
            self.write_output()
            self.data_points.clear()

    def write_output(self):
        self.write(self.data_points)

    def add_measurement(self, esdl_id, timestamp, fields):
        try:
            if hasattr(self.esdl_objects[esdl_id], "name"):
                esdl_name = self.esdl_objects[esdl_id].name
            else:
                esdl_name = self.esdl_type
            item = {
                "measurement": f"{self.esdl_type}",
                "tags": {
                    "simulation_id": self.simulation_id,
                    "model_id": self.model_id,
                    "esdl_id": esdl_id,
                    "esdl_name": esdl_name,
                },
                "time": timestamp,
                "fields": fields,
            }
            return item
        except Exception as e:
            LOGGER.debug(f"Exception: {e} {e.args}")
