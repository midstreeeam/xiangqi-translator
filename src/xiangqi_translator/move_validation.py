"""
Xiangqi move validation logic.
Implements all the rules for legal moves in xiangqi.
"""

from typing import List, Optional, Tuple, Set
from .board import XiangqiBoard, Position, Piece, Color, PieceType


class MoveValidator:
    """Validates xiangqi moves according to game rules."""
    
    def __init__(self, board: XiangqiBoard):
        self.board = board
    
    def is_valid_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if a move from one position to another is valid."""
        # Basic bounds checking
        if not self._is_position_valid(from_pos) or not self._is_position_valid(to_pos):
            return False
        
        piece = self.board.get_piece(from_pos)
        if not piece:
            return False
        
        # Can't capture own piece
        target_piece = self.board.get_piece(to_pos)
        if target_piece and target_piece.color == piece.color:
            return False
        
        # Check piece-specific movement rules
        if not self._is_piece_move_valid(piece, from_pos, to_pos):
            return False
        
        # Check if move puts own king in check
        if self._would_move_expose_king(from_pos, to_pos):
            return False
        
        return True
    
    def _is_position_valid(self, pos: Position) -> bool:
        """Check if position is within board bounds."""
        return 0 <= pos.file <= 8 and 0 <= pos.rank <= 9
    
    def _is_piece_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Check if piece can legally move from one position to another."""
        if piece.piece_type == PieceType.KING:
            return self._is_king_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.ADVISOR:
            return self._is_advisor_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.ELEPHANT:
            return self._is_elephant_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.HORSE:
            return self._is_horse_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.CHARIOT:
            return self._is_chariot_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.CANNON:
            return self._is_cannon_move_valid(piece, from_pos, to_pos)
        elif piece.piece_type == PieceType.PAWN:
            return self._is_pawn_move_valid(piece, from_pos, to_pos)
        return False
    
    def _is_king_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate king movement."""
        # Must stay within palace
        if not self.board.is_within_palace(to_pos, piece.color):
            return False
        
        # Can only move one step orthogonally
        file_diff = abs(to_pos.file - from_pos.file)
        rank_diff = abs(to_pos.rank - from_pos.rank)
        
        if not ((file_diff == 1 and rank_diff == 0) or (file_diff == 0 and rank_diff == 1)):
            return False
        
        # Check for flying king rule (kings cannot face each other)
        if self._would_kings_face_each_other(from_pos, to_pos):
            return False
        
        return True
    
    def _is_advisor_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate advisor movement."""
        # Must stay within palace
        if not self.board.is_within_palace(to_pos, piece.color):
            return False
        
        # Can only move one step diagonally
        file_diff = abs(to_pos.file - from_pos.file)
        rank_diff = abs(to_pos.rank - from_pos.rank)
        
        return file_diff == 1 and rank_diff == 1
    
    def _is_elephant_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate elephant movement."""
        # Must stay on own side of river
        if not self.board.is_within_territory(to_pos, piece.color):
            return False
        
        # Must move exactly two points diagonally
        file_diff = to_pos.file - from_pos.file
        rank_diff = to_pos.rank - from_pos.rank
        
        if abs(file_diff) != 2 or abs(rank_diff) != 2:
            return False
        
        # Check blocking point (elephant eye)
        block_file = from_pos.file + file_diff // 2
        block_rank = from_pos.rank + rank_diff // 2
        block_pos = Position(block_file, block_rank)
        
        return self.board.get_piece(block_pos) is None
    
    def _is_horse_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate horse movement."""
        file_diff = to_pos.file - from_pos.file
        rank_diff = to_pos.rank - from_pos.rank
        
        # Horse moves in L-shape: 2+1 or 1+2
        if not ((abs(file_diff) == 2 and abs(rank_diff) == 1) or 
                (abs(file_diff) == 1 and abs(rank_diff) == 2)):
            return False
        
        # Check horse leg (blocking point)
        if abs(file_diff) == 2:
            # Moving horizontally first
            block_file = from_pos.file + file_diff // 2
            block_rank = from_pos.rank
        else:
            # Moving vertically first
            block_file = from_pos.file
            block_rank = from_pos.rank + rank_diff // 2
        
        block_pos = Position(block_file, block_rank)
        return self.board.get_piece(block_pos) is None
    
    def _is_chariot_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate chariot movement."""
        # Must move in straight line (orthogonally)
        if from_pos.file != to_pos.file and from_pos.rank != to_pos.rank:
            return False
        
        # Check path is clear
        return self._is_path_clear(from_pos, to_pos)
    
    def _is_cannon_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate cannon movement."""
        # Must move in straight line (orthogonally)
        if from_pos.file != to_pos.file and from_pos.rank != to_pos.rank:
            return False
        
        target_piece = self.board.get_piece(to_pos)
        
        if target_piece is None:
            # Non-capturing move: path must be clear
            return self._is_path_clear(from_pos, to_pos)
        else:
            # Capturing move: must have exactly one piece between source and target
            return self._count_pieces_between(from_pos, to_pos) == 1
    
    def _is_pawn_move_valid(self, piece: Piece, from_pos: Position, to_pos: Position) -> bool:
        """Validate pawn movement."""
        file_diff = to_pos.file - from_pos.file
        rank_diff = to_pos.rank - from_pos.rank
        
        # Pawn can only move one step
        if abs(file_diff) + abs(rank_diff) != 1:
            return False
        
        # Check direction based on color and position
        if piece.color == Color.RED:
            # Red pawns move up (increasing rank)
            if rank_diff < 0:
                return False
            
            # Before crossing river, can only move forward
            if from_pos.rank < 5 and file_diff != 0:
                return False
        else:
            # Black pawns move down (decreasing rank) 
            if rank_diff > 0:
                return False
            
            # Before crossing river, can only move forward
            if from_pos.rank > 4 and file_diff != 0:
                return False
        
        return True
    
    def _is_path_clear(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if path between two positions is clear of pieces."""
        file_step = 0 if from_pos.file == to_pos.file else (1 if to_pos.file > from_pos.file else -1)
        rank_step = 0 if from_pos.rank == to_pos.rank else (1 if to_pos.rank > from_pos.rank else -1)
        
        current_file = from_pos.file + file_step
        current_rank = from_pos.rank + rank_step
        
        while current_file != to_pos.file or current_rank != to_pos.rank:
            if self.board.get_piece(Position(current_file, current_rank)) is not None:
                return False
            current_file += file_step
            current_rank += rank_step
        
        return True
    
    def _count_pieces_between(self, from_pos: Position, to_pos: Position) -> int:
        """Count pieces between two positions (exclusive of endpoints)."""
        file_step = 0 if from_pos.file == to_pos.file else (1 if to_pos.file > from_pos.file else -1)
        rank_step = 0 if from_pos.rank == to_pos.rank else (1 if to_pos.rank > from_pos.rank else -1)
        
        count = 0
        current_file = from_pos.file + file_step
        current_rank = from_pos.rank + rank_step
        
        while current_file != to_pos.file or current_rank != to_pos.rank:
            if self.board.get_piece(Position(current_file, current_rank)) is not None:
                count += 1
            current_file += file_step
            current_rank += rank_step
        
        return count
    
    def _would_kings_face_each_other(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if move would result in kings facing each other."""
        # Create a temporary board state
        temp_board = self.board.copy()
        temp_board.move_piece(from_pos, to_pos)
        
        # Find both kings
        red_king_pos = None
        black_king_pos = None
        
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = temp_board.get_piece(pos)
                if piece and piece.piece_type == PieceType.KING:
                    if piece.color == Color.RED:
                        red_king_pos = pos
                    else:
                        black_king_pos = pos
        
        if not red_king_pos or not black_king_pos:
            return False
        
        # Check if kings are on same file
        if red_king_pos.file != black_king_pos.file:
            return False
        
        # Check if there are no pieces between kings
        validator = MoveValidator(temp_board)
        return validator._is_path_clear(red_king_pos, black_king_pos)
    
    def _would_move_expose_king(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if move would expose own king to check."""
        # Create temporary board state
        temp_board = self.board.copy()
        moving_piece = temp_board.get_piece(from_pos)
        temp_board.move_piece(from_pos, to_pos)
        
        # Find own king
        king_pos = None
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = temp_board.get_piece(pos)
                if (piece and piece.piece_type == PieceType.KING and 
                    piece.color == moving_piece.color):
                    king_pos = pos
                    break
        
        if not king_pos:
            return False
        
        # Check if any enemy piece can attack the king
        validator = MoveValidator(temp_board)
        enemy_color = Color.BLACK if moving_piece.color == Color.RED else Color.RED
        
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = temp_board.get_piece(pos)
                if piece and piece.color == enemy_color:
                    if validator._is_piece_move_valid(piece, pos, king_pos):
                        return True
        
        return False
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the given color's king is in check."""
        # Find the king
        king_pos = None
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = self.board.get_piece(pos)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    king_pos = pos
                    break
        
        if not king_pos:
            return False
        
        # Check if any enemy piece can attack the king
        enemy_color = Color.BLACK if color == Color.RED else Color.RED
        
        for rank in range(10):
            for file in range(9):
                pos = Position(file, rank)
                piece = self.board.get_piece(pos)
                if piece and piece.color == enemy_color:
                    if self._is_piece_move_valid(piece, pos, king_pos):
                        return True
        
        return False
    
    def get_legal_moves(self, color: Color) -> List[Tuple[Position, Position]]:
        """Get all legal moves for the given color."""
        legal_moves = []
        
        for rank in range(10):
            for file in range(9):
                from_pos = Position(file, rank)
                piece = self.board.get_piece(from_pos)
                
                if piece and piece.color == color:
                    # Try all possible destination squares
                    for to_rank in range(10):
                        for to_file in range(9):
                            to_pos = Position(to_file, to_rank)
                            if self.is_valid_move(from_pos, to_pos):
                                legal_moves.append((from_pos, to_pos))
        
        return legal_moves
    
    def is_checkmate(self, color: Color) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        
        return len(self.get_legal_moves(color)) == 0
    
    def is_stalemate(self, color: Color) -> bool:
        """Check if the given color is in stalemate."""
        if self.is_in_check(color):
            return False
        
        return len(self.get_legal_moves(color)) == 0 