# Boost.UT Tests CMakeLists.txt

# Create Boost.UT test executable
add_executable(yaal_boost_ut_tests
    main.cpp
    # Note: .cpp files are included in main.cpp, not compiled separately
)

# Link libraries - use the main project's dependencies
target_link_libraries(yaal_boost_ut_tests 
    PRIVATE 
        taocpp::pegtl
        yaal_parser
        Boost::ut
)

# Include directories
target_include_directories(yaal_boost_ut_tests 
    PRIVATE 
        .
        ..  # For accessing parent directory headers
)

# Set target properties
set_target_properties(yaal_boost_ut_tests PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Register the test with CTest
add_test(
    NAME yaal_boost_ut_tests
    COMMAND yaal_boost_ut_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

# Set test properties
set_tests_properties(yaal_boost_ut_tests PROPERTIES
    TIMEOUT 60
    LABELS "cpp;parser;unit;boost-ut"
)

# Add custom target to run Boost.UT tests manually
add_custom_target(run_boost_ut_tests
    COMMAND yaal_boost_ut_tests
    DEPENDS yaal_boost_ut_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running YAAL Boost.UT tests"
)