#!/usr/bin/env python3
"""Test runner script for YAAL parser tests"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests using pytest"""
    
    # Change to the test directory
    test_dir = Path(__file__).parent
    
    print("🧪 Running YAAL Parser Tests")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = [
        "uv", "run", "pytest",
        "tests/",
        "--cov=yaal_parser",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=test_dir, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("\n📊 Coverage report generated in htmlcov/")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: 'uv' command not found")
        print("Please install uv: https://docs.astral.sh/uv/")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_specific_test(test_pattern):
    """Run specific test pattern"""
    
    test_dir = Path(__file__).parent
    
    cmd = [
        "uv", "run", "pytest",
        f"tests/{test_pattern}",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=test_dir, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_pattern = sys.argv[1]
        exit_code = run_specific_test(test_pattern)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)