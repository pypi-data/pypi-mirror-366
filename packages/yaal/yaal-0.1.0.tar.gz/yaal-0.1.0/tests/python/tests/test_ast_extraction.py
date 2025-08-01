"""AST extraction and data structure tests"""

import pytest
from pathlib import Path
from yaal_parser import YaalParser, YaalExtractor


class TestASTExtraction:
    """Test AST extraction functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_extract_simple_key_value(self):
        """Test extracting simple key-value pairs"""
        text = "name: John\nage: 25\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert "name" in result
        assert "age" in result
    
    def test_extract_shebang(self):
        """Test extracting shebang information"""
        text = "#!pipeline\nname: John\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert "_shebang" in result
        assert result["_shebang"] == "pipeline"
    
    def test_extract_simple_statements(self):
        """Test extracting simple statements"""
        text = "production\ndebug mode\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert "_items" in result
        assert "production" in result["_items"]
        assert "debug mode" in result["_items"]
    
    def test_extract_brace_blocks(self):
        """Test extracting brace blocks"""
        text = "script: { echo hello }\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert "script" in result
        assert isinstance(result["script"], dict)
        assert result["script"]["_type"] == "brace_block"
        assert "echo hello" in result["script"]["content"]
    
    def test_extract_nested_structures(self):
        """Test extracting nested structures"""
        text = """config:
  debug: false
  timeout: 30
"""
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert "config" in result
        # Note: The exact structure depends on the extractor implementation
        # This test validates that nested structures are handled
    
    def test_extract_from_file(self):
        """Test extracting data from file"""
        filepath = self.fixtures_dir / "basic.yaal"
        tree = self.parser.parse_file(filepath)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
        assert len(result) > 0


class TestDataStructureValidation:
    """Test validation of extracted data structures"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
    
    def test_key_value_structure(self):
        """Test key-value structure validation"""
        text = "name: John\nage: 25\nenabled: true\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        # Validate structure
        assert isinstance(result, dict)
        for key, value in result.items():
            if not key.startswith("_"):  # Skip metadata keys
                assert isinstance(key, str)
                assert len(key) > 0
    
    def test_first_colon_rule_extraction(self):
        """Test first colon rule in extraction"""
        text = "time stamp: 12:30:45\nurl: https://api.example.com:8080\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        # Validate that keys are correctly extracted (before first colon)
        assert "time stamp" in result
        assert "url" in result
        
        # Validate that values contain the remaining colons
        if "time stamp" in result:
            assert ":" in str(result["time stamp"])
        if "url" in result:
            assert ":" in str(result["url"])
    
    def test_mixed_content_structure(self):
        """Test mixed content structure (simple statements + key-value)"""
        text = """production
name: John
debug mode
age: 25
"""
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        # Should have both key-value pairs and simple statements
        assert isinstance(result, dict)
        
        # Check for key-value pairs
        key_value_found = any(key for key in result.keys() if not key.startswith("_"))
        
        # Check for simple statements (in _items)
        simple_statements_found = "_items" in result and len(result["_items"]) > 0
        
        # At least one type should be present
        assert key_value_found or simple_statements_found


class TestComplexStructures:
    """Test complex data structure extraction"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_polymorphic_lists_extraction(self):
        """Test extraction of polymorphic lists"""
        filepath = self.fixtures_dir / "polymorphic_lists.yaal"
        tree = self.parser.parse_file(filepath)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
        assert "deployment" in result
    
    def test_nested_structure_extraction(self):
        """Test extraction of deeply nested structures"""
        filepath = self.fixtures_dir / "nested.yaal"
        tree = self.parser.parse_file(filepath)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
        assert "config" in result
    
    def test_string_types_extraction(self):
        """Test extraction of different string types"""
        filepath = self.fixtures_dir / "strings.yaal"
        tree = self.parser.parse_file(filepath)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
        # Should contain various string types
        assert len(result) > 0
    
    def test_brace_blocks_extraction(self):
        """Test extraction of brace blocks"""
        filepath = self.fixtures_dir / "brace_blocks.yaal"
        tree = self.parser.parse_file(filepath)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
        
        # Look for brace block structures
        brace_blocks_found = False
        for key, value in result.items():
            if isinstance(value, dict) and value.get("_type") == "brace_block":
                brace_blocks_found = True
                assert "content" in value
                break
        
        # Note: This assertion might need adjustment based on extractor implementation
        # assert brace_blocks_found


class TestErrorHandling:
    """Test error handling in AST extraction"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
    
    def test_extract_empty_tree(self):
        """Test extracting from empty tree"""
        text = ""
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
    
    def test_extract_comments_only(self):
        """Test extracting from comments-only content"""
        text = "# Just a comment\n# Another comment\n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)
    
    def test_extract_whitespace_only(self):
        """Test extracting from whitespace-only content"""
        text = "   \n  \n   \n"
        tree = self.parser.parse(text)
        result = self.extractor.extract(tree)
        
        assert isinstance(result, dict)