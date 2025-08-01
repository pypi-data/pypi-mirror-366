#include "test_helpers.hpp"

TEST(BasicParsing, empty_input) {
    ASSERT_TRUE(TestHelpers::parse_text(""));
}

TEST(BasicParsing, simple_key_value) {
    ASSERT_TRUE(TestHelpers::parse_text("name: John\n"));
}

TEST(BasicParsing, multiple_key_values) {
    std::string text = "name: John\nage: 25\nenabled: true\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, simple_statement) {
    ASSERT_TRUE(TestHelpers::parse_text("production\n"));
}

TEST(BasicParsing, multiple_simple_statements) {
    std::string text = "production\ndebug mode\nhostname localhost\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, mixed_simple_and_compound) {
    std::string text = "production\nname: John\ndebug mode\nage: 25\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, keys_with_spaces) {
    std::string text = "api endpoint: https://example.com\nlog file: /var/log/app.log\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, first_colon_rule) {
    std::string text = "time stamp: 12:30:45\nurl: https://api.example.com:8080/v1\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, comments) {
    std::string text = "# This is a comment\nname: John\n# Another comment\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, inline_comments) {
    std::string text = "name: John  # inline comment\nage: 25  # another inline comment\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, whitespace_handling) {
    std::string text = "   name   :   John   \n   age   :   25   \n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(BasicParsing, file_parsing_basic) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/basic.yaal"));
}

TEST(BasicParsing, file_parsing_simple_statements) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/simple_statements.yaal"));
}

TEST(BasicParsing, file_parsing_keys_with_spaces) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/keys_with_spaces.yaal"));
}

TEST(BasicParsing, file_parsing_first_colon_rule) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/first_colon_rule.yaal"));
}

TEST(BasicParsing, file_parsing_comments) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/comments.yaal"));
}