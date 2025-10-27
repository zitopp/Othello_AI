# Othello Game Logic
# This file contains the core game mechanics

import random

class OthelloGame:
    def __init__(self):
        # Create an 8x8 board (0 = empty, 1 = black, 2 = white)
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        # Starting position: 2 white and 2 black pieces in the center
        self.board[3][3] = 2  # White
        self.board[3][4] = 1  # Black
        self.board[4][3] = 1  # Black
        self.board[4][4] = 2  # White
        self.current_player = 1  # Black always starts (standard Othello rule)
    
    def print_board(self):
        """Display the board in the terminal"""
        print("\n  0 1 2 3 4 5 6 7")
        for i in range(8):
            print(i, end=' ')
            for j in range(8):
                if self.board[i][j] == 0:
                    print('.', end=' ')
                elif self.board[i][j] == 1:
                    print('B', end=' ')  # Black
                else:
                    print('W', end=' ')  # White
            print()
    
    def is_valid_move(self, row, col, player):
        """Check if a move is valid for the given player"""
        # Square must be empty
        if self.board[row][col] != 0:
            return False
        
        opponent = 3 - player  # If player is 1, opponent is 2. If player is 2, opponent is 1.
        
        # Check all 8 directions (up, down, left, right, and 4 diagonals)
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            # Keep moving in this direction
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == opponent:
                    found_opponent = True
                elif self.board[r][c] == player:
                    # Found our piece! Valid if we passed opponent pieces
                    if found_opponent:
                        return True
                    break
                else:
                    # Empty square, stop checking this direction
                    break
                r += dr
                c += dc
        
        return False
    
    def make_move(self, row, col, player):
        """Place a piece and flip opponent's pieces"""
        # First, check if move is valid
        if not self.is_valid_move(row, col, player):
            return False

        # Place the piece
        self.board[row][col] = player
        opponent = 3 - player

        # Check all 8 directions
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            pieces_to_flip = []  # Store pieces we need to flip

            # Move in this direction and collect opponent pieces
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == opponent:
                    pieces_to_flip.append((r, c))  # Found opponent piece
                elif self.board[r][c] == player:
                    # Found our piece! Flip all collected pieces
                    for flip_r, flip_c in pieces_to_flip:
                        self.board[flip_r][flip_c] = player
                    break  # Stop checking this direction
                else:
                    break  # Empty square, stop

                r += dr
                c += dc

        return True
    
    def get_valid_moves(self, player):
        """Get all valid moves for a player"""
        valid_moves = []  # Empty list to store moves
        
        # Loop through all rows (0 to 7)
        for row in range(8):
            # Loop through all columns (0 to 7)
            for col in range(8):
                # Check if this position is valid
                if self.is_valid_move(row, col, player):
                    # Add it to the list as a tuple (row, col)
                    valid_moves.append((row, col))
        
        return valid_moves
    
    def is_game_over(self):
        """Check if the game is finished"""
        # Get valid moves for both players
        black_moves = self.get_valid_moves(1)
        white_moves = self.get_valid_moves(2)
        
        # Game over if BOTH have no moves
        return len(black_moves) == 0 and len(white_moves) == 0
    
    def get_winner(self):
        """Count pieces and determine the winner"""
        black_count = sum(row.count(1) for row in self.board)
        white_count = sum(row.count(2) for row in self.board)
        
        if black_count > white_count:
            return 1  # Black wins
        elif white_count > black_count:
            return 2  # White wins
        else:
            return 0  # Draw
    
    # Static helper methods for AI (work on any board state)
    @staticmethod
    def is_valid_move_on_board(board, row, col, player):
        """Check if a move is valid on any board state"""
        if board[row][col] != 0:
            return False
        
        opponent = 3 - player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == opponent:
                    found_opponent = True
                elif board[r][c] == player:
                    if found_opponent:
                        return True
                    break
                else:
                    break
                r += dr
                c += dc
        
        return False
    
    @staticmethod
    def get_valid_moves_on_board(board, player):
        """Get all valid moves for a player on any board state"""
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if OthelloGame.is_valid_move_on_board(board, row, col, player):
                    valid_moves.append((row, col))
        return valid_moves
    
    @staticmethod
    def simulate_move_on_board(board, row, col, player):
        """Simulate a move on a board copy and return new board"""
        import copy
        new_board = copy.deepcopy(board)
        
        new_board[row][col] = player
        opponent = 3 - player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            pieces_to_flip = []
            
            while 0 <= r < 8 and 0 <= c < 8:
                if new_board[r][c] == opponent:
                    pieces_to_flip.append((r, c))
                elif new_board[r][c] == player:
                    for flip_r, flip_c in pieces_to_flip:
                        new_board[flip_r][flip_c] = player
                    break
                else:
                    break
                r += dr
                c += dc
        
        return new_board


if __name__ == "__main__":
    # Quick test
    game = OthelloGame()
    game.print_board()
    print("\nOthello game initialized!")