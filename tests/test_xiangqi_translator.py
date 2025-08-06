#!/usr/bin/env python3
"""
Comprehensive test suite for the Xiangqi Translator.
Tests all functionality including move translation, validation, error handling, and edge cases.
"""

import unittest
import sys
import os

# Ensure we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xiangqi_translator import (
    XiangqiBoard, 
    XiangqiTranslator, 
    translate_from_fen,
    get_initial_board,
    validate_move,
    get_legal_moves,
    Color,
    PieceType,
    Position
)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality."""
    
    def setUp(self):
        """Set up test board."""
        self.board = get_initial_board()
        self.fen = self.board.to_fen()
    
    def test_initial_position(self):
        """Test initial board setup."""
        board = get_initial_board()
        expected_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        self.assertEqual(board.to_fen(), expected_fen)
        self.assertEqual(board.active_color, Color.RED)
    
    def test_basic_translation(self):
        """Test basic move translation."""
        result = translate_from_fen(self.fen, "炮二平五")
        self.assertTrue(result.success)
        self.assertEqual(result.iccs_move, "h2e2")
    
    def test_move_validation(self):
        """Test move validation."""
        result = validate_move(self.fen, "h2", "e2")
        self.assertTrue(result['valid'])
        
        result = validate_move(self.fen, "h2", "a9")  # Invalid
        self.assertFalse(result['valid'])
    
    def test_legal_moves(self):
        """Test legal moves generation."""
        result = get_legal_moves(self.fen)
        self.assertTrue(result['success'])
        self.assertGreater(len(result['moves']), 0)


class TestChineseNotationParsing(unittest.TestCase):
    """Test Chinese notation parsing."""
    
    def test_standard_notation_parsing(self):
        """Test parsing of standard Chinese notation."""
        from xiangqi_translator.chinese_notation import parse_chinese_move
        
        test_cases = [
            ("炮二平五", PieceType.CANNON, 2, "traverse", 5),
            ("马八进七", PieceType.HORSE, 8, "advance", 7),
            ("车九退一", PieceType.CHARIOT, 9, "retreat", 1),
            ("兵三进一", PieceType.PAWN, 3, "advance", 1),
            ("将五进一", PieceType.KING, 5, "advance", 1),
        ]
        
        for chinese_move, expected_piece, expected_file, expected_movement, expected_target in test_cases:
            with self.subTest(move=chinese_move):
                parsed = parse_chinese_move(chinese_move, Color.RED)
                self.assertIsNotNone(parsed, f"Failed to parse {chinese_move}")
                self.assertEqual(parsed.piece_type, expected_piece)
                self.assertEqual(parsed.source_file, expected_file)
                self.assertEqual(parsed.movement, expected_movement)
                self.assertEqual(parsed.target, expected_target)
    
    def test_invalid_notation(self):
        """Test handling of invalid Chinese notation."""
        from xiangqi_translator.chinese_notation import parse_chinese_move
        
        invalid_moves = [
            "将十进十",  # Invalid numbers
            "xyz123",    # Invalid characters
            "马",        # Incomplete move
        ]
        
        for invalid_move in invalid_moves:
            with self.subTest(move=invalid_move):
                parsed = parse_chinese_move(invalid_move, Color.RED)
                self.assertIsNone(parsed, f"Should not parse invalid move: {invalid_move}")


class TestAmbiguousMovesAndDisambiguation(unittest.TestCase):
    """Test ambiguous moves and disambiguation."""
    
    def test_ambiguity_detection(self):
        """Test that ambiguous moves are detected."""
        # Position with two cannons in same file
        ambiguous_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/7C1/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        
        result = translate_from_fen(ambiguous_fen, "炮二平五")
        self.assertFalse(result.success)
        self.assertIn("不明确", result.error_message)
    
    def test_disambiguation_works(self):
        """Test that disambiguation works correctly."""
        ambiguous_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/7C1/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        
        # Test front and back disambiguation
        front_result = translate_from_fen(ambiguous_fen, "前炮平五")
        self.assertTrue(front_result.success)
        
        back_result = translate_from_fen(ambiguous_fen, "后炮平五")
        self.assertTrue(back_result.success)
        
        # They should be different moves
        self.assertNotEqual(front_result.iccs_move, back_result.iccs_move)


class TestHorseBlocking(unittest.TestCase):
    """Test horse leg blocking (蹩马腿) functionality."""
    
    def test_basic_horse_blocking(self):
        """Test basic horse leg blocking scenarios."""
        # Position with horse at e1 and blocking piece at e2
        blocked_fen = "9/9/9/9/9/9/9/4P4/4N4/9 w - - 0 1"
        
        # Test moves that should be blocked
        result = validate_move(blocked_fen, "e1", "f3")
        self.assertFalse(result['valid'], "Move should be blocked by horse leg")
        
        result = validate_move(blocked_fen, "e1", "d3")
        self.assertFalse(result['valid'], "Move should be blocked by horse leg")
    
    def test_no_blocking_control(self):
        """Test scenarios where horse should NOT be blocked."""
        # Clear position with no blocking
        clear_fen = "9/9/9/9/9/9/9/9/4N4/9 w - - 0 1"
        
        # All valid horse moves should be allowed
        result = validate_move(clear_fen, "e1", "f3")
        self.assertTrue(result['valid'], "Move should be allowed with no blocking")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_fen_handling(self):
        """Test handling of invalid FEN strings."""
        invalid_fens = [
            "invalid_fen",
            "rnbakabnr/9/1c5c1",  # Incomplete FEN
        ]
        
        for invalid_fen in invalid_fens:
            with self.subTest(fen=invalid_fen):
                result = translate_from_fen(invalid_fen, "炮二平五")
                self.assertFalse(result.success)
                self.assertIsNotNone(result.error_message)
    
    def test_invalid_chinese_notation(self):
        """Test handling of invalid Chinese notation."""
        fen = get_initial_board().to_fen()
        
        invalid_moves = [
            "将十进十",    # Invalid numbers
            "xyz123",      # Invalid characters
            "马",          # Incomplete
        ]
        
        for invalid_move in invalid_moves:
            with self.subTest(move=invalid_move):
                result = translate_from_fen(fen, invalid_move)
                self.assertFalse(result.success)
                self.assertIsNotNone(result.error_message)


class TestIntegration(unittest.TestCase):
    """Integration tests covering full workflows."""
    
    def test_complete_move_sequence(self):
        """Test a complete sequence of moves."""
        moves_sequence = [
            "炮二平五",  # Central cannon
            "兵三进一",  # Pawn advance
        ]
        
        translator = XiangqiTranslator()
        current_board = get_initial_board()
        
        for move in moves_sequence:
            result = translator.translate_move(current_board, move, include_board_after=True)
            self.assertTrue(result.success, f"Move {move} failed: {result.error_message}")
            self.assertIsNotNone(result.iccs_move)
            self.assertIsNotNone(result.board_after_move)
            current_board = result.board_after_move
    
    def test_board_state_after_move(self):
        """Test board state after moves."""
        fen = get_initial_board().to_fen()
        result = translate_from_fen(fen, "炮二平五", include_board_after=True)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.board_after_move)
        
        # Check that the cannon moved correctly
        from_pos = Position.from_string("h2")
        to_pos = Position.from_string("e2")
        
        self.assertIsNone(result.board_after_move.get_piece(from_pos))  # Source empty
        piece = result.board_after_move.get_piece(to_pos)
        self.assertIsNotNone(piece)  # Destination has piece
        self.assertEqual(piece.piece_type, PieceType.CANNON)
        self.assertEqual(piece.color, Color.RED)


class TestPerformance(unittest.TestCase):
    """Basic performance tests."""
    
    def test_translation_performance(self):
        """Test that translations complete in reasonable time."""
        import time
        
        fen = get_initial_board().to_fen()
        start_time = time.time()
        
        # Translate 100 moves
        for _ in range(100):
            result = translate_from_fen(fen, "炮二平五")
            self.assertTrue(result.success)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Should complete in reasonable time (less than 10ms per translation)
        self.assertLess(avg_time, 0.01, f"Average translation time too slow: {avg_time:.3f}s")


if __name__ == "__main__":
    unittest.main(verbosity=2)