import unittest

from dots_infrastructure.CalculationServiceHelperFunctions import get_single_param_with_name, get_vector_param_with_name

class TestLogicAddingCalculations(unittest.TestCase):

    def test_get_single_param_with_name(self):
        # Arrange
        param_dict = {
            "a/b/active_power": 1,
            "a/b/reactive_power": 2
        }
        name = "active_power"

        # Execute
        result = get_single_param_with_name(param_dict, name)
        expected_result = 1

        # Assert
        self.assertEqual(result, expected_result)

    def test_get_vector_param_with_name(self):
        # Arrange
        param_dict = {
            "a/a/active_power": 1,
            "a/b/active_power": 2,
            "a/c/reactive_power": 3
        }
        name = "active_power"

        # Execute
        result = get_vector_param_with_name(param_dict, name)
        expected_result = [1, 2]

        # Assert
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()