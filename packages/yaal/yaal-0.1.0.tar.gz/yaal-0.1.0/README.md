# YAAL Parser Implementation

This project contains both Python (Lark) and C++ (PEGTL) implementations of parsers for the YAAL (Yet Another Abstract Language) specification.

## YAAL Language Features

YAAL is a flexible, statement-based language that supports:

- **Dual nature**: Same syntax for data structures and executable programs
- **Statement model**: Simple statements (no colons) and compound statements (key:value)
- **First colon rule**: Everything before first colon = key, everything after = value
- **Shebang support**: Context switching with `#!pipeline`, `#!hibrid-code`, etc.
- **Brace blocks**: Raw content containers with balanced brace matching
- **Triple-quoted strings**: Multiline string support
- **Flexible keys**: Keys can contain spaces and special characters
- **Indentation-based nesting**: Spaces-only (no tabs)

## Parser Implementations

### C++ Parser (PEGTL)

**Location**: `src/cpp/`

**Features**:
- Complete YAAL specification compliance
- Fast parsing with PEGTL library
- Detailed AST visitor pattern
- Comprehensive error handling

**Building**:
```bash
cmake -B build -S src/cpp
cmake --build build
```

**Usage**:
```bash
./build/yaal <filename.yaal>
```

### Python Parser (Lark)

**Location**: `src/py/yaal/`

**Features**:
- YAAL grammar in Lark format
- Python indentation handling
- Command-line interface
- Graceful dependency handling

**Dependencies**:
```bash
pip install lark
```

**Usage**:
```bash
python3 src/py/yaal/yaal.py <filename.yaal>
```

## Example YAAL Files

### Basic Example (`test_input.yaal`)
```yaal
#!pipeline
name: John
api endpoint: https://api.example.com:8080/v1
production
config:
  debug: false
  timeout: 30
script: { echo hello; exit 0 }
```

### Comprehensive Example (`comprehensive_test.yaal`)
Demonstrates all YAAL features including:
- Shebang lines
- Simple and compound statements
- Keys with spaces
- Triple-quoted strings
- Brace blocks
- Nested structures
- Polymorphic lists

## Grammar Highlights

### Lark Grammar (`src/py/yaal/yaal.lark`)
```lark
start: [shebang_line] file_input

shebang_line: \"#!\" IDENTIFIER _NEWLINE

?stmt: simple_stmt | compound_stmt

simple_stmt: line_content _NEWLINE
compound_stmt: key_part \":\" value_part _NEWLINE?

brace_block: \"{\" brace_content \"}\"
quoted_string: ESCAPED_STRING | TRIPLE_QUOTED_STRING
```

### PEGTL Grammar (`src/cpp/yaal.cpp`)
```cpp
struct shebang_line : pegtl::seq<pegtl::string<'#', '!'>, identifier, pegtl::eol> {};
struct simple_stmt : pegtl::seq<line_content, _NEWLINE> {};
struct compound_stmt : pegtl::seq<key_part, pegtl::one<':'>, /* ... */> {};
struct brace_block : pegtl::seq<pegtl::one<'{'>, brace_content, pegtl::one<'}'>> {};
```

## Testing

Both parsers have been tested with:
- Basic YAAL syntax
- Complex nested structures
- All string types (unquoted, quoted, triple-quoted)
- Brace blocks with nested content
- Real-world examples from the YAAL specification

## Compliance

✅ **Complete YAAL specification compliance**  
✅ **All examples from https://github.com/zokrezyl/yaal-lang parse successfully**  
✅ **Proper error handling and reporting**  
✅ **Extensible architecture for semantic analysis**  

## Next Steps

1. **Semantic Analysis**: Add interpretation and execution capabilities
2. **Context Handlers**: Implement shebang-based context switching
3. **Integration**: Connect to YAAL execution engines
4. **Tooling**: Add syntax highlighting, LSP support, etc.

Both parsers provide a solid foundation for building YAAL-based tools and applications.