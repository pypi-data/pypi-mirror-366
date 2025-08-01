#include "test_helpers.hpp"

TEST(StringHandling, unquoted_strings) {
    std::string text = "name: John Doe\ndescription: This is a description\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, double_quoted_strings) {
    std::string text = "description: \"this is quoted\"\ncommand: \"echo hello world\"\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, triple_quoted_strings) {
    std::string text = "documentation: \"\"\"This is multiline\nwith colons: 12:30:45\nand URLs: https://example.com\"\"\"\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, strings_with_colons) {
    std::string text = "time: 12:30:45\nurl: https://example.com:8080\ndatabase: postgresql://user:pass@host:5432/db\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, escaped_characters) {
    std::string text = "message: \"Hello \\\"world\\\" with escaping\"\npath: \"C:\\\\Users\\\\test\"\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, empty_strings) {
    std::string text = "empty1: \"\"\nempty2: \"\"\"\"\"\"\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, strings_with_special_chars) {
    std::string text = "unicode: café\nemoji: 🚀\naccents: naïve\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, very_long_strings) {
    std::string long_value(1000, 'a');
    std::string text = "long_value: " + long_value + "\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, multiline_content) {
    std::string text = "script: \"\"\"#!/bin/bash\necho \"Starting application\"\nfor i in {1..5}; do\n  echo \"Step $i\"\ndone\necho \"Complete\"\"\"\"\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(StringHandling, strings_file) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/strings.yaal"));
}