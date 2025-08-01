"""Basic parser functionality tests"""

import pytest
from pathlib import Path
from yaal_parser import YaalParser, YaalParseError


class TestBasicParsing:
    """Test basic parsing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_parser_initialization(self):
        """Test parser can be initialized"""
        parser = YaalParser()
        assert parser is not None
        assert parser.parser is not None
    
    def test_parse_empty_string(self):
        """Test parsing empty string"""
        result = self.parser.parse("")
        assert result is not None
    
    def test_parse_simple_key_value(self):
        """Test parsing simple key-value pairs"""
        text = "name: John\nage: 25\n"
        result = self.parser.parse(text)
        assert result is not None
        assert result.data == "start"
    
    def test_parse_simple_statement(self):
        """Test parsing simple statements (no colons)"""
        text = "production\ndebug mode enabled\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_parse_with_shebang(self):
        """Test parsing with shebang line"""
        text = "#!pipeline\nname: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_parse_file_basic(self):
        """Test parsing basic file"""
        filepath = self.fixtures_dir / "basic.yaal"
        result = self.parser.parse_file(filepath)
        assert result is not None
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent.yaal")
    
    def test_validate_valid_syntax(self):
        """Test validation of valid syntax"""
        text = "name: John\nage: 25\n"
        assert self.parser.validate(text) is True
    
    def test_validate_invalid_syntax(self):
        """Test validation of invalid syntax"""
        text = "invalid_quotes: \"unclosed string\n"
        assert self.parser.validate(text) is False
    
    def test_parse_error_handling(self):
        """Test proper error handling for invalid syntax"""
        text = "invalid_quotes: \"unclosed string\n"
        with pytest.raises(YaalParseError):
            self.parser.parse(text)


class TestKeyValueParsing:
    """Test key-value parsing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_basic_key_value(self):
        """Test basic key-value parsing"""
        text = "name: John\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_keys_with_spaces(self):
        """Test keys containing spaces"""
        text = "api endpoint: https://example.com\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_first_colon_rule(self):
        """Test first colon rule - everything after first colon is value"""
        text = "time stamp: 12:30:45\n"
        result = self.parser.parse(text)
        assert result is not None
        
        text = "url: https://api.example.com:8080/v1\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_empty_value(self):
        """Test key with empty value"""
        text = "empty_key:\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_quoted_values(self):
        """Test quoted string values"""
        text = 'description: "this is quoted"\n'
        result = self.parser.parse(text)
        assert result is not None
    
    def test_triple_quoted_values(self):
        """Test triple-quoted multiline values"""
        text = '''documentation: """
This is multiline
with colons: 12:30:45
"""\n'''
        result = self.parser.parse(text)
        assert result is not None


class TestSimpleStatements:
    """Test simple statement parsing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_single_simple_statement(self):
        """Test single simple statement"""
        text = "production\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multiple_simple_statements(self):
        """Test multiple simple statements"""
        text = "production\ndebug mode\nhostname localhost\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_simple_statements_with_spaces(self):
        """Test simple statements containing spaces"""
        text = "debug mode enabled\nsome random text here\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_mixed_simple_and_compound(self):
        """Test mixing simple statements and key-value pairs"""
        text = """production
name: John
debug mode enabled
age: 25
"""
        result = self.parser.parse(text)
        assert result is not None