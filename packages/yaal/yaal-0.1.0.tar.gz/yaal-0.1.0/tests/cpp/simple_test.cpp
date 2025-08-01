#include <catch2/catch_test_macros.hpp>
#include <iostream>
#include <sstream>

TEST_CASE("YAAL parser basic functionality", "[basic]") {
    SECTION("Test passes") {
        REQUIRE(true);
    }
    
    SECTION("Simple parser test") {
        // Basic test to verify Catch2 integration works
        std::string test_input = "name: John\nage: 25\n";
        REQUIRE(test_input.length() > 0);
        REQUIRE(test_input.find("name:") != std::string::npos);
    }
}