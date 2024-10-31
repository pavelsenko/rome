import os
import ast

class UnitTestGenerator:
    def __init__(self, project_dir, uncovered_functions):
        self.project_dir = project_dir
        self.uncovered_functions = uncovered_functions
        self.test_dir = os.path.join(project_dir, 'tst')
        self.existing_tests = set()

    def get_existing_tests(self):
        """Collect existing test methods to avoid duplicates."""
        for dirpath, dirnames, filenames in os.walk(self.test_dir):
            for filename in filenames:
                if filename.startswith('test_') and filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, 'r', encoding='utf-8') as file:
                        try:
                            node = ast.parse(file.read(), filename=filepath)
                            for child in ast.walk(node):
                                if isinstance(child, ast.FunctionDef):
                                    self.existing_tests.add(child.name)
                        except SyntaxError as e:
                            print(f"SyntaxError in file {filepath}: {e}")

    def generate_tests(self):
        """Generate unit test files for uncovered functions."""
        self.get_existing_tests()
        for func_full_name in self.uncovered_functions:
            parts = func_full_name.split('.')
            if len(parts) >= 2:
                module_path = '.'.join(parts[:-1])
                function_name = parts[-1]
                test_class_name = f"Test{function_name.capitalize()}"
                test_method_name = f"test_{function_name}"

                # Avoid duplicate test methods
                if test_method_name in self.existing_tests:
                    continue

                # Create test file path
                module_file = module_path.replace('.', os.sep) + '.py'
                module_relpath = os.path.relpath(module_file, self.project_dir)
                test_file_name = f"test_{os.path.basename(module_file)}"
                test_file_dir = os.path.join(self.test_dir, os.path.dirname(module_relpath))
                os.makedirs(test_file_dir, exist_ok=True)
                test_file_path = os.path.join(test_file_dir, test_file_name)

                # Generate test code
                test_code = self.create_test_code(module_path, function_name, test_class_name, test_method_name)

                # Write to test file
                with open(test_file_path, 'a', encoding='utf-8') as test_file:
                    test_file.write(test_code)

                print(f"Generated test for {func_full_name} at {test_file_path}")

    def create_test_code(self, module_path, function_name, test_class_name, test_method_name):
        """Create the code for the unit test."""
        test_code = f"""
import unittest
from {module_path} import {function_name}

class {test_class_name}(unittest.TestCase):
    def {test_method_name}(self):
        # TODO: Implement test case for {function_name}
        # Example input parameters
        input_params = {{'param1': value1, 'param2': value2}}  # Replace with actual parameters

        # If the function returns a value
        result = {function_name}(**input_params)
        expected_result = None  # Define the expected result
        self.assertEqual(result, expected_result)

        # If the function modifies a dict parameter
        # initial_dict = {{'key': 'initial_value'}}
        # {function_name}(initial_dict)
        # expected_dict = {{'key': 'modified_value'}}
        # self.assertEqual(initial_dict, expected_dict)

if __name__ == '__main__':
    unittest.main()
"""
        return test_code

if __name__ == "__main__":
    # Assume we have a list of uncovered functions from the analyzer
    project_directory = 'path_to_your_project'  # Replace with your project path
    uncovered_functions = [
        'module.submodule.function_name',
        'module.ClassName.method_name',
        # Add more functions as needed
    ]

    test_generator = UnitTestGenerator(project_directory, uncovered_functions)
    test_generator.generate_tests()

