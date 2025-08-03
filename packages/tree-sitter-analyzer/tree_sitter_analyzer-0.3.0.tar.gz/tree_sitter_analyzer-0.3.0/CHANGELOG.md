# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-08-02

### 🎉 Major Quality & AI Collaboration Release

This release represents a complete transformation of the project's code quality standards and introduces comprehensive AI collaboration capabilities.

### ✨ Added

#### 🤖 AI/LLM Collaboration Framework
- **NEW**: [LLM_CODING_GUIDELINES.md](LLM_CODING_GUIDELINES.md) - Comprehensive coding standards for AI systems
- **NEW**: [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md) - Best practices for human-AI collaboration
- **NEW**: `llm_code_checker.py` - Specialized quality checker for AI-generated code
- **NEW**: AI-specific code generation templates and patterns
- **NEW**: Quality gates and success metrics for AI-generated code

#### 🔧 Development Infrastructure
- **NEW**: Pre-commit hooks with comprehensive quality checks (Black, Ruff, Bandit, isort)
- **NEW**: GitHub Actions CI/CD pipeline with multi-platform testing
- **NEW**: [CODE_STYLE_GUIDE.md](CODE_STYLE_GUIDE.md) - Detailed coding standards and best practices
- **NEW**: GitHub Issue and Pull Request templates
- **NEW**: Automated security scanning with Bandit
- **NEW**: Multi-Python version testing (3.10, 3.11, 3.12, 3.13)

#### 📚 Documentation Enhancements
- **NEW**: Comprehensive code style guide with examples
- **NEW**: AI collaboration section in README.md
- **NEW**: Enhanced CONTRIBUTING.md with pre-commit setup
- **NEW**: Quality check commands and workflows

### 🚀 Enhanced

#### Code Quality Infrastructure
- **ENHANCED**: `check_quality.py` script with comprehensive quality checks
- **ENHANCED**: All documentation commands verified and tested
- **ENHANCED**: Error handling and exception management throughout codebase
- **ENHANCED**: Type hints coverage and documentation completeness

#### Testing & Validation
- **ENHANCED**: All 1203+ tests now pass consistently
- **ENHANCED**: Documentation examples verified to work correctly
- **ENHANCED**: MCP setup commands tested and validated
- **ENHANCED**: CLI functionality thoroughly tested

### 🔧 Fixed

#### Technical Debt Resolution
- **FIXED**: ✅ **Complete technical debt elimination** - All quality checks now pass
- **FIXED**: Code formatting issues across entire codebase
- **FIXED**: Import organization and unused variable cleanup
- **FIXED**: Missing type annotations and docstrings
- **FIXED**: Inconsistent error handling patterns
- **FIXED**: 159 whitespace and formatting issues automatically resolved

#### Code Quality Issues
- **FIXED**: Deprecated function warnings and proper migration paths
- **FIXED**: Exception chaining and error context preservation
- **FIXED**: Mutable default arguments and other anti-patterns
- **FIXED**: String concatenation performance issues
- **FIXED**: Import order and organization issues

### 🎯 Quality Metrics Achieved

- ✅ **100% Black formatting compliance**
- ✅ **Zero Ruff linting errors**
- ✅ **All tests passing (1203+ tests)**
- ✅ **Comprehensive type checking**
- ✅ **Security scan compliance**
- ✅ **Documentation completeness**

### 🛠️ Developer Experience

#### New Tools & Commands
```bash
# Comprehensive quality check
python check_quality.py

# AI-specific code quality check
python llm_code_checker.py [file_or_directory]

# Pre-commit hooks setup
uv run pre-commit install

# Auto-fix common issues
python check_quality.py --fix
```

#### AI Collaboration Support
```bash
# For AI systems - run before generating code
python check_quality.py --new-code-only
python llm_code_checker.py --check-all

# For AI-generated code review
python llm_code_checker.py path/to/new_file.py
```

### 📋 Migration Guide

#### For Contributors
1. **Install pre-commit hooks**: `uv run pre-commit install`
2. **Review new coding standards**: See [CODE_STYLE_GUIDE.md](CODE_STYLE_GUIDE.md)
3. **Use quality check script**: `python check_quality.py` before committing

#### For AI Systems
1. **Read LLM guidelines**: [LLM_CODING_GUIDELINES.md](LLM_CODING_GUIDELINES.md)
2. **Follow collaboration guide**: [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md)
3. **Use specialized checker**: `python llm_code_checker.py` for code validation

### 🎊 Impact

This release establishes Tree-sitter Analyzer as a **premier example of AI-friendly software development**, featuring:

- **Zero technical debt** with enterprise-grade code quality
- **Comprehensive AI collaboration framework** for high-quality AI-assisted development
- **Professional development infrastructure** with automated quality gates
- **Extensive documentation** for both human and AI contributors
- **Proven quality metrics** with 100% compliance across all checks

**This is a foundational release that sets the standard for future development and collaboration.**

## [0.2.1] - 2025-08-02

### Changed
- **Improved documentation**: Updated all UV command examples to use `--output-format=text` for better readability
- **Enhanced user experience**: CLI commands now provide cleaner text output instead of verbose JSON

### Documentation Updates
- Updated README.md with improved command examples
- Updated MCP_SETUP_DEVELOPERS.md with correct CLI test commands
- Updated CONTRIBUTING.md with proper testing commands
- All UV run commands now include `--output-format=text` for consistent user experience

## [0.2.0] - 2025-08-02

### Added
- **New `--quiet` option** for CLI to suppress INFO-level logging
- **Enhanced parameter validation** for partial read commands
- **Improved MCP tool names** for better clarity and AI assistant integration
- **Comprehensive test coverage** with 1283 passing tests
- **UV package manager support** for easier environment management

### Changed
- **BREAKING**: Renamed MCP tool `format_table` to `analyze_code_structure` for better clarity
- **Improved**: All Japanese comments translated to English for international development
- **Enhanced**: Test stability with intelligent fallback mechanisms for complex Java parsing
- **Updated**: Documentation to reflect new tool names and features

### Fixed
- **Resolved**: Previously skipped complex Java structure analysis test now passes
- **Fixed**: Robust error handling for environment-dependent parsing scenarios
- **Improved**: Parameter validation with better error messages

### Technical Improvements
- **Performance**: Optimized analysis engine with better caching
- **Reliability**: Enhanced error handling and logging throughout the codebase
- **Maintainability**: Comprehensive test suite with no skipped tests
- **Documentation**: Complete English localization of codebase

## [0.1.3] - Previous Release

### Added
- Initial MCP server implementation
- Multi-language code analysis support
- Table formatting capabilities
- Partial file reading functionality

### Features
- Java, JavaScript, Python language support
- Tree-sitter based parsing
- CLI and MCP interfaces
- Extensible plugin architecture

---

## Migration Guide

### From 0.1.x to 0.2.0

#### MCP Tool Name Changes
If you're using the MCP server, update your tool calls:

**Before:**
```json
{
  "tool": "format_table",
  "arguments": { ... }
}
```

**After:**
```json
{
  "tool": "analyze_code_structure", 
  "arguments": { ... }
}
```

#### New CLI Options
Take advantage of the new `--quiet` option for cleaner output:

```bash
# New quiet mode
tree-sitter-analyzer file.java --structure --quiet

# Enhanced parameter validation
tree-sitter-analyzer file.java --partial-read --start-line 1 --end-line 10
```

#### UV Support
You can now use UV for package management:

```bash
# Install with UV
uv add tree-sitter-analyzer

# Run with UV
uv run tree-sitter-analyzer file.java --structure
```

---

For more details, see the [README](README.md) and [documentation](docs/).
