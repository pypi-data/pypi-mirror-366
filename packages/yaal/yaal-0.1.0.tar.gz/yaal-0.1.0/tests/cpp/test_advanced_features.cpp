#include "test_helpers.hpp"

TEST(AdvancedFeatures, shebang_pipeline) {
    std::string text = "#!pipeline\nname: value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Shebang: #!pipeline"));
}

TEST(AdvancedFeatures, shebang_hibrid_code) {
    std::string text = "#!hibrid-code\nname: value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Shebang: #!hibrid-code"));
}

TEST(AdvancedFeatures, shebang_custom) {
    std::string text = "#!custom-context\nname: value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, no_shebang) {
    std::string text = "name: value\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, shebang_file) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/shebang.yaal"));
}

TEST(AdvancedFeatures, simple_brace_block) {
    std::string text = "script: { echo hello }\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Brace block: { echo hello }"));
}

TEST(AdvancedFeatures, multiline_brace_block) {
    std::string text = "script: {\n  echo hello\n  exit 0\n}\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, nested_brace_blocks) {
    std::string text = "nested: { outer { inner content } more }\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, brace_block_with_special_chars) {
    std::string text = "script: { echo hello:world; test $VAR }\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, empty_brace_block) {
    std::string text = "script: {}\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, brace_blocks_file) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/brace_blocks.yaal"));
}

TEST(AdvancedFeatures, simple_nesting) {
    std::string text = "config:\n  debug: false\n  timeout: 30\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, deep_nesting) {
    std::string text = "config:\n  database:\n    credentials:\n      username: admin\n      password: secret\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, mixed_nesting) {
    std::string text = "config:\n  production\n  debug: false\n  servers:\n    web-01\n    web-02\n    database: db-01\n";
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(AdvancedFeatures, nested_file) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/nested.yaal"));
}

TEST(AdvancedFeatures, polymorphic_lists) {
    ASSERT_TRUE(TestHelpers::parse_file("fixtures/polymorphic_lists.yaal"));
}