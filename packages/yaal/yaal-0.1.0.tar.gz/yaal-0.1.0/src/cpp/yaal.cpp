#include <iostream>
#include <tao/pegtl.hpp>

namespace pegtl = tao::pegtl;

namespace grammar {

// Basic characters (spaces only, no tabs)
struct space : pegtl::one<' '> {};
struct spaces : pegtl::plus<space> {};
struct optional_spaces : pegtl::star<space> {};
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
struct single_quoted : pegtl::seq<pegtl::one<'\''>, pegtl::star<pegtl::not_one<'\''> >, pegtl::one<'\''>> {};
struct triple_quoted : pegtl::seq<pegtl::string<'"', '"', '"'>, pegtl::until<pegtl::string<'"', '"', '"'>>> {};
struct quoted_string : pegtl::sor<triple_quoted, double_quoted, single_quoted> {};

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

// Indentation (simplified for now)
struct INDENT : pegtl::success {}; // Placeholder for indentation management
struct DEDENT : pegtl::success {}; // Placeholder for indentation management

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
  std::string shebang_context;
  int indent_level = 0;
};

struct ASTVisitor {
  explicit ASTVisitor(Context &ctx) : ctx(ctx) {}

  void visitShebang(const std::string &content) {
    std::cout << "Shebang: " << content << "\n";
    ctx.shebang_context = content;
  }

  void visitSimpleStmt(const std::string &content) {
    std::cout << "Simple statement: " << content << "\n";
  }

  void visitKeyPart(const std::string &key) {
    std::string trimmed_key = key;
    // Trim leading/trailing spaces
    size_t start = trimmed_key.find_first_not_of(" \t");
    size_t end = trimmed_key.find_last_not_of(" \t");
    if (start != std::string::npos && end != std::string::npos) {
      trimmed_key = trimmed_key.substr(start, end - start + 1);
    }
    std::cout << "Key: " << trimmed_key << "\n";
  }

  void visitContentValue(const std::string &value) {
    std::string trimmed_value = value;
    // Trim leading/trailing spaces but preserve internal structure
    size_t start = trimmed_value.find_first_not_of(" \t");
    if (start != std::string::npos) {
      trimmed_value = trimmed_value.substr(start);
    }
    size_t end = trimmed_value.find_last_not_of(" \t");
    if (end != std::string::npos) {
      trimmed_value = trimmed_value.substr(0, end + 1);
    }
    std::cout << "Value: " << trimmed_value << "\n";
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
    std::string content = in.string();
    size_t pos = content.find("!");
    if (pos != std::string::npos) {
      std::string context = content.substr(pos + 1);
      // Remove newline
      if (!context.empty() && context.back() == '\n') {
        context.pop_back();
      }
      visitor.visitShebang(context);
    }
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
    // Note: leaveCompoundStmt() should be called when the compound statement ends,
    // not immediately after entering. This will be handled by the suite rule or
    // at the end of compound statement processing.
  }
};

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <file.yaal>\n";
    return 1;
  }

  try {
    pegtl::file_input input(argv[1]);
    Context ctx;
    ASTVisitor visitor(ctx);

    if (pegtl::parse<grammar::start, Action>(input, visitor)) {
      std::cout << "\n✓ Parsing succeeded.\n";
      if (!ctx.shebang_context.empty()) {
        std::cout << "Document context: " << ctx.shebang_context << "\n";
      }
    } else {
      std::cerr << "✗ Parsing failed.\n";
      return 1;
    }
  } catch (const std::exception &e) {
    std::cerr << "Error: " << e.what() << "\n";
    return 1;
  }

  return 0;
}