#pragma once
#include <iostream>
#include <string>
#include <vector>
#include <functional>

// Test framework utilities for YAAL parser

class TestFramework {
public:
    struct TestCase {
        std::string name;
        std::string category;
        std::function<bool()> test_func;
        bool passed = false;
    };
    
    void register_test(const std::string& category, const std::string& name, std::function<bool()> test_func);
    void run_all();
    int get_exit_code() const { return failed_tests > 0 ? 1 : 0; }
    
private:
    std::vector<TestCase> tests;
    int passed_tests = 0;
    int failed_tests = 0;
};

extern TestFramework g_test_framework;

#define TEST(category, name) \
    bool test_##category##_##name(); \
    struct TestRegistrar_##category##_##name { \
        TestRegistrar_##category##_##name() { \
            g_test_framework.register_test(#category, #name, test_##category##_##name); \
        } \
    }; \
    static TestRegistrar_##category##_##name registrar_##category##_##name; \
    bool test_##category##_##name()

#define ASSERT_TRUE(condition) \
    if (!(condition)) { \
        std::cout << "    ASSERTION FAILED: " << #condition << std::endl; \
        return false; \
    }

#define ASSERT_FALSE(condition) ASSERT_TRUE(!(condition))
#define ASSERT_EQ(a, b) ASSERT_TRUE((a) == (b))
