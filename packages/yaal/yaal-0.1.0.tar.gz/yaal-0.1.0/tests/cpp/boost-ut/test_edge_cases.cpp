#include <boost/ut.hpp>
#include "test_helpers.hpp"

namespace ut = boost::ut;
using namespace ut;

namespace edge_cases_tests {

suite edge_cases = [] {
    "empty_input"_test = [] {
        expect(test_helpers::parse_text(""));
    };

    "whitespace_only"_test = [] {
        expect(test_helpers::parse_text("   \n  \n   \n"));
    };

    "comments_only"_test = [] {
        std::string text = "# Just a comment\n# Another comment\n";
        expect(test_helpers::parse_text(text));
    };

    "single_character_key"_test = [] {
        std::string text = "a: value\nb: another\n";
        expect(test_helpers::parse_text(text));
    };

    "single_character_value"_test = [] {
        std::string text = "key: a\nanother: b\n";
        expect(test_helpers::parse_text(text));
    };

    "very_long_key"_test = [] {
        std::string long_key(1000, 'a');
        std::string text = long_key + ": value\n";
        expect(test_helpers::parse_text(text));
    };

    "very_long_value"_test = [] {
        std::string long_value(1000, 'a');
        std::string text = "key: " + long_value + "\n";
        expect(test_helpers::parse_text(text));
    };

    "numbers_as_keys"_test = [] {
        std::string text = "123: numeric key\n456.789: float key\n";
        expect(test_helpers::parse_text(text));
    };

    "special_characters_in_keys"_test = [] {
        std::string text = "key-with-dashes: value\nkey_with_underscores: value\nkey.with.dots: value\n";
        expect(test_helpers::parse_text(text));
    };

    "mixed_indentation_levels"_test = [] {
        std::string text = "level1:\n  level2a: value\n    level3: deep value\n  level2b: another value\n";
        expect(test_helpers::parse_text(text));
    };

    "maximum_nesting_depth"_test = [] {
        std::string text = "level0:\n";
        for (int i = 1; i < 20; i++) {
            text += std::string(i * 2, ' ') + "level" + std::to_string(i) + ":\n";
        }
        text += std::string(20 * 2, ' ') + "value: deep\n";
        
        expect(test_helpers::parse_text(text));
    };

    "many_siblings"_test = [] {
        std::string text = "";
        for (int i = 0; i < 100; i++) {
            text += "key" + std::to_string(i) + ": value" + std::to_string(i) + "\n";
        }
        expect(test_helpers::parse_text(text));
    };

    "large_brace_block"_test = [] {
        std::string large_content = "echo " + std::string(1000, 'a');
        std::string text = "script: { " + large_content + " }\n";
        expect(test_helpers::parse_text(text));
    };

    "many_colons_in_value"_test = [] {
        std::string many_colons = "";
        for (int i = 0; i < 50; i++) {
            many_colons += "part" + std::to_string(i) + ":";
        }
        many_colons += "final";
        std::string text = "key: " + many_colons + "\n";
        expect(test_helpers::parse_text(text));
    };

    "unix_line_endings"_test = [] {
        std::string text = "key1: value1\nkey2: value2\n";
        expect(test_helpers::parse_text(text));
    };

    "windows_line_endings"_test = [] {
        std::string text = "key1: value1\r\nkey2: value2\r\n";
        expect(test_helpers::parse_text(text));
    };

    "mixed_line_endings"_test = [] {
        std::string text = "key1: value1\nkey2: value2\r\nkey3: value3\n";
        expect(test_helpers::parse_text(text));
    };

    "no_final_newline"_test = [] {
        std::string text = "key1: value1\nkey2: value2";  // No final newline
        expect(test_helpers::parse_text(text));
    };

    "multiple_final_newlines"_test = [] {
        std::string text = "key1: value1\nkey2: value2\n\n\n";
        expect(test_helpers::parse_text(text));
    };
};

} // namespace edge_cases_tests