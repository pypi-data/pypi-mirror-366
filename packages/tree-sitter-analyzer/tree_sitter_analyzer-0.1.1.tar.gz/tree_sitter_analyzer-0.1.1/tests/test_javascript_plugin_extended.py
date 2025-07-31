#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extended Tests for JavaScript Plugin

Additional test cases to improve coverage for JavaScript plugin functionality.
"""

import sys

# Add project root to path
sys.path.insert(0, ".")

import pytest
import pytest_asyncio
# Mock functionality now provided by pytest-mock

from tree_sitter_analyzer.models import Class, Function, Import, Variable
from tree_sitter_analyzer.plugins.javascript_plugin import (
    JavaScriptElementExtractor,
    JavaScriptPlugin,
)


@pytest.fixture
def extractor():
    """Fixture to provide JavaScriptElementExtractor instance"""
    return JavaScriptElementExtractor()


class TestJavaScriptElementExtractorExtended:
    """Extended tests for JavaScript element extractor"""

    def test_extract_function_info_with_valid_node(self, extractor, mocker):
        """Test function info extraction with valid node"""
        # Mock node structure for function declaration
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (3, 1)
        mock_node.start_byte = 0
        mock_node.end_byte = 34

        # Mock identifier child for function name - "testFunc" is at position 9-17
        mock_identifier = mocker.MagicMock()
        mock_identifier.type = "identifier"
        mock_identifier.start_byte = 9
        mock_identifier.end_byte = 17

        # Mock formal parameters - "a" is at position 18-19
        mock_params = mocker.MagicMock()
        mock_params.type = "formal_parameters"
        mock_param_child = mocker.MagicMock()
        mock_param_child.type = "identifier"
        mock_param_child.start_byte = 18
        mock_param_child.end_byte = 19
        mock_params.children = [mock_param_child]

        mock_node.children = [mock_identifier, mock_params]

        source_code = "function testFunc(a) { return a; }"

        function = extractor._extract_function_info(mock_node, source_code)

        assert function is not None
        assert isinstance(function, Function)
        assert function.name == "testFunc"
        assert function.parameters == ["a"]
        assert function.language == "javascript"

    def test_extract_function_info_with_arrow_function(self, extractor, mocker):
        """Test function info extraction with arrow function structure"""
        # Mock node structure for arrow function
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (1, 0)
        mock_node.start_byte = 0
        mock_node.end_byte = 29

        # Mock variable declarator
        mock_declarator = mocker.MagicMock()
        mock_declarator.type = "variable_declarator"

        # Mock identifier for function name - "myFunc" is at position 6-12
        mock_identifier = mocker.MagicMock()
        mock_identifier.type = "identifier"
        mock_identifier.start_byte = 6
        mock_identifier.end_byte = 12

        # Mock arrow function
        mock_arrow_func = mocker.MagicMock()
        mock_arrow_func.type = "arrow_function"

        # Mock formal parameters - "x" is at position 16-17
        mock_params = mocker.MagicMock()
        mock_params.type = "formal_parameters"
        mock_param_child = mocker.MagicMock()
        mock_param_child.type = "identifier"
        mock_param_child.start_byte = 16
        mock_param_child.end_byte = 17
        mock_params.children = [mock_param_child]

        mock_arrow_func.children = [mock_params]
        mock_declarator.children = [mock_identifier, mock_arrow_func]
        mock_node.children = [mock_declarator]

        source_code = "const myFunc = (x) => x * 2;"

        function = extractor._extract_function_info(mock_node, source_code)

        assert function is not None
        assert function.name == "myFunc"
        assert function.parameters == ["x"]

    def test_extract_function_info_with_no_name(self, extractor, mocker):
        """Test function info extraction with no name node"""
        mock_node = mocker.MagicMock()
        mock_node.children = []

        function = extractor._extract_function_info(mock_node, "function() {}")

        assert function is None

    def test_extract_function_info_with_exception(self, extractor, mocker):
        """Test function info extraction with exception"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = None  # This will cause exception

        function = extractor._extract_function_info(mock_node, "test")

        assert function is None

    def test_extract_class_info_with_valid_node(self, extractor, mocker):
        """Test class info extraction with valid node"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (5, 1)
        mock_node.start_byte = 0
        mock_node.end_byte = 34

        # Mock identifier for class name - "MyClass" is at position 6-13
        mock_identifier = mocker.MagicMock()
        mock_identifier.type = "identifier"
        mock_identifier.start_byte = 6
        mock_identifier.end_byte = 13

        mock_node.children = [mock_identifier]

        source_code = "class MyClass { constructor() {} }"

        cls = extractor._extract_class_info(mock_node, source_code)

        assert cls is not None
        assert isinstance(cls, Class)
        assert cls.name == "MyClass"
        assert cls.class_type == "class"
        assert cls.language == "javascript"

    def test_extract_class_info_with_no_name(self, extractor, mocker):
        """Test class info extraction with no name node"""
        mock_node = mocker.MagicMock()
        mock_node.children = []

        cls = extractor._extract_class_info(mock_node, "class {}")

        assert cls is None

    def test_extract_class_info_with_exception(self, extractor, mocker):
        """Test class info extraction with exception"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = None  # This will cause exception

        cls = extractor._extract_class_info(mock_node, "test")

        assert cls is None

    def test_extract_variable_info_with_valid_node(self, extractor, mocker):
        """Test variable info extraction with valid node"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (1, 0)
        mock_node.start_byte = 0
        mock_node.end_byte = 15

        # Mock variable declarator
        mock_declarator = mocker.MagicMock()
        mock_declarator.type = "variable_declarator"

        # Mock identifier for variable name - "myVar" is at position 4-9
        mock_identifier = mocker.MagicMock()
        mock_identifier.type = "identifier"
        mock_identifier.start_byte = 4
        mock_identifier.end_byte = 9

        mock_declarator.children = [mock_identifier]
        mock_node.children = [mock_declarator]

        source_code = "let myVar = 42;"

        variable = extractor._extract_variable_info(mock_node, source_code)

        assert variable is not None
        assert isinstance(variable, Variable)
        assert variable.name == "myVar"
        assert variable.language == "javascript"

    def test_extract_variable_info_with_no_name(self, extractor, mocker):
        """Test variable info extraction with no name node"""
        mock_node = mocker.MagicMock()
        mock_declarator = mocker.MagicMock()
        mock_declarator.type = "variable_declarator"
        mock_declarator.children = []
        mock_node.children = [mock_declarator]

        variable = extractor._extract_variable_info(mock_node, "let;")

        assert variable is None

    def test_extract_variable_info_with_exception(self, extractor, mocker):
        """Test variable info extraction with exception"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = None  # This will cause exception

        variable = extractor._extract_variable_info(mock_node, "test")

        assert variable is None

    def test_extract_import_info_with_valid_node(self, extractor, mocker):
        """Test import info extraction with valid node"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (1, 0)
        mock_node.start_byte = 0
        mock_node.end_byte = 27

        # Mock string node for import source - "'./module'" is at position 16-26
        mock_string = mocker.MagicMock()
        mock_string.type = "string"
        mock_string.start_byte = 16
        mock_string.end_byte = 26

        mock_node.children = [mock_string]

        source_code = "import foo from './module';"

        imp = extractor._extract_import_info(mock_node, source_code)

        assert imp is not None
        assert isinstance(imp, Import)
        assert imp.name == "import"
        assert imp.module_path == "./module"
        assert imp.language == "javascript"

    def test_extract_import_info_with_double_quotes(self, extractor, mocker):
        """Test import info extraction with double quotes"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = (0, 0)
        mock_node.end_point = (1, 0)
        mock_node.start_byte = 0
        mock_node.end_byte = 27

        # Mock string node for import source - '"./module"' is at position 16-26
        mock_string = mocker.MagicMock()
        mock_string.type = "string"
        mock_string.start_byte = 16
        mock_string.end_byte = 26

        mock_node.children = [mock_string]

        source_code = 'import foo from "./module";'

        imp = extractor._extract_import_info(mock_node, source_code)

        assert imp is not None
        assert imp.module_path == "./module"

    def test_extract_import_info_with_no_source(self, extractor, mocker):
        """Test import info extraction with no source node"""
        mock_node = mocker.MagicMock()
        mock_node.children = []

        imp = extractor._extract_import_info(mock_node, "import;")

        assert imp is None

    def test_extract_import_info_with_exception(self, extractor, mocker):
        """Test import info extraction with exception"""
        mock_node = mocker.MagicMock()
        mock_node.start_point = None  # This will cause exception

        imp = extractor._extract_import_info(mock_node, "test")

        assert imp is None

    def test_extract_functions_with_language_available(self, extractor, mocker):
        """Test function extraction with language available"""
        # Mock tree with language
        mock_language = mocker.MagicMock()
        mock_query = mocker.MagicMock()
        mock_query.captures.return_value = {"func.declaration": []}
        mock_language.query.return_value = mock_query

        mock_tree = mocker.MagicMock()
        mock_tree.language = mock_language
        mock_tree.root_node = mocker.MagicMock()

        source_code = "function test() { return 'hello'; }"

        functions = extractor.extract_functions(mock_tree, source_code)

        assert isinstance(functions, list)
        # Should call query 4 times (for each function pattern: function_declaration, method_definition, arrow_function, function_expression)
        assert mock_language.query.call_count == 4

    def test_extract_functions_with_exception(self, extractor, mocker):
        """Test function extraction with exception during query"""
        mock_language = mocker.MagicMock()
        mock_language.query.side_effect = Exception("Query failed")

        mock_tree = mocker.MagicMock()
        mock_tree.language = mock_language

        functions = extractor.extract_functions(mock_tree, "test code")

        # Should return empty list on exception
        assert functions == []

    def test_extract_classes_with_exception(self, extractor, mocker):
        """Test class extraction with exception during query"""
        mock_language = mocker.MagicMock()
        mock_language.query.side_effect = Exception("Query failed")

        mock_tree = mocker.MagicMock()
        mock_tree.language = mock_language

        classes = extractor.extract_classes(mock_tree, "test code")

        assert classes == []

    def test_extract_variables_with_exception(self, extractor, mocker):
        """Test variable extraction with exception during query"""
        mock_language = mocker.MagicMock()
        mock_language.query.side_effect = Exception("Query failed")

        mock_tree = mocker.MagicMock()
        mock_tree.language = mock_language

        variables = extractor.extract_variables(mock_tree, "test code")

        assert variables == []

    def test_extract_imports_with_exception(self, extractor, mocker):
        """Test import extraction with exception during query"""
        mock_language = mocker.MagicMock()
        mock_language.query.side_effect = Exception("Query failed")

        mock_tree = mocker.MagicMock()
        mock_tree.language = mock_language

        imports = extractor.extract_imports(mock_tree, "test code")

        assert imports == []


class TestJavaScriptPluginExtended:
    """Extended tests for JavaScript plugin"""

    def test_plugin_properties(self):
        """Test JavaScript plugin properties"""
        plugin = JavaScriptPlugin()

        assert plugin.language_name == "javascript"
        assert plugin.get_language_name() == "javascript"
        assert ".js" in plugin.file_extensions
        assert ".mjs" in plugin.file_extensions
        assert ".jsx" in plugin.file_extensions
        assert plugin.get_file_extensions() == [".js", ".mjs", ".jsx"]

    def test_create_extractor(self):
        """Test extractor creation"""
        plugin = JavaScriptPlugin()
        extractor = plugin.create_extractor()

        assert isinstance(extractor, JavaScriptElementExtractor)

    def test_get_extractor(self):
        """Test get extractor method"""
        plugin = JavaScriptPlugin()
        extractor = plugin.get_extractor()

        assert isinstance(extractor, JavaScriptElementExtractor)

    def test_tree_sitter_language_caching(self):
        """Test tree-sitter language caching"""
        plugin = JavaScriptPlugin()

        # First call
        language1 = plugin.get_tree_sitter_language()

        # Second call should return cached result
        language2 = plugin.get_tree_sitter_language()

        # Should be the same object (cached)
        assert language1 is language2

    def test_tree_sitter_language_loading(self):
        """Test tree-sitter language loading"""
        plugin = JavaScriptPlugin()
        language = plugin.get_tree_sitter_language()

        # Language may be None if tree-sitter-javascript is not available
        assert language is None or hasattr(language, "query")


class TestJavaScriptPluginErrorHandling:
    """Test error handling in JavaScript plugin"""

    def test_extract_functions_without_language(self, mocker):
        """Test function extraction without language"""
        extractor = JavaScriptElementExtractor()
        mock_tree = mocker.MagicMock()
        mock_tree.language = None

        functions = extractor.extract_functions(mock_tree, "function test() {}")

        assert functions == []

    def test_extract_classes_without_language(self, mocker):
        """Test class extraction without language"""
        extractor = JavaScriptElementExtractor()
        mock_tree = mocker.MagicMock()
        mock_tree.language = None

        classes = extractor.extract_classes(mock_tree, "class Test {}")

        assert classes == []

    def test_extract_variables_without_language(self, mocker):
        """Test variable extraction without language"""
        extractor = JavaScriptElementExtractor()
        mock_tree = mocker.MagicMock()
        mock_tree.language = None

        variables = extractor.extract_variables(mock_tree, "let x = 1;")

        assert variables == []

    def test_extract_imports_without_language(self, mocker):
        """Test import extraction without language"""
        extractor = JavaScriptElementExtractor()
        mock_tree = mocker.MagicMock()
        mock_tree.language = None

        imports = extractor.extract_imports(mock_tree, "import './module';")

        assert imports == []
