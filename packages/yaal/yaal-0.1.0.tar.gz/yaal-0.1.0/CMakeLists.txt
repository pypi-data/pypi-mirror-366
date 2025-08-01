# YAAL Parser Project
# CMakeLists.txt for the root directory using CPM.cmake for dependency management

cmake_minimum_required(VERSION 3.14 FATAL_ERROR)

# Project definition
project(yaal-parser
    VERSION 1.0.0
    DESCRIPTION "YAAL (Yet Another Abstract Language) Parser - C++ and Python implementations"
    LANGUAGES CXX
)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Include CPM.cmake for dependency management
include(src/cpp/CPM.cmake)

# Project options
option(YAAL_BUILD_TESTS "Build YAAL tests" ON)
option(YAAL_BUILD_EXAMPLES "Build YAAL examples" ON)
option(YAAL_BUILD_BENCHMARKS "Build YAAL benchmarks" OFF)
option(YAAL_ENABLE_COVERAGE "Enable code coverage" OFF)

# Set default build type to Release if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Compiler-specific options
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
    if(YAAL_ENABLE_COVERAGE)
        add_compile_options(--coverage)
        add_link_options(--coverage)
    endif()
elseif(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    add_compile_options(/W4)
endif()

# Dependencies using CPM.cmake
message(STATUS "Adding dependencies with CPM.cmake...")

# PEGTL - Parsing Expression Grammar Template Library
CPMAddPackage(
    NAME PEGTL
    GITHUB_REPOSITORY taocpp/PEGTL
    GIT_TAG 3.2.8
    OPTIONS
        "PEGTL_BUILD_TESTS OFF"
        "PEGTL_BUILD_EXAMPLES OFF"
)

# Optional: fmt library for better string formatting
if(YAAL_BUILD_EXAMPLES OR YAAL_BUILD_TESTS)
    CPMAddPackage(
        NAME fmt
        GITHUB_REPOSITORY fmtlib/fmt
        GIT_TAG 9.1.0
        OPTIONS
            "FMT_INSTALL ON"
    )
endif()

# Optional: Boost.UT for testing
if(YAAL_BUILD_TESTS)
    CPMAddPackage(
        NAME ut
        GITHUB_REPOSITORY boost-ext/ut
        GIT_TAG v1.1.9
        OPTIONS
            "BUILD_BENCHMARKS OFF"
            "BUILD_EXAMPLES OFF"
            "BUILD_TESTS OFF"
    )
    
    # Create alias for easier usage
    if(TARGET ut)
        add_library(Boost::ut ALIAS ut)
    endif()
endif()

# Optional: Google Benchmark for performance testing
if(YAAL_BUILD_BENCHMARKS)
    CPMAddPackage(
        NAME benchmark
        GITHUB_REPOSITORY google/benchmark
        GIT_TAG v1.8.3
        OPTIONS
            "BENCHMARK_ENABLE_TESTING OFF"
            "BENCHMARK_ENABLE_INSTALL OFF"
    )
endif()

# Create YAAL parser library
add_library(yaal_parser STATIC)

# Add source files to the library
target_sources(yaal_parser
    PRIVATE
        src/cpp/yaal.cpp
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS src/cpp
        FILES
            # Add header files here when they exist
)

# Include directories
target_include_directories(yaal_parser
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/cpp>
        $<INSTALL_INTERFACE:include>
)

# Link dependencies
target_link_libraries(yaal_parser
    PUBLIC
        taocpp::pegtl
)

if(TARGET fmt::fmt)
    target_link_libraries(yaal_parser PUBLIC fmt::fmt)
endif()

# Set target properties
set_target_properties(yaal_parser PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
    POSITION_INDEPENDENT_CODE ON
)

# Create main executable
add_executable(yaal_main src/cpp/yaal.cpp)
target_link_libraries(yaal_main PRIVATE yaal_parser)
set_target_properties(yaal_main PROPERTIES OUTPUT_NAME yaal)

# Enable testing
if(YAAL_BUILD_TESTS)
    enable_testing()
endif()

# Add subdirectories
if(YAAL_BUILD_TESTS)
    add_subdirectory(tests/cpp)
    add_subdirectory(tests/cpp/boost-ut)
endif()

# Examples (if any exist)
if(YAAL_BUILD_EXAMPLES AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/examples")
    add_subdirectory(examples)
endif()

# Installation configuration
include(GNUInstallDirs)

# Install the library
install(TARGETS yaal_parser yaal_main
    EXPORT yaal-parser-targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Install the export set
install(EXPORT yaal-parser-targets
    FILE yaal-parser-targets.cmake
    NAMESPACE yaal::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/yaal-parser
)

# Create and install config files
include(CMakePackageConfigHelpers)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/yaal-parser-config.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/yaal-parser-config.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/yaal-parser
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/yaal-parser-config-version.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/yaal-parser-config.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/yaal-parser-config-version.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/yaal-parser
)

# Custom targets for convenience
add_custom_target(format
    COMMAND find src tests -name "*.cpp" -o -name "*.hpp" | xargs clang-format -i
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Formatting source code with clang-format"
)

add_custom_target(run-tests
    COMMAND ctest --output-on-failure
    DEPENDS yaal_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running all tests"
)

# Print configuration summary
message(STATUS "")
message(STATUS "YAAL Parser Configuration Summary:")
message(STATUS "==================================")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build tests: ${YAAL_BUILD_TESTS}")
message(STATUS "Build examples: ${YAAL_BUILD_EXAMPLES}")
message(STATUS "Build benchmarks: ${YAAL_BUILD_BENCHMARKS}")
message(STATUS "Enable coverage: ${YAAL_ENABLE_COVERAGE}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")

message(STATUS "Dependencies managed by CPM:")
message(STATUS "  PEGTL: 3.2.8")
message(STATUS "  fmt: 9.1.0")
if(YAAL_BUILD_TESTS)
    message(STATUS "  Boost.UT: 1.1.9")
endif()
if(YAAL_BUILD_BENCHMARKS)
    message(STATUS "  Google Benchmark: 1.8.3")
endif()
message(STATUS "")

# CPM.cmake configuration summary
if(CPM_SOURCE_CACHE)
    message(STATUS "CPM source cache: ${CPM_SOURCE_CACHE}")
else()
    message(STATUS "CPM source cache: Not set (consider setting CPM_SOURCE_CACHE environment variable)")
endif()
message(STATUS "")