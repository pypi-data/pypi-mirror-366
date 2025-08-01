#include <boost/ut.hpp>

// Include all test files
#include "test_basic_parsing.cpp"
#include "test_advanced_features.cpp"
#include "test_string_handling.cpp"
#include "test_edge_cases.cpp"
#include "test_integration.cpp"
#include "test_ast_output.cpp"

int main() {
    // All tests are automatically registered via the suite declarations
    // in each test file, so we just need to return from main
    return 0;
}