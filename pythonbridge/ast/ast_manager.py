from tree_sitter import Language, Parser, Query, QueryCursor, Node
from typing import Generator
import tree_sitter_python as tspython
from collections import defaultdict
import os

# Set up the parser
# PY_LANGUAGE = Language(tspython.language())
# parser = Parser(PY_LANGUAGE)


class ASTManager:
    """
    Manages Abstract Syntax Tree (AST) parsing and relationship extraction for Python files.

    This class uses tree-sitter to parse Python source code and extract structural information
    including imports, class definitions, function definitions, methods, and their relationships.

    Attributes:
        language (Language): The tree-sitter language object for Python
        parser (Parser): The tree-sitter parser instance
        tree (Tree): The parsed AST of the current file
        current_file_name (str): Base name of the currently parsed file
    """

    def __init__(self):
        """Initialize the AST manager with a Python language parser."""
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        self.tree = None
        self.current_file_name = None

    def create_ast(self, file_path: str):
        """
        Parse a Python file and create its Abstract Syntax Tree.

        Args:
            file_path (str): Absolute or relative path to the Python file to parse
        """
        try:
            with open(file_path, "r") as file:
                content = file.read()
                self.tree = self.parser.parse(bytes(content, "utf8"))
                self.current_file_name = os.path.basename(file_path)
        except FileNotFoundError as e:
            print(f"file is not found: {e}")
            return None

    def traverse_tree(self, node: Node) -> Generator[Node, None, None]:
        """
        Depth-first traversal of the AST starting from a given node. (code available in python treesitter)

        This generator yields every node in the subtree in depth-first order,
        visiting each node exactly once.

        Args:
            node (Node): The root node to start traversal from
        """
        cursor = node.walk()

        visited_children = False
        while True:
            if not visited_children:
                # yield will pause the function and gives one node
                yield cursor.node
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break

    def print_node_vals(self, node) -> None:
        """
        Debug utility to print detailed information about a node.

        Args:
            node (Node): The tree-sitter node to inspect
        """
        print(f"Type: {node.type}")
        print(f"Text: {node.text.decode('utf8')}")
        print(f"Start: {node.start_point}")
        print(f"End: {node.end_point}")
        print(f"Start byte: {node.start_byte}")
        print(f"End byte: {node.end_byte}")

    def check_parent_is_class(self, node) -> bool:
        """
        Check if a node is nested inside a class definition.

        Walks up the ancestor chain to determine if any parent is a class_definition.
        Used to distinguish standalone functions from class methods.

        Args:
            node (Node): The node to check
        """
        current = node
        while current is not None:
            # if its a class return True
            if current.type == "class_definition":
                return True
            # Move up one level
            current = current.parent
        return False

    def get_relationships(self) -> dict:
        """
        Extract all structural relationships from the parsed AST.

        This is the main analysis method that queries the AST for:
        - Import statements (import and from...import)
        - Class definitions
        - Standalone function definitions (excluding methods)
        - Methods and which classes they belong to
        - Function calls within standalone functions
        - Class instantiations

        Returns:
            dict: A dictionary with the following keys:
                - "imports": List of import statements
                - "imports_from": List of from...import statements
                - "class_def": List of class definitions
                - "function_def": List of standalone function definitions
                - "method": List of methods and their parent classes
                - "call": List of function calls
                - "instantiation": List of class instantiations

        Structure of relationship entries:
            {
                "caller": str,  # File name or function/class name
                "callee": str,  # What is being imported/called/defined
                "type": str,    # Optional: type of relationship
                "location": tuple  # (start_point, end_point)
            }
        """

        # dictionary to store all relationships
        relationships = defaultdict(list)

        # query for imports, functions, classes
        query = Query(
            self.language,
            """
            (import_statement) @import
            (import_from_statement) @import_from

            (function_definition
            name: (identifier) @function.def
            body: (block) @function.block)

            (class_definition
            name: (identifier) @class.def
            body: (block) @class.block)
            """,
        )

        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(self.tree.root_node)

        # extract regular imports (import os)
        if "import" in captures:
            for node in captures["import"]:
                relationships["imports"].append(
                    {
                        "caller": self.current_file_name,
                        "callee": node.text.decode("utf8"),
                        "location": (node.start_point, node.end_point),
                    }
                )

        # extract from imports (from x import y)
        if "import_from" in captures:
            for node in captures["import_from"]:
                relationships["imports_from"].append(
                    {
                        "caller": self.current_file_name,
                        "callee": node.text.decode("utf8"),
                        "location": (node.start_point, node.end_point),
                    }
                )

        # extract all class definitions
        if "class.def" in captures:
            for node in captures["class.def"]:
                relationships["class_def"].append(
                    {
                        "caller": self.current_file_name,
                        "callee": node.text.decode("utf8"),
                        "location": (node.start_point, node.end_point),
                    }
                )

        # extract all function definitions
        if "function.def" in captures:
            for node in captures["function.def"]:
                if self.check_parent_is_class(node):
                    continue
                self.print_node_vals(node)
                relationships["function_def"].append(
                    {
                        "caller": self.current_file_name,
                        "callee": node.text.decode("utf8"),
                        "location": (node.start_point, node.end_point),
                    }
                )

        # extract all methods within classes
        if "class.def" in captures:
            # every class found in a file
            for i, class_name_node in enumerate(captures["class.def"]):
                class_name = class_name_node.text.decode("utf8")
                class_def_node = class_name_node.parent
                class_body = class_def_node.child_by_field_name("body")

                # search through all the nodes within the class body
                for node in self.traverse_tree(class_body):
                    # (the method in the class)
                    if node.type == "function_definition":
                        # function name within class
                        method_name_node = node.child_by_field_name("name")
                        if method_name_node:
                            callee_name = method_name_node.text.decode("utf8")

                            if callee_name:
                                relationships["method"].append(
                                    {
                                        "caller": class_name,
                                        "callee": callee_name,
                                        "type": "class_method",
                                        "location": (node.start_point, node.end_point),
                                    }
                                )

        # extract all other function calls within functions and class instantiations
        if "function.def" in captures:
            # enumerate will line function name with the body (0 with 0, 1 with 1, etc.)
            for i, func_name_node in enumerate(captures["function.def"]):
                if self.check_parent_is_class(func_name_node):
                    continue
                func_name = func_name_node.text.decode("utf8")
                func_def_node = func_name_node.parent
                func_body = func_def_node.child_by_field_name("body")
                # loop through the function body and search for function calls
                for node in self.traverse_tree(func_body):
                    # call nodes represent any function calls
                    if node.type == "call":
                        function_name_node = node.child_by_field_name("function")
                        if function_name_node:
                            callee_name = function_name_node.text.decode("utf8")

                            # safety check for empty string
                            if callee_name:
                                # if class instantiation
                                if callee_name[0].isupper():
                                    relationships["instantiation"].append(
                                        {
                                            "caller": func_name,
                                            "callee": callee_name,
                                            "type": "class_instantiation",
                                            "location": (
                                                node.start_point,
                                                node.end_point,
                                            ),
                                        }
                                    )

                                # regular function
                                else:
                                    relationships["call"].append(
                                        {
                                            "caller": func_name,
                                            "callee": callee_name,
                                            "type": "function_call",
                                            "location": (
                                                node.start_point,
                                                node.end_point,
                                            ),
                                        }
                                    )

        return dict(relationships)
