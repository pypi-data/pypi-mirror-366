import base64
from datetime import datetime, timedelta
from threading import Thread
import time
from typing import List
import unittest
import helics as h

from unittest.mock import MagicMock

from dots_infrastructure import CalculationServiceHelperFunctions
from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SimulatorConfiguration, SubscriptionDescription, TimeStepInformation
from dots_infrastructure.EsdlHelper import EsdlHelper
from dots_infrastructure.HelicsFederateHelpers import HelicsEsdlMessageFederateExecutor, HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
from esdl.esdl import EnergySystem

BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 120
CALCULATION_SERVICES = ["PVInstallation", "EConnection", "EnergyMarket", "Carriers"]
STR_INFLUX_TEST_PORT = "test-port"
INFLUX_USERNAME = "test-username"
INFLUX_PASSWORD = "test-password"
INFLUX_DB_NAME = "test-database-name"
INFLUX_HOST = "test-host"
SIMULATION_ID = "test-id"
BROKER_IP = "127.0.0.1"

MS_TO_BROKER_DISCONNECT = 60000

def simulator_environment_e_pv():
    return SimulatorConfiguration("PVInstallation", ['176af591-6d9d-4751-bb0f-fac7e99b1c3d','b8766109-5328-416f-9991-e81a5cada8a6'], "Mock-PV", BROKER_IP, BROKER_TEST_PORT, SIMULATION_ID, SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, INFLUX_HOST, STR_INFLUX_TEST_PORT, INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DB_NAME, h.HelicsLogLevel.DEBUG, CALCULATION_SERVICES)

class CalculationServicePVDispatch(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_pv
        super().__init__()
        self.influx_connector = InfluxDBMock()
        publictations_values = [
            PublicationDescription(True, "PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]
        subscriptions_values = []
        pv_installation_period_in_seconds = 30
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, 0, False, False, True, "pvdispatch_calculation", subscriptions_values, publictations_values, self.pvdispatch_calculation)
        self.add_calculation(info)

        self.influx_connector = InfluxDBMock()
        publictations_values = []
        subscriptions_values = [
            SubscriptionDescription("EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE),
            SubscriptionDescription("EnergyMarket", "Price", "EUR", h.HelicsDataType.DOUBLE)
        ]
        pv_installation_period_in_seconds = 60
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, 0, False, False, True, "process_econnection_dispatch", subscriptions_values, publictations_values, self.process_econnection_dispatch)
        self.add_calculation(info)


    def pvdispatch_calculation(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        ret_val["PV_Dispatch"] = time_step_number.current_time_step_number
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch", simulation_time, ret_val["PV_Dispatch"])
        return ret_val
    
    def process_econnection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        return ret_val

class CalculationServicePVDispatchMultipleOutputs(HelicsSimulationExecutor):
    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_pv
        super().__init__()
        self.influx_connector = InfluxDBMock()
        publictations_values = [
            PublicationDescription(True, "PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE),
            PublicationDescription(True, "PVInstallation", "PV_Dispatch2", "W", h.HelicsDataType.DOUBLE)
        ]
        subscriptions_values = []
        pv_installation_period_in_seconds = 30
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, 0, True, False, True, "pvdispatch_calculation", subscriptions_values, publictations_values, self.pvdispatch_calculation)
        self.add_calculation(info)


    def pvdispatch_calculation(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        ret_val["PV_Dispatch"] = time_step_number.current_time_step_number
        ret_val["PV_Dispatch2"] = time_step_number.current_time_step_number
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch", simulation_time, ret_val["PV_Dispatch"])
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch2", simulation_time, ret_val["PV_Dispatch2"])
        return ret_val

def simulator_environment_energy_market():
    return SimulatorConfiguration("EnergyMarket", ["b612fc89-a752-4a30-84bb-81ebffc56b50"], "Mock-MarketService", BROKER_IP, BROKER_TEST_PORT, SIMULATION_ID, SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, INFLUX_HOST, STR_INFLUX_TEST_PORT, INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DB_NAME, h.HelicsLogLevel.DEBUG, CALCULATION_SERVICES)

class CalculationServiceMarketService(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_energy_market
        super().__init__()
        self.influx_connector = InfluxDBMock()
        self.calculation_service_initialized = False

        publication_values = [
            PublicationDescription(True, "EnergyMarket", "Price", "EUR", h.HelicsDataType.DOUBLE),
        ]

        energy_market_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(energy_market_period_in_seconds, 0, False, False, True, "MarketPrice", None, publication_values, self.energy_market_price)

        self.add_calculation(calculation_information)

    def energy_market_price(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        ret_val["Price"] = time_step_number.current_time_step_number
        return ret_val

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-Econnection", BROKER_IP, BROKER_TEST_PORT, SIMULATION_ID, SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, INFLUX_HOST, STR_INFLUX_TEST_PORT, INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DB_NAME, h.HelicsLogLevel.DEBUG, CALCULATION_SERVICES)

class CalculationServiceEConnection(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock()
        self.calculation_service_initialized = False

        subscriptions_values_dispatch = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        publication_values_dispatch = [
            PublicationDescription(True, "EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 30

        calculation_information = HelicsCalculationInformation(e_connection_period_in_seconds, 0, False, False, True, "EConnectionDispatch", subscriptions_values_dispatch, publication_values_dispatch, self.e_connection_dispatch)
        self.add_calculation(calculation_information)

        subscriptions_values_schedule = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE),
            SubscriptionDescription("EnergyMarket", "Price", "EUR", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_scedule_in_seconds = 60

        calculation_information_schedule = HelicsCalculationInformation(e_connection_period_scedule_in_seconds, 0, False, False, True, "EConnectionSchedule", subscriptions_values_schedule, None, self.e_connection_da_schedule)
        self.add_calculation(calculation_information_schedule)

    def init_calculation_service(self, energy_system: EnergySystem):
        self.calculation_service_initialized = True

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        pv_dispatch = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch")
        ret_val = {}
        time.sleep(1)
        ret_val["EConnectionDispatch"] = pv_dispatch
        self.influx_connector.set_time_step_data_point(esdl_id, "EConnectionDispatch", simulation_time, ret_val["EConnectionDispatch"])
        return ret_val
    
    def e_connection_da_schedule(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        pv_dispatch = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch")
        price = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "Price")
        ret_val["Schedule"] = [pv_dispatch * price , pv_dispatch * price, pv_dispatch * price]
        self.influx_connector.set_time_step_data_point(esdl_id, "DAScedule", simulation_time, ret_val["Schedule"])
        return ret_val

def simulator_environment_e_commonity():
    return SimulatorConfiguration("Carriers", ["02fafa20-a1bd-488e-a4db-f3c0ca7ff51a"], "Mock-Commonity", BROKER_IP, BROKER_TEST_PORT, SIMULATION_ID, SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, INFLUX_HOST, STR_INFLUX_TEST_PORT, INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DB_NAME, h.HelicsLogLevel.DEBUG, CALCULATION_SERVICES)

class CalculationServiceElectricityCommodity(HelicsSimulationExecutor):
    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_commonity
        super().__init__()
        self.influx_connector = InfluxDBMock()

        subscriptions_values = [
            SubscriptionDescription("EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        commodity_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(commodity_period_in_seconds, 0, False, False, True, "Loadflow", subscriptions_values, None, self.load_flow)
        self.add_calculation(calculation_information)

    def load_flow(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        load = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "EConnectionDispatch")
        self.influx_connector.set_time_step_data_point(esdl_id, "load_flow", simulation_time, load)

class CalculationServiceMultiplePvInputsEConnection(HelicsSimulationExecutor):
    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock()

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE),
            SubscriptionDescription("PVInstallation", "PV_Dispatch2", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 30

        calculation_information = HelicsCalculationInformation(e_connection_period_in_seconds, 0, False, False, True, "EConnectionDispatch", subscriptions_values, [], self.e_connection_dispatch)
        self.add_calculation(calculation_information)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        pv_dispatch = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch")
        pv_dispatch2 = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch2")
        ret_val = {}
        ret_val["EConnectionDispatch"] = pv_dispatch
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch", simulation_time, pv_dispatch)
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch2", simulation_time, pv_dispatch2)
        return ret_val

class CalculationServiceEConnectionException(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock()

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        publication_values = [
            PublicationDescription(True, "EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(e_connection_period_in_seconds, 0, False, False, True, "EConnectionDispatch", subscriptions_values, publication_values, self.e_connection_dispatch)
        self.add_calculation(calculation_information)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        raise Exception("Test-exception")

class CalculationServiceEConnectionControlLoop(HelicsSimulationExecutor):
    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock()

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        publication_values_dispatch = [
            PublicationDescription(True, "EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 30

        calculation_information = HelicsCalculationInformation(e_connection_period_in_seconds, 0, False, False, True, "EConnectionDispatch", subscriptions_values, publication_values_dispatch, self.e_connection_dispatch)
        self.add_calculation(calculation_information)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        pv_dispatch = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch")
        ret_val = {}
        ret_val["EConnectionDispatch"] = pv_dispatch
        time.sleep(1)
        return ret_val

class CalculationServicePVDispatchControlLoop(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_pv
        super().__init__()
        self.influx_connector = InfluxDBMock()
        publictations_values = [
            PublicationDescription(True, "PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]
        subscriptions_values = []
        pv_installation_period_in_seconds = 30
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, 0, False, False, True, "pvdispatch_calculation", subscriptions_values, publictations_values, self.pvdispatch_calculation)
        self.add_calculation(info)

        self.influx_connector = InfluxDBMock()
        publictations_values = []
        subscriptions_values = [
            SubscriptionDescription("EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]
        pv_installation_period_in_seconds = 30
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, 0, False, False, True, "process_econnection_dispatch", subscriptions_values, publictations_values, self.process_econnection_dispatch)
        self.add_calculation(info)

    def init_calculation_service(self, energy_system : EnergySystem):
        self.next_pv_dispatch = 1.0

    def pvdispatch_calculation(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        ret_val["PV_Dispatch"] = self.next_pv_dispatch
        return ret_val
    
    def process_econnection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        self.next_pv_dispatch = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "EConnectionDispatch") + 1
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch", simulation_time, self.next_pv_dispatch)
        ret_val = {}
        return ret_val

class CalculationServiceEConnectionOffset(HelicsSimulationExecutor):
    
    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock()
        publictations_values = [
            PublicationDescription(True, "EConnection", "EConnection_DateTime", "Datetime", h.HelicsDataType.STRING)
        ]
        subscriptions_values = []
        econnection_installation_period_in_seconds = 60
        info = HelicsCalculationInformation(econnection_installation_period_in_seconds, 30, False, False, True, "econnection_calculation", subscriptions_values, publictations_values, self.econnection_calculation)
        self.add_calculation(info)

    def econnection_calculation(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        ret_val = {}
        ret_val_datetime = simulation_time.strftime("%d-%m-%Y, %H:%M:%S")
        ret_val["EConnection_DateTime"] = ret_val_datetime
        return ret_val

class CalculationServiceCarriersOffset(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_commonity
        super().__init__()
        self.influx_connector = InfluxDBMock()
        subscriptions_values = [
            SubscriptionDescription("EConnection", "EConnection_DateTime", "Datetime", h.HelicsDataType.STRING)
        ]
        carriers_period_in_seconds = 60
        info = HelicsCalculationInformation(carriers_period_in_seconds, 0, False, False, True, "carrier_calculation", subscriptions_values, [], self.carrier_calculation)
        self.add_calculation(info)

    def carrier_calculation(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        received_datetime_str = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, "EConnection_DateTime")
        received_datetime = datetime.strptime(received_datetime_str, "%d-%m-%Y, %H:%M:%S")
        datetime_to_save = received_datetime + timedelta(seconds=10)
        self.influx_connector.set_time_step_data_point(esdl_id, "EConnection_DateTime", simulation_time, datetime_to_save.strftime("%d-%m-%Y, %H:%M:%S"))
        ret_val = {}
        return ret_val

class TestSimulation(unittest.TestCase):

    def start_helics_broker(self, federates):
        broker = h.helicsCreateBroker("zmq", "helics_broker_test", f"-f {federates} --loglevel=debug --timeout='60s' --globaltime --port {BROKER_TEST_PORT}")
        broker.wait_for_disconnect(MS_TO_BROKER_DISCONNECT)

    def setUp(self):
        with open("test.esdl", mode="r") as esdl_file:
            encoded_base64_esdl = base64.b64encode(esdl_file.read().encode('utf-8')).decode('utf-8')

        self.wait_for_esdl_file = HelicsEsdlMessageFederateExecutor.wait_for_esdl_file
        self.esdl_message_init_federate = HelicsEsdlMessageFederateExecutor.init_federate 
        self.calculationServiceHelperFunctions_get_simulator_configuration_from_environment = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment
        HelicsEsdlMessageFederateExecutor.wait_for_esdl_file = MagicMock(return_value=EsdlHelper(encoded_base64_esdl))
        HelicsEsdlMessageFederateExecutor.init_federate = MagicMock()
        LOGGER.setLevel("DEBUG")

    def tearDown(self):
        HelicsEsdlMessageFederateExecutor.wait_for_esdl_file = self.wait_for_esdl_file 
        HelicsEsdlMessageFederateExecutor.init_federate = self.esdl_message_init_federate 
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = self.calculationServiceHelperFunctions_get_simulator_configuration_from_environment

    def start_broker(self, n_federates):
        self.broker_thread = Thread(target = self.start_helics_broker, args = [ n_federates ])
        self.broker_thread.start()

    def stop_broker(self):
        self.broker_thread.join()

    def test_given_calculation_with_multiple_outputs_all_outputs_get_published_and_consumed(self):
        # Arrange 
        self.start_broker(2)

        expected_data_point_values_dispatch = []
        for i in range(1, 5):
            expected_data_point_values_dispatch.append(i)
            expected_data_point_values_dispatch.append(i)

        # Execute
        cs_econnection = CalculationServiceMultiplePvInputsEConnection()
        cs_dispatch = CalculationServicePVDispatchMultipleOutputs()

        cs_econnection.start_simulation()
        cs_dispatch.start_simulation()
        cs_econnection.stop_simulation()
        cs_dispatch.stop_simulation()
        self.stop_broker()

        # Assert
        actual_data_point_values_dispatch = [dp.value for dp in cs_econnection.influx_connector.data_points]
        self.assertListEqual(expected_data_point_values_dispatch, actual_data_point_values_dispatch)

    def test_given_exception_occurss_termination_bool_is_set_to_true(self):
        # Arrange 
        self.start_broker(2)
        e_connection_dispatch_period_in_seconds = 60
        pv_period = 30

        # Execute
        cs_econnection = CalculationServiceEConnectionException()
        cs_dispatch = CalculationServicePVDispatch()

        cs_econnection.start_simulation()
        cs_dispatch.start_simulation()
        
        with self.assertRaises(RuntimeError):
            cs_econnection.stop_simulation()
            cs_dispatch.stop_simulation()

        self.stop_broker()

        # Assert
        # No data should be generated as exception is generated right away
        self.assertEqual(len(cs_econnection.influx_connector.data_points), 0) 
        self.assertTrue(all([calculation.running_status.exception and calculation.running_status.terminated for calculation in cs_econnection.calculations]))
        
        # 2 pv panels produce data at most 3 times so
        self.assertLessEqual(len(cs_econnection.influx_connector.data_points), 2 * e_connection_dispatch_period_in_seconds / pv_period + 1)

    def test_given_a_set_of_calculation_services_then_simulation_executes_as_expected(self):
        # Arrange 
        self.start_broker(6)

        e_connection_dispatch_period_in_seconds = 30
        e_connection_period_scedule_in_seconds = 60
        pv_period = 30
        expected_data_point_values_dispatch = [i for i in range(1, 5)]
        expected_data_point_values_loadflow = expected_data_point_values_dispatch
        expected_data_point_values_schedule = [[i * 2.0 * i, i * 2.0 * i, i * 2.0 * i] for i in range(1, 3)]

        # Execute
        cs_econnection = CalculationServiceEConnection()
        cs_dispatch = CalculationServicePVDispatch()
        cs_market = CalculationServiceMarketService()
        cs_electricity_commodity = CalculationServiceElectricityCommodity()

        cs_econnection.start_simulation()
        cs_dispatch.start_simulation()
        cs_market.start_simulation()
        cs_electricity_commodity.start_simulation()
        cs_econnection.stop_simulation()
        cs_dispatch.stop_simulation()
        cs_market.stop_simulation()
        cs_electricity_commodity.stop_simulation()
        self.stop_broker()

        # Assert
        actual_data_point_values_dispatch = [dp.value for dp in cs_econnection.influx_connector.data_points if not isinstance(dp.value, List)]
        actual_data_point_values_schedule = [dp.value for dp in cs_econnection.influx_connector.data_points if isinstance(dp.value, List)]
        actual_data_point_values_loadflow = [dp.value for dp in cs_electricity_commodity.influx_connector.data_points]
        self.assertListEqual(expected_data_point_values_dispatch, actual_data_point_values_dispatch)
        self.assertListEqual(expected_data_point_values_schedule, actual_data_point_values_schedule)
        self.assertListEqual(expected_data_point_values_loadflow, actual_data_point_values_loadflow)
        self.assertEqual(len(cs_econnection.influx_connector.data_points), 
                         SIMULATION_DURATION_IN_SECONDS / e_connection_dispatch_period_in_seconds + 
                         SIMULATION_DURATION_IN_SECONDS / e_connection_period_scedule_in_seconds)
        self.assertEqual(len(cs_dispatch.influx_connector.data_points), SIMULATION_DURATION_IN_SECONDS / pv_period * 2)
        self.assertTrue(cs_econnection.calculation_service_initialized)

    def test_given_a_two_calculation_services_in_control_loop_then_data_is_exchanged_as_expected(self):
        # Arrange 
        self.start_broker(3)
        expected_data_point_values_dispatch = []
        for i in range(2, 6):
            expected_data_point_values_dispatch.append(i)
            expected_data_point_values_dispatch.append(i)

        # Execute
        cs_econnection = CalculationServiceEConnectionControlLoop()
        cs_dispatch = CalculationServicePVDispatchControlLoop()

        cs_econnection.start_simulation()
        cs_dispatch.start_simulation()
        cs_econnection.stop_simulation()
        cs_dispatch.stop_simulation()
        self.stop_broker()

        # Assert
        actual_data_point_values_dispatch = [dp.value for dp in cs_dispatch.influx_connector.data_points ]
        self.assertListEqual(expected_data_point_values_dispatch, actual_data_point_values_dispatch)

    def test_given_a_calculation_service_has_offset_then_first_execution_is_at_offset_time(self):
        # Arrange 
        self.start_broker(1)
        expected_data_point_values_dispatch = [datetime(2024, 1, 1, 0, 0, 40).strftime("%d-%m-%Y, %H:%M:%S"), datetime(2024, 1, 1, 0, 1, 40).strftime("%d-%m-%Y, %H:%M:%S")]

        # Execute
        cs_dispatch = CalculationServiceEConnectionOffset()
        cs_electricity_commodity = CalculationServiceCarriersOffset()
        cs_dispatch.start_simulation()
        cs_electricity_commodity.start_simulation()
        cs_dispatch.stop_simulation()
        cs_electricity_commodity.stop_simulation()
        self.stop_broker()

        # Assert
        actual_data_point_values_dispatch = [dp.value for dp in cs_electricity_commodity.influx_connector.data_points]
        self.assertListEqual(expected_data_point_values_dispatch, actual_data_point_values_dispatch)


if __name__ == '__main__':
    unittest.main()