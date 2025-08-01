#include <boost/ut.hpp>
#include "test_helpers.hpp"

namespace ut = boost::ut;
using namespace ut;

namespace basic_parsing_tests {

suite basic_parsing = [] {
    "empty_input"_test = [] {
        expect(test_helpers::parse_text(""));
    };

    "simple_key_value"_test = [] {
        expect(test_helpers::parse_text("name: John\n"));
    };

    "multiple_key_values"_test = [] {
        std::string text = "name: John\nage: 25\nenabled: true\n";
        expect(test_helpers::parse_text(text));
    };

    "simple_statement"_test = [] {
        expect(test_helpers::parse_text("production\n"));
    };

    "multiple_simple_statements"_test = [] {
        std::string text = "production\ndebug mode\nhostname localhost\n";
        expect(test_helpers::parse_text(text));
    };

    "mixed_simple_and_compound"_test = [] {
        std::string text = "production\nname: John\ndebug mode\nage: 25\n";
        expect(test_helpers::parse_text(text));
    };

    "keys_with_spaces"_test = [] {
        std::string text = "api endpoint: https://example.com\nlog file: /var/log/app.log\n";
        expect(test_helpers::parse_text(text));
    };

    "first_colon_rule"_test = [] {
        std::string text = "time stamp: 12:30:45\nurl: https://api.example.com:8080/v1\n";
        expect(test_helpers::parse_text(text));
    };

    "comments"_test = [] {
        std::string text = "# This is a comment\nname: John\n# Another comment\n";
        expect(test_helpers::parse_text(text));
    };

    "inline_comments"_test = [] {
        std::string text = "name: John  # inline comment\nage: 25  # another inline comment\n";
        expect(test_helpers::parse_text(text));
    };

    "whitespace_handling"_test = [] {
        std::string text = "   name   :   John   \n   age   :   25   \n";
        expect(test_helpers::parse_text(text));
    };

    "file_parsing_basic"_test = [] {
        expect(test_helpers::parse_file("../fixtures/basic.yaal"));
    };

    "file_parsing_simple_statements"_test = [] {
        expect(test_helpers::parse_file("../fixtures/simple_statements.yaal"));
    };

    "file_parsing_keys_with_spaces"_test = [] {
        expect(test_helpers::parse_file("../fixtures/keys_with_spaces.yaal"));
    };

    "file_parsing_first_colon_rule"_test = [] {
        expect(test_helpers::parse_file("../fixtures/first_colon_rule.yaal"));
    };

    "file_parsing_comments"_test = [] {
        expect(test_helpers::parse_file("../fixtures/comments.yaal"));
    };
};

} // namespace basic_parsing_tests