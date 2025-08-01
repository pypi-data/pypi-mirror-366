#include "test_helpers.hpp"

TEST(ASTOutput, shebang_detection) {
    std::string text = "#!pipeline\nname: value\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Shebang: #!pipeline"));
}

TEST(ASTOutput, simple_statement_detection) {
    std::string text = "production\ndebug mode\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Simple statement: production"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Simple statement: debug mode"));
}

TEST(ASTOutput, key_value_detection) {
    std::string text = "name: John\nage: 25\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: name"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Value: John"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: age"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Value: 25"));
}

TEST(ASTOutput, brace_block_detection) {
    std::string text = "script: { echo hello }\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: script"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Brace block: { echo hello }"));
}

TEST(ASTOutput, compound_statement_structure) {
    std::string text = "config:\n  debug: false\n  timeout: 30\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: config"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Entering compound statement"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Leaving compound statement"));
}

TEST(ASTOutput, nested_structure_depth) {
    std::string text = "level1:\n  level2:\n    level3: value\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    // Count the number of compound statement entries and exits
    int enter_count = TestHelpers::count_occurrences(output, "Entering compound statement");
    int leave_count = TestHelpers::count_occurrences(output, "Leaving compound statement");
    
    ASSERT_TRUE(enter_count >= 3);  // At least 3 levels
    ASSERT_EQ(enter_count, leave_count);  // Balanced entries and exits
}

TEST(ASTOutput, first_colon_rule_parsing) {
    std::string text = "time stamp: 12:30:45\nurl: https://api.example.com:8080/v1\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: time stamp"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Value: 12:30:45"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: url"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Value: https://api.example.com:8080/v1"));
}

TEST(ASTOutput, mixed_content_parsing) {
    std::string text = "production\nname: John\ndebug mode\nage: 25\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    // Should have both simple statements and key-value pairs
    ASSERT_TRUE(TestHelpers::output_contains(output, "Simple statement: production"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Simple statement: debug mode"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: name"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: age"));
}

TEST(ASTOutput, complex_brace_blocks) {
    std::string text = "script: {\n  echo \"Starting\"\n  for i in {1..5}; do\n    echo \"Step $i\"\n  done\n  echo \"Complete\"\n}\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: script"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Brace block:"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "echo \"Starting\""));
}

TEST(ASTOutput, whitespace_handling) {
    std::string text = "   name   :   John   \n   age   :   25   \n";
    std::string output = TestHelpers::parse_with_output(text);
    
    // Keys and values should be parsed correctly despite extra whitespace
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key:"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Value:"));
}

TEST(ASTOutput, parsing_success_message) {
    std::string text = "name: John\n";
    std::string output = TestHelpers::parse_with_output(text);
    
    ASSERT_TRUE(TestHelpers::output_contains(output, "Parsing succeeded"));
}