#pragma once

#include <iostream>
#include <tao/pegtl.hpp>

namespace pegtl = tao::pegtl;

namespace grammar {

// Basic characters
struct space : pegtl::one<' '> {};  // Spaces only, no tabs
struct not_colon_newline_quote : pegtl::not_one<':', '\n', '"'> {};
struct not_brace_newline_quote : pegtl::not_one<'{', '}', '\n', '"'> {};
struct not_newline : pegtl::not_one<'\n'> {};

// Shebang support
struct identifier_char : pegtl::sor<pegtl::alnum, pegtl::one<'_', '-'>> {};
struct identifier : pegtl::seq<pegtl::sor<pegtl::alpha, pegtl::one<'_'>>, pegtl::star<identifier_char>> {};
struct shebang_line : pegtl::seq<pegtl::string<'#', '!'>, identifier, pegtl::eol> {};

// String handling
struct escaped_char : pegtl::seq<pegtl::one<'\\'>, pegtl::one<'"', '\\', 'n', 't', 'r'>> {};
struct unescaped_char : pegtl::not_one<'"', '\\'> {};
struct double_quoted : pegtl::seq<pegtl::one<'"'>, pegtl::star<pegtl::sor<escaped_char, unescaped_char>>, pegtl::one<'"'>> {};
struct triple_quoted : pegtl::seq<pegtl::string<'"', '"', '"'>, pegtl::until<pegtl::string<'"', '"', '"'>>> {};
struct quoted_string : pegtl::sor<triple_quoted, double_quoted> {};

// Brace blocks - balanced brace matching
struct brace_content;
struct nested_brace : pegtl::seq<pegtl::one<'{'>, brace_content, pegtl::one<'}'>> {};
struct brace_content : pegtl::star<pegtl::sor<nested_brace, pegtl::not_one<'{', '}'>>> {};
struct brace_block : pegtl::seq<pegtl::one<'{'>, brace_content, pegtl::one<'}'>> {};

// Key-value parsing with first colon rule
struct key_part : pegtl::plus<not_colon_newline_quote> {};  // Everything before first colon
struct unquoted_value : pegtl::plus<not_brace_newline_quote> {};  // Value content
struct content_value : pegtl::sor<quoted_string, brace_block, unquoted_value> {};  // Try brace_block before unquoted_value

// Line content for simple statements (no colon)
struct unquoted_line : pegtl::plus<not_colon_newline_quote> {};
struct line_content : pegtl::sor<quoted_string, unquoted_line> {};

// Comments and newlines
struct comment : pegtl::seq<pegtl::one<'#'>, pegtl::until<pegtl::eolf>> {};
struct newline : pegtl::seq<pegtl::star<space>, pegtl::eol> {};
struct _NEWLINE : pegtl::plus<pegtl::sor<newline, comment>> {};

// Indentation (placeholder, requires custom state management)
struct INDENT : pegtl::success {}; // Implement indentation logic externally
struct DEDENT : pegtl::success {}; // Implement indentation logic externally

// Forward declarations
struct stmt;
struct suite : pegtl::sor<_NEWLINE, pegtl::seq<_NEWLINE, INDENT, pegtl::plus<stmt>, DEDENT>> {};

// Statements
struct simple_stmt : pegtl::seq<line_content, _NEWLINE> {};  // Line without colon
struct compound_stmt : pegtl::seq<key_part, pegtl::one<':'>, pegtl::star<space>, pegtl::opt<pegtl::sor<content_value, suite>>, pegtl::opt<_NEWLINE>> {};  // Line with colon
struct stmt : pegtl::sor<simple_stmt, compound_stmt> {};

// Top-level file input
struct file_input : pegtl::star<pegtl::sor<_NEWLINE, stmt>> {};
struct start : pegtl::seq<pegtl::opt<shebang_line>, file_input> {};

} // namespace grammar

struct Context {
  // put your contextual information here
};

struct ASTVisitor {
  explicit ASTVisitor(Context &ctx) : ctx(ctx) {}

  void visitShebang(const std::string &content) {
    std::cout << "Shebang: " << content << "\n";
  }

  void visitSimpleStmt(const std::string &content) {
    std::cout << "Simple statement: " << content << "\n";
  }

  void visitKeyPart(const std::string &key) {
    std::cout << "Key: " << key << "\n";
  }

  void visitContentValue(const std::string &value) {
    std::cout << "Value: " << value << "\n";
  }

  void visitBraceBlock(const std::string &content) {
    std::cout << "Brace block: " << content << "\n";
  }

  void enterCompoundStmt() {
    std::cout << "Entering compound statement\n";
  }

  void leaveCompoundStmt() {
    std::cout << "Leaving compound statement\n";
  }

  Context &ctx;
};

template <typename Rule> struct Action {};

template <> struct Action<grammar::shebang_line> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.visitShebang(in.string());
  }
};

template <> struct Action<grammar::simple_stmt> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.visitSimpleStmt(in.string());
  }
};

template <> struct Action<grammar::key_part> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.visitKeyPart(in.string());
  }
};

template <> struct Action<grammar::content_value> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.visitContentValue(in.string());
  }
};

template <> struct Action<grammar::brace_block> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.visitBraceBlock(in.string());
  }
};

template <> struct Action<grammar::compound_stmt> {
  template <typename Input>
  static void apply(const Input &in, ASTVisitor &visitor) {
    visitor.enterCompoundStmt();
  }
};

template <> struct Action<grammar::suite> {
  template <typename Input>
  static void apply(const Input &, ASTVisitor &visitor) {
    visitor.leaveCompoundStmt();
  }
};