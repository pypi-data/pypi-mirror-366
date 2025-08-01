#!/bin/bash
# YAAL Examples Validation Script
# Tests all example files against both C++ and Python parsers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_FILES=0
CPP_PASS=0
CPP_FAIL=0
PYTHON_PASS=0
PYTHON_FAIL=0

echo -e "${BLUE}YAAL Examples Validation${NC}"
echo -e "${BLUE}========================${NC}"
echo

# Check if C++ parser exists
if [ ! -f "./build/yaal" ]; then
    echo -e "${YELLOW}Warning: C++ parser not found at ./build/yaal${NC}"
    echo -e "${YELLOW}Run 'cmake -B build -S . -DYAAL_BUILD_EXAMPLES=OFF && cmake --build build' to build the C++ parser${NC}"
    CPP_AVAILABLE=false
else
    CPP_AVAILABLE=true
fi

# Check if Python parser is available
if ! uv run --project tests/python python -c "from yaal_parser import YaalParser" > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Python parser not available${NC}"
    echo -e "${YELLOW}Run 'make python-test' to set up the Python environment${NC}"
    PYTHON_AVAILABLE=false
else
    PYTHON_AVAILABLE=true
fi

echo

# Test each example file
for file in examples/*.yaal; do
    if [ ! -f "$file" ]; then
        continue
    fi
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    filename=$(basename "$file")
    
    echo -e "${BLUE}Testing: $filename${NC}"
    echo "----------------------------------------"
    
    # Test C++ parser
    if [ "$CPP_AVAILABLE" = true ]; then
        if timeout 30 ./build/yaal "$file" > /dev/null 2>&1; then
            echo -e "✅ C++ parser: ${GREEN}PASS${NC}"
            CPP_PASS=$((CPP_PASS + 1))
        else
            echo -e "❌ C++ parser: ${RED}FAIL${NC}"
            CPP_FAIL=$((CPP_FAIL + 1))
            # Show error for debugging
            echo -e "${RED}Error output:${NC}"
            timeout 30 ./build/yaal "$file" 2>&1 | head -3
        fi
    else
        echo -e "⏭️  C++ parser: ${YELLOW}SKIPPED${NC}"
    fi
    
    # Test Python parser
    if [ "$PYTHON_AVAILABLE" = true ]; then
        if timeout 30 uv run --project tests/python python -c "
from yaal_parser import YaalParser, YaalExtractor
parser = YaalParser()
extractor = YaalExtractor()
tree = parser.parse_file('$file')
data = extractor.extract(tree)
" > /dev/null 2>&1; then
            echo -e "✅ Python parser: ${GREEN}PASS${NC}"
            PYTHON_PASS=$((PYTHON_PASS + 1))
        else
            echo -e "❌ Python parser: ${RED}FAIL${NC}"
            PYTHON_FAIL=$((PYTHON_FAIL + 1))
            # Show error for debugging
            echo -e "${RED}Error output:${NC}"
            timeout 30 uv run --project tests/python python -c "
from yaal_parser import YaalParser
parser = YaalParser()
parser.parse_file('$file')
" 2>&1 | head -3
        fi
    else
        echo -e "⏭️  Python parser: ${YELLOW}SKIPPED${NC}"
    fi
    
    echo
done

# Summary
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}=================${NC}"
echo -e "Total files tested: ${TOTAL_FILES}"
echo

if [ "$CPP_AVAILABLE" = true ]; then
    echo -e "${BLUE}C++ Parser Results:${NC}"
    echo -e "  ✅ Passed: ${GREEN}${CPP_PASS}${NC}"
    echo -e "  ❌ Failed: ${RED}${CPP_FAIL}${NC}"
    if [ $CPP_FAIL -eq 0 ]; then
        echo -e "  🎉 ${GREEN}All C++ tests passed!${NC}"
    fi
    echo
fi

if [ "$PYTHON_AVAILABLE" = true ]; then
    echo -e "${BLUE}Python Parser Results:${NC}"
    echo -e "  ✅ Passed: ${GREEN}${PYTHON_PASS}${NC}"
    echo -e "  ❌ Failed: ${RED}${PYTHON_FAIL}${NC}"
    if [ $PYTHON_FAIL -eq 0 ]; then
        echo -e "  🎉 ${GREEN}All Python tests passed!${NC}"
    fi
    echo
fi

# Overall result
if [ "$CPP_AVAILABLE" = true ] && [ "$PYTHON_AVAILABLE" = true ]; then
    if [ $CPP_FAIL -eq 0 ] && [ $PYTHON_FAIL -eq 0 ]; then
        echo -e "🎉 ${GREEN}All parsers passed all tests!${NC}"
        exit 0
    else
        echo -e "⚠️  ${YELLOW}Some tests failed. Check the output above for details.${NC}"
        exit 1
    fi
elif [ "$CPP_AVAILABLE" = true ]; then
    if [ $CPP_FAIL -eq 0 ]; then
        echo -e "🎉 ${GREEN}C++ parser passed all tests!${NC}"
        exit 0
    else
        echo -e "⚠️  ${YELLOW}C++ parser tests failed.${NC}"
        exit 1
    fi
elif [ "$PYTHON_AVAILABLE" = true ]; then
    if [ $PYTHON_FAIL -eq 0 ]; then
        echo -e "🎉 ${GREEN}Python parser passed all tests!${NC}"
        exit 0
    else
        echo -e "⚠️  ${YELLOW}Python parser tests failed.${NC}"
        exit 1
    fi
else
    echo -e "⚠️  ${YELLOW}No parsers available for testing.${NC}"
    exit 1
fi