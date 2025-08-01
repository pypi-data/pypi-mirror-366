#pragma once

#include <boost/ut.hpp>
#include "../yaal_parser.hpp"  // Include the parser header from parent directory
#include <fstream>
#include <sstream>
#include <iostream>

namespace test_helpers {

// Parse YAAL text and return success/failure
inline bool parse_text(const std::string& text) {
    try {
        pegtl::string_input input(text, "test_input");
        Context ctx;
        ASTVisitor visitor(ctx);
        return pegtl::parse<grammar::start, Action>(input, visitor);
    } catch (...) {
        return false;
    }
}

// Parse YAAL file and return success/failure
inline bool parse_file(const std::string& filepath) {
    try {
        pegtl::file_input input(filepath);
        Context ctx;
        ASTVisitor visitor(ctx);
        return pegtl::parse<grammar::start, Action>(input, visitor);
    } catch (...) {
        return false;
    }
}

// Read file content
inline std::string read_file(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filepath);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

// Parse and capture visitor output
inline std::string parse_with_output(const std::string& text) {
    // Redirect cout to capture output
    std::stringstream captured_output;
    std::streambuf* orig_cout = std::cout.rdbuf();
    std::cout.rdbuf(captured_output.rdbuf());
    
    try {
        pegtl::string_input input(text, "test_input");
        Context ctx;
        ASTVisitor visitor(ctx);
        bool success = pegtl::parse<grammar::start, Action>(input, visitor);
        
        // Restore cout
        std::cout.rdbuf(orig_cout);
        
        if (success) {
            return captured_output.str();
        } else {
            return "";
        }
    } catch (...) {
        // Restore cout
        std::cout.rdbuf(orig_cout);
        return "";
    }
}

// Check if output contains expected text
inline bool output_contains(const std::string& output, const std::string& expected) {
    return output.find(expected) != std::string::npos;
}

// Count occurrences of text in output
inline int count_occurrences(const std::string& output, const std::string& text) {
    int count = 0;
    size_t pos = 0;
    while ((pos = output.find(text, pos)) != std::string::npos) {
        count++;
        pos += text.length();
    }
    return count;
}

} // namespace test_helpers