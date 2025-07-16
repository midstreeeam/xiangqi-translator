"""
Chinese xiangqi move notation parser.
Handles traditional Chinese notation like "马八进二" (Horse from 8th file advances 2 points).
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from .board import Color, PieceType


# Chinese piece names mapping
CHINESE_PIECES = {
    # Red pieces (traditional characters)
    '帅': PieceType.KING,
    '仕': PieceType.ADVISOR,
    '相': PieceType.ELEPHANT,
    '马': PieceType.HORSE,
    '车': PieceType.CHARIOT,
    '炮': PieceType.CANNON,
    '兵': PieceType.PAWN,
    
    # Black pieces (traditional characters)
    '将': PieceType.KING,
    '士': PieceType.ADVISOR,
    '象': PieceType.ELEPHANT,
    # 马, 车 are same for both colors
    '砲': PieceType.CANNON,  # Alternative cannon character
    '卒': PieceType.PAWN,
}

# Chinese numbers for files and positions
CHINESE_NUMBERS = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9,
    '１': 1, '２': 2, '３': 3, '４': 4, '５': 5,
    '６': 6, '７': 7, '８': 8, '９': 9,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9,
}

# Movement direction indicators
MOVEMENT_INDICATORS = {
    '进': 'advance',
    '退': 'retreat', 
    '平': 'traverse',
}

# Alternative movement indicators
MOVEMENT_INDICATORS.update({
    '上': 'advance',  # Up (for black pieces, this means advance)
    '下': 'retreat',  # Down
    '横': 'traverse',  # Horizontal
})


@dataclass
class ParsedMove:
    """Represents a parsed Chinese move notation."""
    piece_type: PieceType
    color: Color
    source_file: int  # 1-9 (Chinese notation)
    movement: str  # 'advance', 'retreat', 'traverse'
    target: int  # Target file (for traverse) or distance (for advance/retreat)
    is_front: Optional[bool] = None  # For disambiguating pieces in tandem (前/后)
    is_middle: Optional[bool] = None  # For middle piece in three pieces tandem (中)


class ChineseNotationParser:
    """Parser for Chinese xiangqi move notation."""
    
    def __init__(self):
        # Pattern for standard move notation: 马八进二
        self.standard_pattern = re.compile(
            r'([帅仕相马车炮兵将士象砲卒])([一二三四五六七八九１２３４５６７８９123456789])([进退平上下横])([一二三四五六七八九１２３４５６７８９123456789])'
        )
        
        # Pattern with front/back disambiguation: 前马进二
        self.disambig_pattern = re.compile(
            r'([前后中])([帅仕相马车炮兵将士象砲卒])([进退平上下横])([一二三四五六七八九１２３４５６７８９123456789])'
        )
    
    def parse_move(self, move_str: str, color: Color) -> Optional[ParsedMove]:
        """
        Parse Chinese move notation.
        
        Args:
            move_str: Chinese move notation like "马八进二"
            color: Color of the moving player
            
        Returns:
            ParsedMove object or None if parsing fails
        """
        move_str = move_str.strip()
        
        # Try disambiguated pattern first (前马进二, 后车退一)
        match = self.disambig_pattern.match(move_str)
        if match:
            disambig, piece_char, movement_char, target_char = match.groups()
            
            piece_type = CHINESE_PIECES.get(piece_char)
            if not piece_type:
                return None
                
            movement = MOVEMENT_INDICATORS.get(movement_char)
            if not movement:
                return None
                
            target = CHINESE_NUMBERS.get(target_char)
            if target is None:
                return None
                
            is_front = None
            is_middle = None
            if disambig == '前':
                is_front = True
            elif disambig == '后':
                is_front = False
            elif disambig == '中':
                is_middle = True
                
            return ParsedMove(
                piece_type=piece_type,
                color=color,
                source_file=0,  # Will be determined later
                movement=movement,
                target=target,
                is_front=is_front,
                is_middle=is_middle
            )
        
        # Try standard pattern (马八进二)
        match = self.standard_pattern.match(move_str)
        if match:
            piece_char, source_char, movement_char, target_char = match.groups()
            
            piece_type = CHINESE_PIECES.get(piece_char)
            if not piece_type:
                return None
                
            source_file = CHINESE_NUMBERS.get(source_char)
            if source_file is None:
                return None
                
            movement = MOVEMENT_INDICATORS.get(movement_char)
            if not movement:
                return None
                
            target = CHINESE_NUMBERS.get(target_char)
            if target is None:
                return None
                
            return ParsedMove(
                piece_type=piece_type,
                color=color,
                source_file=source_file,
                movement=movement,
                target=target
            )
        
        return None
    
    def convert_file_to_board_coordinate(self, chinese_file: int, color: Color) -> int:
        """
        Convert Chinese file number (1-9) to board file coordinate (0-8).
        In Chinese notation, files are numbered 1-9 from right to left for each player.
        
        Args:
            chinese_file: Chinese file number (1-9)
            color: Player color
            
        Returns:
            Board file coordinate (0-8)
        """
        if color == Color.RED:
            # For Red: file 1 = board file 8, file 9 = board file 0
            return 9 - chinese_file
        else:
            # For Black: file 1 = board file 0, file 9 = board file 8
            return chinese_file - 1
    
    def convert_board_coordinate_to_file(self, board_file: int, color: Color) -> int:
        """
        Convert board file coordinate (0-8) to Chinese file number (1-9).
        
        Args:
            board_file: Board file coordinate (0-8)
            color: Player color
            
        Returns:
            Chinese file number (1-9)
        """
        if color == Color.RED:
            # For Red: board file 0 = file 9, board file 8 = file 1
            return 9 - board_file
        else:
            # For Black: board file 0 = file 1, board file 8 = file 9
            return board_file + 1
    
    def is_valid_move_notation(self, move_str: str) -> bool:
        """Check if the move string is valid Chinese notation."""
        return (self.standard_pattern.match(move_str) is not None or 
                self.disambig_pattern.match(move_str) is not None)


# Convenience functions
def parse_chinese_move(move_str: str, color: Color) -> Optional[ParsedMove]:
    """Parse Chinese move notation string."""
    parser = ChineseNotationParser()
    return parser.parse_move(move_str, color)


def convert_chinese_file_to_coordinate(chinese_file: int, color: Color) -> int:
    """Convert Chinese file number to board coordinate."""
    parser = ChineseNotationParser()
    return parser.convert_file_to_board_coordinate(chinese_file, color)


def convert_coordinate_to_chinese_file(board_file: int, color: Color) -> int:
    """Convert board coordinate to Chinese file number."""
    parser = ChineseNotationParser()
    return parser.convert_board_coordinate_to_file(board_file, color) 