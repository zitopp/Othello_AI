# Othello AI Game

A complete Othello (Reversi) game implementation with AI opponent using Minimax algorithm with Alpha-Beta pruning.

## Features

- **Game Logic**: Full Othello rules implementation
- **AI Player**: Minimax algorithm with Alpha-Beta pruning
- **Multiple Difficulty Levels**: Easy, Medium, Hard
- **Evaluation Heuristics**:
  - Positional scoring (corners, edges)
  - Mobility (number of valid moves)
  - Coin parity (piece count)
  - Corner occupancy
- **Terminal Interface**: Play in console
- **Random Starting Player**: Either Black or White can start

## How to Play

### Human vs Human
```bash
python terminal_ui.py
```

### Human vs AI
```bash
python play_vs_ai.py
```

Choose difficulty, color, and start playing!

## Game Rules

- 8x8 board
- Black (B) and White (W) players
- Place pieces to flip opponent pieces
- Game ends when neither player has valid moves
- Winner is the player with most pieces

## AI Implementation

The AI uses:
- **Minimax** with **Alpha-Beta pruning** for efficient search
- **Multi-factor evaluation**:
  - Weight matrix for strategic positions
  - Mobility analysis
  - Corner control
  - Piece count
  
Depth levels:
- Easy: 2 moves ahead
- Medium: 4 moves ahead
- Hard: 6 moves ahead

## Project Structure

```
Othello_AI/
├── game.py          # Core game logic
├── ai.py            # AI implementation
├── terminal_ui.py   # Human vs Human
├── play_vs_ai.py    # Human vs AI
└── gui.py           # GUI (coming soon)
```