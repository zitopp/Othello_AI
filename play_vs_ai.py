# Play Othello against AI
from game import OthelloGame
from ai import OthelloAI

def play_vs_ai():
    """Play Othello: Human vs AI"""
    game = OthelloGame()
    
    # Choose difficulty
    print("=" * 40)
    print("Othello - Human vs AI")
    print("=" * 40)
    print("\nChoose AI difficulty:")
    print("1 - Easy (depth 2)")
    print("2 - Medium (depth 4)")
    print("3 - Hard (depth 6)")
    
    while True:
        try:
            choice = input("\nEnter difficulty (1-3): ")
            difficulty_map = {"1": 2, "2": 4, "3": 6}
            if choice in difficulty_map:
                ai_depth = difficulty_map[choice]
                break
            print("Invalid choice! Enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\nGame cancelled!")
            return
    
    ai = OthelloAI(game, difficulty=ai_depth)
    
    # Choose player color
    print("\nChoose your color:")
    print("1 - Black (goes first)")
    print("2 - White (goes second)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-2): ")
            if choice in ["1", "2"]:
                human_player = int(choice)
                ai_player = 3 - human_player
                break
            print("Invalid choice! Enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nGame cancelled!")
            return
    
    print("\n" + "=" * 40)
    print("Black goes first (standard Othello rule)")
    if human_player == 1:
        print("You play as Black - You go first!")
    else:
        print("You play as White - AI goes first!")
    print("=" * 40)
    
    # Main game loop
    while not game.is_game_over():
        game.print_board()
        
        player_name = "Black" if game.current_player == 1 else "White"
        print(f"\n{player_name}'s turn")
        
        valid_moves = game.get_valid_moves(game.current_player)
        
        if not valid_moves:
            print(f"{player_name} has no valid moves. Skipping turn.")
            game.current_player = 3 - game.current_player
            continue
        
        # Human turn
        if game.current_player == human_player:
            print(f"Valid moves: {valid_moves}")
            
            while True:
                try:
                    move_input = input("Enter your move (row col) or 'h' for hint: ")
                    
                    if move_input.lower() == 'h':
                        # Show AI's suggested move as hint
                        hint_move = ai.get_best_move(human_player)
                        print(f"Hint: Try {hint_move}")
                        continue
                    
                    row, col = map(int, move_input.split())
                    
                    if game.make_move(row, col, game.current_player):
                        break
                    else:
                        print("Invalid move! Try again.")
                except (ValueError, IndexError):
                    print("Invalid input! Enter two numbers (e.g., '2 3') or 'h' for hint.")
                except KeyboardInterrupt:
                    print("\nGame interrupted!")
                    return
        
        # AI turn
        else:
            print("AI is thinking...")
            ai_move = ai.get_best_move(game.current_player)
            
            if ai_move:
                print(f"AI plays: {ai_move}")
                game.make_move(ai_move[0], ai_move[1], game.current_player)
            else:
                print("AI has no valid moves.")
        
        # Switch player
        game.current_player = 3 - game.current_player
    
    # Game over
    game.print_board()
    print("\n" + "=" * 40)
    print("GAME OVER!")
    
    winner = game.get_winner()
    if winner == human_player:
        print("🎉 You win!")
    elif winner == ai_player:
        print("🤖 AI wins!")
    else:
        print("It's a draw!")
    
    # Show final score
    black_count = sum(row.count(1) for row in game.board)
    white_count = sum(row.count(2) for row in game.board)
    print(f"Final Score - Black: {black_count}, White: {white_count}")
    print("=" * 40)


if __name__ == "__main__":
    play_vs_ai()
