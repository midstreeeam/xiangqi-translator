#!/usr/bin/env python3
"""
Quick test script for Xiangqi Translator.
Run this for a fast verification that everything works.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def quick_test():
    """Run a quick functionality test."""
    try:
        # Test imports
        from xiangqi_translator import translate_from_fen, get_initial_board
        
        # Test basic functionality
        board = get_initial_board()
        fen = board.to_fen()
        
        # Test translation
        result = translate_from_fen(fen, "炮二平五")
        
        if result.success:
            print(f"✓ Quick test PASSED")
            print(f"  Translation: '炮二平五' → '{result.iccs_move}'")
            return True
        else:
            print(f"✗ Quick test FAILED: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"✗ Quick test ERROR: {e}")
        return False


def main():
    """Run quick test."""
    print("Xiangqi Translator - Quick Test")
    print("=" * 40)
    
    success = quick_test()
    
    if success:
        print("\nFor comprehensive testing, run:")
        print("  python tests/run_all_tests.py")
        print("\nFor usage examples, run:")
        print("  python examples/basic_usage.py")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 