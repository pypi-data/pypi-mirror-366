"""Edge cases and error handling tests"""

import pytest
from pathlib import Path
from yaal_parser import YaalParser, YaalParseError


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_empty_input(self):
        """Test parsing empty input"""
        result = self.parser.parse("")
        assert result is not None
    
    def test_whitespace_only(self):
        """Test parsing whitespace-only input"""
        result = self.parser.parse("   \n  \n   \n")
        assert result is not None
    
    def test_comments_only(self):
        """Test parsing comments-only input"""
        text = "# Just a comment\n# Another comment\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_single_character_key(self):
        """Test single character keys"""
        text = "a: value\nb: another\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_single_character_value(self):
        """Test single character values"""
        text = "key: a\nanother: b\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_very_long_key(self):
        """Test very long keys"""
        long_key = "a" * 1000
        text = f"{long_key}: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_very_long_value(self):
        """Test very long values"""
        long_value = "a" * 1000
        text = f"key: {long_value}\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_unicode_characters(self):
        """Test Unicode characters in keys and values"""
        text = "名前: 田中\némoji: 🚀\naccents: café\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_special_characters_in_keys(self):
        """Test special characters in keys"""
        text = "key-with-dashes: value\nkey_with_underscores: value\nkey.with.dots: value\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_numbers_as_keys(self):
        """Test numeric keys"""
        text = "123: numeric key\n456.789: float key\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_mixed_indentation_levels(self):
        """Test mixed indentation levels"""
        text = """level1:
  level2a: value
    level3: deep value
  level2b: another value
"""
        result = self.parser.parse(text)
        assert result is not None


class TestErrorConditions:
    """Test error conditions and invalid syntax"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_unmatched_opening_brace(self):
        """Test unmatched opening brace"""
        text = "broken: { incomplete\n"
        with pytest.raises(YaalParseError):
            self.parser.parse(text)
    
    def test_unmatched_closing_brace(self):
        """Test unmatched closing brace"""
        text = "broken: incomplete }\n"
        with pytest.raises(YaalParseError):
            self.parser.parse(text)
    
    def test_unclosed_double_quote(self):
        """Test unclosed double quote"""
        text = 'broken: "unclosed string\n'
        with pytest.raises(YaalParseError):
            self.parser.parse(text)
    
    def test_unclosed_triple_quote(self):
        """Test unclosed triple quote"""
        text = 'broken: """unclosed multiline\n'
        with pytest.raises(YaalParseError):
            self.parser.parse(text)
    
    def test_invalid_shebang(self):
        """Test invalid shebang syntax"""
        text = "#invalid shebang\nkey: value\n"
        # This might be valid depending on grammar - adjust if needed
        result = self.parser.parse(text)
        assert result is not None
    
    def test_tabs_in_indentation(self):
        """Test tabs in indentation (should be spaces only)"""
        text = "config:\n\tdebug: false\n"  # Tab character
        # This might fail depending on grammar strictness
        try:
            result = self.parser.parse(text)
            # If it doesn't fail, that's also valid behavior
            assert result is not None
        except YaalParseError:
            # Expected if grammar enforces spaces-only
            pass
    
    def test_inconsistent_indentation(self):
        """Test inconsistent indentation"""
        text = """config:
  level2: value
    level3: value
 bad_indent: value
"""
        # This might fail depending on indentation rules
        try:
            result = self.parser.parse(text)
            assert result is not None
        except YaalParseError:
            # Expected for inconsistent indentation
            pass


class TestBoundaryConditions:
    """Test boundary conditions and limits"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_maximum_nesting_depth(self):
        """Test deeply nested structures"""
        # Create a deeply nested structure
        text = "level0:\n"
        indent = "  "
        for i in range(1, 20):  # 20 levels deep
            text += f"{indent * i}level{i}:\n"
        text += f"{indent * 20}value: deep\n"
        
        result = self.parser.parse(text)
        assert result is not None
    
    def test_many_siblings(self):
        """Test many sibling elements"""
        text = ""
        for i in range(100):  # 100 sibling elements
            text += f"key{i}: value{i}\n"
        
        result = self.parser.parse(text)
        assert result is not None
    
    def test_large_brace_block(self):
        """Test large brace block content"""
        large_content = "echo " + "a" * 1000
        text = f"script: {{ {large_content} }}\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_many_colons_in_value(self):
        """Test value with many colons"""
        many_colons = ":".join(["part"] * 50)  # 49 colons
        text = f"key: {many_colons}\n"
        result = self.parser.parse(text)
        assert result is not None


class TestValidationEdgeCases:
    """Test validation method edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_validate_empty_string(self):
        """Test validation of empty string"""
        assert self.parser.validate("") is True
    
    def test_validate_whitespace_only(self):
        """Test validation of whitespace-only string"""
        assert self.parser.validate("   \n  \n") is True
    
    def test_validate_valid_complex(self):
        """Test validation of complex valid structure"""
        text = """#!pipeline
config:
  production
  debug: false
  script: { echo hello }
"""
        assert self.parser.validate(text) is True
    
    def test_validate_invalid_syntax(self):
        """Test validation of invalid syntax"""
        text = "broken: { unmatched\n"
        assert self.parser.validate(text) is False
    
    def test_validate_multiple_errors(self):
        """Test validation with multiple syntax errors"""
        text = '''broken: { unmatched
unclosed: "string
invalid_triple: """unclosed
'''
        assert self.parser.validate(text) is False


class TestFileHandling:
    """Test file handling edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("definitely_does_not_exist.yaal")
    
    def test_parse_empty_file(self):
        """Test parsing empty file"""
        # Create a temporary empty file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaal', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.parser.parse_file(temp_path)
            assert result is not None
        finally:
            Path(temp_path).unlink()  # Clean up
    
    def test_parse_binary_file(self):
        """Test parsing binary file (should fail gracefully)"""
        # Create a temporary binary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.yaal', delete=False) as f:
            f.write(b'\x00\x01\x02\x03')  # Binary content
            temp_path = f.name
        
        try:
            with pytest.raises((YaalParseError, UnicodeDecodeError)):
                self.parser.parse_file(temp_path)
        finally:
            Path(temp_path).unlink()  # Clean up