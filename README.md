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

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

### Modern Web App (Recommended) 🔥
```bash
python app.py
```
Then open http://127.0.0.1:5000 in your browser

**Features:**
- ✨ Beautiful gradient UI with smooth GSAP animations
- 🎮 Silky smooth piece placement and flip animations
- 💫 Hover effects and visual feedback
- 🤖 Human vs Human and Human vs AI modes
- 💡 Built-in hint system with pulse animation
- 📱 Responsive design
- 🎨 Modern design (no Java GUI vibes!)

### Desktop GUI (Alternative)
```bash
python gui.py
```
- tkinter-based interface
- Good for offline use
- Easy asset swapping (add your Photoshop designs!)

### Terminal - Human vs Human
```bash
python terminal_ui.py
```

### Terminal - Human vs AI
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
├── game.py              # Core game logic
├── ai.py                # AI with Minimax + Alpha-Beta
├── gui.py               # Modern GUI (customtkinter)
├── terminal_ui.py       # Terminal: Human vs Human
├── play_vs_ai.py        # Terminal: Human vs AI
├── requirements.txt     # Python dependencies
├── ASSETS_README.md     # Guide for custom assets
└── assets/              # (optional) Your custom images
    ├── black.png
    ├── white.png
    └── board.png
```

## Custom Assets

See `ASSETS_README.md` for how to add your Photoshop designs!

The GUI will:
- Load your custom PNG assets from `assets/` folder
- Auto-resize them to fit the board
- Fall back to clean placeholders if no assets exist

Supported custom assets:
- `black.png` - Black piece design
- `white.png` - White piece design
- `board.png` - Board background texture