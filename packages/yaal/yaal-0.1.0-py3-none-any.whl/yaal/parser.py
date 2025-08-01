"""YAAL Parser Implementation using Lark"""

import os
from pathlib import Path
from typing import Optional, Union, Any
from lark import Lark, Tree, Token
from lark.indenter import PythonIndenter
from lark.exceptions import LarkError


class YaalParseError(Exception):
    """Exception raised when YAAL parsing fails"""
    pass


class YaalParser:
    """YAAL language parser using Lark"""
    
    def __init__(self, grammar_file: Optional[str] = None):
        """Initialize the YAAL parser
        
        Args:
            grammar_file: Path to the grammar file. If None, uses the default grammar.
        """
        if grammar_file is None:
            grammar_file = Path(__file__).parent / "grammar.lark"
        
        try:
            with open(grammar_file, "r") as f:
                grammar_content = f.read()
            
            self.parser = Lark(
                grammar_content,
                parser="lalr",
                postlex=PythonIndenter(),
                start="start"
            )
        except Exception as e:
            raise YaalParseError(f"Failed to initialize parser: {e}")
    
    def parse(self, text: str) -> Tree:
        """Parse YAAL text and return the AST
        
        Args:
            text: YAAL source code to parse
            
        Returns:
            Lark Tree representing the parsed AST
            
        Raises:
            YaalParseError: If parsing fails
        """
        try:
            # Ensure text ends with newline for proper parsing
            if not text.endswith('\n'):
                text += '\n'
            
            return self.parser.parse(text)
        except LarkError as e:
            raise YaalParseError(f"Parse error: {e}")
    
    def parse_file(self, filepath: Union[str, Path]) -> Tree:
        """Parse a YAAL file and return the AST
        
        Args:
            filepath: Path to the YAAL file
            
        Returns:
            Lark Tree representing the parsed AST
            
        Raises:
            YaalParseError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Check for binary content (null bytes)
            if '\x00' in content:
                raise YaalParseError(f"Binary content detected in file {filepath}")
            return self.parse(content)
        except (FileNotFoundError, UnicodeDecodeError):
            raise
        except Exception as e:
            raise YaalParseError(f"Failed to parse file {filepath}: {e}")
    
    def validate(self, text: str) -> bool:
        """Validate YAAL text without returning the AST
        
        Args:
            text: YAAL source code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse(text)
            return True
        except YaalParseError:
            return False


class YaalASTVisitor:
    """Base class for visiting YAAL AST nodes"""
    
    def visit(self, node: Union[Tree, Token]) -> Any:
        """Visit a node in the AST"""
        if isinstance(node, Tree):
            method_name = f"visit_{node.data}"
            if hasattr(self, method_name):
                return getattr(self, method_name)(node)
            else:
                return self.generic_visit(node)
        elif isinstance(node, Token):
            return self.visit_token(node)
        else:
            return node
    
    def generic_visit(self, node: Tree) -> Any:
        """Default visit method for unhandled node types"""
        return [self.visit(child) for child in node.children if child is not None]
    
    def visit_token(self, token: Token) -> Any:
        """Visit a token node"""
        return token.value


class YaalExtractor(YaalASTVisitor):
    """Extract structured data from YAAL AST"""
    
    def __init__(self):
        self.result = {}
        self.current_context = [self.result]
    
    def extract(self, tree: Tree) -> dict:
        """Extract structured data from the AST"""
        self.visit(tree)
        return self.result
    
    def visit_start(self, node: Tree) -> None:
        """Visit the start node"""
        for child in node.children:
            if child is not None:
                self.visit(child)
            elif len(node.children) > 1 and child is None:
                # Check if this might be a shebang that was parsed but not captured
                # This is a workaround for the grammar issue
                pass
    
    def visit_shebang_line(self, node: Tree) -> None:
        """Visit shebang line"""
        # Extract shebang identifier from SHEBANG token
        for child in node.children:
            if child is not None and isinstance(child, Token):
                # Extract the identifier part after #!
                shebang_value = child.value
                if shebang_value.startswith('#!'):
                    self.result["_shebang"] = shebang_value[2:]  # Remove #!
                else:
                    self.result["_shebang"] = shebang_value
    
    def visit_simple_stmt(self, node: Tree) -> None:
        """Visit simple statement"""
        content = ""
        for child in node.children:
            if child is not None:
                if isinstance(child, Token):
                    content += child.value
                else:
                    visited = self.visit(child)
                    if isinstance(visited, str):
                        content += visited
                    elif isinstance(visited, list) and len(visited) == 1:
                        content += str(visited[0])
                    else:
                        content += str(visited)
        
        # Add to current context as a list item
        current = self.current_context[-1]
        if "_items" not in current:
            current["_items"] = []
        current["_items"].append(content.strip())
    
    def visit_compound_stmt(self, node: Tree) -> None:
        """Visit compound statement (key-value pair)"""
        key = None
        value = None
        
        for child in node.children:
            if child is not None and hasattr(child, 'data'):
                if child.data == "key_part":
                    key = self.visit(child)
                elif child.data == "value_part":
                    value = self.visit(child)
                elif child.data == "suite":
                    # Handle nested suite
                    nested_dict = {}
                    self.current_context.append(nested_dict)
                    self.visit(child)
                    self.current_context.pop()
                    value = nested_dict
        
        if key:
            current = self.current_context[-1]
            key = key.strip()
            if value is not None:
                current[key] = value
            else:
                # Empty value, prepare for nested content
                current[key] = {"_items": []}
                # Don't change context for empty values in compound statements
    
    def visit_key_part(self, node: Tree) -> str:
        """Visit key part of compound statement"""
        return "".join(self.visit(child) for child in node.children)
    
    def visit_value_part(self, node: Tree) -> Any:
        """Visit value part of compound statement"""
        if not node.children:
            return None
        
        for child in node.children:
            if child is not None:
                result = self.visit(child)
                # Return the result directly - don't convert dicts to strings
                if isinstance(result, (dict, str)):
                    return result
                elif isinstance(result, list) and len(result) == 1:
                    return result[0]
                return result
        return None
    
    def visit_content_value(self, node: Tree) -> Any:
        """Visit content value"""
        for child in node.children:
            if child is not None:
                visited = self.visit(child)
                # Return dicts directly (for brace blocks)
                if isinstance(visited, dict):
                    return visited
                elif isinstance(visited, str):
                    return visited.strip()
                elif isinstance(visited, list) and len(visited) == 1:
                    return str(visited[0]).strip()
                else:
                    return str(visited).strip()
        return ""
    
    def visit_brace_block(self, node: Tree) -> dict:
        """Visit brace block"""
        content = ""
        for child in node.children:
            if child is not None and hasattr(child, 'data') and child.data == "brace_content":
                content = self.visit(child)
        return {"_type": "brace_block", "content": content}
    
    def visit_brace_content(self, node: Tree) -> str:
        """Visit brace content"""
        result = ""
        for child in node.children:
            if child is not None:
                visited = self.visit(child)
                if isinstance(visited, str):
                    result += visited
                else:
                    result += str(visited)
        return result
    
    def visit_brace_item(self, node: Tree) -> str:
        """Visit brace item"""
        result = ""
        for child in node.children:
            if child is not None:
                if isinstance(child, Token):
                    result += child.value
                elif hasattr(child, 'data') and child.data == 'brace_content':
                    # Nested brace content
                    result += "{" + self.visit(child) + "}"
                else:
                    result += str(self.visit(child))
        return result
    
    def visit_quoted_string(self, node: Tree) -> str:
        """Visit quoted string"""
        for child in node.children:
            if child is not None and isinstance(child, Token):
                if child.type == 'TRIPLE_QUOTED_STRING':
                    # Extract content from triple-quoted string
                    content = child.value
                    if content.startswith('"""') and content.endswith('"""'):
                        return content[3:-3]  # Remove the triple quotes
                    return content
                elif child.type == 'ESCAPED_STRING':
                    # Handle escaped strings (remove outer quotes and process escapes)
                    content = child.value
                    if content.startswith('"') and content.endswith('"'):
                        return content[1:-1].encode().decode('unicode_escape')
                    return content
                else:
                    # Handle other string types (like single quotes)
                    content = child.value
                    if (content.startswith("'") and content.endswith("'")) or \
                       (content.startswith('"') and content.endswith('"')):
                        return content[1:-1]  # Remove outer quotes
                    return content
        
        # Fallback for other cases
        return "".join(str(self.visit(child)) for child in node.children if child is not None)
    
    def visit_single_quoted(self, node: Tree) -> str:
        """Visit single quoted string"""
        for child in node.children:
            if child is not None and isinstance(child, Token):
                content = child.value
                if content.startswith("'") and content.endswith("'"):
                    return content[1:-1]  # Remove outer quotes
                return content
        return "".join(str(self.visit(child)) for child in node.children if child is not None)
    
    def visit_line_content(self, node: Tree) -> str:
        """Visit line content"""
        result = ""
        for child in node.children:
            if child is not None:
                if isinstance(child, Token):
                    result += child.value
                else:
                    result += str(self.visit(child))
        return result.strip()
    
    def visit_suite(self, node: Tree) -> None:
        """Visit suite (indented block)"""
        for child in node.children:
            if child is not None:
                self.visit(child)
    
    def visit_unquoted_line(self, node: Tree) -> str:
        """Visit unquoted line"""
        result = ""
        for child in node.children:
            if child is not None:
                if isinstance(child, Token):
                    result += child.value
                else:
                    result += str(self.visit(child))
        return result.strip()