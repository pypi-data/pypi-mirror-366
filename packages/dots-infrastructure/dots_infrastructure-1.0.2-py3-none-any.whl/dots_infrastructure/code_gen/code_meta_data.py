from dataclasses import dataclass
from typing import List

from dataclasses_json import DataClassJsonMixin

@dataclass
class CalculationServiceInputData(DataClassJsonMixin):
    name : str
    esdl_type : str
    description : str
    unit : str
    data_type : str
    python_name : str | None = None


@dataclass
class CalculationServiceOutputData(DataClassJsonMixin):
    name : str
    description : str
    unit : str
    data_type : str
    python_data_type : str | None = None
    python_name : str | None = None


@dataclass
class Calculation(DataClassJsonMixin):
    name : str
    description : str
    time_period_in_seconds : int
    offset_in_seconds : int
    inputs : List[CalculationServiceInputData]
    outputs : List[CalculationServiceOutputData]
    calculation_function_name : str | None = None
    calculation_output_class_name : str | None = None


@dataclass
class RelevantLink(DataClassJsonMixin):
    name : str
    url : str
    description : str


@dataclass
class CalculationServiceMetaData(DataClassJsonMixin):
    name : str
    esdl_type : str
    description : str
    calculations : List[Calculation]
    relevant_links : List[RelevantLink] | None = None
    keywords : List[str] | None = None