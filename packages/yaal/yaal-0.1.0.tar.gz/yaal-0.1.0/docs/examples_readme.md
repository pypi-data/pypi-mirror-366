# YAAL Parser Examples

This directory contains comprehensive examples demonstrating all features of the YAAL (Yet Another Abstract Language) parser. These examples can be used to test both the C++ and Python implementations of the parser.

**NEW**: Added advanced multiline string examples showcasing complex interactions with brace blocks and deep nesting scenarios.

## Example Files Overview

### 1. `01_basic_features.yaal`
**Purpose**: Demonstrates fundamental YAAL syntax
**Features Covered**:
- Simple key-value pairs
- Keys with spaces and special characters
- Simple statements (items without colons)
- Empty values
- First colon rule (multiple colons in values)
- Comments

### 2. `02_string_types.yaal`
**Purpose**: Shows all supported string types
**Features Covered**:
- Unquoted strings
- Double-quoted strings with escape sequences
- Single-quoted strings (literal)
- Triple-quoted multiline strings
- Special characters in strings

### 3. `03_nested_structures.yaal`
**Purpose**: Demonstrates hierarchical data organization
**Features Covered**:
- Simple nesting with indentation
- Multiple levels of nesting
- Mixed content (values and nested structures)
- Complex nested configurations
- Arrays represented as nested items

### 4. `04_brace_blocks.yaal`
**Purpose**: Shows executable code blocks
**Features Covered**:
- Simple shell commands
- Multi-line scripts
- Complex logic with conditionals
- Database operations
- Nested braces
- Python and other language scripts

### 5. `05_shebang_executable.yaal`
**Purpose**: Demonstrates executable YAAL files
**Features Covered**:
- Shebang line (`#!pipeline`)
- Pipeline configuration
- Environment setup
- Processing steps with executable blocks
- Error handling and monitoring

### 6. `06_mixed_content.yaal`
**Purpose**: Tests complex indentation patterns
**Features Covered**:
- Mixed content types at different levels
- Complex indentation patterns
- Values with nested suites
- Deep nesting with mixed content
- Infrastructure-as-code patterns

### 7. `07_real_world_config.yaal`
**Purpose**: Complete application configuration example
**Features Covered**:
- Production-ready configuration
- Database connections
- Microservices setup
- Security configuration
- Monitoring and observability
- Deployment scripts
- Backup and disaster recovery

### 8. `08_edge_cases.yaal`
**Purpose**: Tests parser robustness
**Features Covered**:
- Unicode and international characters
- Special characters in keys and values
- Empty and whitespace handling
- Very long values and keys
- Numeric-like strings
- URLs and complex formats
- JSON and XML as string values

### 9. `09_documentation.yaal`
**Purpose**: Self-documenting configuration example
**Features Covered**:
- Comprehensive documentation structure
- Syntax guide within YAAL
- Best practices and conventions
- Detailed comments and examples
- Project metadata

### 10. `10_performance_test.yaal`
**Purpose**: Performance and stress testing
**Features Covered**:
- Deep nesting (10+ levels)
- Wide structures (50+ siblings)
- Large multiline strings
- Complex brace blocks
- Mixed complex structures
- Performance monitoring configuration

### 11. `11_multiline_advanced.yaal`
**Purpose**: Advanced multiline string usage in complex scenarios
**Features Covered**:
- Multiline strings at different nesting levels
- Database migration scripts with SQL
- Docker configurations and Dockerfiles
- Kubernetes manifests and YAML content
- Complex monitoring and alerting configurations
- Documentation generation with embedded code
- Mixed content with values and nested structures

### 12. `12_multiline_brace_combinations.yaal`
**Purpose**: Complex interactions between multiline strings and brace blocks
**Features Covered**:
- Multiline strings containing brace-like syntax (treated as literal)
- Brace blocks generating multiline content
- Nested structures with both multiline strings and executable blocks
- CI/CD pipeline configurations
- Infrastructure as code with Terraform
- Database operations with SQL and shell scripts
- Documentation generation with mixed content types
- Deep nesting (3+ levels) with multiline strings and brace blocks

## Running the Examples

### Using the C++ Parser

```bash
# Build the C++ parser first
make cpp-build

# Test individual files
./build/yaal_main examples/01_basic_features.yaal
./build/yaal_main examples/02_string_types.yaal

# Test all examples
for file in examples/*.yaal; do
    echo "Testing $file..."
    ./build/yaal_main "$file"
done
```

### Using the Python Parser

```bash
# Test individual files
uv run --project tests/python python -c "
from yaal_parser import YaalParser, YaalExtractor
parser = YaalParser()
extractor = YaalExtractor()

# Parse and extract data
tree = parser.parse_file('examples/01_basic_features.yaal')
data = extractor.extract(tree)
print('Parsed successfully!')
print('Data structure:', data)
"

# Test all examples
for file in examples/*.yaal; do
    echo "Testing $file with Python parser..."
    uv run --project tests/python python -c "
from yaal_parser import YaalParser
parser = YaalParser()
try:
    tree = parser.parse_file('$file')
    print('✅ Parsed successfully')
except Exception as e:
    print('❌ Parse failed:', e)
"
done
```

### Validation Script

You can create a simple validation script to test both parsers:

```bash
#!/bin/bash
# validate_examples.sh

echo "Validating YAAL examples..."
echo "=========================="

for file in examples/*.yaal; do
    echo
    echo "Testing: $(basename "$file")"
    echo "----------------------------------------"
    
    # Test C++ parser
    if ./build/yaal_main "$file" > /dev/null 2>&1; then
        echo "✅ C++ parser: PASS"
    else
        echo "❌ C++ parser: FAIL"
    fi
    
    # Test Python parser
    if uv run --project tests/python python -c "
from yaal_parser import YaalParser
parser = YaalParser()
parser.parse_file('$file')
" > /dev/null 2>&1; then
        echo "✅ Python parser: PASS"
    else
        echo "❌ Python parser: FAIL"
    fi
done

echo
echo "Validation complete!"
```

## Example Categories

### **Basic Syntax Examples**
- `01_basic_features.yaal`
- `02_string_types.yaal`

### **Structure Examples**
- `03_nested_structures.yaal`
- `06_mixed_content.yaal`

### **Executable Examples**
- `04_brace_blocks.yaal`
- `05_shebang_executable.yaal`

### **Real-World Examples**
- `07_real_world_config.yaal`
- `09_documentation.yaal`
- `11_multiline_advanced.yaal`
- `12_multiline_brace_combinations.yaal`

### **Testing Examples**
- `08_edge_cases.yaal`
- `10_performance_test.yaal`

## Expected Parser Behavior

All examples should:
1. **Parse successfully** without syntax errors
2. **Preserve data structure** when extracted
3. **Handle Unicode** and special characters correctly
4. **Maintain indentation** relationships
5. **Process executable blocks** appropriately

## Common Use Cases Demonstrated

1. **Configuration Management**: Database connections, server settings, environment variables
2. **Infrastructure as Code**: Kubernetes deployments, Docker configurations, cloud resources
3. **CI/CD Pipelines**: Build scripts, deployment procedures, testing workflows
4. **Documentation**: Self-documenting configurations, API specifications
5. **Data Processing**: ETL pipelines, data transformation scripts
6. **Monitoring**: Alerting rules, metrics collection, health checks

## Notes for Parser Developers

- These examples test **all major parser features**
- They include **edge cases** and **stress tests**
- Each file is **self-contained** and can be tested independently
- Comments explain **what each section tests**
- Examples progress from **simple to complex**
- **Real-world scenarios** are included for practical validation

Use these examples to:
- **Validate parser correctness**
- **Test performance characteristics**
- **Verify feature completeness**
- **Debug parsing issues**
- **Demonstrate YAAL capabilities**