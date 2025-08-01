#include <boost/ut.hpp>
#include "test_helpers.hpp"

namespace ut = boost::ut;
using namespace ut;

namespace string_handling_tests {

suite string_handling = [] {
    "unquoted_strings"_test = [] {
        std::string text = "name: John Doe\ndescription: This is a description\n";
        expect(test_helpers::parse_text(text));
    };

    "double_quoted_strings"_test = [] {
        std::string text = "description: \"this is quoted\"\ncommand: \"echo hello world\"\n";
        expect(test_helpers::parse_text(text));
    };

    "triple_quoted_strings"_test = [] {
        std::string text = "documentation: \"\"\"This is multiline\nwith colons: 12:30:45\nand URLs: https://example.com\"\"\"\n";
        expect(test_helpers::parse_text(text));
    };

    "strings_with_colons"_test = [] {
        std::string text = "time: 12:30:45\nurl: https://example.com:8080\ndatabase: postgresql://user:pass@host:5432/db\n";
        expect(test_helpers::parse_text(text));
    };

    "escaped_characters"_test = [] {
        std::string text = "message: \"Hello \\\"world\\\" with escaping\"\npath: \"C:\\\\Users\\\\test\"\n";
        expect(test_helpers::parse_text(text));
    };

    "empty_strings"_test = [] {
        std::string text = "empty1: \"\"\nempty2: \"\"\"\"\"\"\n";
        expect(test_helpers::parse_text(text));
    };

    "strings_with_special_chars"_test = [] {
        std::string text = "unicode: café\nemoji: 🚀\naccents: naïve\n";
        expect(test_helpers::parse_text(text));
    };

    "very_long_strings"_test = [] {
        std::string long_value(1000, 'a');
        std::string text = "long_value: " + long_value + "\n";
        expect(test_helpers::parse_text(text));
    };

    "multiline_content"_test = [] {
        std::string text = "script: \"\"\"#!/bin/bash\necho \"Starting application\"\nfor i in {1..5}; do\n  echo \"Step $i\"\ndone\necho \"Complete\"\"\"\"\n";
        expect(test_helpers::parse_text(text));
    };

    "strings_file"_test = [] {
        expect(test_helpers::parse_file("../fixtures/strings.yaal"));
    };
};

} // namespace string_handling_tests