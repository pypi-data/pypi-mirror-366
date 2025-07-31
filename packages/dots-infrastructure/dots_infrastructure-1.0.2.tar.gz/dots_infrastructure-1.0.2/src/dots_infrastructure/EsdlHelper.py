from base64 import b64decode
from typing import List
from esdl.esdl_handler import EnergySystemHandler

from esdl import esdl
from esdl import EnergySystem
from dots_infrastructure.DataClasses import CalculationServiceInput, EsdlId, SubscriptionDescription
from dots_infrastructure.Logger import LOGGER

class EsdlHelper:

    def __init__(self, esdl_string_base64):
        self.energy_system = self._get_energy_system_from_base64_encoded_esdl_string(esdl_string_base64)
        self.non_connected_esdl_ids = []
        self.esdl_object_mapping : dict = self._get_esdl_id_object_mapping(self.energy_system, self.non_connected_esdl_ids)

    def _get_energy_system_from_base64_encoded_esdl_string(self, esdl_string_base64) -> EnergySystem:
        esdl_string = b64decode(esdl_string_base64 + b"==".decode("utf-8")).decode("utf-8")
        LOGGER.debug(f"Parsing esdl string of {len(esdl_string)} characters")
        esh = EnergySystemHandler()
        esh.load_from_string(esdl_string)
        return esh.get_energy_system()
    
    def _get_esdl_id_object_mapping(self, energy_system : EnergySystem, non_connected_esdl_ids : List) -> esdl:
        ret_val = {}
        for obj in energy_system.eAllContents():
            if hasattr(obj, "id"):
                ret_val[obj.id] = obj
                if not isinstance(obj, esdl.EnergyAsset):
                    non_connected_esdl_ids.append(obj.id)
        ret_val[energy_system.id] = energy_system
        return ret_val
    
    def extract_calculation_service_name(self, calculation_services: List[str], esdl_obj) -> str:
        esdl_obj_type_name = type(esdl_obj).__name__
        name = next(
            (
                calc_service_name
                for calc_service_name in calculation_services
                if calc_service_name == esdl_obj_type_name
            ),
            None,
        )
        
        return name
    
    def add_connected_esdl_object(self, subscriptions: List[SubscriptionDescription], calculation_services: List[str], input_descriptions : List[SubscriptionDescription], connected_asset: esdl, simulator_asset: esdl.EnergyAsset):
        calc_service_name = self.extract_calculation_service_name(calculation_services, connected_asset)
    
        if calc_service_name:
            input_descriptions = [input_description for input_description in input_descriptions if input_description.esdl_type == calc_service_name]
            for input_description in input_descriptions:
                new_input = CalculationServiceInput(input_description.esdl_type, input_description.input_name, connected_asset.id, input_description.input_unit, input_description.input_type, simulator_asset.id)
                new_input.helics_sub_key = f'{new_input.esdl_asset_type}/{new_input.input_name}/{new_input.input_esdl_id}'
                if new_input not in subscriptions:
                    subscriptions.append(new_input)
    
    def add_calc_services_from_ports_recursive(
        self,
        calculation_services: List[str],
        connected_input_esdl_objects: List[CalculationServiceInput],
        input_descriptions : List[SubscriptionDescription],
        model_esdl_asset: esdl.EnergyAsset,
        start_asset : esdl.EnergyAsset,
        visited_assets : List[str]
    ):
        if model_esdl_asset.id not in visited_assets:
            visited_assets.append(model_esdl_asset.id)
            for port in model_esdl_asset.port:
                for connected_port in port.connectedTo:
                    connected_asset = connected_port.eContainer()
                    self.add_connected_esdl_object(
                        connected_input_esdl_objects, calculation_services, input_descriptions, connected_asset, start_asset
                    )
                    if connected_asset.port != None and connected_asset.port != []:
                        self.add_calc_services_from_ports_recursive(calculation_services, connected_input_esdl_objects, input_descriptions, connected_asset, start_asset, visited_assets)

    def add_calc_services_from_building(self, calculation_services: List[str], connected_input_esdl_objects: List[CalculationServiceInput], input_descriptions : List[SubscriptionDescription], model_esdl_asset: esdl.EnergyAsset, building : esdl.Building):
        for esdl_entity in building.eAllContents():
            if isinstance(esdl_entity, esdl.EnergyAsset):
                self.add_connected_esdl_object(
                        connected_input_esdl_objects, calculation_services, input_descriptions, esdl_entity, model_esdl_asset
                    )

    def add_calc_services_from_ports(
        self,
        calculation_services: List[str],
        connected_input_esdl_objects: List[CalculationServiceInput],
        input_descriptions : List[SubscriptionDescription],
        model_esdl_asset: esdl.EnergyAsset
    ):
        visited_assets = []
        for port in model_esdl_asset.port:
            if isinstance(port, esdl.InPort):
                for connected_asset in port.connectedTo:
                    visited_assets.append(connected_asset.eContainer().id)
        if isinstance(model_esdl_asset.eContainer(), esdl.Building):
            self.add_calc_services_from_building(calculation_services, connected_input_esdl_objects, input_descriptions, model_esdl_asset, model_esdl_asset.eContainer())

        self.add_calc_services_from_ports_recursive(calculation_services, connected_input_esdl_objects, input_descriptions, model_esdl_asset, model_esdl_asset, visited_assets)

    def add_calc_services_from_non_connected_objects(
        self,
        calculation_services: List[str],
        connected_input_esdl_objects: List[SubscriptionDescription],
        input_descriptions : List[SubscriptionDescription],
        model_esdl_asset: esdl.EnergyAsset
    ):
        for esdl_id in self.non_connected_esdl_ids:
            self.add_connected_esdl_object(
                connected_input_esdl_objects, calculation_services, input_descriptions, self.esdl_object_mapping[esdl_id], model_esdl_asset
            )
        self.add_connected_esdl_object(connected_input_esdl_objects, calculation_services, input_descriptions, self.energy_system, model_esdl_asset)
    
    def add_calc_services_from_all_objects(
        self,
        calculation_services: List[str],
        connected_input_esdl_objects: List[SubscriptionDescription],
        input_descriptions : List[SubscriptionDescription],
        model_esdl_asset: esdl.EnergyAsset
    ):
        for esdl_obj in self.esdl_object_mapping.values():
            self.add_connected_esdl_object(
                connected_input_esdl_objects, calculation_services, input_descriptions, esdl_obj, model_esdl_asset
            )
    
    def get_connected_input_esdl_objects(
        self,
        esdl_id: EsdlId,
        calculation_services: List[str],
        input_descriptions : List[SubscriptionDescription]
    ) -> List[CalculationServiceInput]:
        model_esdl_obj = self.esdl_object_mapping[esdl_id]
    
        connected_input_esdl_objects: List[CalculationServiceInput] = []
        if isinstance(model_esdl_obj, esdl.EnergyAsset):
            self.add_calc_services_from_ports(
                calculation_services, connected_input_esdl_objects, input_descriptions, model_esdl_obj
            )
            self.add_calc_services_from_non_connected_objects(
                calculation_services, connected_input_esdl_objects, input_descriptions, model_esdl_obj
            )
        else:
            self.add_calc_services_from_all_objects(
                calculation_services, connected_input_esdl_objects, input_descriptions, model_esdl_obj
            )
        return connected_input_esdl_objects