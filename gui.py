# Modern GUI for Othello using CustomTkinter
import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw
import os
from game import OthelloGame
from ai import OthelloAI

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OthelloGUI:
    def __init__(self):
        # Main window
        self.root = ctk.CTk()
        self.root.title("Othello AI - Modern Edition")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # Game state
        self.game = None
        self.ai = None
        self.human_player = None
        self.ai_player = None
        self.game_mode = None  # "pvp" or "ai"
        self.animating = False
        
        # Visual settings
        self.cell_size = 70
        self.board_size = self.cell_size * 8
        self.board_offset_x = 20
        self.board_offset_y = 20
        
        # Colors
        self.bg_color = "#1a1a1a"
        self.board_color = "#2d5016"
        self.grid_color = "#1a3a0f"
        self.valid_move_color = "#90EE90"
        self.highlight_color = "#FFD700"
        
        # Asset storage
        self.images = {}
        self.animation_frames = []
        
        # Create UI
        self.create_menu_screen()
        
    def create_placeholder_assets(self):
        """Create placeholder circular pieces if no assets exist"""
        size = self.cell_size - 10
        
        # Black piece
        black_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(black_img)
        draw.ellipse([2, 2, size-2, size-2], fill='#1a1a1a', outline='#ffffff', width=2)
        self.images['black'] = ImageTk.PhotoImage(black_img)
        
        # White piece
        white_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(white_img)
        draw.ellipse([2, 2, size-2, size-2], fill='#f5f5f5', outline='#1a1a1a', width=2)
        self.images['white'] = ImageTk.PhotoImage(white_img)
        
        # Valid move indicator
        valid_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(valid_img)
        draw.ellipse([5, 5, size-5, size-5], fill=(144, 238, 144, 100), outline='#90EE90', width=2)
        self.images['valid'] = ImageTk.PhotoImage(valid_img)
        
        # Highlight
        highlight_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(highlight_img)
        draw.rectangle([0, 0, size, size], outline='#FFD700', width=3)
        self.images['highlight'] = ImageTk.PhotoImage(highlight_img)
    
    def load_custom_assets(self):
        """Load custom assets from assets/ folder (if they exist)"""
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        if not os.path.exists(assets_dir):
            print("No assets folder found, using placeholders")
            self.create_placeholder_assets()
            return
        
        try:
            # Try to load custom pieces
            black_path = os.path.join(assets_dir, 'black.png')
            white_path = os.path.join(assets_dir, 'white.png')
            
            if os.path.exists(black_path):
                img = Image.open(black_path).resize((self.cell_size - 10, self.cell_size - 10), Image.Resampling.LANCZOS)
                self.images['black'] = ImageTk.PhotoImage(img)
            
            if os.path.exists(white_path):
                img = Image.open(white_path).resize((self.cell_size - 10, self.cell_size - 10), Image.Resampling.LANCZOS)
                self.images['white'] = ImageTk.PhotoImage(img)
            
            # Board background
            board_path = os.path.join(assets_dir, 'board.png')
            if os.path.exists(board_path):
                img = Image.open(board_path).resize((self.board_size, self.board_size), Image.Resampling.LANCZOS)
                self.images['board_bg'] = ImageTk.PhotoImage(img)
            
            # If any failed, create placeholders
            if 'black' not in self.images or 'white' not in self.images:
                self.create_placeholder_assets()
                
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.create_placeholder_assets()
    
    def create_menu_screen(self):
        """Create the main menu"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.root,
            text="OTHELLO",
            font=ctk.CTkFont(size=60, weight="bold")
        )
        title.pack(pady=(100, 20))
        
        subtitle = ctk.CTkLabel(
            self.root,
            text="Modern AI Edition",
            font=ctk.CTkFont(size=20)
        )
        subtitle.pack(pady=(0, 60))
        
        # Buttons
        btn_pvp = ctk.CTkButton(
            self.root,
            text="Human vs Human",
            font=ctk.CTkFont(size=18),
            width=300,
            height=50,
            command=lambda: self.start_game("pvp")
        )
        btn_pvp.pack(pady=15)
        
        btn_ai = ctk.CTkButton(
            self.root,
            text="Human vs AI",
            font=ctk.CTkFont(size=18),
            width=300,
            height=50,
            command=self.show_ai_setup
        )
        btn_ai.pack(pady=15)
        
        btn_quit = ctk.CTkButton(
            self.root,
            text="Quit",
            font=ctk.CTkFont(size=18),
            width=300,
            height=50,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=self.root.quit
        )
        btn_quit.pack(pady=15)
    
    def show_ai_setup(self):
        """Show AI difficulty and color selection"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.root,
            text="AI Setup",
            font=ctk.CTkFont(size=40, weight="bold")
        )
        title.pack(pady=(80, 40))
        
        # Difficulty selection
        diff_label = ctk.CTkLabel(
            self.root,
            text="Choose Difficulty:",
            font=ctk.CTkFont(size=20)
        )
        diff_label.pack(pady=(0, 10))
        
        self.difficulty_var = ctk.StringVar(value="medium")
        
        diff_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        diff_frame.pack(pady=20)
        
        ctk.CTkRadioButton(
            diff_frame,
            text="Easy (Depth 2)",
            variable=self.difficulty_var,
            value="easy",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        ctk.CTkRadioButton(
            diff_frame,
            text="Medium (Depth 4)",
            variable=self.difficulty_var,
            value="medium",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        ctk.CTkRadioButton(
            diff_frame,
            text="Hard (Depth 6)",
            variable=self.difficulty_var,
            value="hard",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        # Color selection
        color_label = ctk.CTkLabel(
            self.root,
            text="Choose Your Color:",
            font=ctk.CTkFont(size=20)
        )
        color_label.pack(pady=(30, 10))
        
        self.color_var = ctk.StringVar(value="black")
        
        color_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        color_frame.pack(pady=20)
        
        ctk.CTkRadioButton(
            color_frame,
            text="Black (You go first)",
            variable=self.color_var,
            value="black",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        ctk.CTkRadioButton(
            color_frame,
            text="White (AI goes first)",
            variable=self.color_var,
            value="white",
            font=ctk.CTkFont(size=16)
        ).pack(pady=5)
        
        # Start button
        start_btn = ctk.CTkButton(
            self.root,
            text="Start Game",
            font=ctk.CTkFont(size=18),
            width=250,
            height=50,
            command=lambda: self.start_game("ai")
        )
        start_btn.pack(pady=(30, 10))
        
        # Back button
        back_btn = ctk.CTkButton(
            self.root,
            text="Back",
            font=ctk.CTkFont(size=16),
            width=150,
            height=40,
            fg_color="gray",
            command=self.create_menu_screen
        )
        back_btn.pack(pady=10)
    
    def start_game(self, mode):
        """Initialize and start the game"""
        self.game_mode = mode
        self.game = OthelloGame()
        
        if mode == "ai":
            # Set up AI
            difficulty_map = {"easy": 2, "medium": 4, "hard": 6}
            depth = difficulty_map[self.difficulty_var.get()]
            self.ai = OthelloAI(self.game, difficulty=depth)
            
            self.human_player = 1 if self.color_var.get() == "black" else 2
            self.ai_player = 3 - self.human_player
        
        self.create_game_screen()
        
        # If AI is first, make its move
        if mode == "ai" and self.game.current_player == self.ai_player:
            self.root.after(500, self.make_ai_move)
    
    def create_game_screen(self):
        """Create the game board UI"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Load assets
        self.load_custom_assets()
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left side - Board
        board_frame = ctk.CTkFrame(main_frame, width=self.board_size + 40, height=self.board_size + 40)
        board_frame.pack(side="left", padx=(0, 20))
        board_frame.pack_propagate(False)
        
        # Canvas for board
        self.canvas = Canvas(
            board_frame,
            width=self.board_size,
            height=self.board_size,
            bg=self.board_color,
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        
        # Right side - Info panel
        info_frame = ctk.CTkFrame(main_frame, width=300)
        info_frame.pack(side="right", fill="y")
        info_frame.pack_propagate(False)
        
        # Game info
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="OTHELLO",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.info_label.pack(pady=(20, 10))
        
        # Turn indicator
        self.turn_label = ctk.CTkLabel(
            info_frame,
            text="Black's Turn",
            font=ctk.CTkFont(size=18)
        )
        self.turn_label.pack(pady=10)
        
        # Score
        self.score_label = ctk.CTkLabel(
            info_frame,
            text="Black: 2\nWhite: 2",
            font=ctk.CTkFont(size=16)
        )
        self.score_label.pack(pady=20)
        
        # Buttons
        hint_btn = ctk.CTkButton(
            info_frame,
            text="Hint",
            width=200,
            height=40,
            command=self.show_hint
        )
        hint_btn.pack(pady=10)
        
        restart_btn = ctk.CTkButton(
            info_frame,
            text="New Game",
            width=200,
            height=40,
            command=self.start_game if self.game_mode else self.create_menu_screen
        )
        restart_btn.pack(pady=10)
        
        menu_btn = ctk.CTkButton(
            info_frame,
            text="Main Menu",
            width=200,
            height=40,
            fg_color="gray",
            command=self.create_menu_screen
        )
        menu_btn.pack(pady=10)
        
        # Draw initial board
        self.draw_board()
        self.update_info()
    
    def draw_board(self):
        """Draw the game board"""
        self.canvas.delete("all")
        
        # Draw background if available
        if 'board_bg' in self.images:
            self.canvas.create_image(0, 0, anchor='nw', image=self.images['board_bg'])
        
        # Draw grid
        for i in range(9):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size, fill=self.grid_color, width=2)
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size, y, fill=self.grid_color, width=2)
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece != 0:
                    self.draw_piece(row, col, piece)
        
        # Draw valid moves
        if not self.animating:
            self.draw_valid_moves()
    
    def draw_piece(self, row, col, player, tag="piece"):
        """Draw a piece on the board"""
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        
        img_key = 'black' if player == 1 else 'white'
        self.canvas.create_image(x, y, image=self.images[img_key], tags=tag)
    
    def draw_valid_moves(self):
        """Highlight valid moves"""
        self.canvas.delete("valid")
        
        if self.game_mode == "ai" and self.game.current_player == self.ai_player:
            return  # Don't show hints during AI turn
        
        valid_moves = self.game.get_valid_moves(self.game.current_player)
        
        for row, col in valid_moves:
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            
            # Draw semi-transparent circle
            r = (self.cell_size - 10) // 2
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="", outline=self.valid_move_color, width=2, tags="valid"
            )
    
    def on_canvas_click(self, event):
        """Handle mouse click on board"""
        if self.animating:
            return
        
        if self.game.is_game_over():
            return
        
        # AI turn - ignore clicks
        if self.game_mode == "ai" and self.game.current_player == self.ai_player:
            return
        
        # Convert click to board coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        # Try to make move
        if self.game.make_move(row, col, self.game.current_player):
            self.animate_move(row, col)
    
    def on_canvas_hover(self, event):
        """Handle mouse hover for visual feedback"""
        if self.animating:
            return
        
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        # Clear previous hover
        self.canvas.delete("hover")
        
        if 0 <= row < 8 and 0 <= col < 8:
            valid_moves = self.game.get_valid_moves(self.game.current_player)
            if (row, col) in valid_moves:
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                r = (self.cell_size - 10) // 2
                self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill="", outline=self.highlight_color, width=3, tags="hover"
                )
    
    def animate_move(self, row, col):
        """Animate piece placement and flips"""
        self.animating = True
        
        # Redraw board to show new piece
        self.draw_board()
        
        # Switch player
        self.game.current_player = 3 - self.game.current_player
        
        # Small delay then check game state
        self.root.after(300, self.after_move)
    
    def after_move(self):
        """Called after move animation"""
        self.animating = False
        self.update_info()
        
        # Check if game over
        if self.game.is_game_over():
            self.show_game_over()
            return
        
        # Check if current player has no moves
        if not self.game.get_valid_moves(self.game.current_player):
            # Skip turn
            player_name = "Black" if self.game.current_player == 1 else "White"
            self.turn_label.configure(text=f"{player_name} has no moves!\nSkipping turn...")
            self.game.current_player = 3 - self.game.current_player
            self.root.after(1500, self.after_move)
            return
        
        # If AI mode and AI's turn, make AI move
        if self.game_mode == "ai" and self.game.current_player == self.ai_player:
            self.root.after(500, self.make_ai_move)
        else:
            self.draw_valid_moves()
    
    def make_ai_move(self):
        """AI makes a move"""
        if self.animating:
            return
        
        self.turn_label.configure(text="AI is thinking...")
        self.root.update()
        
        # Get AI move
        move = self.ai.get_best_move(self.game.current_player)
        
        if move:
            row, col = move
            self.game.make_move(row, col, self.game.current_player)
            self.animate_move(row, col)
        else:
            # AI has no moves, skip
            self.game.current_player = 3 - self.game.current_player
            self.after_move()
    
    def show_hint(self):
        """Show a hint for the current player"""
        if self.animating or self.game.is_game_over():
            return
        
        if self.game_mode == "ai" and self.game.current_player == self.ai_player:
            return
        
        # Use AI to get best move
        temp_ai = OthelloAI(self.game, difficulty=4)
        hint_move = temp_ai.get_best_move(self.game.current_player)
        
        if hint_move:
            row, col = hint_move
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            
            # Flash the hint
            self.canvas.delete("hint")
            r = self.cell_size // 2 - 5
            hint = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="", outline="#FFD700", width=4, tags="hint"
            )
            
            # Remove after 2 seconds
            self.root.after(2000, lambda: self.canvas.delete("hint"))
    
    def update_info(self):
        """Update info panel"""
        # Update turn
        player_name = "Black" if self.game.current_player == 1 else "White"
        self.turn_label.configure(text=f"{player_name}'s Turn")
        
        # Update score
        black_count = sum(row.count(1) for row in self.game.board)
        white_count = sum(row.count(2) for row in self.game.board)
        self.score_label.configure(text=f"Black: {black_count}\nWhite: {white_count}")
    
    def show_game_over(self):
        """Show game over screen"""
        winner = self.game.get_winner()
        black_count = sum(row.count(1) for row in self.game.board)
        white_count = sum(row.count(2) for row in self.game.board)
        
        if winner == 1:
            result = "Black Wins!"
        elif winner == 2:
            result = "White Wins!"
        else:
            result = "Draw!"
        
        # Create popup
        popup = ctk.CTkToplevel(self.root)
        popup.title("Game Over")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()
        
        ctk.CTkLabel(
            popup,
            text="GAME OVER",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=(40, 20))
        
        ctk.CTkLabel(
            popup,
            text=result,
            font=ctk.CTkFont(size=28)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            popup,
            text=f"Final Score:\nBlack: {black_count}\nWhite: {white_count}",
            font=ctk.CTkFont(size=18)
        ).pack(pady=20)
        
        ctk.CTkButton(
            popup,
            text="New Game",
            width=200,
            height=40,
            command=lambda: [popup.destroy(), self.start_game(self.game_mode)]
        ).pack(pady=10)
        
        ctk.CTkButton(
            popup,
            text="Main Menu",
            width=200,
            height=40,
            fg_color="gray",
            command=lambda: [popup.destroy(), self.create_menu_screen()]
        ).pack(pady=10)
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = OthelloGUI()
    app.run()
