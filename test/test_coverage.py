import os
import ast

class CodeCoverageAnalyzer:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.test_dir = os.path.join(project_dir, 'tst')
        self.function_definitions = set()
        self.function_calls_in_tests = set()

    def get_function_definitions(self):
        for dirpath, dirnames, filenames in os.walk(self.project_dir):
            # Skip the 'tst' directory and its subdirectories
            if self.test_dir in dirpath:
                continue
            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, 'r', encoding='utf-8') as file:
                        try:
                            node = ast.parse(file.read(), filename=filepath)
                            self.extract_function_definitions(node, filepath)
                        except SyntaxError as e:
                            print(f"SyntaxError in file {filepath}: {e}")

    def extract_function_definitions(self, node, filepath):
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                function_name = child.name
                # Get the module path relative to the project directory
                module_path = os.path.relpath(filepath, self.project_dir)
                module_name = module_path.replace(os.sep, '.')[:-3]  # remove .py extension
                full_function_name = f"{module_name}.{function_name}"
                self.function_definitions.add(full_function_name)
            elif isinstance(child, ast.ClassDef):
                class_name = child.name
                for item in child.body:
                    if isinstance(item, ast.FunctionDef):
                        function_name = item.name
                        module_path = os.path.relpath(filepath, self.project_dir)
                        module_name = module_path.replace(os.sep, '.')[:-3]
                        full_function_name = f"{module_name}.{class_name}.{function_name}"
                        self.function_definitions.add(full_function_name)

    def get_function_calls_in_tests(self):
        for dirpath, dirnames, filenames in os.walk(self.test_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, 'r', encoding='utf-8') as file:
                        try:
                            node = ast.parse(file.read(), filename=filepath)
                            self.extract_function_calls(node)
                        except SyntaxError as e:
                            print(f"SyntaxError in file {filepath}: {e}")

    def extract_function_calls(self, node):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name):
                    function_name = func.id
                    self.function_calls_in_tests.add(function_name)
                elif isinstance(func, ast.Attribute):
                    # For method calls like obj.method()
                    function_name = func.attr
                    self.function_calls_in_tests.add(function_name)

    def analyze_coverage(self):
        total_functions = len(self.function_definitions)
        if total_functions == 0:
            print("No functions found in the project code.")
            return
        covered_functions = set()
        for func_def in self.function_definitions:
            func_name = func_def.split('.')[-1]  # Get the function name
            if func_name in self.function_calls_in_tests:
                covered_functions.add(func_def)
        uncovered_functions = self.function_definitions - covered_functions
        coverage_percentage = (len(covered_functions) / total_functions) * 100

        print(f"Total functions in project code: {total_functions}")
        print(f"Functions covered by tests: {len(covered_functions)}")
        print(f"Coverage percentage: {coverage_percentage:.2f}%")
        print("\nFunctions not covered by tests:")
        for func in sorted(uncovered_functions):
            print(func)

if __name__ == "__main__":
    project_directory = 'path_to_your_project'  # Replace with your project path
    analyzer = CodeCoverageAnalyzer(project_directory)
    analyzer.get_function_definitions()
    analyzer.get_function_calls_in_tests()
    analyzer.analyze_coverage()
