from concurrent.futures import ThreadPoolExecutor
import dataclasses
from datetime import timedelta
import math
import traceback
from typing import List
import helics as h
from esdl import esdl

from dots_infrastructure import Common
from dots_infrastructure.Constants import TimeRequestType
from dots_infrastructure.DataClasses import CalculationServiceInput, CalculationServiceOutput, HelicsCalculationInformation, HelicsMessageFederateInformation, PublicationDescription, RunningStatus, SubscriptionDescription, TimeStepInformation
from dots_infrastructure.EsdlHelper import EsdlHelper
from dots_infrastructure.Logger import LOGGER
from dots_infrastructure import CalculationServiceHelperFunctions
from dots_infrastructure.influxdb_connector import InfluxDBConnector

class HelicsFederateExecutor:

    def __init__(self):
        self.simulator_configuration = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment()

    def init_default_federate_info(self):
        federate_info = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetBroker(federate_info, self.simulator_configuration.broker_ip)
        h.helicsFederateInfoSetBrokerPort(federate_info, self.simulator_configuration.broker_port)
        h.helicsFederateInfoSetCoreType(federate_info, h.HelicsCoreType.ZMQ)
        h.helicsFederateInfoSetIntegerProperty(federate_info, h.HelicsProperty.INT_LOG_LEVEL, h.HelicsLogLevel.NO_PRINT)
        return federate_info

    def init_calculation_service_federate_info(self, info : HelicsCalculationInformation):
        federate_info = self.init_default_federate_info()
        h.helicsFederateInfoSetTimeProperty(federate_info, h.HelicsProperty.TIME_PERIOD, info.federate_time_period)
        h.helicsFederateInfoSetTimeProperty(federate_info, h.HelicsProperty.TIME_DELTA, info.time_delta)
        h.helicsFederateInfoSetTimeProperty(federate_info, h.HelicsProperty.TIME_OFFSET, info.offset)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFederateFlag.UNINTERRUPTIBLE, info.uninterruptible)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFederateFlag.WAIT_FOR_CURRENT_TIME_UPDATE, info.wait_for_current_time_update)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFlag.TERMINATE_ON_ERROR, info.terminate_on_error)
        return federate_info

class HelicsEsdlMessageFederateExecutor(HelicsFederateExecutor):
    def __init__(self, info : HelicsMessageFederateInformation):
        super().__init__()
        self.helics_message_federate_information = info
        self.message_federate = None
        self.message_enpoint = None

    def init_federate(self):
        federate_info = self.init_default_federate_info()
        self.message_federate = h.helicsCreateMessageFederate(f"{self.simulator_configuration.model_id}", federate_info)
        self.message_enpoint = h.helicsFederateRegisterEndpoint(self.message_federate, self.helics_message_federate_information.endpoint_name)

    def wait_for_esdl_file(self) -> EsdlHelper:
        h.helicsFederateEnterExecutingMode(self.message_federate)
        esdl_file_base64 = ""
        while h.helicsFederateRequestTime(self.message_federate, h.HELICS_TIME_MAXTIME) != h.HELICS_TIME_MAXTIME:
            LOGGER.debug("Fetching an esdl message string at time")
            esdl_file_base64_part = ""
            if h.helicsEndpointHasMessage(self.message_enpoint):
                esdl_file_base64_part_bytes = h.helicsMessageGetBytes(h.helicsEndpointGetMessage(self.message_enpoint))
                esdl_file_base64_part = esdl_file_base64_part_bytes.decode()
                LOGGER.debug(f"Received part of esdl file with: {len(esdl_file_base64_part)} characters")
            esdl_file_base64 += esdl_file_base64_part

        LOGGER.debug("Destroying esdl message federate")
        Common.destroy_federate(self.message_federate)
        esdl_helper = EsdlHelper(esdl_file_base64)

        return esdl_helper

class HelicsValueFederateExecutor(HelicsFederateExecutor):

    WAIT_FOR_INPUT_ITERATION_DURATION_SECONDS = 0.002

    def __init__(self, info : HelicsCalculationInformation):
        super().__init__()
        self.input_dict : dict[str, List[CalculationServiceInput]] = {}
        self.output_dict : dict[str, List[CalculationServiceOutput]] = {}
        self.all_inputs : List[CalculationServiceInput] = []
        self.helics_value_federate_info = info
        self.energy_system : esdl.EnergySystem = None
        self.value_federate : h.HelicsValueFederate = None
        self.running_status = RunningStatus()

    def init_outputs(self, pubs : List[PublicationDescription], value_federate : h.HelicsValueFederate):
        outputs = CalculationServiceHelperFunctions.generate_publications_from_value_descriptions(pubs, self.simulator_configuration)
        for output in outputs:
            key = f'{output.esdl_asset_type}/{output.output_name}/{output.output_esdl_id}'
            LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Registering publication with key: {key}")
            if output.global_flag:
                pub = h.helicsFederateRegisterGlobalPublication(value_federate, key, output.output_type, output.output_unit)
            else:
                pub = h.helicsFederateRegisterPublication(value_federate, key, output.output_type, output.output_unit)
            output.helics_publication = pub
            if output.output_esdl_id in self.output_dict:
                self.output_dict[output.output_esdl_id].append(output)
            else:
                self.output_dict[output.output_esdl_id] = [output]

    def init_inputs(self, subs : List[SubscriptionDescription], esdl_helper : EsdlHelper, value_federate : h.HelicsValueFederate):
        inputs : List[CalculationServiceInput] = []
        for esdl_id in self.simulator_configuration.esdl_ids:
            inputs_for_esdl_object = esdl_helper.get_connected_input_esdl_objects(esdl_id, self.simulator_configuration.calculation_services, subs)
            self.remove_duplicate_subscriptions_and_update_inputs(inputs, inputs_for_esdl_object)
            self.input_dict[esdl_id] = inputs_for_esdl_object

        for input in inputs:
            LOGGER.debug(f"[{self.value_federate.name}] Subscribing to publication with key: {input.helics_sub_key}")
            sub = h.helicsFederateRegisterSubscription(value_federate, input.helics_sub_key, input.input_unit)
            input.helics_input = sub

        self.all_inputs = inputs
        LOGGER.debug(f"Registered inputs: {inputs}")

    def remove_duplicate_subscriptions_and_update_inputs(self, inputs : List[CalculationServiceInput], inputs_for_esdl_object : List[CalculationServiceInput]):
        for i, new_input in enumerate(inputs_for_esdl_object):
            existing_input = next((input for input in inputs if input.helics_sub_key == new_input.helics_sub_key), None)
            if existing_input:
                inputs_for_esdl_object[i] = existing_input
            else:
                inputs.append(new_input)

    def init_federate(self, esdl_helper : EsdlHelper):
        federate_info = self.init_calculation_service_federate_info(self.helics_value_federate_info)
        self.value_federate = h.helicsCreateValueFederate(f"{self.simulator_configuration.model_id}/{self.helics_value_federate_info.calculation_name}", federate_info)
        self.init_inputs(self.helics_value_federate_info.inputs, esdl_helper, self.value_federate)
        self.init_outputs(self.helics_value_federate_info.outputs, self.value_federate)
        self.energy_system = esdl_helper.energy_system

    def get_helics_value(self, helics_sub : CalculationServiceInput):
        ret_val = None
        input_type = helics_sub.input_type
        sub = helics_sub.helics_input
        if h.helicsInputIsUpdated(sub):
            LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Getting value for subscription: {helics_sub.helics_sub_key} with type: {helics_sub.input_type} updated time: {h.helicsInputLastUpdateTime(sub)}")
            if input_type == h.HelicsDataType.BOOLEAN:
                ret_val = h.helicsInputGetBoolean(sub)
            elif input_type == h.HelicsDataType.COMPLEX_VECTOR:
                ret_val = h.helicsInputGetComplexVector(sub)
            elif input_type == h.HelicsDataType.DOUBLE:
                ret_val = h.helicsInputGetDouble(sub)
            elif input_type == h.HelicsDataType.COMPLEX:
                ret_val = h.helicsInputGetComplex(sub)
            elif input_type == h.HelicsDataType.INT:
                ret_val = h.helicsInputGetInteger(sub)
            elif input_type == h.HelicsDataType.JSON:
                ret_val = h.helicsInputGetString(sub)
            elif input_type == h.HelicsDataType.NAMED_POINT:
                ret_val = h.helicsInputGetNamedPoint(sub)
            elif input_type == h.HelicsDataType.STRING:
                ret_val = h.helicsInputGetString(sub)
            elif input_type == h.HelicsDataType.RAW:
                ret_val = h.helicsInputGetRawValue(sub)
            elif input_type == h.HelicsDataType.TIME:
                ret_val = h.helicsInputGetTime(sub)
            elif input_type == h.HelicsDataType.VECTOR:
                ret_val = h.helicsInputGetVector(sub)
            elif input_type == h.HelicsDataType.ANY:
                ret_val = h.helicsInputGetBytes(sub)
            else:
                raise ValueError("Unsupported Helics Data Type")
            LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Got value: {ret_val} from {helics_sub.helics_sub_key}")

        if ret_val == None:
            LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] No new value for input: {helics_sub.helics_sub_key}")
        return ret_val

    def publish_helics_value(self, helics_output : CalculationServiceOutput, value):
        LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Publishing value: {value} for publication: {helics_output.helics_publication.name} with type: {helics_output.output_type.name}")
        pub = helics_output.helics_publication
        output_type = helics_output.output_type
        if output_type == h.HelicsDataType.BOOLEAN:
            h.helicsPublicationPublishBoolean(pub, value)
        elif output_type == h.HelicsDataType.COMPLEX_VECTOR:
            h.helicsPublicationPublishComplexVector(pub, value)
        elif output_type == h.HelicsDataType.DOUBLE:
            h.helicsPublicationPublishDouble(pub, value)
        elif output_type == h.HelicsDataType.COMPLEX:
            h.helicsPublicationPublishComplex(pub, value)
        elif output_type == h.HelicsDataType.INT:
            h.helicsPublicationPublishInteger(pub, value)
        elif output_type == h.HelicsDataType.JSON:
            h.helicsPublicationPublishString(pub, value)
        elif output_type == h.HelicsDataType.NAMED_POINT:
            h.helicsPublicationPublishNamedPoint(pub, value)
        elif output_type == h.HelicsDataType.STRING:
            h.helicsPublicationPublishString(pub, value)
        elif output_type == h.HelicsDataType.RAW:
            h.helicsPublicationPublishRaw(pub, value)
        elif output_type == h.HelicsDataType.TIME:
            h.helicsPublicationPublishTime(pub, value)
        elif output_type == h.HelicsDataType.VECTOR:
            h.helicsPublicationPublishVector(pub, value)
        elif output_type == h.HelicsDataType.ANY:
            h.helicsPublicationPublishBytes(pub, value)
        else:
            raise ValueError("Unsupported Helics Data Type")

    def finalize_simulation(self):
        Common.destroy_federate(self.value_federate)
        self.running_status.terminated = True

    def start_value_federate(self):
        self.enter_simulation_loop()
        self.finalize_simulation()

    def initialize_and_start_federate(self, esdl_helper : EsdlHelper):
        LOGGER.debug(f"[{self.simulator_configuration.model_id}/{self.helics_value_federate_info.calculation_name}] Initializing federate")
        self.init_federate(esdl_helper)
        LOGGER.debug(f"[{self.simulator_configuration.model_id}/{self.helics_value_federate_info.calculation_name}] Starting federate")
        self.start_value_federate()

    def _compute_time_step_number(self, time_of_timestep_to_compute):
        return int(math.floor(time_of_timestep_to_compute / self.helics_value_federate_info.time_period_in_seconds))

    def _init_calculation_params(self):
        ret_val = {}
        for esdl_id in self.simulator_configuration.esdl_ids:
            ret_val[esdl_id] = {} 
        for esdl_id in self.simulator_configuration.esdl_ids:
            if esdl_id in self.input_dict:
                inputs = self.input_dict[esdl_id]
                for helics_input in inputs:
                    ret_val[esdl_id][helics_input.helics_sub_key] = None
        return ret_val
    
    def _init_input_dict(self):
        input_dict = {}
        for input in self.all_inputs:
            input_dict[input.helics_sub_key] = None
        return input_dict

    def _publish_outputs(self, esdl_id, pub_values):
        if len(self.helics_value_federate_info.outputs) > 0:
            outputs = self.output_dict[esdl_id]
            for output in outputs:
                value_to_publish = pub_values[output.output_name]
                self.publish_helics_value(output, value_to_publish)

    def _gather_new_inputs(self, calculation_params, input_dict):
        for input in self.all_inputs:
            new_value = self.get_helics_value(input)
            if new_value != None:
                input_dict[input.helics_sub_key] = new_value

        for esdl_id in self.simulator_configuration.esdl_ids:
            if esdl_id in self.input_dict.keys():
                inputs = self.input_dict[esdl_id]
                for helics_input in inputs:
                    calculation_params[esdl_id][helics_input.helics_sub_key] = input_dict[helics_input.helics_sub_key]

    def _get_request_time(self, granted_time):
        requested_time = 0
        if self.helics_value_federate_info.time_request_type == TimeRequestType.PERIOD:
            if granted_time == 0 and self.helics_value_federate_info.offset > 0:
                requested_time = self.helics_value_federate_info.offset
            else:
                requested_time = granted_time + self.helics_value_federate_info.time_period_in_seconds
        if self.helics_value_federate_info.time_request_type == TimeRequestType.ON_INPUT:
            requested_time = h.HELICS_TIME_MAXTIME
        return requested_time

    def _gather_all_required_inputs(self, calculation_params : dict, granted_time : h.HelicsTime):
        LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Gathering all inputs")
        input_dict = self._init_input_dict()
        self._gather_new_inputs(calculation_params, input_dict)
        new_granted_time = granted_time
        
        while not CalculationServiceHelperFunctions.dictionary_has_values_for_all_keys(input_dict):
            LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] requesting max time again to wait for new inputs")
            new_granted_time = h.helicsFederateRequestTime(self.value_federate, h.HELICS_TIME_MAXTIME)
            self._gather_new_inputs(calculation_params, input_dict)
        return new_granted_time

    def enter_simulation_loop(self):
        LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Entering HELICS execution mode {self.helics_value_federate_info.calculation_name}")
        h.helicsFederateEnterExecutingMode(self.value_federate)
        LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Entered HELICS execution mode {self.helics_value_federate_info.calculation_name}")

        total_interval = self.simulator_configuration.simulation_duration_in_seconds
        max_time_step_number = self._compute_time_step_number(total_interval)
        granted_time = 0
        granted_time = self.request_new_granted_time(granted_time)
        terminate_requested = False
        calculation_params = self._init_calculation_params()
        while granted_time <= total_interval and not terminate_requested:

            time_step_number = self._compute_time_step_number(granted_time)
            time_step_information = TimeStepInformation(time_step_number, max_time_step_number)
            granted_time = self._gather_all_required_inputs(calculation_params, granted_time)
            simulator_time = self.simulator_configuration.start_time + timedelta(seconds = granted_time)

            for esdl_id in self.simulator_configuration.esdl_ids:
                try:
                    if not terminate_requested:
                        LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Executing calculation {self.helics_value_federate_info.calculation_name} for esdl_id {esdl_id} at time {granted_time}")
                        pub_values = self.helics_value_federate_info.calculation_function(calculation_params[esdl_id], simulator_time, time_step_information, esdl_id, self.energy_system)

                        if dataclasses.is_dataclass(pub_values):
                            pub_values = dataclasses.asdict(pub_values)

                        LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Finished calculation {self.helics_value_federate_info.calculation_name} for esdl_id {esdl_id} at time {granted_time}")
                        self._publish_outputs(esdl_id, pub_values)
                        calculation_params[esdl_id] = CalculationServiceHelperFunctions.clear_dictionary_values(calculation_params[esdl_id])
                except Exception:
                    LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Exception occurred for esdl_id {esdl_id} at time {granted_time} terminating simulation...")
                    traceback.print_exc()
                    terminate_requested = True
                    self.running_status.exception = True

            LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Finished {granted_time} of {total_interval} and terminate requested {terminate_requested}")
            granted_time = self.request_new_granted_time(granted_time)

        LOGGER.info(f"[{h.helicsFederateGetName(self.value_federate)}] Finalizing federate at {granted_time} of {total_interval} and terminate requested {terminate_requested}")

    def request_new_granted_time(self, granted_time):
        time_to_request = self._get_request_time(granted_time)
        LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Requesting time: {time_to_request} for calculation {self.helics_value_federate_info.calculation_name}")
        granted_time = h.helicsFederateRequestTime(self.value_federate, time_to_request)
        LOGGER.debug(f"[{h.helicsFederateGetName(self.value_federate)}] Time granted: {granted_time} for calculation {self.helics_value_federate_info.calculation_name}")
        return granted_time

class HelicsSimulationExecutor:

    def __init__(self):
        self.simulator_configuration = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment()
        self.calculations: List[HelicsValueFederateExecutor] = []
        self.energy_system = None
        self.influx_connector = InfluxDBConnector(self.simulator_configuration.influx_host, self.simulator_configuration.influx_port, self.simulator_configuration.influx_username, self.simulator_configuration.influx_password, self.simulator_configuration.influx_database_name)

    def add_calculation(self, info : HelicsCalculationInformation):
        if info.inputs == None:
            info.inputs = []
        if info.outputs == None:
            info.outputs = []
        info.federate_time_period = info.time_period_in_seconds
        if len(info.inputs) > 0:
            info.time_request_type = TimeRequestType.ON_INPUT
            info.federate_time_period = 0
        self.calculations.append(HelicsValueFederateExecutor(info))

    def _get_esdl_from_so(self):
        esdl_message_federate = HelicsEsdlMessageFederateExecutor(HelicsMessageFederateInformation('esdl'))
        esdl_message_federate.init_federate()
        esdl_helper = esdl_message_federate.wait_for_esdl_file()
        return esdl_helper

    def _init_influxdb(self, esdl_helper : EsdlHelper):
        esdl_objects = esdl_helper.esdl_object_mapping
        self.influx_connector.init_profile_output_data(self.simulator_configuration.simulation_id, self.simulator_configuration.model_id, self.simulator_configuration.esdl_type, esdl_objects)
        self.influx_connector.connect()

    def init_calculation_service(self, energy_system : esdl.EnergySystem):
        pass

    def init_simulation(self) -> esdl.EnergySystem:
        esdl_helper = self._get_esdl_from_so()
        self._init_influxdb(esdl_helper)
        self.init_calculation_service(esdl_helper.energy_system)
        return esdl_helper
    
    def _assert_that_periods_of_calculation_are_smaller_than_simulation_duration(self):
        simulation_duration = self.simulator_configuration.simulation_duration_in_seconds
        for calculation in self.calculations:
            if calculation.helics_value_federate_info.time_period_in_seconds > simulation_duration:
                raise RuntimeError(f"Calculation: {calculation.helics_value_federate_info.calculation_name} has a period > the simulatino duration therefore it will not execute")

    def start_simulation(self):
        self._assert_that_periods_of_calculation_are_smaller_than_simulation_duration()
        esdl_helper = self.init_simulation()
        self.exe = ThreadPoolExecutor(len(self.calculations))
        for calculation in self.calculations:
            self.exe.submit(calculation.initialize_and_start_federate, esdl_helper)

    def stop_simulation(self):
        self.exe.shutdown()
        LOGGER.debug(f"Writing data to influx for calculation service {self.simulator_configuration.model_id}")
        self.influx_connector.write_output()
        if any([calculation.running_status.exception for calculation in self.calculations]):
            failed_calulation = next((calculation for calculation in self.calculations if calculation.running_status.exception == True), None)
            raise RuntimeError(f"Calculation service had an exception calculation: {failed_calulation.helics_value_federate_info.calculation_name} failed")