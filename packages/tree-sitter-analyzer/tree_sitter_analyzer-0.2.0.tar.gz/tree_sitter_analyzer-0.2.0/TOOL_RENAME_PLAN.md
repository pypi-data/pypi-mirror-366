# MCP Tool Rename Plan

## Current Issues with Tool Names

### 1. `format_table` - MISLEADING NAME
**Current:** `format_table`
**Problem:** Sounds like a table formatting utility
**Actual Function:** Analyzes code structure and generates detailed analysis tables
**Proposed:** `analyze_code_structure`

### 2. Other Tool Names Review

**Current Tools (from codebase analysis):**
- `analyze_code_scale` ✅ **GOOD** - Clear purpose
- `format_table` ❌ **BAD** - Misleading
- `read_code_partial` ✅ **GOOD** - Clear purpose  
- `analyze_code_universal` ✅ **GOOD** - Clear purpose

## Rename Implementation Plan

### Phase 1: Add New Tool Names (Backward Compatible)
```python
# In table_format_tool.py
def get_tool_definition(self) -> Any:
    return Tool(
        name="analyze_code_structure",  # NEW NAME
        description="Analyze code structure and generate detailed tables (classes, methods, fields)",
        inputSchema=self.get_tool_schema(),
    )
```

### Phase 2: Update Documentation
- Update all documentation to use new names
- Add migration notes for existing users

### Phase 3: Deprecation (Future Release)
- Keep old names working but add deprecation warnings
- Update examples and guides

## Rationale for New Names

### `analyze_code_structure`
- **Clear Purpose:** Immediately tells users it analyzes code structure
- **LLM Friendly:** AI assistants will understand this is for code analysis
- **Consistent:** Matches the pattern of other `analyze_*` tools
- **Descriptive:** Explains what kind of analysis (structure)

## Files to Update

1. `tree_sitter_analyzer/mcp/tools/table_format_tool.py`
2. `tree_sitter_analyzer/mcp/server.py`
3. `README.md`
4. `MCP_USAGE_GUIDE.md`
5. `MCP_SETUP_USERS.md`
6. `MCP_SETUP_DEVELOPERS.md`
7. All example documentation

## Testing Plan

1. Update tool definition
2. Test MCP server registration
3. Test Claude Desktop integration
4. Verify backward compatibility (if maintained)
5. Update all documentation examples