import unittest
import tempfile
import os
from pythonbridge.ast.ast_manager import ASTManager


class TestCreateAST(unittest.TestCase):
    """Tests for the create_ast method."""

    def setUp(self):
        self.manager = ASTManager()

    def test_create_ast_valid_file(self):
        """Test parsing a valid Python file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write("def hello():\n    pass\n")
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            self.assertIsNotNone(self.manager.tree)
            self.assertEqual(
                self.manager.current_file_name, os.path.basename(tmp_file_path)
            )
        finally:
            os.unlink(tmp_file_path)

    def test_create_ast_nonexistent_file(self):
        """Test parsing a nonexistent file returns None."""
        result = self.manager.create_ast("/nonexistent/path/file.py")
        self.assertIsNone(result)
        self.assertIsNone(self.manager.tree)


class TestCheckParentIsClass(unittest.TestCase):
    """Tests for the check_parent_is_class method."""

    def setUp(self):
        self.manager = ASTManager()

    def test_function_inside_class_returns_true(self):
        """Test that a method inside a class returns True."""
        code = """
class MyClass:
    def my_method(self):
        pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            # Find the function definition node
            for node in self.manager.traverse_tree(self.manager.tree.root_node):
                if node.type == "function_definition":
                    self.assertTrue(self.manager.check_parent_is_class(node))
                    break
        finally:
            os.unlink(tmp_file_path)

    def test_standalone_function_returns_false(self):
        """Test that a standalone function returns False."""
        code = """
def standalone_function():
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            # Find the function definition node
            for node in self.manager.traverse_tree(self.manager.tree.root_node):
                if node.type == "function_definition":
                    self.assertFalse(self.manager.check_parent_is_class(node))
                    break
        finally:
            os.unlink(tmp_file_path)


class TestGetRelationships(unittest.TestCase):
    """Tests for the get_relationships method."""

    def setUp(self):
        self.manager = ASTManager()

    def test_extracts_regular_imports(self):
        """Test that regular import statements are extracted."""
        code = "import os\nimport sys\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("imports", relationships)
            self.assertEqual(len(relationships["imports"]), 2)
            callees = [r["callee"] for r in relationships["imports"]]
            self.assertIn("import os", callees)
            self.assertIn("import sys", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_from_imports(self):
        """Test that from...import statements are extracted."""
        code = "from os import path\nfrom sys import argv\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("imports_from", relationships)
            self.assertEqual(len(relationships["imports_from"]), 2)
            callees = [r["callee"] for r in relationships["imports_from"]]
            self.assertIn("from os import path", callees)
            self.assertIn("from sys import argv", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_class_definitions(self):
        """Test that class definitions are extracted."""
        code = """
class MyClass:
    pass

class AnotherClass:
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("class_def", relationships)
            self.assertEqual(len(relationships["class_def"]), 2)
            callees = [r["callee"] for r in relationships["class_def"]]
            self.assertIn("MyClass", callees)
            self.assertIn("AnotherClass", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_standalone_functions(self):
        """Test that standalone function definitions are extracted."""
        code = """
def my_function():
    pass

def another_function():
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("function_def", relationships)
            self.assertEqual(len(relationships["function_def"]), 2)
            callees = [r["callee"] for r in relationships["function_def"]]
            self.assertIn("my_function", callees)
            self.assertIn("another_function", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_excludes_methods_from_function_definitions(self):
        """Test that class methods are not included in function_def."""
        code = """
class MyClass:
    def my_method(self):
        pass

def standalone():
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("function_def", relationships)
            self.assertEqual(len(relationships["function_def"]), 1)
            self.assertEqual(relationships["function_def"][0]["callee"], "standalone")
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_methods_with_class_info(self):
        """Test that methods are extracted with their parent class."""
        code = """
class MyClass:
    def method_one(self):
        pass

    def method_two(self):
        pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("method", relationships)
            self.assertEqual(len(relationships["method"]), 2)
            for method in relationships["method"]:
                self.assertEqual(method["caller"], "MyClass")
                self.assertEqual(method["type"], "class_method")
            callees = [m["callee"] for m in relationships["method"]]
            self.assertIn("method_one", callees)
            self.assertIn("method_two", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_function_calls(self):
        """Test that function calls within functions are extracted."""
        code = """
def caller():
    helper()
    another_helper()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("call", relationships)
            self.assertEqual(len(relationships["call"]), 2)
            for call in relationships["call"]:
                self.assertEqual(call["caller"], "caller")
                self.assertEqual(call["type"], "function_call")
            callees = [c["callee"] for c in relationships["call"]]
            self.assertIn("helper", callees)
            self.assertIn("another_helper", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_extracts_class_instantiations(self):
        """Test that class instantiations are extracted."""
        code = """
def create_objects():
    obj1 = MyClass()
    obj2 = AnotherClass()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIn("instantiation", relationships)
            self.assertEqual(len(relationships["instantiation"]), 2)
            for inst in relationships["instantiation"]:
                self.assertEqual(inst["caller"], "create_objects")
                self.assertEqual(inst["type"], "class_instantiation")
            callees = [i["callee"] for i in relationships["instantiation"]]
            self.assertIn("MyClass", callees)
            self.assertIn("AnotherClass", callees)
        finally:
            os.unlink(tmp_file_path)

    def test_relationships_include_location(self):
        """Test that all relationships include location information."""
        code = "import os\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            for import_rel in relationships["imports"]:
                self.assertIn("location", import_rel)
                self.assertIsInstance(import_rel["location"], tuple)
                self.assertEqual(len(import_rel["location"]), 2)
        finally:
            os.unlink(tmp_file_path)

    def test_relationships_include_caller_as_filename(self):
        """Test that file-level relationships use filename as caller."""
        code = "import os\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            for import_rel in relationships["imports"]:
                self.assertEqual(
                    import_rel["caller"], os.path.basename(tmp_file_path)
                )
        finally:
            os.unlink(tmp_file_path)

    def test_empty_file_returns_empty_relationships(self):
        """Test that an empty file returns empty relationships dict."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write("")
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            self.assertIsInstance(relationships, dict)
            # Should be an empty dict or have empty lists
            for key in relationships:
                self.assertEqual(len(relationships[key]), 0)
        finally:
            os.unlink(tmp_file_path)

    def test_complex_file_extracts_all_relationships(self):
        """Test a complex file with multiple relationship types."""
        code = """
import os
from sys import path

class DataProcessor:
    def __init__(self):
        self.data = []

    def process(self, item):
        self.data.append(item)

def main():
    processor = DataProcessor()
    helper()

def helper():
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            self.manager.create_ast(tmp_file_path)
            relationships = self.manager.get_relationships()

            # Check imports
            self.assertEqual(len(relationships["imports"]), 1)
            self.assertEqual(len(relationships["imports_from"]), 1)

            # Check class definition
            self.assertEqual(len(relationships["class_def"]), 1)
            self.assertEqual(relationships["class_def"][0]["callee"], "DataProcessor")

            # Check standalone functions (should not include class methods)
            self.assertEqual(len(relationships["function_def"]), 2)
            func_names = [f["callee"] for f in relationships["function_def"]]
            self.assertIn("main", func_names)
            self.assertIn("helper", func_names)
            self.assertNotIn("__init__", func_names)
            self.assertNotIn("process", func_names)

            # Check methods
            self.assertEqual(len(relationships["method"]), 2)
            method_names = [m["callee"] for m in relationships["method"]]
            self.assertIn("__init__", method_names)
            self.assertIn("process", method_names)

            # Check instantiation
            self.assertEqual(len(relationships["instantiation"]), 1)
            self.assertEqual(
                relationships["instantiation"][0]["callee"], "DataProcessor"
            )
            self.assertEqual(relationships["instantiation"][0]["caller"], "main")

            # Check function call
            self.assertEqual(len(relationships["call"]), 1)
            self.assertEqual(relationships["call"][0]["callee"], "helper")
            self.assertEqual(relationships["call"][0]["caller"], "main")
        finally:
            os.unlink(tmp_file_path)


if __name__ == "__main__":
    unittest.main()
