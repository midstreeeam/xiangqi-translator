"""
Xiangqi board representation and piece definitions.
"""

from enum import Enum
from typing import List, Optional, Dict, Tuple, Union
import re


class Color(Enum):
    RED = "red"
    BLACK = "black"


class PieceType(Enum):
    KING = "king"      # 帅/将
    ADVISOR = "advisor"  # 仕/士  
    ELEPHANT = "elephant"  # 相/象
    HORSE = "horse"    # 马
    CHARIOT = "chariot"  # 车
    CANNON = "cannon"  # 炮/砲
    PAWN = "pawn"      # 兵/卒


class Piece:
    """Represents a xiangqi piece."""
    
    def __init__(self, piece_type: PieceType, color: Color):
        self.piece_type = piece_type
        self.color = color
    
    def __str__(self):
        """String representation for FEN notation."""
        char_map = {
            (PieceType.KING, Color.RED): 'K',
            (PieceType.KING, Color.BLACK): 'k',
            (PieceType.ADVISOR, Color.RED): 'A',
            (PieceType.ADVISOR, Color.BLACK): 'a',
            (PieceType.ELEPHANT, Color.RED): 'B',
            (PieceType.ELEPHANT, Color.BLACK): 'b',
            (PieceType.HORSE, Color.RED): 'N',
            (PieceType.HORSE, Color.BLACK): 'n',
            (PieceType.CHARIOT, Color.RED): 'R',
            (PieceType.CHARIOT, Color.BLACK): 'r',
            (PieceType.CANNON, Color.RED): 'C',
            (PieceType.CANNON, Color.BLACK): 'c',
            (PieceType.PAWN, Color.RED): 'P',
            (PieceType.PAWN, Color.BLACK): 'p',
        }
        return char_map[(self.piece_type, self.color)]
    
    @classmethod
    def from_char(cls, char: str) -> Optional['Piece']:
        """Create piece from FEN character."""
        char_map = {
            'K': (PieceType.KING, Color.RED),
            'k': (PieceType.KING, Color.BLACK),
            'A': (PieceType.ADVISOR, Color.RED),
            'a': (PieceType.ADVISOR, Color.BLACK),
            'B': (PieceType.ELEPHANT, Color.RED),
            'b': (PieceType.ELEPHANT, Color.BLACK),
            'N': (PieceType.HORSE, Color.RED),
            'n': (PieceType.HORSE, Color.BLACK),
            'R': (PieceType.CHARIOT, Color.RED),
            'r': (PieceType.CHARIOT, Color.BLACK),
            'C': (PieceType.CANNON, Color.RED),
            'c': (PieceType.CANNON, Color.BLACK),
            'P': (PieceType.PAWN, Color.RED),
            'p': (PieceType.PAWN, Color.BLACK),
        }
        if char in char_map:
            piece_type, color = char_map[char]
            return cls(piece_type, color)
        return None
    
    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.piece_type == other.piece_type and self.color == other.color


class Position:
    """Represents a position on the xiangqi board."""
    
    def __init__(self, file: int, rank: int):
        """
        Args:
            file: 0-8 (a-i)
            rank: 0-9 (0 is red side, 9 is black side)
        """
        self.file = file
        self.rank = rank
    
    def __str__(self):
        """Convert to ICCS coordinate notation (e.g., 'a0', 'i9')."""
        file_char = chr(ord('a') + self.file)
        return f"{file_char}{self.rank}"
    
    @classmethod
    def from_string(cls, pos_str: str) -> 'Position':
        """Create position from ICCS string like 'a0', 'i9'."""
        file = ord(pos_str[0]) - ord('a')
        rank = int(pos_str[1])
        return cls(file, rank)
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.file == other.file and self.rank == other.rank
    
    def __hash__(self):
        return hash((self.file, self.rank))


class XiangqiBoard:
    """Represents a xiangqi board state."""
    
    def __init__(self):
        # 9x10 board: files a-i (0-8), ranks 0-9
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(9)] for _ in range(10)]
        self.active_color = Color.RED
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
    def get_piece(self, pos: Position) -> Optional[Piece]:
        """Get piece at position."""
        return self.board[pos.rank][pos.file]
    
    def set_piece(self, pos: Position, piece: Optional[Piece]):
        """Set piece at position."""
        self.board[pos.rank][pos.file] = piece
    
    def move_piece(self, from_pos: Position, to_pos: Position) -> Optional[Piece]:
        """Move piece from one position to another. Returns captured piece if any."""
        piece = self.get_piece(from_pos)
        captured = self.get_piece(to_pos)
        
        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)
        
        return captured
    
    def is_within_palace(self, pos: Position, color: Color) -> bool:
        """Check if position is within the palace for given color."""
        if color == Color.RED:
            return 3 <= pos.file <= 5 and 0 <= pos.rank <= 2
        else:  # BLACK
            return 3 <= pos.file <= 5 and 7 <= pos.rank <= 9
    
    def is_within_territory(self, pos: Position, color: Color) -> bool:
        """Check if position is within the territory (same side of river) for given color."""
        if color == Color.RED:
            return 0 <= pos.rank <= 4
        else:  # BLACK
            return 5 <= pos.rank <= 9
    
    def to_fen(self) -> str:
        """Convert board to FEN notation."""
        fen_parts = []
        
        # Board position (from rank 9 to 0, black to red)
        for rank in range(9, -1, -1):
            rank_str = ""
            empty_count = 0
            
            for file in range(9):
                piece = self.board[rank][file]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    rank_str += str(piece)
            
            if empty_count > 0:
                rank_str += str(empty_count)
            
            fen_parts.append(rank_str)
        
        board_fen = "/".join(fen_parts)
        
        # Active color
        color_char = "w" if self.active_color == Color.RED else "b"
        
        # Castling availability (not applicable in xiangqi)
        castling = "-"
        
        # En passant (not applicable in xiangqi)
        en_passant = "-"
        
        # Halfmove clock and fullmove number
        return f"{board_fen} {color_char} {castling} {en_passant} {self.halfmove_clock} {self.fullmove_number}"
    
    @classmethod
    def from_fen(cls, fen: str) -> 'XiangqiBoard':
        """Create board from FEN notation."""
        parts = fen.strip().split()
        if len(parts) < 4:
            raise ValueError("Invalid FEN string")
        
        board = cls()
        
        # Parse board position
        ranks = parts[0].split("/")
        if len(ranks) != 10:
            raise ValueError("Invalid board in FEN - must have 10 ranks")
        
        for rank_idx, rank_str in enumerate(ranks):
            rank = 9 - rank_idx  # FEN goes from black side (rank 9) to red side (rank 0)
            file = 0
            
            for char in rank_str:
                if char.isdigit():
                    file += int(char)  # Empty squares
                else:
                    piece = Piece.from_char(char)
                    if piece:
                        board.set_piece(Position(file, rank), piece)
                    file += 1
        
        # Parse active color
        if len(parts) > 1:
            board.active_color = Color.RED if parts[1] == "w" else Color.BLACK
        
        # Parse halfmove clock and fullmove number
        if len(parts) > 4:
            board.halfmove_clock = int(parts[4])
        if len(parts) > 5:
            board.fullmove_number = int(parts[5])
        
        return board
    
    @classmethod
    def initial_position(cls) -> 'XiangqiBoard':
        """Create board with initial xiangqi position."""
        fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        return cls.from_fen(fen)
    
    def copy(self) -> 'XiangqiBoard':
        """Create a copy of the board."""
        return XiangqiBoard.from_fen(self.to_fen())
    
    def __str__(self):
        """String representation of the board."""
        lines = []
        for rank in range(9, -1, -1):
            line = f"{rank} "
            for file in range(9):
                piece = self.board[rank][file]
                line += str(piece) if piece else "."
                line += " "
            lines.append(line)
        
        lines.append("  a b c d e f g h i")
        return "\n".join(lines) 