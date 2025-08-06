# Xiangqi Translator

A Python library that converts Chinese xiangqi (Chinese chess) move notation to Pikafish-compatible ICCS (International Computer Chess Correspondence) format.

## Features

- ✅ Translate Chinese notation (like "炮二平五") to ICCS format (like "h2e2")
- ✅ Support for all xiangqi pieces and move types
- ✅ Ambiguity detection and disambiguation (前/后/中)
- ✅ Move validation according to xiangqi rules
- ✅ Board state tracking and FEN support
- ✅ High performance (1000+ translations per second)
- ✅ Pure Python with no external dependencies

## Installation

```bash
# Install from source
git clone https://github.com/midstreeeam/xiangqi-translator.git
cd xiangqi-translator
pip install -e .

# Or install development dependencies
pip install -r requirements-dev.txt
```

## Quick Start

```python
from xiangqi_translator import translate_from_fen, get_initial_board

# Get initial board position
board = get_initial_board()
fen = board.to_fen()

# Translate Chinese move to ICCS
result = translate_from_fen(fen, "炮二平五")
print(f"Chinese move: 炮二平五")
print(f"ICCS move: {result.iccs_move}")  # h2e2
print(f"Success: {result.success}")      # True
```

## Usage Examples

See `examples/basic_usage.py` for comprehensive usage examples.

## Testing

```bash
# Quick test
python test.py

# Run all tests with pytest (if installed)
python -m pytest tests/ -v

# Run tests directly
python tests/test_xiangqi_translator.py
python tests/test_ambiguous_moves.py

# Run examples
python examples/basic_usage.py
```

## Project Structure

```
xiangqi-translator/
├── src/xiangqi_translator/    # Main package code
├── tests/                     # Test files
├── examples/                  # Usage examples
├── pyproject.toml            # Package configuration
├── requirements-dev.txt      # Development dependencies
└── README.md                 # This file
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 src/

# Run tests
python -m pytest tests/

# Build package
python -m build
```

## License

See LICENSE file for details.
