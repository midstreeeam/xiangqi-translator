"""
Xiangqi Translator - Convert Chinese xiangqi notation to Pikafish-compatible ICCS format.

This package provides functionality to:
1. Parse Chinese xiangqi move notation (like "马八进二")
2. Validate moves according to xiangqi rules
3. Convert to standardized ICCS coordinate format (like "h2e2")
4. Output board state after moves
"""

from .board import XiangqiBoard, Position, Piece, Color, PieceType
from .chinese_notation import ChineseNotationParser, ParsedMove, parse_chinese_move
from .move_validation import MoveValidator
from .translator import XiangqiTranslator, TranslationResult, translate_chinese_move, translate_from_fen

__version__ = "1.0.0"
__author__ = "xiangqi-translator"

# Main API functions
__all__ = [
    # Core classes
    'XiangqiBoard',
    'Position', 
    'Piece',
    'Color',
    'PieceType',
    
    # Translation
    'XiangqiTranslator',
    'TranslationResult',
    'translate_chinese_move',
    'translate_from_fen',
    
    # Parsing
    'ChineseNotationParser',
    'ParsedMove',
    'parse_chinese_move',
    
    # Validation
    'MoveValidator',
]


def translate(board_fen: str, chinese_move: str, include_board_after: bool = True) -> dict:
    """
    Main API function to translate Chinese xiangqi notation to ICCS format.
    
    Args:
        board_fen: FEN string representing the board position
        chinese_move: Chinese move notation (e.g., "马八进二")
        include_board_after: Whether to include the board state after the move
        
    Returns:
        Dictionary with translation result:
        {
            'success': bool,
            'iccs_move': str or None,  # e.g., "h2e2"
            'error_message': str or None,
            'board_after_fen': str or None,  # FEN after move if include_board_after=True
            'board_after_ascii': str or None  # ASCII representation if include_board_after=True
        }
    
    Example:
        >>> result = translate("rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1", "炮二平五")
        >>> print(result)
        {
            'success': True,
            'iccs_move': 'h2e2',
            'error_message': None,
            'board_after_fen': 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C2C4/9/RNBAKABNR b - - 0 1',
            'board_after_ascii': '...'
        }
    """
    try:
        result = translate_from_fen(board_fen, chinese_move, include_board_after)
        
        response = {
            'success': result.success,
            'iccs_move': result.iccs_move,
            'error_message': result.error_message,
            'board_after_fen': None,
            'board_after_ascii': None
        }
        
        if result.board_after_move:
            response['board_after_fen'] = result.board_after_move.to_fen()
            response['board_after_ascii'] = str(result.board_after_move)
        
        return response
        
    except Exception as e:
        return {
            'success': False,
            'iccs_move': None,
            'error_message': f"Unexpected error: {str(e)}",
            'board_after_fen': None,
            'board_after_ascii': None
        }


def get_initial_board() -> XiangqiBoard:
    """Get the initial xiangqi board position."""
    return XiangqiBoard.initial_position()


def validate_move(board_fen: str, from_square: str, to_square: str) -> dict:
    """
    Validate if a move is legal in the given position.
    
    Args:
        board_fen: FEN string representing the board position
        from_square: Source square in ICCS format (e.g., "h2")
        to_square: Target square in ICCS format (e.g., "e2")
        
    Returns:
        Dictionary with validation result:
        {
            'valid': bool,
            'error_message': str or None
        }
    """
    try:
        board = XiangqiBoard.from_fen(board_fen)
        validator = MoveValidator(board)
        
        from_pos = Position.from_string(from_square)
        to_pos = Position.from_string(to_square)
        
        is_valid = validator.is_valid_move(from_pos, to_pos)
        
        return {
            'valid': is_valid,
            'error_message': "Invalid move" if not is_valid else None
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error_message': f"Validation error: {str(e)}"
        }


def get_legal_moves(board_fen: str, color: str = None) -> dict:
    """
    Get all legal moves for the given position.
    
    Args:
        board_fen: FEN string representing the board position
        color: "red" or "black" (if None, uses active color from FEN)
        
    Returns:
        Dictionary with legal moves:
        {
            'success': bool,
            'moves': List[str],  # List of moves in ICCS format
            'error_message': str or None
        }
    """
    try:
        board = XiangqiBoard.from_fen(board_fen)
        validator = MoveValidator(board)
        
        if color is None:
            move_color = board.active_color
        else:
            move_color = Color.RED if color.lower() == "red" else Color.BLACK
        
        legal_moves = validator.get_legal_moves(move_color)
        iccs_moves = [f"{from_pos}{to_pos}" for from_pos, to_pos in legal_moves]
        
        return {
            'success': True,
            'moves': iccs_moves,
            'error_message': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'moves': [],
            'error_message': f"Error getting legal moves: {str(e)}"
        }
