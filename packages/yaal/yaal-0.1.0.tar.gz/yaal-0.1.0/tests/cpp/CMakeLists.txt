# YAAL C++ Tests CMakeLists.txt

# Enable testing
enable_testing()

# Create test executable using the existing custom test framework
add_executable(yaal_tests
    main.cpp
    test_framework.cpp
    test_basic_parsing.cpp
    test_advanced_features.cpp
    test_string_handling.cpp
    test_edge_cases.cpp
    test_integration.cpp
    test_ast_output.cpp
)

# Link libraries - use the main project's dependencies
target_link_libraries(yaal_tests 
    PRIVATE 
        taocpp::pegtl
        yaal_parser
)

# Include directories
target_include_directories(yaal_tests PRIVATE .)

# Set target properties
set_target_properties(yaal_tests PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Register the test with CTest
add_test(
    NAME yaal_cpp_tests
    COMMAND yaal_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

# Set test properties
set_tests_properties(yaal_cpp_tests PROPERTIES
    TIMEOUT 30
    LABELS "cpp;parser;unit"
)

# Add custom target to run tests manually
add_custom_target(run_cpp_tests
    COMMAND yaal_tests
    DEPENDS yaal_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running YAAL C++ tests"
)