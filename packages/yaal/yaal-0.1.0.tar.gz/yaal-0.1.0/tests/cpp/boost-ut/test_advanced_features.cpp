#include <boost/ut.hpp>
#include "test_helpers.hpp"

namespace ut = boost::ut;
using namespace ut;

namespace advanced_features_tests {

suite advanced_features = [] {
    "shebang_pipeline"_test = [] {
        std::string text = "#!pipeline\nname: value\n";
        expect(test_helpers::parse_text(text));
        
        std::string output = test_helpers::parse_with_output(text);
        expect(test_helpers::output_contains(output, "Shebang: #!pipeline"));
    };

    "shebang_hibrid_code"_test = [] {
        std::string text = "#!hibrid-code\nname: value\n";
        expect(test_helpers::parse_text(text));
        
        std::string output = test_helpers::parse_with_output(text);
        expect(test_helpers::output_contains(output, "Shebang: #!hibrid-code"));
    };

    "shebang_custom"_test = [] {
        std::string text = "#!custom-context\nname: value\n";
        expect(test_helpers::parse_text(text));
    };

    "no_shebang"_test = [] {
        std::string text = "name: value\n";
        expect(test_helpers::parse_text(text));
    };

    "shebang_file"_test = [] {
        expect(test_helpers::parse_file("../fixtures/shebang.yaal"));
    };

    "simple_brace_block"_test = [] {
        std::string text = "script: { echo hello }\n";
        expect(test_helpers::parse_text(text));
        
        std::string output = test_helpers::parse_with_output(text);
        expect(test_helpers::output_contains(output, "Brace block: { echo hello }"));
    };

    "multiline_brace_block"_test = [] {
        std::string text = "script: {\n  echo hello\n  exit 0\n}\n";
        expect(test_helpers::parse_text(text));
    };

    "nested_brace_blocks"_test = [] {
        std::string text = "nested: { outer { inner content } more }\n";
        expect(test_helpers::parse_text(text));
    };

    "brace_block_with_special_chars"_test = [] {
        std::string text = "script: { echo hello:world; test $VAR }\n";
        expect(test_helpers::parse_text(text));
    };

    "empty_brace_block"_test = [] {
        std::string text = "script: {}\n";
        expect(test_helpers::parse_text(text));
    };

    "brace_blocks_file"_test = [] {
        expect(test_helpers::parse_file("../fixtures/brace_blocks.yaal"));
    };

    "simple_nesting"_test = [] {
        std::string text = "config:\n  debug: false\n  timeout: 30\n";
        expect(test_helpers::parse_text(text));
    };

    "deep_nesting"_test = [] {
        std::string text = "config:\n  database:\n    credentials:\n      username: admin\n      password: secret\n";
        expect(test_helpers::parse_text(text));
    };

    "mixed_nesting"_test = [] {
        std::string text = "config:\n  production\n  debug: false\n  servers:\n    web-01\n    web-02\n    database: db-01\n";
        expect(test_helpers::parse_text(text));
    };

    "nested_file"_test = [] {
        expect(test_helpers::parse_file("../fixtures/nested.yaal"));
    };

    "polymorphic_lists"_test = [] {
        expect(test_helpers::parse_file("../fixtures/polymorphic_lists.yaal"));
    };
};

} // namespace advanced_features_tests