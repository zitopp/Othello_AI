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
        # Lightweight transposition table to cache evaluated positions
        self.tt = {}
        self.max_tt_size = 200000
        
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

        score, best_move = self.minimax(self.game.board, self.depth, player, -math.inf, math.inf, True)
        return best_move
    
    def minimax(self, board, depth, player, alpha, beta, is_maximizing):
        
        tt_key = (self._board_key(board), player, depth, is_maximizing)
        if tt_key in self.tt:
            return self.tt[tt_key]

        if depth == 0 or self.is_terminal(board):
            val = self.evaluate(board, player)
            res = (val, None)
            if len(self.tt) > self.max_tt_size:
                self.tt.clear()
            self.tt[tt_key] = res
            return res
        
        valid_moves = self.get_valid_moves_from_board(board, player)


        if valid_moves:
            wm = self.weight_matrix
            if is_maximizing:
                valid_moves.sort(key=lambda mv: wm[mv[0]][mv[1]], reverse=True)
            else:
                valid_moves.sort(key=lambda mv: wm[mv[0]][mv[1]])
        
        # No valid moves - pass turn to opponent
        if not valid_moves:
            opponent = 3 - player
            score, _ = self.minimax(board, depth - 1, opponent, alpha, beta, not is_maximizing)
            return score, None
        
        best_move = None
        is_root = (depth == self.depth)
        
        if is_maximizing:
            max_eval = -math.inf
            if is_root:
                print(f"\nevaluating {len(valid_moves)} possible moves:")
                print(f"{'move':<15} {'score':<10} {'status'}")
                print("-" * 40)
            
            for move in valid_moves:
                new_board = self.simulate_move(board, move, player)
                eval, _ = self.minimax(new_board, depth - 1, 3 - player, alpha, beta, False)
                
                status = ""
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    status = "<- best"
                
                if is_root:
                    print(f"{str(move):<15} {eval:>8.2f}  {status}")
                
                alpha = max(alpha, eval)
                if beta <= alpha:
                    if is_root:
                        print(f"{'(pruned)':<15} {'---':<10} (alpha-beta cutoff)")
                    break  # Beta cutoff
            
            res = (max_eval, best_move)
            if len(self.tt) > self.max_tt_size:
                self.tt.clear()
            self.tt[tt_key] = res
            return res
        
        else:
            min_eval = math.inf
            if is_root:
                print(f"\nevaluating {len(valid_moves)} possible moves min:")
                print(f"{'move':<15} {'score':<10} {'status'}")
                print("-" * 40)
            
            for move in valid_moves:
                new_board = self.simulate_move(board, move, player)
                eval, _ = self.minimax(new_board, depth - 1, 3 - player, alpha, beta, True)
                
                status = ""
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                    status = "<- best"
                
                if is_root:
                    print(f"{str(move):<15} {eval:>8.2f}  {status}")
                
                beta = min(beta, eval)
                if beta <= alpha:
                    if is_root:
                        print(f"{'(pruned)':<15} {'---':<10} (alpha-beta cutoff)")
                    break  # Alpha cutoff
            
            res = (min_eval, best_move)
            if len(self.tt) > self.max_tt_size:
                self.tt.clear()
            self.tt[tt_key] = res
            return res
    
    def evaluate(self, board, player):
        """
        Evaluate the board using the scientifically derived weight matrix.
        The matrix already encodes all strategic knowledge (corners, edges, etc.)
        """
        opponent = 3 - player
        score = 0.0
        wm = self.weight_matrix
        for i in range(8):
            br = board[i]
            wmr = wm[i]
            for j in range(8):
                v = br[j]
                if v == player:
                    score += wmr[j]
                elif v == opponent:
                    score -= wmr[j]
        return score
    
    def is_terminal(self, board):
        """Check if game is over - uses fast adjacency scan"""
        return not (OthelloGame.has_any_move_on_board(board, 1) or OthelloGame.has_any_move_on_board(board, 2))
    
    def get_valid_moves_from_board(self, board, player):
        """Get valid moves from a board state - uses static game method"""
        return OthelloGame.get_valid_moves_on_board(board, player)
    
    def simulate_move(self, board, move, player):
        """Simulate a move and return new board state - uses static game method"""
        row, col = move
        return OthelloGame.simulate_move_on_board(board, row, col, player)

    def _board_key(self, board):
        # Compact 64-byte key for the transposition table
        return bytes(board[i][j] for i in range(8) for j in range(8))
