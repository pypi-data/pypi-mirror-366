import unittest
import base64
import helics as h

from dots_infrastructure.EsdlHelper import EsdlHelper
from dots_infrastructure.DataClasses import CalculationServiceInput, SubscriptionDescription

class TestParse(unittest.TestCase):

    def setUp(self):
        with open("test-input-extraction-network.esdl", mode="r") as esdl_file:
            self.encoded_base64_esdl = base64.b64encode(esdl_file.read().encode('utf-8')).decode('utf-8')

    def test_assets_in_building_can_get_inputs_from_other_assets_inside_building(self):
        # Arrange
        simulator_esdl_id = '15bc27e8-97db-427c-959e-e2a2fca27f75'

        esdl_helper = EsdlHelper(self.encoded_base64_esdl)

        subscription_descriptions = [
            SubscriptionDescription(esdl_type="ElectricityDemand",input_name="active_power",input_unit="W",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="ElectricityDemand",input_name="reactive_power",input_unit="VAr",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EConnection",input_name="heat_to_dw",input_unit="W",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="HybridHeatPump",input_name="buffer_temperature",input_unit="K",input_type=h.HelicsDataType.DOUBLE),
            SubscriptionDescription(esdl_type="HybridHeatPump",input_name="house_temperatures",input_unit="K",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EVChargingStation",input_name="state_of_charge_ev",input_unit="J",input_type=h.HelicsDataType.DOUBLE)
        ]

        expected_input_descriptions = [
            CalculationServiceInput("EConnection", "heat_to_dw", '7415cddb-b735-4646-b772-47f101b5c7a8', "W", h.HelicsDataType.VECTOR, simulator_esdl_id, "EConnection/heat_to_dw/7415cddb-b735-4646-b772-47f101b5c7a8"),
            CalculationServiceInput("ElectricityDemand", "active_power", '5ad97622-7226-40b1-a163-260b3478b1e3', "W", h.HelicsDataType.VECTOR, simulator_esdl_id, "ElectricityDemand/active_power/5ad97622-7226-40b1-a163-260b3478b1e3"),
            CalculationServiceInput("ElectricityDemand", "reactive_power", '5ad97622-7226-40b1-a163-260b3478b1e3', "VAr", h.HelicsDataType.VECTOR, simulator_esdl_id, "ElectricityDemand/reactive_power/5ad97622-7226-40b1-a163-260b3478b1e3")
        ]

        calculation_services = [
            "ElectricityDemand",
            "EConnection"
        ]

        # Execute
        inputs = esdl_helper.get_connected_input_esdl_objects(simulator_esdl_id, calculation_services, subscription_descriptions)

        # Assert correct assets are extracted from esdl file
        self.assertListEqual(expected_input_descriptions, inputs)
    
    def test_esdl_entity_recevies_subscriptions_from_connected_entities(self):

        # Arrange
        simulator_esdl_id = '7415cddb-b735-4646-b772-47f101b5c7a8'

        esdl_helper = EsdlHelper(self.encoded_base64_esdl)

        subscription_descriptions = [
            SubscriptionDescription(esdl_type="ElectricityDemand",input_name="active_power",input_unit="W",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="ElectricityDemand",input_name="reactive_power",input_unit="VAr",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="PVInstallation",input_name="potential_active_power",input_unit="W",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="HybridHeatPump",input_name="buffer_temperature",input_unit="K",input_type=h.HelicsDataType.DOUBLE),
            SubscriptionDescription(esdl_type="HybridHeatPump",input_name="house_temperatures",input_unit="K",input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EVChargingStation",input_name="state_of_charge_ev",input_unit="J",input_type=h.HelicsDataType.DOUBLE)
        ]

        expected_input_descriptions = [
            CalculationServiceInput("ElectricityDemand", "active_power", '5ad97622-7226-40b1-a163-260b3478b1e3', "W", h.HelicsDataType.VECTOR, simulator_esdl_id, "ElectricityDemand/active_power/5ad97622-7226-40b1-a163-260b3478b1e3"),
            CalculationServiceInput("ElectricityDemand", "reactive_power", '5ad97622-7226-40b1-a163-260b3478b1e3', "VAr", h.HelicsDataType.VECTOR, simulator_esdl_id, "ElectricityDemand/reactive_power/5ad97622-7226-40b1-a163-260b3478b1e3"),
            CalculationServiceInput("PVInstallation", "potential_active_power", '208c4a92-148a-4893-b474-37cad47b2fcb', "W", h.HelicsDataType.VECTOR, simulator_esdl_id, "PVInstallation/potential_active_power/208c4a92-148a-4893-b474-37cad47b2fcb"),
            CalculationServiceInput("EVChargingStation", "state_of_charge_ev", '2c285e74-f018-4305-bdf5-dd0f49fcbeab', "J", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EVChargingStation/state_of_charge_ev/2c285e74-f018-4305-bdf5-dd0f49fcbeab"),
            CalculationServiceInput("HybridHeatPump", "buffer_temperature", '15bc27e8-97db-427c-959e-e2a2fca27f75', "K", h.HelicsDataType.DOUBLE, simulator_esdl_id, "HybridHeatPump/buffer_temperature/15bc27e8-97db-427c-959e-e2a2fca27f75"),
            CalculationServiceInput("HybridHeatPump", "house_temperatures", '15bc27e8-97db-427c-959e-e2a2fca27f75', "K", h.HelicsDataType.VECTOR, simulator_esdl_id, "HybridHeatPump/house_temperatures/15bc27e8-97db-427c-959e-e2a2fca27f75")
        ]

        calculation_services = [
            "ElectricityDemand",
            "PVInstallation",
            "EVChargingStation",
            "HeatPump",
            "HybridHeatPump"
        ]

        # Execute
        inputs = esdl_helper.get_connected_input_esdl_objects(simulator_esdl_id, calculation_services, subscription_descriptions)

        # Assert correct assets are extracted from esdl file
        self.assertListEqual(expected_input_descriptions, inputs)

    def test_esdl_entity_can_subscribe_to_non_connected_inputs(self):
        simulator_esdl_id = '7415cddb-b735-4646-b772-47f101b5c7a8'

        esdl_helper = EsdlHelper(self.encoded_base64_esdl)

        subscription_descriptions = [
            SubscriptionDescription("EnergyMarket", "DA_Price", "EUR", h.HelicsDataType.DOUBLE)
        ]

        expected_input_descriptions = [
            CalculationServiceInput("EnergyMarket", "DA_Price", '80f75d42-80a8-446e-8611-cb24154f2bd5', "EUR", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EnergyMarket/DA_Price/80f75d42-80a8-446e-8611-cb24154f2bd5")
        ]

        calculation_services = [
            "EnergyMarket"
        ]

        # Execute
        inputs = esdl_helper.get_connected_input_esdl_objects(simulator_esdl_id, calculation_services, subscription_descriptions)

        # Assert correct assets are extracted from esdl file
        self.assertListEqual(expected_input_descriptions, inputs)

    def test_esdl_entity_has_two_publications_then_connected_entity_can_subscribe_to_both(self):

        # Arrange

        simulator_esdl_id = '7415cddb-b735-4646-b772-47f101b5c7a8'

        esdl_helper = EsdlHelper(self.encoded_base64_esdl)

        subscription_descriptions = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE),
            SubscriptionDescription("PVInstallation", "PV_Dispatch2", "W", h.HelicsDataType.DOUBLE)
        ]

        expected_input_descriptions = [
            CalculationServiceInput("PVInstallation", "PV_Dispatch", '208c4a92-148a-4893-b474-37cad47b2fcb', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "PVInstallation/PV_Dispatch/208c4a92-148a-4893-b474-37cad47b2fcb"),
            CalculationServiceInput("PVInstallation", "PV_Dispatch2", '208c4a92-148a-4893-b474-37cad47b2fcb', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "PVInstallation/PV_Dispatch2/208c4a92-148a-4893-b474-37cad47b2fcb")
        ]

        calculation_services = [
            "PVInstallation"
        ]

        # Execute
        inputs = esdl_helper.get_connected_input_esdl_objects(simulator_esdl_id, calculation_services, subscription_descriptions)

        # Assert correct assets are extracted from esdl file
        self.assertListEqual(expected_input_descriptions, inputs)

    def test_non_energy_entity_subscriptions_are_correctly_extracted(self):
        # Arrange
        simulator_esdl_id = '06c59a5e-aa84-4a4d-90db-56fbe4eb266c'

        esdl_helper = EsdlHelper(self.encoded_base64_esdl)

        subscription_descriptions = [
            SubscriptionDescription("EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        expected_input_descriptions = [
            CalculationServiceInput("EConnection", "EConnectionDispatch", '7415cddb-b735-4646-b772-47f101b5c7a8', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/7415cddb-b735-4646-b772-47f101b5c7a8"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'fd7fc047-30b1-48e3-99d9-1bc882772170', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/fd7fc047-30b1-48e3-99d9-1bc882772170"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '8f155685-c164-4d0c-ad3f-3419f4b97c82', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/8f155685-c164-4d0c-ad3f-3419f4b97c82"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '1f776d2a-ea5b-43e1-94a1-aac7e8381e41', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/1f776d2a-ea5b-43e1-94a1-aac7e8381e41"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '8e43e731-e4a4-46ac-a5b0-7aec5031878b', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/8e43e731-e4a4-46ac-a5b0-7aec5031878b"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'f10ff819-1d81-4cc7-82dc-b02ffbc60bfc', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/f10ff819-1d81-4cc7-82dc-b02ffbc60bfc"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '221c77de-74f8-4293-bb4e-2dd39dee1acd', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/221c77de-74f8-4293-bb4e-2dd39dee1acd"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '18f85d6d-6051-4cdf-ab4c-e80a404e3c74', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/18f85d6d-6051-4cdf-ab4c-e80a404e3c74"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", '891c0abb-f6e8-4eb3-9045-d6c87120d281', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/891c0abb-f6e8-4eb3-9045-d6c87120d281"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'a6c6d5d0-ca19-4579-85f9-8fd99f77aaf3', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/a6c6d5d0-ca19-4579-85f9-8fd99f77aaf3"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'e69bae01-d2db-4829-bbb7-71148ead969b', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/e69bae01-d2db-4829-bbb7-71148ead969b"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'c569d7a1-d2d7-4c05-8e31-c641ea48e9ff', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/c569d7a1-d2d7-4c05-8e31-c641ea48e9ff"),
            CalculationServiceInput("EConnection", "EConnectionDispatch", 'b2c3bb3b-0b40-4bc2-975c-cd648fe03065', "W", h.HelicsDataType.DOUBLE, simulator_esdl_id, "EConnection/EConnectionDispatch/b2c3bb3b-0b40-4bc2-975c-cd648fe03065")
        ]

        calculation_services = [
            "EConnection"
        ]

        # Execute
        inputs = esdl_helper.get_connected_input_esdl_objects(simulator_esdl_id, calculation_services, subscription_descriptions)

        # Assert correct assets are extracted from esdl file
        self.assertListEqual(expected_input_descriptions, inputs)

if __name__ == '__main__':
    unittest.main()