#include <boost/ut.hpp>
#include "test_helpers.hpp"

namespace ut = boost::ut;
using namespace ut;

namespace ast_output_tests {

suite ast_output = [] {
    "shebang_detection"_test = [] {
        std::string text = "#!pipeline\nname: value\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Shebang: #!pipeline"));
    };

    "simple_statement_detection"_test = [] {
        std::string text = "production\ndebug mode\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Simple statement: production"));
        expect(test_helpers::output_contains(output, "Simple statement: debug mode"));
    };

    "key_value_detection"_test = [] {
        std::string text = "name: John\nage: 25\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Key: name"));
        expect(test_helpers::output_contains(output, "Value: John"));
        expect(test_helpers::output_contains(output, "Key: age"));
        expect(test_helpers::output_contains(output, "Value: 25"));
    };

    "brace_block_detection"_test = [] {
        std::string text = "script: { echo hello }\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Key: script"));
        expect(test_helpers::output_contains(output, "Brace block: { echo hello }"));
    };

    "compound_statement_structure"_test = [] {
        std::string text = "config:\n  debug: false\n  timeout: 30\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Key: config"));
        expect(test_helpers::output_contains(output, "Entering compound statement"));
        expect(test_helpers::output_contains(output, "Leaving compound statement"));
    };

    "nested_structure_depth"_test = [] {
        std::string text = "level1:\n  level2:\n    level3: value\n";
        std::string output = test_helpers::parse_with_output(text);
        
        // Count the number of compound statement entries and exits
        int enter_count = test_helpers::count_occurrences(output, "Entering compound statement");
        int leave_count = test_helpers::count_occurrences(output, "Leaving compound statement");
        
        expect(enter_count >= 3_i);  // At least 3 levels
        expect(enter_count == leave_count);  // Balanced entries and exits
    };

    "first_colon_rule_parsing"_test = [] {
        std::string text = "time stamp: 12:30:45\nurl: https://api.example.com:8080/v1\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Key: time stamp"));
        expect(test_helpers::output_contains(output, "Value: 12:30:45"));
        expect(test_helpers::output_contains(output, "Key: url"));
        expect(test_helpers::output_contains(output, "Value: https://api.example.com:8080/v1"));
    };

    "mixed_content_parsing"_test = [] {
        std::string text = "production\nname: John\ndebug mode\nage: 25\n";
        std::string output = test_helpers::parse_with_output(text);
        
        // Should have both simple statements and key-value pairs
        expect(test_helpers::output_contains(output, "Simple statement: production"));
        expect(test_helpers::output_contains(output, "Simple statement: debug mode"));
        expect(test_helpers::output_contains(output, "Key: name"));
        expect(test_helpers::output_contains(output, "Key: age"));
    };

    "complex_brace_blocks"_test = [] {
        std::string text = "script: {\n  echo \"Starting\"\n  for i in {1..5}; do\n    echo \"Step $i\"\n  done\n  echo \"Complete\"\n}\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Key: script"));
        expect(test_helpers::output_contains(output, "Brace block:"));
        expect(test_helpers::output_contains(output, "echo \"Starting\""));
    };

    "whitespace_handling"_test = [] {
        std::string text = "   name   :   John   \n   age   :   25   \n";
        std::string output = test_helpers::parse_with_output(text);
        
        // Keys and values should be parsed correctly despite extra whitespace
        expect(test_helpers::output_contains(output, "Key:"));
        expect(test_helpers::output_contains(output, "Value:"));
    };

    "parsing_success_message"_test = [] {
        std::string text = "name: John\n";
        std::string output = test_helpers::parse_with_output(text);
        
        expect(test_helpers::output_contains(output, "Parsing succeeded"));
    };
};

} // namespace ast_output_tests