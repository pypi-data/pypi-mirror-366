#!/usr/bin/env python3

import sys
import os

try:
    from lark import Lark, Transformer
    from lark.indenter import PythonIndenter
    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False
    print("Warning: Lark not available. Install with: pip install lark")


class YaalTransformer(Transformer):
    def __init__(self):
        self.shebang_context = None
        self.indent_level = 0

    def start(self, items):
        result = {"_items": []}
        shebang_found = False
        
        for item in items:
            if item is not None:
                if isinstance(item, dict) and "_shebang" in item:
                    self.shebang_context = item["_shebang"]
                    result["_shebang"] = item["_shebang"]
                    shebang_found = True
                elif isinstance(item, list):
                    # Process file_input items
                    for subitem in item:
                        if subitem is not None:
                            self._add_item_to_result(result, subitem)
                else:
                    self._add_item_to_result(result, item)
        
        return result

    def _add_item_to_result(self, result, item):
        if isinstance(item, dict):
            if item.get("type") == "simple_stmt":
                result["_items"].append(item["content"])
            elif item.get("type") == "compound_stmt":
                key = item["key"]
                value = item.get("value")
                
                if key not in result:
                    if isinstance(value, dict) and value.get("_type") == "brace_block":
                        result[key] = {"_type": "brace_block", "_content": value["_content"]}
                    elif isinstance(value, dict) and "_items" in value:
                        result[key] = value
                    else:
                        result[key] = {"_items": [value] if value is not None else [""]}
                else:
                    # Handle multiple values for same key
                    if not isinstance(result[key], list):
                        result[key] = [result[key]]
                    result[key].append(value)

    def shebang_line(self, items):
        return {"_shebang": str(items[0])}
    
    def file_input(self, items):
        return [item for item in items if item is not None]

    def simple_stmt(self, items):
        return {"type": "simple_stmt", "content": str(items[0]).strip()}

    def compound_stmt(self, items):
        key = str(items[0]).strip()
        value = None
        suite = None
        
        # Parse items: key, optional value, optional suite
        for item in items[1:]:
            if isinstance(item, dict) and "_items" in item:
                suite = item
            elif item is not None:
                value = item
        
        if suite:
            return {"type": "compound_stmt", "key": key, "value": suite}
        else:
            return {"type": "compound_stmt", "key": key, "value": value}

    def key_part(self, items):
        return str(items[0]).strip()

    def value_part(self, items):
        if not items:
            return None
        return items[0]

    def content_value(self, items):
        if not items:
            return None
        return items[0]

    def unquoted_value(self, items):
        if not items:
            return None
        return str(items[0]).strip()

    def brace_block(self, items):
        content = "".join(str(item) for item in items) if items else ""
        return {"_type": "brace_block", "_content": content}

    def brace_content(self, items):
        return "".join(str(item) for item in items) if items else ""

    def suite(self, items):
        result = {"_items": []}
        for item in items:
            if item is not None:
                self._add_item_to_result(result, item)
        return result

    def line_content(self, items):
        return str(items[0]).strip()

    def unquoted_line(self, items):
        return str(items[0]).strip()

    def quoted_string(self, items):
        content = str(items[0])
        # Handle different quote types
        if content.startswith('"""') and content.endswith('"""'):
            return content[3:-3]  # Remove triple quotes
        elif content.startswith('"') and content.endswith('"'):
            return content[1:-1]  # Remove double quotes
        elif content.startswith("'") and content.endswith("'"):
            return content[1:-1]  # Remove single quotes
        return content

    def single_quoted(self, items):
        content = str(items[0])
        return content[1:-1]  # Remove single quotes


def parse(data, grammar_file="yaal.lark", debug=False):
    if not LARK_AVAILABLE:
        print("Cannot parse: Lark library not available")
        return None
        
    try:
        grammar_path = os.path.join(os.path.dirname(__file__), grammar_file)
        with open(grammar_path, "r") as fh:
            if debug:
                grammar = Lark(fh, parser="lalr", postlex=PythonIndenter())
                tree = grammar.parse(data)
                print("✓ Parsing successful!")
                print(tree.pretty())
                return tree
            else:
                grammar = Lark(fh, parser="lalr", postlex=PythonIndenter(), transformer=YaalTransformer())
                result = grammar.parse(data)
                return result

    except Exception as e:
        print(f"✗ Parse error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        raise


def parse_file(filename, debug=False):
    with open(filename, "r") as fh:
        return parse(fh.read(), debug=debug)


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        debug = "--debug" in sys.argv
        try:
            result = parse_file(filename, debug)
            if not debug:
                print("✓ Parsing succeeded!")
                print("Result:", result)
        except Exception as e:
            print(f"Failed to parse {filename}: {e}")
            sys.exit(1)
    else:
        print("Usage: python yaal.py <file.yaal> [--debug]")


if __name__ == "__main__":
    main()