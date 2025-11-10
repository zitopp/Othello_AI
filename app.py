# Flask Backend for Othello
from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import secrets
from game import OthelloGame
from ai import OthelloAI

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Store game sessions
games = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Create a new game"""
    data = request.json
    game_mode = data.get('mode', 'pvp')  # 'pvp' or 'ai'
    difficulty = data.get('difficulty', 4)
    human_player = data.get('human_player', 1)
    
    # Generate unique game ID
    game_id = secrets.token_urlsafe(16)
    
    # Create game
    game = OthelloGame()
    
    # Store game state
    games[game_id] = {
        'game': game,
        'mode': game_mode,
        'ai': OthelloAI(game, difficulty=difficulty) if game_mode == 'ai' else None,
        'human_player': human_player,
        'ai_player': 3 - human_player if game_mode == 'ai' else None
    }
    
    return jsonify({
        'game_id': game_id,
        'board': game.board,
        'current_player': game.current_player,
        'valid_moves': game.get_valid_moves(game.current_player),
        'score': get_score(game)
    })

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Get current game state"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'valid_moves': game.get_valid_moves(game.current_player),
        'score': get_score(game),
        'game_over': game.is_game_over(),
        'winner': game.get_winner() if game.is_game_over() else None
    })

@app.route('/api/move/<game_id>', methods=['POST'])
def make_move(game_id):
    """Make a move"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Get flipped pieces BEFORE applying the move so we can animate correctly on the frontend
    flipped = get_flipped_pieces(game, row, col, game.current_player)
    
    # Make move (mutates board)
    if not game.make_move(row, col, game.current_player):
        return jsonify({'error': 'Invalid move'}), 400
    
    # Switch player
    old_player = game.current_player
    game.current_player = 3 - game.current_player
    
    # Check if new player has moves
    valid_moves = game.get_valid_moves(game.current_player)
    skipped = False
    
    if not valid_moves and not game.is_game_over():
        # Skip turn
        game.current_player = 3 - game.current_player
        valid_moves = game.get_valid_moves(game.current_player)
        skipped = True
    
    return jsonify({
        'success': True,
        'board': game.board,
        'current_player': game.current_player,
        'valid_moves': valid_moves,
        'score': get_score(game),
        'game_over': game.is_game_over(),
        'winner': game.get_winner() if game.is_game_over() else None,
        'flipped': flipped,
        'skipped': skipped
    })

@app.route('/api/ai_move/<game_id>', methods=['POST'])
def ai_move(game_id):
    """Get AI move"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    ai = game_data['ai']
    
    if not ai:
        return jsonify({'error': 'No AI in this game'}), 400
    
    # Get AI move
    move = ai.get_best_move(game.current_player)
    
    if not move:
        return jsonify({'error': 'AI has no moves'}), 400
    
    row, col = move
    
    # Compute flipped pieces BEFORE mutating the board for proper animation
    flipped = get_flipped_pieces(game, row, col, game.current_player)
    
    # Make move (mutates board)
    game.make_move(row, col, game.current_player)
    
    # Switch player
    game.current_player = 3 - game.current_player
    
    # Check if new player has moves
    valid_moves = game.get_valid_moves(game.current_player)
    skipped = False
    
    if not valid_moves and not game.is_game_over():
        # Skip turn
        game.current_player = 3 - game.current_player
        valid_moves = game.get_valid_moves(game.current_player)
        skipped = True
    
    return jsonify({
        'success': True,
        'move': {'row': row, 'col': col},
        'board': game.board,
        'current_player': game.current_player,
        'valid_moves': valid_moves,
        'score': get_score(game),
        'game_over': game.is_game_over(),
        'winner': game.get_winner() if game.is_game_over() else None,
        'flipped': flipped,
        'skipped': skipped
    })

@app.route('/api/hint/<game_id>', methods=['GET'])
def get_hint(game_id):
    """Get hint for current player"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = games[game_id]
    game = game_data['game']
    
    # Create temporary AI
    temp_ai = OthelloAI(game, difficulty=4)
    hint = temp_ai.get_best_move(game.current_player)
    
    if not hint:
        return jsonify({'error': 'No moves available'}), 400
    
    return jsonify({
        'hint': {'row': hint[0], 'col': hint[1]}
    })

def get_score(game):
    """Get current score"""
    black = sum(row.count(1) for row in game.board)
    white = sum(row.count(2) for row in game.board)
    return {'black': black, 'white': white}

def get_flipped_pieces(game, row, col, player):
    """Get list of pieces that were flipped (for animation)"""
    # This is a helper to track flipped pieces
    # We'll reconstruct from the move logic
    flipped = []
    opponent = 3 - player
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for dr, dc in directions:
        r, c = row + dr, col + dc
        temp_flipped = []
        
        while 0 <= r < 8 and 0 <= c < 8:
            if game.board[r][c] == opponent:
                temp_flipped.append([r, c])
            elif game.board[r][c] == player:
                flipped.extend(temp_flipped)
                break
            else:
                break
            r += dr
            c += dc
    
    return flipped

if __name__ == '__main__':
    app.run(debug=True, port=5000)
