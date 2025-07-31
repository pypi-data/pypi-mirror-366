#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Tests for CLI module

This module provides comprehensive test coverage for the CLI functionality,
focusing on uncovered code paths to improve overall coverage.
Follows TDD principles and .roo-config.json requirements.
"""

import json
import logging
import os
import sys
import tempfile
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from tree_sitter_analyzer.cli_main import main


@pytest.fixture
def sample_java_file():
    """Fixture providing a temporary Java file for testing"""
    java_code = '''
package com.example.test;

import java.util.List;

/**
 * Sample class for testing
 */
public class TestClass {
    private String field1;
    
    /**
     * Constructor
     */
    public TestClass(String field1) {
        this.field1 = field1;
    }
    
    /**
     * Public method
     */
    public String getField1() {
        return field1;
    }
}
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False, encoding='utf-8') as f:
        f.write(java_code)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestCLIAdvancedOptions:
    """Test cases for advanced CLI options"""

    def test_advanced_option_json_output(self, monkeypatch, sample_java_file):
        """Test --advanced option with JSON output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--advanced", "--output-format", "json"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_advanced_option_text_output(self, monkeypatch, sample_java_file):
        """Test --advanced option with text output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--advanced", "--output-format", "text"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_advanced_option_analysis_failure(self, monkeypatch, sample_java_file):
        """Test --advanced option when analysis fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--advanced"])
        
        # Mock the UnifiedAnalysisEngine.analyze method to return failed result
        with patch('tree_sitter_analyzer.core.analysis_engine.UnifiedAnalysisEngine.analyze') as mock_analyze:
            from tree_sitter_analyzer.models import AnalysisResult
            
            # Create a failed analysis result
            failed_result = AnalysisResult(
                file_path=sample_java_file,
                line_count=0,
                elements=[],
                node_count=0,
                query_results={},
                source_code="",
                language="java",
                success=False,
                error_message="Mocked analysis failure"
            )
            mock_analyze.return_value = failed_result
            
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "解析に失敗しました" in error_output

    def test_statistics_option(self, monkeypatch, sample_java_file):
        """Test --statistics option"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--advanced", "--statistics"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_statistics_option_json(self, monkeypatch, sample_java_file):
        """Test --statistics option with JSON output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--advanced", "--statistics", "--output-format", "json"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0


class TestCLISummaryOption:
    """Test cases for --summary option"""

    def test_summary_option_default(self, monkeypatch, sample_java_file):
        """Test --summary option with default types"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--summary"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_summary_option_specific_types(self, monkeypatch, sample_java_file):
        """Test --summary option with specific types"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--summary=classes,methods,fields"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_summary_option_json(self, monkeypatch, sample_java_file):
        """Test --summary option with JSON output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--summary", "--output-format", "json"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_summary_option_analysis_failure(self, monkeypatch, sample_java_file):
        """Test --summary option when analysis fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--summary"])
        
        # Mock the UnifiedAnalysisEngine.analyze method to return failed result
        with patch('tree_sitter_analyzer.core.analysis_engine.UnifiedAnalysisEngine.analyze') as mock_analyze:
            from tree_sitter_analyzer.models import AnalysisResult
            
            # Create a failed analysis result
            failed_result = AnalysisResult(
                file_path=sample_java_file,
                line_count=0,
                elements=[],
                node_count=0,
                query_results={},
                source_code="",
                language="java",
                success=False,
                error_message="Mocked analysis failure"
            )
            mock_analyze.return_value = failed_result
            
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "解析に失敗しました" in error_output


class TestCLIStructureOption:
    """Test cases for --structure option"""

    def test_structure_option_json(self, monkeypatch, sample_java_file):
        """Test --structure option with JSON output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--structure", "--output-format", "json"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_structure_option_text(self, monkeypatch, sample_java_file):
        """Test --structure option with text output"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--structure", "--output-format", "text"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_structure_option_analysis_failure(self, monkeypatch, sample_java_file):
        """Test --structure option when analysis fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--structure"])
        
        # Mock the UnifiedAnalysisEngine.analyze method to return failed result
        with patch('tree_sitter_analyzer.core.analysis_engine.UnifiedAnalysisEngine.analyze') as mock_analyze:
            from tree_sitter_analyzer.models import AnalysisResult
            
            # Create a failed analysis result
            failed_result = AnalysisResult(
                file_path=sample_java_file,
                line_count=0,
                elements=[],
                node_count=0,
                query_results={},
                source_code="",
                language="java",
                success=False,
                error_message="Mocked analysis failure"
            )
            mock_analyze.return_value = failed_result
            
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "解析に失敗しました" in error_output


class TestCLITableOption:
    """Test cases for --table option"""

    def test_table_option_full(self, monkeypatch, sample_java_file):
        """Test --table option with full format"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--table", "full"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_table_option_compact(self, monkeypatch, sample_java_file):
        """Test --table option with compact format"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--table", "compact"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_table_option_csv(self, monkeypatch, sample_java_file):
        """Test --table option with CSV format"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--table", "csv"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_table_option_analysis_failure(self, monkeypatch, sample_java_file):
        """Test --table option when analysis fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--table", "full"])
        
        # Mock the UnifiedAnalysisEngine.analyze method to return failed result
        with patch('tree_sitter_analyzer.core.analysis_engine.UnifiedAnalysisEngine.analyze') as mock_analyze:
            from tree_sitter_analyzer.models import AnalysisResult
            
            # Create a failed analysis result
            failed_result = AnalysisResult(
                file_path=sample_java_file,
                line_count=0,
                elements=[],
                node_count=0,
                query_results={},
                source_code="",
                language="java",
                success=False,
                error_message="Mocked analysis failure"
            )
            mock_analyze.return_value = failed_result
            
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "解析に失敗しました" in error_output


class TestCLIPartialReadOption:
    """Test cases for --partial-read option"""

    def test_partial_read_basic(self, monkeypatch, sample_java_file):
        """Test --partial-read option with basic parameters"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "1", "--end-line", "5"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_partial_read_missing_start_line(self, monkeypatch, sample_java_file):
        """Test --partial-read option without required --start-line"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--start-lineが必須です" in error_output

    def test_partial_read_invalid_start_line(self, monkeypatch, sample_java_file):
        """Test --partial-read option with invalid start line"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "0"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--start-lineは1以上である必要があります" in error_output

    def test_partial_read_invalid_end_line(self, monkeypatch, sample_java_file):
        """Test --partial-read option with invalid end line"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "5", "--end-line", "3"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--end-lineは--start-line以上である必要があります" in error_output

    def test_partial_read_invalid_start_column(self, monkeypatch, sample_java_file):
        """Test --partial-read option with invalid start column"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "1", "--start-column", "-1"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--start-columnは0以上である必要があります" in error_output

    def test_partial_read_invalid_end_column(self, monkeypatch, sample_java_file):
        """Test --partial-read option with invalid end column"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "1", "--end-column", "-1"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--end-columnは0以上である必要があります" in error_output

    def test_partial_read_failure(self, monkeypatch, sample_java_file):
        """Test --partial-read option when reading fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--partial-read", "--start-line", "1"])
        
        with patch('tree_sitter_analyzer.cli.commands.partial_read_command.read_file_partial', return_value=None):
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "ファイルの部分読み込みに失敗しました" in error_output


class TestCLIQueryHandling:
    """Test cases for query handling"""

    def test_describe_query_not_found(self, monkeypatch, sample_java_file):
        """Test --describe-query with non-existent query"""
        monkeypatch.setattr(sys, "argv", ["cli", "--describe-query", "nonexistent_query", "--language", "java"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "見つかりません" in error_output

    def test_describe_query_exception(self, monkeypatch, sample_java_file):
        """Test --describe-query with exception"""
        monkeypatch.setattr(sys, "argv", ["cli", "--describe-query", "class", "--language", "java"])
        
        with patch('tree_sitter_analyzer.cli.info_commands.query_loader.get_query_description', side_effect=ValueError("Test error")):
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "Test error" in error_output


class TestCLILanguageHandling:
    """Test cases for language handling"""

    def test_unsupported_language_fallback(self, monkeypatch, sample_java_file):
        """Test unsupported language with Java fallback"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--language", "unsupported_lang"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "Java解析エンジンで試行します" in output


class TestCLIQueryExecution:
    """Test cases for query execution"""

    def test_query_execution_no_results(self, monkeypatch, sample_java_file):
        """Test query execution with no results"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--query-key", "class"])
        
        with patch('tree_sitter_analyzer.cli.commands.base_command.get_analysis_engine') as mock_engine_factory:
            mock_engine = Mock()
            from tree_sitter_analyzer.models import AnalysisResult
            import asyncio

            async def mock_analyze(*args, **kwargs):
                return AnalysisResult(
                    file_path=sample_java_file,
                    language="java",
                    success=True,
                    elements=[],
                    line_count=0,
                    node_count=0,
                    query_results={},
                )

            mock_engine.analyze = mock_analyze
            mock_engine_factory.return_value = mock_engine
            
            mock_stdout = StringIO()
            monkeypatch.setattr("sys.stdout", mock_stdout)
            
            try:
                main()
            except SystemExit:
                pass
            
            output = mock_stdout.getvalue()
            assert "マッチする結果は見つかりませんでした" in output

    def test_query_execution_parse_failure(self, monkeypatch, sample_java_file):
        """Test query execution when parsing fails"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--query-key", "class"])
        
        with patch('tree_sitter_analyzer.cli.commands.base_command.get_analysis_engine') as mock_engine_factory:
            mock_engine = Mock()
            from tree_sitter_analyzer.models import AnalysisResult
            import asyncio

            async def mock_analyze(*args, **kwargs):
                return AnalysisResult(
                    file_path=sample_java_file,
                    language="java",
                    success=False,
                    elements=[],
                    line_count=0,
                    node_count=0,
                    query_results={},
                    error_message="Parse failure"
                )

            mock_engine.analyze = mock_analyze
            mock_engine_factory.return_value = mock_engine
            
            try:
                main()
            except SystemExit as e:
                assert e.code == 1

    def test_no_query_or_advanced_error(self, monkeypatch, sample_java_file):
        """Test error when neither query nor --advanced is specified"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "クエリまたは--advancedオプションを指定してください" in error_output

    def test_query_not_found_error(self, monkeypatch, sample_java_file):
        """Test error when query is not found"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--query-key", "nonexistent"])
        
        with patch('tree_sitter_analyzer.query_loader.get_query', return_value=None):
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "見つかりません" in error_output

    def test_query_exception_error(self, monkeypatch, sample_java_file):
        """Test error when query loading raises exception"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--query-key", "class"])
        
        with patch('tree_sitter_analyzer.cli.commands.query_command.query_loader.get_query', side_effect=ValueError("Query error")):
            mock_stderr = StringIO()
            monkeypatch.setattr("sys.stderr", mock_stderr)
            
            try:
                main()
            except SystemExit:
                pass
            
            error_output = mock_stderr.getvalue()
            assert "Query error" in error_output


class TestCLILoggingConfiguration:
    """Test cases for logging configuration"""

    def test_table_option_logging_suppression(self, monkeypatch, sample_java_file):
        """Test that --table option suppresses logging"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--table", "full"])
        
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            try:
                main()
            except SystemExit:
                pass
            
            # Should have set logging level to ERROR
            mock_logger.setLevel.assert_called_with(logging.ERROR)


# Additional test markers for categorization
pytestmark = [
    pytest.mark.unit
]


class TestCLIAdditionalCoverage:
    """Additional test cases to improve CLI coverage"""

    def test_show_supported_languages(self, monkeypatch):
        """Test --show-supported-languages option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--show-supported-languages"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "サポートされている言語:" in output

    def test_show_supported_extensions(self, monkeypatch):
        """Test --show-supported-extensions option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--show-supported-extensions"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "サポートされている拡張子:" in output

    def test_show_common_queries(self, monkeypatch):
        """Test --show-common-queries option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--show-common-queries"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0

    def test_show_query_languages(self, monkeypatch):
        """Test --show-query-languages option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--show-query-languages"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "クエリサポートされている言語:" in output

    def test_list_queries_with_language(self, monkeypatch):
        """Test --list-queries with --language option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--list-queries", "--language", "java"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "利用可能なクエリキー (java):" in output

    def test_list_queries_with_file(self, monkeypatch, sample_java_file):
        """Test --list-queries with file path"""
        monkeypatch.setattr(sys, "argv", ["cli", "--list-queries", sample_java_file])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "利用可能なクエリキー" in output

    def test_list_queries_all_languages(self, monkeypatch):
        """Test --list-queries without language specification"""
        monkeypatch.setattr(sys, "argv", ["cli", "--list-queries"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "サポートされている言語:" in output

    def test_describe_query_with_language(self, monkeypatch):
        """Test --describe-query with --language option"""
        monkeypatch.setattr(sys, "argv", ["cli", "--describe-query", "class", "--language", "java"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "クエリキー 'class'" in output

    def test_describe_query_with_file(self, monkeypatch, sample_java_file):
        """Test --describe-query with file path"""
        monkeypatch.setattr(sys, "argv", ["cli", "--describe-query", "class", sample_java_file])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "クエリキー 'class'" in output

    def test_describe_query_missing_language_and_file(self, monkeypatch):
        """Test --describe-query without language or file"""
        monkeypatch.setattr(sys, "argv", ["cli", "--describe-query", "class"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "--languageまたは対象ファイルの指定が必要です" in error_output

    def test_missing_file_path_error(self, monkeypatch):
        """Test error when file path is missing"""
        monkeypatch.setattr(sys, "argv", ["cli"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "ファイルパスが指定されていません" in error_output

    def test_nonexistent_file_error(self, monkeypatch):
        """Test error when file does not exist"""
        monkeypatch.setattr(sys, "argv", ["cli", "/nonexistent/file.java", "--query-key", "class"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "ファイルが見つかりません" in error_output

    def test_unknown_language_detection(self, monkeypatch):
        """Test unknown language detection"""
        # Create a file with unknown extension
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unknown', delete=False) as f:
            f.write("some content")
            unknown_file = f.name
        
        monkeypatch.setattr(sys, "argv", ["cli", unknown_file, "--query-key", "class"])
        mock_stderr = StringIO()
        monkeypatch.setattr("sys.stderr", mock_stderr)
        
        try:
            main()
        except SystemExit:
            pass
        
        error_output = mock_stderr.getvalue()
        assert "言語を判定できませんでした" in error_output
        
        # Cleanup
        import os
        if os.path.exists(unknown_file):
            os.unlink(unknown_file)

    def test_unsupported_language_fallback(self, monkeypatch, sample_java_file):
        """Test unsupported language with fallback to Java"""
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--language", "unsupported", "--query-key", "class"])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert "Java解析エンジンで試行します" in output

    def test_query_string_option(self, monkeypatch, sample_java_file):
        """Test --query-string option"""
        query_string = "(class_declaration) @class"
        monkeypatch.setattr(sys, "argv", ["cli", sample_java_file, "--query-string", query_string])
        mock_stdout = StringIO()
        monkeypatch.setattr("sys.stdout", mock_stdout)
        
        try:
            main()
        except SystemExit:
            pass
        
        output = mock_stdout.getvalue()
        assert len(output) > 0