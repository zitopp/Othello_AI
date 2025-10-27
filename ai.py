# AI for Othello using Minimax with Alpha-Beta Pruning
import math
from game import OthelloGame

class OthelloAI:
    def __init__(self, game, difficulty=4):
        """
        Initialize the AI
        game: OthelloGame instance
        difficulty: search depth (higher = stronger but slower)
        """
        self.game = game
        self.depth = difficulty
        
        # Position weight matrix (scientifically derived values)
        self.weight_matrix = [
            [16.16, -3.03,  0.99,  0.43,  0.43,  0.99, -3.03, 16.16],
            [-4.12, -1.81, -0.08, -0.27, -0.27, -0.08, -1.81, -4.12],
            [ 1.33, -0.04,  0.51,  0.07,  0.07,  0.51, -0.04,  1.33],
            [ 0.63, -0.18, -0.04, -0.01, -0.01, -0.04, -0.18,  0.63],
            [ 0.63, -0.18, -0.04, -0.01, -0.01, -0.04, -0.18,  0.63],
            [ 1.33, -0.04,  0.51,  0.07,  0.07,  0.51, -0.04,  1.33],
            [-4.12, -1.81, -0.08, -0.27, -0.27, -0.08, -1.81, -4.12],
            [16.16, -3.03,  0.99,  0.43,  0.43,  0.99, -3.03, 16.16]
        ]
    
    def get_best_move(self, player):
        """Get the best move for the given player using minimax"""
        _, best_move = self.minimax(self.game.board, self.depth, player, -math.inf, math.inf, True)
        return best_move
    
    def minimax(self, board, depth, player, alpha, beta, is_maximizing):
        """
        Minimax with alpha-beta pruning
        
        board: current board state
        depth: remaining search depth
        player: current player (1 or 2)
        alpha: best value for maximizer
        beta: best value for minimizer
        is_maximizing: True if maximizing player
        """
        # Base case: depth 0 or game over
        if depth == 0 or self.is_terminal(board):
            return self.evaluate(board, player), None
        
        valid_moves = self.get_valid_moves_from_board(board, player)
        
        # No valid moves - pass turn to opponent
        if not valid_moves:
            opponent = 3 - player
            score, _ = self.minimax(board, depth - 1, opponent, alpha, beta, not is_maximizing)
            return score, None
        
        best_move = None
        
        if is_maximizing:
            max_eval = -math.inf
            for move in valid_moves:
                new_board = self.simulate_move(board, move, player)
                eval, _ = self.minimax(new_board, depth - 1, 3 - player, alpha, beta, False)
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval, best_move
        
        else:
            min_eval = math.inf
            for move in valid_moves:
                new_board = self.simulate_move(board, move, player)
                eval, _ = self.minimax(new_board, depth - 1, 3 - player, alpha, beta, True)
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval, best_move
    
    def evaluate(self, board, player):
        """
        Evaluate the board using the scientifically derived weight matrix.
        The matrix already encodes all strategic knowledge (corners, edges, etc.)
        """
        opponent = 3 - player
        score = 0
        
        for i in range(8):
            for j in range(8):
                if board[i][j] == player:
                    score += self.weight_matrix[i][j]
                elif board[i][j] == opponent:
                    score -= self.weight_matrix[i][j]
        
        return score
    
    def is_terminal(self, board):
        """Check if game is over - uses static game methods"""
        player1_moves = OthelloGame.get_valid_moves_on_board(board, 1)
        player2_moves = OthelloGame.get_valid_moves_on_board(board, 2)
        return len(player1_moves) == 0 and len(player2_moves) == 0
    
    def get_valid_moves_from_board(self, board, player):
        """Get valid moves from a board state - uses static game method"""
        return OthelloGame.get_valid_moves_on_board(board, player)
    
    def simulate_move(self, board, move, player):
        """Simulate a move and return new board state - uses static game method"""
        row, col = move
        return OthelloGame.simulate_move_on_board(board, row, col, player)
