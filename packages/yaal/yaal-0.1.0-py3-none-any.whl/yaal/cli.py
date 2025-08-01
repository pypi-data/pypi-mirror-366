#!/usr/bin/env python3
"""YAAL Parser Command Line Interface"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .parser import YaalParser, YaalExtractor, YaalParseError


def parse_command(args: argparse.Namespace) -> int:
    """Parse a YAAL file and optionally extract data"""
    parser = YaalParser()
    
    try:
        if args.file == "-":
            content = sys.stdin.read()
            tree = parser.parse(content)
        else:
            tree = parser.parse_file(args.file)
        
        if args.extract:
            extractor = YaalExtractor()
            data = extractor.extract(tree)
            
            if args.output_format == "json":
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif args.output_format == "pretty":
                import pprint
                pprint.pprint(data)
            else:
                print(data)
        else:
            if args.verbose:
                print(tree.pretty())
            else:
                print("✓ Parsing succeeded")
        
        return 0
        
    except YaalParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def validate_command(args: argparse.Namespace) -> int:
    """Validate YAAL file syntax"""
    parser = YaalParser()
    
    try:
        if args.file == "-":
            content = sys.stdin.read()
            parser.parse(content)
        else:
            parser.parse_file(args.file)
        
        print(f"✓ {args.file}: Valid YAAL syntax")
        return 0
        
    except YaalParseError as e:
        print(f"✗ {args.file}: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"✗ File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


def extract_command(args: argparse.Namespace) -> int:
    """Extract structured data from YAAL file"""
    parser = YaalParser()
    extractor = YaalExtractor()
    
    try:
        if args.file == "-":
            content = sys.stdin.read()
            tree = parser.parse(content)
        else:
            tree = parser.parse_file(args.file)
        
        data = extractor.extract(tree)
        
        if args.output:
            output_path = Path(args.output)
            if args.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(str(data))
        else:
            if args.format == "json":
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif args.format == "pretty":
                import pprint
                pprint.pprint(data)
            else:
                print(data)
        
        return 0
        
    except YaalParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="yaal",
        description="YAAL (Yet Another Abstract Language) Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yaal parse config.yaal                    # Parse and validate
  yaal parse config.yaal --extract --json  # Parse and extract as JSON
  yaal validate *.yaal                     # Validate multiple files
  yaal extract config.yaal -o data.json    # Extract to file
  cat config.yaal | yaal parse -           # Parse from stdin
        """,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse YAAL file and optionally extract data",
    )
    parse_parser.add_argument(
        "file",
        help="YAAL file to parse (use '-' for stdin)",
    )
    parse_parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract structured data from parsed tree",
    )
    parse_parser.add_argument(
        "--output-format",
        choices=["json", "pretty", "raw"],
        default="raw",
        help="Output format for extracted data",
    )
    parse_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed parse tree",
    )
    parse_parser.set_defaults(func=parse_command)
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate YAAL file syntax",
    )
    validate_parser.add_argument(
        "file",
        nargs="+",
        help="YAAL file(s) to validate (use '-' for stdin)",
    )
    validate_parser.set_defaults(func=lambda args: sum(
        validate_command(argparse.Namespace(file=f)) for f in args.file
    ))
    
    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract structured data from YAAL file",
    )
    extract_parser.add_argument(
        "file",
        help="YAAL file to extract from (use '-' for stdin)",
    )
    extract_parser.add_argument(
        "--format", "-f",
        choices=["json", "pretty", "raw"],
        default="json",
        help="Output format",
    )
    extract_parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)",
    )
    extract_parser.set_defaults(func=extract_command)
    
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())