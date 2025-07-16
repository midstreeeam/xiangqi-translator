#!/usr/bin/env python3
"""
Basic Usage Examples for Xiangqi Translator
Shows how to use the library to translate Chinese xiangqi moves to ICCS format.
"""

import sys
import os

# Add the parent src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xiangqi_translator import (
    translate_from_fen,
    get_initial_board,
    validate_move,
    get_legal_moves,
    XiangqiTranslator
)


def basic_translation_example():
    """Show basic translation from Chinese notation to ICCS."""
    print("=" * 60)
    print("BASIC TRANSLATION EXAMPLE")
    print("=" * 60)
    
    # Get initial board FEN
    initial_board = get_initial_board()
    fen = initial_board.to_fen()
    
    print(f"Initial position FEN: {fen}\n")
    
    # Example moves to translate
    moves = [
        "炮二平五",  # Central cannon
        "马二进三",  # Horse advance
        "兵三进一",  # Pawn advance
        "车九平八",  # Chariot move
    ]
    
    print("Translating Chinese moves to ICCS format:")
    print("-" * 40)
    
    for chinese_move in moves:
        result = translate_from_fen(fen, chinese_move)
        
        if result.success:
            print(f"✓ {chinese_move:8} → {result.iccs_move}")
        else:
            print(f"✗ {chinese_move:8} → Error: {result.error_message}")
    
    print()


def move_validation_example():
    """Show move validation functionality."""
    print("=" * 60)
    print("MOVE VALIDATION EXAMPLE")
    print("=" * 60)
    
    initial_board = get_initial_board()
    fen = initial_board.to_fen()
    
    print("Validating ICCS moves:")
    print("-" * 40)
    
    # Test various moves
    test_moves = [
        ("h2", "e2"),  # Valid cannon move
        ("h0", "g2"),  # Valid horse move  
        ("e0", "e5"),  # Invalid king move (too far)
        ("a0", "i0"),  # Invalid chariot move (blocked)
    ]
    
    for from_sq, to_sq in test_moves:
        result = validate_move(fen, from_sq, to_sq)
        move_str = f"{from_sq}-{to_sq}"
        
        if result['valid']:
            print(f"✓ {move_str:8} → Valid")
        else:
            print(f"✗ {move_str:8} → Invalid: {result.get('error_message', 'Unknown error')}")
    
    print()


def legal_moves_example():
    """Show legal move generation."""
    print("=" * 60)
    print("LEGAL MOVES EXAMPLE")
    print("=" * 60)
    
    initial_board = get_initial_board()
    fen = initial_board.to_fen()
    
    print("Getting legal moves for red from initial position:")
    print("-" * 40)
    
    result = get_legal_moves(fen, "red")
    
    if result['success']:
        moves = result['moves']
        print(f"Found {len(moves)} legal moves:")
        
        # Group moves by piece type based on starting square
        cannon_moves = [m for m in moves if m.startswith(('h2', 'b2'))]
        horse_moves = [m for m in moves if m.startswith(('h0', 'b0'))]
        pawn_moves = [m for m in moves if m[1] == '3']  # Pawns start on rank 3
        
        print(f"  Cannon moves: {len(cannon_moves)} (e.g., {cannon_moves[:3] if cannon_moves else 'none'})")
        print(f"  Horse moves:  {len(horse_moves)} (e.g., {horse_moves[:3] if horse_moves else 'none'})")
        print(f"  Pawn moves:   {len(pawn_moves)} (e.g., {pawn_moves[:3] if pawn_moves else 'none'})")
        
        if len(moves) > 20:
            print(f"  ... and {len(moves) - 20} more")
        else:
            print(f"  All moves: {moves}")
    else:
        print(f"✗ Error getting legal moves: {result['error_message']}")
    
    print()


def disambiguation_example():
    """Show disambiguation handling."""
    print("=" * 60)
    print("DISAMBIGUATION EXAMPLE")
    print("=" * 60)
    
    # Custom position with two cannons in same file
    custom_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/7C1/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
    
    print("Custom position with two cannons in file 2:")
    print(f"FEN: {custom_fen}\n")
    
    moves_to_test = [
        "炮二平五",   # Ambiguous - should fail
        "前炮平五",   # Front cannon - should work
        "后炮平五",   # Back cannon - should work
    ]
    
    print("Testing disambiguation:")
    print("-" * 40)
    
    for chinese_move in moves_to_test:
        result = translate_from_fen(custom_fen, chinese_move)
        
        if result.success:
            print(f"✓ {chinese_move:8} → {result.iccs_move}")
        else:
            print(f"✗ {chinese_move:8} → Error: {result.error_message}")
    
    print()


def game_sequence_example():
    """Show a sequence of moves in a game."""
    print("=" * 60)
    print("GAME SEQUENCE EXAMPLE")
    print("=" * 60)
    
    print("Playing a sequence of moves:")
    print("-" * 40)
    
    # Start with initial position
    translator = XiangqiTranslator()
    current_board = get_initial_board()
    
    # Sequence of moves
    moves = [
        "炮二平五",  # Central cannon
        "兵三进一",  # Pawn advance
    ]
    
    for i, chinese_move in enumerate(moves, 1):
        print(f"Move {i}: {chinese_move}")
        
        result = translator.translate_move(current_board, chinese_move, include_board_after=True)
        
        if result.success:
            print(f"  → ICCS: {result.iccs_move}")
            print(f"  → FEN after move: {result.board_after_move.to_fen()}")
            current_board = result.board_after_move
        else:
            print(f"  → Error: {result.error_message}")
            break
        
        print()


def error_handling_example():
    """Show error handling for invalid inputs."""
    print("=" * 60)
    print("ERROR HANDLING EXAMPLE")
    print("=" * 60)
    
    initial_board = get_initial_board()
    fen = initial_board.to_fen()
    
    print("Testing error handling:")
    print("-" * 40)
    
    # Test various invalid inputs
    invalid_moves = [
        "将十进十",    # Invalid Chinese numbers
        "xyz123",      # Invalid characters
        "马",          # Incomplete move
        "炮二平十",    # Invalid target position
    ]
    
    for invalid_move in invalid_moves:
        result = translate_from_fen(fen, invalid_move)
        print(f"✗ '{invalid_move}' → {result.error_message}")
    
    # Test invalid FEN
    print("\nTesting invalid FEN:")
    result = translate_from_fen("invalid_fen", "炮二平五")
    print(f"✗ Invalid FEN → {result.error_message}")
    
    print()


def performance_example():
    """Show basic performance measurement."""
    print("=" * 60)
    print("PERFORMANCE EXAMPLE")
    print("=" * 60)
    
    import time
    
    initial_board = get_initial_board()
    fen = initial_board.to_fen()
    
    print("Measuring translation performance:")
    print("-" * 40)
    
    # Time a single translation
    start_time = time.time()
    result = translate_from_fen(fen, "炮二平五")
    end_time = time.time()
    
    if result.success:
        print(f"Single translation: {(end_time - start_time) * 1000:.2f}ms")
    else:
        print(f"Translation failed: {result.error_message}")
    
    # Time multiple translations
    num_translations = 100
    start_time = time.time()
    
    for _ in range(num_translations):
        translate_from_fen(fen, "炮二平五")
    
    end_time = time.time()
    avg_time = (end_time - start_time) / num_translations
    
    print(f"Average over {num_translations} translations: {avg_time * 1000:.2f}ms")
    print(f"Translations per second: {1.0 / avg_time:.0f}")
    
    print()


def main():
    """Run all examples."""
    print("XIANGQI TRANSLATOR - BASIC USAGE EXAMPLES")
    print("Version: 1.0.0")
    print()
    
    try:
        basic_translation_example()
        move_validation_example()
        legal_moves_example()
        disambiguation_example()
        game_sequence_example()
        error_handling_example()
        performance_example()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 