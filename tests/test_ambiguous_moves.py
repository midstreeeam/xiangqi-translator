#!/usr/bin/env python3
"""
Test script for ambiguous move handling in Xiangqi Translator.
Tests disambiguation when multiple pieces could make the same move.
"""

import sys
import os

# Add the parent src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xiangqi_translator import XiangqiBoard, translate_from_fen


def test_ambiguous_cannons():
    print("=== Testing Ambiguous Cannon Moves ===\n")
    
    # Create a custom position with two red cannons in file 2 (board file h, which is Chinese file 2 for red)
    # Let's put one cannon at h2 and another at h5
    custom_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/7C1/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
    
    board = XiangqiBoard.from_fen(custom_fen)
    print("Custom position with two cannons in file 2:")
    print(board)
    print(f"FEN: {custom_fen}\n")
    
    # Test 1: Try ambiguous move "炮二平五"
    print("1. Testing ambiguous move '炮二平五':")
    print("-" * 40)
    result = translate_from_fen(custom_fen, "炮二平五", include_board_after=False)
    
    if result.success:
        print(f"✓ Translated to: {result.iccs_move}")
        print("WARNING: This should probably fail due to ambiguity!")
    else:
        print(f"✗ Error (expected): {result.error_message}")
    
    print()
    
    # Test 2: Try disambiguated moves
    print("2. Testing disambiguated moves:")
    print("-" * 40)
    
    # Front cannon
    result = translate_from_fen(custom_fen, "前炮平五", include_board_after=False)
    if result.success:
        print(f"✓ 前炮平五 -> {result.iccs_move}")
    else:
        print(f"✗ 前炮平五 failed: {result.error_message}")
    
    # Back cannon  
    result = translate_from_fen(custom_fen, "后炮平五", include_board_after=False)
    if result.success:
        print(f"✓ 后炮平五 -> {result.iccs_move}")
    else:
        print(f"✗ 后炮平五 failed: {result.error_message}")
    
    print()


def test_other_ambiguous_cases():
    print("=== Testing Other Ambiguous Cases ===\n")
    
    # Test with horses in same file
    # Create position with two horses in same file
    custom_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4N4/RNBAKA1NR w - - 0 1"
    
    board = XiangqiBoard.from_fen(custom_fen)
    print("Position with potential horse ambiguity:")
    print(board)
    print(f"FEN: {custom_fen}\n")
    
    # Try horse move that might be ambiguous
    result = translate_from_fen(custom_fen, "马五进三", include_board_after=False)
    if result.success:
        print(f"✓ 马五进三 -> {result.iccs_move}")
    else:
        print(f"✗ 马五进三 failed: {result.error_message}")
    
    print()


def test_three_pieces_same_file():
    print("=== Testing Three Pieces in Same File ===\n")
    
    # Create position with three pawns in same file (after crossing river)
    # This is a more complex disambiguation case
    custom_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/4P4/4P4/P1P1P1P1P/1C2P2C1/9/RNBAKABNR w - - 0 1"
    
    board = XiangqiBoard.from_fen(custom_fen)
    print("Position with three pawns in same file:")
    print(board)
    print(f"FEN: {custom_fen}\n")
    
    # Test middle pawn notation
    result = translate_from_fen(custom_fen, "中兵进一", include_board_after=False)
    if result.success:
        print(f"✓ 中兵进一 -> {result.iccs_move}")
    else:
        print(f"✗ 中兵进一 failed: {result.error_message}")
    
    # Test front pawn
    result = translate_from_fen(custom_fen, "前兵进一", include_board_after=False)
    if result.success:
        print(f"✓ 前兵进一 -> {result.iccs_move}")
    else:
        print(f"✗ 前兵进一 failed: {result.error_message}")
    
    # Test back pawn
    result = translate_from_fen(custom_fen, "后兵进一", include_board_after=False)
    if result.success:
        print(f"✓ 后兵进一 -> {result.iccs_move}")
    else:
        print(f"✗ 后兵进一 failed: {result.error_message}")


def main():
    """Run all ambiguous move tests."""
    print("=" * 60)
    print("XIANGQI TRANSLATOR - AMBIGUOUS MOVE TESTS")
    print("=" * 60)
    print()
    
    try:
        test_ambiguous_cannons()
        test_other_ambiguous_cases()
        test_three_pieces_same_file()
        
        print("\n" + "=" * 60)
        print("All ambiguous move tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 