# Terminal Interface for Othello
from game import OthelloGame

def play_terminal():
    """Play Othello in the terminal (2 players)"""
    game = OthelloGame()
    
    print("=" * 40)
    print("Welcome to Othello!")
    print("Black (B) vs White (W)")
    print("Black goes first")
    print("=" * 40)
    
    while not game.is_game_over():
        game.print_board()
        
        # Show current player
        player_name = "Black" if game.current_player == 1 else "White"
        print(f"\n{player_name}'s turn")
        
        # Get valid moves
        valid_moves = game.get_valid_moves(game.current_player)
        
        if not valid_moves:
            print(f"{player_name} has no valid moves. Skipping turn.")
            game.current_player = 3 - game.current_player
            continue
        
        print(f"Valid moves: {valid_moves}")
        
        # Get player input
        while True:
            try:
                move_input = input("Enter your move (row col): ")
                row, col = map(int, move_input.split())
                
                if game.make_move(row, col, game.current_player):
                    break
                else:
                    print("Invalid move! Try again.")
            except (ValueError, IndexError):
                print("Invalid input! Enter two numbers (e.g., '2 3')")
            except KeyboardInterrupt:
                print("\nGame interrupted!")
                return
        
        # Switch player
        game.current_player = 3 - game.current_player
    
    # Game over
    game.print_board()
    print("\n" + "=" * 40)
    print("GAME OVER!")
    
    winner = game.get_winner()
    if winner == 1:
        print("Black wins!")
    elif winner == 2:
        print("White wins!")
    else:
        print("It's a draw!")
    
    # Show final score
    black_count = sum(row.count(1) for row in game.board)
    white_count = sum(row.count(2) for row in game.board)
    print(f"Final Score - Black: {black_count}, White: {white_count}")
    print("=" * 40)


if __name__ == "__main__":
    play_terminal()