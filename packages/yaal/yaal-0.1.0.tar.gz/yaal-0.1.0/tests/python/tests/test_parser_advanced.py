"""Advanced parser functionality tests"""

import pytest
from pathlib import Path
from yaal_parser import YaalParser, YaalParseError


class TestShebangParsing:
    """Test shebang line parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_shebang_pipeline(self):
        """Test #!pipeline shebang"""
        text = "#!pipeline\nname: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_shebang_hibrid_code(self):
        """Test #!hibrid-code shebang"""
        text = "#!hibrid-code\nname: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_shebang_custom(self):
        """Test custom shebang"""
        text = "#!custom-context\nname: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_no_shebang(self):
        """Test parsing without shebang"""
        text = "name: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_shebang_file(self):
        """Test parsing shebang from file"""
        filepath = self.fixtures_dir / "shebang.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None


class TestBraceBlocks:
    """Test brace block parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_simple_brace_block(self):
        """Test simple brace block"""
        text = "script: { echo hello }\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multiline_brace_block(self):
        """Test multiline brace block"""
        text = """script: {
  echo "hello"
  exit 0
}\n"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_nested_brace_blocks(self):
        """Test nested brace blocks"""
        text = "nested: { outer { inner content } more }\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_brace_block_with_special_chars(self):
        """Test brace blocks with special characters"""
        text = 'script: { echo "hello:world"; test $VAR }\n'
        result = self.parser.parse(text)
        assert result is not None
    
    def test_brace_blocks_file(self):
        """Test parsing brace blocks from file"""
        filepath = self.fixtures_dir / "brace_blocks.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None
    
    def test_unmatched_braces_error(self):
        """Test error handling for unmatched braces"""
        text = "broken: { incomplete\n"
        with pytest.raises(YaalParseError):
            self.parser.parse(text)


class TestNestedStructures:
    """Test nested structure parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_simple_nesting(self):
        """Test simple nested structure"""
        text = """config:
  debug: false
  timeout: 30
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_deep_nesting(self):
        """Test deeply nested structure"""
        text = """config:
  database:
    credentials:
      username: admin
      password: secret
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_mixed_nesting(self):
        """Test mixed simple statements and nested structures"""
        text = """config:
  production
  debug: false
  servers:
    web-01
    web-02
    database: db-01
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_nested_file(self):
        """Test parsing nested structures from file"""
        filepath = self.fixtures_dir / "nested.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None
    
    def test_polymorphic_lists(self):
        """Test polymorphic lists (mixed values and key-value pairs)"""
        filepath = self.fixtures_dir / "polymorphic_lists.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None


class TestStringHandling:
    """Test string parsing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_unquoted_strings(self):
        """Test unquoted string values"""
        text = "name: John Doe\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_double_quoted_strings(self):
        """Test double-quoted strings"""
        text = 'description: "this is quoted"\n'
        result = self.parser.parse(text)
        assert result is not None
    
    def test_triple_quoted_strings(self):
        """Test triple-quoted multiline strings"""
        text = '''documentation: """
This is a multiline string
with colons: 12:30:45
and URLs: https://example.com
"""\n'''
        result = self.parser.parse(text)
        assert result is not None
    
    def test_strings_with_colons(self):
        """Test strings containing colons"""
        text = "time: 12:30:45\nurl: https://example.com:8080\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_strings_file(self):
        """Test parsing strings from file"""
        filepath = self.fixtures_dir / "strings.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None
    
    def test_escaped_characters(self):
        """Test escaped characters in strings"""
        text = r'message: "Hello \"world\" with escaping"' + "\n"
        result = self.parser.parse(text)
        assert result is not None


class TestComments:
    """Test comment parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_line_comments(self):
        """Test line comments"""
        text = "# This is a comment\nname: John\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_inline_comments(self):
        """Test inline comments"""
        text = "name: John  # inline comment\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multiple_comments(self):
        """Test multiple comments"""
        text = """# First comment
# Second comment
name: John
# Another comment
age: 25
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_comments_file(self):
        """Test parsing comments from file"""
        filepath = self.fixtures_dir / "comments.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None


class TestFirstColonRule:
    """Test the first colon rule implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_single_colon(self):
        """Test single colon separation"""
        text = "name: John\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multiple_colons_in_value(self):
        """Test multiple colons in value part"""
        text = "time: 12:30:45\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_url_with_colons(self):
        """Test URL with multiple colons"""
        text = "api: https://api.example.com:8080/v1\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_database_url_with_colons(self):
        """Test database URL with multiple colons"""
        text = "db: postgresql://user:pass@host:5432/db\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_first_colon_rule_file(self):
        """Test first colon rule from file"""
        filepath = self.fixtures_dir / "first_colon_rule.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None