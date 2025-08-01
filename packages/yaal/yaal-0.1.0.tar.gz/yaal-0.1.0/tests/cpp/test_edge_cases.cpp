#include "test_helpers.hpp"

TEST(EdgeCases, empty_input) {
    ASSERT_TRUE(TestHelpers::parse_text(""));
}

TEST(EdgeCases, whitespace_only) {
    ASSERT_TRUE(TestHelpers::parse_text("   \n  \n   \n"));
}

TEST(EdgeCases, comments_only) {
    std::string text = "# Just a comment\n# Another comment\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, single_character_key) {
    std::string text = "a: value\nb: another\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, single_character_value) {
    std::string text = "key: a\nanother: b\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, very_long_key) {
    std::string long_key(1000, 'a');
    std::string text = long_key + ": value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, very_long_value) {
    std::string long_value(1000, 'a');
    std::string text = "key: " + long_value + "\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, numbers_as_keys) {
    std::string text = "123: numeric key\n456.789: float key\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, special_characters_in_keys) {
    std::string text = "key-with-dashes: value\nkey_with_underscores: value\nkey.with.dots: value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, mixed_indentation_levels) {
    std::string text = "level1:\n  level2a: value\n    level3: deep value\n  level2b: another value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, maximum_nesting_depth) {
    std::string text = "level0:\n";
    std::string indent = "  ";
    for (int i = 1; i < 20; i++) {
        text += std::string(i * 2, ' ') + "level" + std::to_string(i) + ":\n";
    }
    text += std::string(20 * 2, ' ') + "value: deep\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, many_siblings) {
    std::string text = "";
    for (int i = 0; i < 100; i++) {
        text += "key" + std::to_string(i) + ": value" + std::to_string(i) + "\n";
    }
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, large_brace_block) {
    std::string large_content = "echo " + std::string(1000, 'a');
    std::string text = "script: { " + large_content + " }\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, many_colons_in_value) {
    std::string many_colons = "";
    for (int i = 0; i < 50; i++) {
        many_colons += "part" + std::to_string(i) + ":";
    }
    many_colons += "final";
    std::string text = "key: " + many_colons + "\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, unix_line_endings) {
    std::string text = "key1: value1\nkey2: value2\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, windows_line_endings) {
    std::string text = "key1: value1\r\nkey2: value2\r\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, mixed_line_endings) {
    std::string text = "key1: value1\nkey2: value2\r\nkey3: value3\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, no_final_newline) {
    std::string text = "key1: value1\nkey2: value2";  // No final newline
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(EdgeCases, multiple_final_newlines) {
    std::string text = "key1: value1\nkey2: value2\n\n\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}