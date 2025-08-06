#!/usr/bin/env python3
"""
Focused tests for ambiguous move handling in Xiangqi Translator.
"""

import sys
import os

# Add the parent src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xiangqi_translator import translate_from_fen


def test_ambiguous_moves():
    """Test ambiguous move detection and disambiguation."""
    print("Testing ambiguous move handling...")
    
    # Position with two cannons in same file
    ambiguous_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/7C1/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
    
    # Test 1: Ambiguous move should fail
    result = translate_from_fen(ambiguous_fen, "炮二平五")
    if result.success:
        print("✗ ERROR: Ambiguous move should fail!")
        return False
    else:
        print(f"✓ Ambiguous move correctly detected: {result.error_message}")
    
    # Test 2: Disambiguated moves should work
    front_result = translate_from_fen(ambiguous_fen, "前炮平五")
    if not front_result.success:
        print(f"✗ ERROR: Front cannon disambiguation failed: {front_result.error_message}")
        return False
    else:
        print(f"✓ Front cannon move: {front_result.iccs_move}")
    
    back_result = translate_from_fen(ambiguous_fen, "后炮平五")
    if not back_result.success:
        print(f"✗ ERROR: Back cannon disambiguation failed: {back_result.error_message}")
        return False
    else:
        print(f"✓ Back cannon move: {back_result.iccs_move}")
    
    # Test 3: They should be different moves
    if front_result.iccs_move == back_result.iccs_move:
        print("✗ ERROR: Front and back moves should be different!")
        return False
    else:
        print("✓ Front and back moves are correctly different")
    
    return True


def main():
    """Run ambiguous move tests."""
    print("=" * 50)
    print("XIANGQI TRANSLATOR - AMBIGUOUS MOVE TESTS")
    print("=" * 50)
    
    try:
        success = test_ambiguous_moves()
        
        if success:
            print("\n✓ All ambiguous move tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 