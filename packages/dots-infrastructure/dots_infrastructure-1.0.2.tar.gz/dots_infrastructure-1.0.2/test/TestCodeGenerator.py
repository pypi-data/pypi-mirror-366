from pathlib import Path
import unittest
from unittest.mock import MagicMock, call

from dots_infrastructure.code_gen.code_gen import CodeGenerator
from dots_infrastructure.code_gen.code_meta_data import Calculation, CalculationServiceInputData, CalculationServiceOutputData, RelevantLink


class TestLogicAddingCalculations(unittest.TestCase):
    def setUp(self):
        self.code_generator = CodeGenerator()
        self.code_generator.render_template = MagicMock()
        self.test_template_dir = Path("test_template_path")
        self.test_output_dir = Path("test_output_dir")
        
    def test_exception_is_raised_when_invalid_data_type_is_provided(self):
        # Arrange
        with open("test_fault_code_gen_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute and Assert
        with self.assertRaises(ValueError):
            self.code_generator.render_calculation_service(self.test_template_dir, input_json, self.test_output_dir)

        with self.assertRaises(ValueError):
            self.code_generator.render_output_dataclasses(self.test_template_dir, input_json, self.test_output_dir)

    def test_when_valid_input_is_supplied_render_template_cs_is_called_correctly(self):
        # Arrange
        with open("test_valid_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute
        self.code_generator.render_calculation_service(self.test_template_dir, input_json, self.test_output_dir)

        # Assert
        expected_inputs = [
            CalculationServiceInputData("input1", "Weather", "input 1 description", "K", "STRING", "input1"),
        ]
        expected_outputs = [
            CalculationServiceOutputData("output1", "output 1 description", "W", "DOUBLE", python_data_type='float', python_name='output1')
        ]
        expected_calculations = [
            Calculation("test calculation", "test", 900, 0, expected_inputs, expected_outputs, calculation_function_name="test_calculation", calculation_output_class_name=None)
        ]
        calls = [
            call(template_path=self.test_template_dir, output_dir=self.test_output_dir, output_file=Path("test_output_dir/test_base.py"), calculations=expected_calculations, name="TestBase", esdl_type="PVInstallation"),
        ]
        self.code_generator.render_template.assert_has_calls(calls)

    def test_when_valid_input_is_supplied_render_template_dataclasses_is_called_correctly(self):
        # Arrange
        with open("test_valid_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute
        self.code_generator.render_output_dataclasses(self.test_template_dir, input_json, self.test_output_dir)

        # Assert
        expected_inputs = [
            CalculationServiceInputData("input1", "Weather", "input 1 description", "K", "STRING", None),
        ]
        expected_outputs = [
            CalculationServiceOutputData("output1", "output 1 description", "W", "DOUBLE", python_data_type='float', python_name='output1')
        ]
        expected_calculations = [
            Calculation("test calculation", "test", 900, 0, expected_inputs, expected_outputs, calculation_function_name=None, calculation_output_class_name='TestCalculationOutput')
        ]
        calls = [
            call(template_path=self.test_template_dir, output_dir=self.test_output_dir, output_file=Path("test_output_dir/test_dataclasses.py"), calculations=expected_calculations),
        ]
        self.code_generator.render_template.assert_has_calls(calls)

if __name__ == '__main__':
    unittest.main()