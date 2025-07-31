from dataclasses import dataclass
from datetime import datetime
from typing import List
import helics as h

from dots_infrastructure.Constants import TimeRequestType

EsdlId = str

@dataclass
class CalculationServiceInput:
    esdl_asset_type : str
    input_name : str
    input_esdl_id : str
    input_unit : str
    input_type : h.HelicsDataType
    simulator_esdl_id : str
    helics_sub_key : str = ""
    helics_input : h.HelicsInput = None

@dataclass 
class CalculationServiceOutput:
    global_flag : bool
    esdl_asset_type : str
    output_name : str
    output_esdl_id : str
    output_type : h.HelicsDataType
    output_unit : str
    helics_publication : h.HelicsPublication = None

@dataclass
class HelicsMessageFederateInformation:
    endpoint_name : str

@dataclass
class SubscriptionDescription:
    esdl_type : str
    input_name : str
    input_unit : str
    input_type : h.HelicsDataType

@dataclass
class PublicationDescription:
    global_flag : bool
    esdl_type : str
    output_name : str
    output_unit : str
    data_type : h.HelicsDataType

@dataclass
class HelicsCalculationInformation:
    time_period_in_seconds : float
    offset : int
    uninterruptible : bool
    wait_for_current_time_update : bool
    terminate_on_error : bool
    calculation_name : str
    inputs : List[SubscriptionDescription]
    outputs : List[PublicationDescription]
    calculation_function : any
    time_delta : float = 0
    federate_time_period = 0
    time_request_type : TimeRequestType = TimeRequestType.PERIOD

@dataclass
class SimulatorConfiguration:
    esdl_type : str
    esdl_ids : List[str]
    model_id : str
    broker_ip : str
    broker_port : int
    simulation_id : str
    simulation_duration_in_seconds : int
    start_time : datetime
    influx_host : str
    influx_port : str
    influx_username : str
    influx_password : str
    influx_database_name : str
    log_level : h.HelicsLogLevel
    calculation_services : List[str]

@dataclass
class SimulaitonDataPoint:
    output_name : str
    datapoint_time : datetime
    value : float
    esdl_id : EsdlId

@dataclass
class TimeStepInformation:
    current_time_step_number : int
    max_time_step_number : int

@dataclass
class RunningStatus:
    terminated : bool = False
    exception : bool = False