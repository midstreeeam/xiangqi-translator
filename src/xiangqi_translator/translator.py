"""
Main xiangqi translator that converts Chinese move notation to standardized ICCS format.
"""

from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

from .board import XiangqiBoard, Position, Piece, Color, PieceType
from .chinese_notation import ChineseNotationParser, ParsedMove
from .move_validation import MoveValidator


@dataclass
class TranslationResult:
    """Result of translating a Chinese move to ICCS format."""
    success: bool
    iccs_move: Optional[str] = None  # e.g., "h2e2"
    error_message: Optional[str] = None
    board_after_move: Optional[XiangqiBoard] = None


class XiangqiTranslator:
    """Main translator for converting Chinese xiangqi notation to ICCS format."""
    
    def __init__(self):
        self.parser = ChineseNotationParser()
    
    def translate_move(self, board: XiangqiBoard, chinese_move: str, 
                      include_board_after: bool = False) -> TranslationResult:
        """
        Translate Chinese move notation to ICCS format.
        
        Args:
            board: Current board state
            chinese_move: Chinese move notation (e.g., "马八进二")
            include_board_after: Whether to include board state after move
            
        Returns:
            TranslationResult with ICCS move or error
        """
        try:
            # Parse the Chinese move
            parsed_move = self.parser.parse_move(chinese_move, board.active_color)
            if not parsed_move:
                return TranslationResult(
                    success=False,
                    error_message=f"无法解析中文棋谱: {chinese_move}"
                )
            
            # Find the actual piece and position
            move_candidates = self._find_move_candidates(board, parsed_move)
            if not move_candidates:
                return TranslationResult(
                    success=False,
                    error_message=f"找不到符合条件的棋子: {chinese_move}"
                )
            
            # Validate and select the correct move
            validator = MoveValidator(board)
            valid_moves = []
            
            for from_pos, to_pos in move_candidates:
                if validator.is_valid_move(from_pos, to_pos):
                    valid_moves.append((from_pos, to_pos))
            
            if not valid_moves:
                return TranslationResult(
                    success=False,
                    error_message=f"无效的移动: {chinese_move}"
                )
            
            if len(valid_moves) > 1:
                return TranslationResult(
                    success=False,
                    error_message=f"移动不明确，找到多个可能的移动: {chinese_move}"
                )
            
            from_pos, to_pos = valid_moves[0]
            iccs_move = f"{from_pos}{to_pos}"
            
            # Create board after move if requested
            board_after = None
            if include_board_after:
                board_after = board.copy()
                board_after.move_piece(from_pos, to_pos)
                board_after.active_color = Color.BLACK if board.active_color == Color.RED else Color.RED
                board_after.fullmove_number += 1 if board.active_color == Color.BLACK else 0
            
            return TranslationResult(
                success=True,
                iccs_move=iccs_move,
                board_after_move=board_after
            )
            
        except Exception as e:
            return TranslationResult(
                success=False,
                error_message=f"翻译错误: {str(e)}"
            )
    
    def _find_move_candidates(self, board: XiangqiBoard, parsed_move: ParsedMove) -> List[Tuple[Position, Position]]:
        """Find all possible moves that match the parsed Chinese notation."""
        candidates = []
        
        # Find all pieces of the specified type and color
        matching_pieces = []
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = board.get_piece(pos)
                if (piece and piece.piece_type == parsed_move.piece_type and 
                    piece.color == parsed_move.color):
                    matching_pieces.append(pos)
        
        # Handle disambiguation for pieces in tandem
        if parsed_move.is_front is not None or parsed_move.is_middle is not None:
            matching_pieces = self._disambiguate_tandem_pieces(
                board, matching_pieces, parsed_move
            )
        elif parsed_move.source_file > 0:
            # Filter by source file if specified
            board_file = self.parser.convert_file_to_board_coordinate(
                parsed_move.source_file, parsed_move.color
            )
            matching_pieces = [pos for pos in matching_pieces if pos.file == board_file]
        
        # Generate target positions based on movement type
        for from_pos in matching_pieces:
            target_positions = self._calculate_target_positions(
                board, from_pos, parsed_move
            )
            for to_pos in target_positions:
                candidates.append((from_pos, to_pos))
        
        return candidates
    
    def _disambiguate_tandem_pieces(self, board: XiangqiBoard, pieces: List[Position], 
                                   parsed_move: ParsedMove) -> List[Position]:
        """Disambiguate pieces in tandem using front/back/middle indicators."""
        if not pieces:
            return pieces
        
        # Group pieces by file
        pieces_by_file = {}
        for pos in pieces:
            if pos.file not in pieces_by_file:
                pieces_by_file[pos.file] = []
            pieces_by_file[pos.file].append(pos)
        
        result = []
        
        for file, file_pieces in pieces_by_file.items():
            if len(file_pieces) < 2:
                continue  # No tandem on this file
            
            # Sort by rank (consider color for front/back)
            if parsed_move.color == Color.RED:
                file_pieces.sort(key=lambda p: p.rank, reverse=True)  # Front = higher rank
            else:
                file_pieces.sort(key=lambda p: p.rank)  # Front = lower rank
            
            if parsed_move.is_front is True:
                result.append(file_pieces[0])  # Front piece
            elif parsed_move.is_front is False:
                result.append(file_pieces[-1])  # Back piece
            elif parsed_move.is_middle is True and len(file_pieces) >= 3:
                result.append(file_pieces[1])  # Middle piece
        
        return result
    
    def _calculate_target_positions(self, board: XiangqiBoard, from_pos: Position, 
                                   parsed_move: ParsedMove) -> List[Position]:
        """Calculate possible target positions based on movement type."""
        target_positions = []
        
        if parsed_move.movement == 'traverse':
            # Horizontal movement to specified file
            target_board_file = self.parser.convert_file_to_board_coordinate(
                parsed_move.target, parsed_move.color
            )
            target_positions.append(Position(target_board_file, from_pos.rank))
            
        elif parsed_move.movement == 'advance':
            target_positions.extend(
                self._calculate_advance_positions(board, from_pos, parsed_move)
            )
            
        elif parsed_move.movement == 'retreat':
            target_positions.extend(
                self._calculate_retreat_positions(board, from_pos, parsed_move)
            )
        
        return target_positions
    
    def _calculate_advance_positions(self, board: XiangqiBoard, from_pos: Position, 
                                   parsed_move: ParsedMove) -> List[Position]:
        """Calculate target positions for advance moves."""
        positions = []
        
        if parsed_move.piece_type in [PieceType.CHARIOT, PieceType.CANNON, PieceType.PAWN, PieceType.KING]:
            # Linear pieces: advance by specified distance
            direction = 1 if parsed_move.color == Color.RED else -1
            new_rank = from_pos.rank + (parsed_move.target * direction)
            if 0 <= new_rank <= 9:
                positions.append(Position(from_pos.file, new_rank))
                
        elif parsed_move.piece_type in [PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT]:
            # Diagonal pieces: target indicates destination file
            target_board_file = self.parser.convert_file_to_board_coordinate(
                parsed_move.target, parsed_move.color
            )
            
            # For these pieces, we need to find valid target positions
            # that match the piece movement rules
            for rank in range(10):
                target_pos = Position(target_board_file, rank)
                if self._is_piece_movement_pattern_valid(
                    parsed_move.piece_type, from_pos, target_pos, 'advance', parsed_move.color
                ):
                    positions.append(target_pos)
        
        return positions
    
    def _calculate_retreat_positions(self, board: XiangqiBoard, from_pos: Position, 
                                   parsed_move: ParsedMove) -> List[Position]:
        """Calculate target positions for retreat moves."""
        positions = []
        
        if parsed_move.piece_type in [PieceType.CHARIOT, PieceType.CANNON, PieceType.PAWN, PieceType.KING]:
            # Linear pieces: retreat by specified distance
            direction = -1 if parsed_move.color == Color.RED else 1
            new_rank = from_pos.rank + (parsed_move.target * direction)
            if 0 <= new_rank <= 9:
                positions.append(Position(from_pos.file, new_rank))
                
        elif parsed_move.piece_type in [PieceType.HORSE, PieceType.ADVISOR, PieceType.ELEPHANT]:
            # Diagonal pieces: target indicates destination file
            target_board_file = self.parser.convert_file_to_board_coordinate(
                parsed_move.target, parsed_move.color
            )
            
            # Find valid target positions for retreat
            for rank in range(10):
                target_pos = Position(target_board_file, rank)
                if self._is_piece_movement_pattern_valid(
                    parsed_move.piece_type, from_pos, target_pos, 'retreat', parsed_move.color
                ):
                    positions.append(target_pos)
        
        return positions
    
    def _is_piece_movement_pattern_valid(self, piece_type: PieceType, from_pos: Position, 
                                       to_pos: Position, movement: str, color: Color) -> bool:
        """Check if the movement pattern is valid for the piece type."""
        if piece_type == PieceType.HORSE:
            # Horse moves in L-shape
            file_diff = abs(to_pos.file - from_pos.file)
            rank_diff = abs(to_pos.rank - from_pos.rank)
            return ((file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2))
        
        elif piece_type == PieceType.ADVISOR:
            # Advisor moves one point diagonally
            file_diff = abs(to_pos.file - from_pos.file)
            rank_diff = abs(to_pos.rank - from_pos.rank)
            return file_diff == 1 and rank_diff == 1
        
        elif piece_type == PieceType.ELEPHANT:
            # Elephant moves two points diagonally
            file_diff = abs(to_pos.file - from_pos.file)
            rank_diff = abs(to_pos.rank - from_pos.rank)
            return file_diff == 2 and rank_diff == 2
        
        return True
    
    def translate_multiple_moves(self, initial_board: XiangqiBoard, 
                               chinese_moves: List[str]) -> List[TranslationResult]:
        """
        Translate multiple moves in sequence.
        
        Args:
            initial_board: Starting board position
            chinese_moves: List of Chinese move notations
            
        Returns:
            List of TranslationResults
        """
        results = []
        current_board = initial_board.copy()
        
        for i, move in enumerate(chinese_moves):
            result = self.translate_move(current_board, move, include_board_after=True)
            results.append(result)
            
            if result.success and result.board_after_move:
                current_board = result.board_after_move
            else:
                # Stop on first error
                break
        
        return results


# Convenience functions
def translate_chinese_move(board: XiangqiBoard, chinese_move: str, 
                         include_board_after: bool = False) -> TranslationResult:
    """Convenience function to translate a single Chinese move."""
    translator = XiangqiTranslator()
    return translator.translate_move(board, chinese_move, include_board_after)


def translate_from_fen(fen: str, chinese_move: str, 
                      include_board_after: bool = False) -> TranslationResult:
    """Convenience function to translate from FEN position."""
    try:
        board = XiangqiBoard.from_fen(fen)
        return translate_chinese_move(board, chinese_move, include_board_after)
    except Exception as e:
        return TranslationResult(
            success=False,
            error_message=f"FEN格式错误: {str(e)}"
        ) 