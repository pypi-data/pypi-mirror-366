import base64
from dataclasses import dataclass
from datetime import datetime
from typing import List
import unittest
from unittest.mock import MagicMock, call, patch

from esdl import EnergySystem
import helics as h

from dots_infrastructure import CalculationServiceHelperFunctions, Common
from dots_infrastructure.Constants import TimeRequestType
from dots_infrastructure.DataClasses import CalculationServiceInput, CalculationServiceOutput, EsdlId, HelicsCalculationInformation, HelicsMessageFederateInformation, PublicationDescription, SimulatorConfiguration, SubscriptionDescription, TimeStepInformation
from dots_infrastructure.HelicsFederateHelpers import HelicsEsdlMessageFederateExecutor, HelicsValueFederateExecutor, HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from dots_infrastructure.test_infra.HelicsMocks import HelicsEndpointMock, HelicsFederateMock

LOGGER.disabled = True

def simulator_environment_e_logic_test():
    return SimulatorConfiguration("LogicTest", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-LogicTest", "127.0.0.1", 2000, "test-id", 5, datetime(2024,1,1), "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

@dataclass
class TestDataClass:
    output1 : str
    output2 : int
    output3 : List

class CalculationServiceEConnection(HelicsSimulationExecutor):

    def __init__(self):
        super().__init__()

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(time_period_in_seconds=e_connection_period_in_seconds, 
                                                               time_request_type=TimeRequestType.PERIOD,
                                                               offset=0,
                                                               wait_for_current_time_update=False, 
                                                               uninterruptible=False, 
                                                               terminate_on_error=True, 
                                                               calculation_name="EConnectionDispatch", 
                                                               inputs=subscriptions_values, 
                                                               outputs=None, 
                                                               calculation_function=self.e_connection_dispatch)
        self.add_calculation(calculation_information)

        publication_values = [
            PublicationDescription(True, "EConnection", "Schedule", "W", h.HelicsDataType.VECTOR)
        ]

        e_connection_period_scedule_in_seconds = 120

        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=e_connection_period_scedule_in_seconds,
                                                                        time_request_type=TimeRequestType.PERIOD,
                                                                        offset=0, 
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=None, 
                                                                        outputs=publication_values, 
                                                                        calculation_function=self.e_connection_da_schedule)
        self.add_calculation(calculation_information_schedule)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):

        return 0
    
    def e_connection_da_schedule(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        return [1.0,2.0,3.0]

class TestLogicAddingCalculations(unittest.TestCase):
    def setUp(self):
        self.get_sim_config_from_env = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment 
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_logic_test

    def tearDown(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_logic_test
        
    def test_simulation_none_input_output_sets_empty_inputs_and_outputs(self):

        # Execute
        cs_econnection = CalculationServiceEConnection()

        # Assert
        self.assertEqual(len(cs_econnection.calculations), 2)
        self.assertEqual(len(cs_econnection.calculations[0].helics_value_federate_info.inputs), 1)
        self.assertEqual(len(cs_econnection.calculations[0].helics_value_federate_info.outputs), 0)
        self.assertEqual(len(cs_econnection.calculations[1].helics_value_federate_info.inputs), 0)
        self.assertEqual(len(cs_econnection.calculations[1].helics_value_federate_info.outputs), 1)

class TestLogicRunningSimulation(unittest.TestCase):

    def setUp(self):
        with open("test.esdl", mode="r") as esdl_file:
            self.encoded_base64_esdl = base64.b64encode(esdl_file.read().encode('utf-8')).decode('utf-8')

        self.federate_get_name = h.helicsFederateGetName
        self.get_sim_config_from_env = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment 
        self.fed_eneter_executing_mode = h.helicsFederateEnterExecutingMode
        self.get_time_property = h.helicsFederateGetTimeProperty 
        self.request_time = h.helicsFederateRequestTime
        self.helics_endpoint_has_message = h.helicsEndpointHasMessage
        self.helics_message_get_bytes = h.helicsMessageGetBytes
        self.helics_endpoint_get_message = h.helicsEndpointGetMessage
        self.helics_create_message_federate = h.helicsCreateMessageFederate
        self.helics_federate_register_endpoint = h.helicsFederateRegisterEndpoint
        self.common_destroy_federate = Common.destroy_federate
        h.helicsFederateGetName = MagicMock(return_value = "LogicTest")
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_logic_test
        h.helicsFederateEnterExecutingMode = MagicMock()
        h.helicsFederateGetTimeProperty = MagicMock(return_value = 5)

        def helics_request_time(a, b):
            return b

        h.helicsFederateRequestTime = MagicMock(side_effect=helics_request_time)
        h.helicsEndpointHasMessage = MagicMock(return_value = True)
        h.helicsEndpointGetMessage = MagicMock(return_value = None)
        h.helicsCreateMessageFederate = MagicMock(return_value = HelicsFederateMock())
        h.helicsFederateRegisterEndpoint = MagicMock(return_value = HelicsEndpointMock())
        Common.destroy_federate = MagicMock()

    def tearDown(self):
        h.helicsFederateGetName = self.federate_get_name
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = self.get_sim_config_from_env 
        h.helicsFederateEnterExecutingMode = self.fed_eneter_executing_mode
        h.helicsFederateGetTimeProperty = self.get_time_property
        h.helicsFederateRequestTime = self.request_time
        h.helicsEndpointHasMessage = self.helics_endpoint_has_message
        h.helicsMessageGetBytes = self.helics_message_get_bytes
        h.helicsCreateMessageFederate = self.helics_create_message_federate 
        h.helicsFederateRegisterEndpoint = self.helics_federate_register_endpoint
        h.helicsEndpointGetMessage = self.helics_endpoint_get_message
        Common.destroy_federate = self.common_destroy_federate

    def test_helics_simulation_loop_started_correctly(self):
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5))
        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateEnterExecutingMode.assert_called_once()
        calculation_information_schedule.calculation_function.assert_called_once_with({}, datetime(2024, 1, 1, 0, 0, 5), TimeStepInformation(1,1), 'f006d594-0743-4de5-a589-a6c2350898da', None)

    def test_when_calculation_has_period_bigger_than_simulation_duration_then_exception_is_raised(self):
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=10,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5),
                                                                        time_delta=0)
        
        executor = HelicsSimulationExecutor()
        executor.init_simulation = MagicMock()
        executor.add_calculation(calculation_information_schedule)
        executor.calculations[0].initialize_and_start_federate = MagicMock()

        # Execute and assert
        with self.assertRaises(RuntimeError):
            executor.start_simulation()
    
    def test_when_time_request_type_period_helicsFederateRequestTime_called_with_period(self):
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5),
                                                                        time_delta=0)
        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateRequestTime.assert_has_calls([call(None, 5), call(None, 10)])

    def test_when_time_request_type_on_input_helicsFederateRequestTime_called_with_helics_max_time(self):
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=60,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5),
                                                                        time_request_type=TimeRequestType.ON_INPUT,
                                                                        time_delta=5)
        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateRequestTime.assert_called_once_with(None, h.HELICS_TIME_MAXTIME)

    def test_when_time_request_type_period_and_has_offset_helicsFederateRequestTime_called_with_offset(self):

        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=2,
                                                                        offset=1,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5),
                                                                        time_request_type=TimeRequestType.PERIOD,
                                                                        time_delta=0)
        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateRequestTime.assert_has_calls([call(None, 1), call(None, 3), call(None, 5), call(None, 7)])

    def test_calculation_is_not_executed_when_all_inputs_are_not_present(self):

        calculation_function = MagicMock()
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=calculation_function)

        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)
        inputs = [
            CalculationServiceInput("test-type", "test-input", "test-input-id", "W", h.HelicsDataType.DOUBLE, "test-id", "test-input-key"),
            CalculationServiceInput("test-type2", "test-input2", "test-input-id2", "W", h.HelicsDataType.DOUBLE, "test-id", "test-input-key2")
        ]
        self.federate_executor.input_dict["f006d594-0743-4de5-a589-a6c2350898da"] = inputs
        self.federate_executor.all_inputs = inputs

        self.return_value = 0

        def helics_value_side_effect(value):
            self.return_value += 1
            if self.return_value > 3:
                return self.return_value 
            return self.return_value  if value == inputs[0] else None

        self.federate_executor.get_helics_value = MagicMock(side_effect=helics_value_side_effect)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        self.assertEqual(self.return_value, 4)
        calculation_function.assert_called_once()

    def test_calculation_is_executed_when_all_inputs_are_present(self):
        calculation_function = MagicMock()
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=calculation_function)

        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)
        test_input_key = "test-input-key"
        test_input_key2 = "test-input-key2"
        inputs = [
            CalculationServiceInput("test-type", "test-input", "test-input-id", "W", h.HelicsDataType.DOUBLE, "test-id", "test-input-key"),
            CalculationServiceInput("test-type2", "test-input2", "test-input-id2", "W", h.HelicsDataType.DOUBLE, "test-id", "test-input-key2")
        ]
        self.federate_executor.input_dict["f006d594-0743-4de5-a589-a6c2350898da"] = inputs
        self.federate_executor.all_inputs = inputs

        self.federate_executor.get_helics_value = MagicMock(return_value=5)
        param_dict = {
            test_input_key : 5,
            test_input_key2 : 5
        }

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        calculation_function.assert_called_once_with(param_dict, datetime(2024, 1, 1, 0, 0, 5), TimeStepInformation(1, 1), 'f006d594-0743-4de5-a589-a6c2350898da', None)

    def test_calculation_can_provide_dataclasses_as_output(self):
        calculation_function = MagicMock(return_value=TestDataClass(output1="test", output2=5, output3=[1, 2, 3]))
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=calculation_function)

        self.federate_executor = HelicsValueFederateExecutor(calculation_information_schedule)
        self.federate_executor._publish_outputs = MagicMock()

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        expected_output_dict = {
            "output1": "test",
            "output2": 5,
            "output3": [1, 2, 3]
        }
        self.federate_executor._publish_outputs.assert_called_once_with('f006d594-0743-4de5-a589-a6c2350898da', expected_output_dict)

    def test_add_calculation_sets_correct_delta_and_period_values(self):
        calculation_function = MagicMock()
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[CalculationServiceInput("test-type", "test-input", "test-input-id", "W", h.HelicsDataType.DOUBLE, "test-id", "test-input-key"),], 
                                                                        outputs=[], 
                                                                        calculation_function=calculation_function)
        
        calculation_information_dispatch = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionDispatch", 
                                                                        inputs=[], 
                                                                        outputs=[CalculationServiceOutput(True, "test-type", "test-output", "test-output-id", h.HelicsDataType.DOUBLE, "W")], 
                                                                        calculation_function=calculation_function)

        simulation_executor = HelicsSimulationExecutor()

        # Execute
        simulation_executor.add_calculation(calculation_information_schedule)
        simulation_executor.add_calculation(calculation_information_dispatch)

        # Assert
        self.assertEqual(len(simulation_executor.calculations), 2)

        self.assertEqual(simulation_executor.calculations[0].helics_value_federate_info.time_request_type, TimeRequestType.ON_INPUT )
        self.assertEqual(simulation_executor.calculations[0].helics_value_federate_info.time_period_in_seconds, 5)
        self.assertEqual(simulation_executor.calculations[0].helics_value_federate_info.federate_time_period, 0)

        self.assertEqual(simulation_executor.calculations[1].helics_value_federate_info.time_request_type, TimeRequestType.PERIOD )
        self.assertEqual(simulation_executor.calculations[1].helics_value_federate_info.time_period_in_seconds, 5)
        self.assertEqual(simulation_executor.calculations[1].helics_value_federate_info.federate_time_period, 5)

    def test_given_waiting_for_esdl_when_full_esdl_is_received_esdl_helper_is_correctly_constructed(self):
        # arrange
        esdl_message_federate = HelicsEsdlMessageFederateExecutor(HelicsMessageFederateInformation('esdl'))
        esdl_message_federate.init_federate()

        self.i = 0
        def helics_request_time(a, b):
            self.i += 1
            return 5 if self.i == 1 else h.HELICS_TIME_MAXTIME

        h.helicsFederateRequestTime = MagicMock(side_effect=helics_request_time)
        h.helicsMessageGetBytes = MagicMock(return_value=self.encoded_base64_esdl.encode())

        # execute
        helper = esdl_message_federate.wait_for_esdl_file()

        self.assertIsNotNone(helper)

    def test_given_waiting_for_esdl_when_full_esdl_is_received_in_parts_esdl_helper_is_correctly_constructed(self):
        # arrange
        esdl_message_federate = HelicsEsdlMessageFederateExecutor(HelicsMessageFederateInformation('esdl'))
        esdl_message_federate.init_federate()

        self.i = 0
        def helics_request_time(a, b):
            self.i += 1
            return 5 if self.i <= 2 else h.HELICS_TIME_MAXTIME

        h.helicsFederateRequestTime = MagicMock(side_effect=helics_request_time)

        self.j = 0
        def helics_message_get_bytes(a):
            self.j += 1
            return self.encoded_base64_esdl[0:int(len(self.encoded_base64_esdl))].encode() if self.j == 1 else self.encoded_base64_esdl[int(len(self.encoded_base64_esdl)):].encode()

        h.helicsMessageGetBytes = MagicMock(side_effect=helics_message_get_bytes)

        # execute
        helper = esdl_message_federate.wait_for_esdl_file()

        self.assertIsNotNone(helper)

if __name__ == '__main__':
    unittest.main()