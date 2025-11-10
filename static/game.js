// Modern Othello Game with GSAP animations

let gameId = null;
let gameMode = null;
let gameState = null;
let isAnimating = false;
let humanPlayer = 1;
let boardInitialized = false;
let aiTimeoutId = null; // track scheduled AI move
let modalOpen = false;  // lock UI when modal is shown

// Initialize game
function init() {
    showMenu();
}

// Only (re)render valid move highlights; does not touch pieces
function clearHighlights() {
    document.querySelectorAll('.cell.valid, .cell.hint').forEach(cell => {
        cell.classList.remove('valid', 'hint');
    });
}

function renderHighlights() {
    // Always start by clearing
    clearHighlights();
    if (!gameState) return;
    // Hide move markers during AI turn or while animating
    if (isAnimating) return;
    if (gameMode === 'ai' && gameState.current_player !== humanPlayer) return;
    if (!gameState.valid_moves || gameState.valid_moves.length === 0) return;
    gameState.valid_moves.forEach(([row, col]) => {
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (cell) cell.classList.add('valid');
    });
}

// Compute flips locally from a board snapshot
function computeFlips(board, row, col, player) {
    const flips = [];
    const opponent = 3 - player;
    const dirs = [
        [-1, -1], [-1, 0], [-1, 1],
        [0, -1],           [0, 1],
        [1, -1],  [1, 0],  [1, 1]
    ];
    for (const [dr, dc] of dirs) {
        let r = row + dr;
        let c = col + dc;
        const temp = [];
        while (r >= 0 && r < 8 && c >= 0 && c < 8) {
            const cell = board[r][c];
            if (cell === opponent) {
                temp.push([r, c]);
                r += dr; c += dc;
                continue;
            }
            if (cell === player) {
                if (temp.length > 0) flips.push(...temp);
            }
            break;
        }
    }
    return flips;
}

// Screen transitions
function showMenu() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('menu-screen').classList.add('active');
    gsap.from('#menu-screen', { opacity: 0, y: 50, duration: 0.8, ease: 'power3.out' });
}

function showAISetup() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('ai-setup-screen').classList.add('active');
    gsap.from('#ai-setup-screen', { opacity: 0, y: 50, duration: 0.8, ease: 'power3.out' });
    
    // Initialize difficulty slider
    initDifficultySlider();
}

// Color selection function
function selectColor(color) {
    console.log('Selected color:', color);
    
    // Remove active class from all circles
    document.querySelectorAll('.color-circle').forEach(circle => {
        circle.classList.remove('active');
    });
    
    // Add active class to selected circle
    const selectedCircle = document.querySelector(`.color-circle[data-color="${color}"]`);
    selectedCircle.classList.add('active');
    
    // Animate selection
    gsap.from(selectedCircle, {
        scale: 0.9,
        duration: 0.4,
        ease: 'elastic.out(1, 0.5)'
    });
}

function initDifficultySlider() {
    const slider = document.getElementById('difficulty-slider');
    const display = document.getElementById('difficulty-display');
    let isDragging = false;
    
    function updateDifficulty() {
        const value = parseInt(slider.value);
        display.classList.remove('easy', 'medium', 'hard');
        
        if (value === 1) {
            display.textContent = 'Easy';
            display.classList.add('easy');
        } else if (value === 2) {
            display.textContent = 'Medium';
            display.classList.add('medium');
        } else {
            display.textContent = 'Hard';
            display.classList.add('hard');
        }
        
        // Animate the display box
        gsap.from(display, {
            scale: 1.1,
            duration: 0.4,
            ease: 'elastic.out(1, 0.5)'
        });
    }
    
    // Magnetic snapping effect
    function snapToNearest() {
        if (!isDragging) return;
        
        const currentValue = parseFloat(slider.value);
        let targetValue;
        
        // Determine which snap point is closest
        if (currentValue < 1.5) {
            targetValue = 1;
        } else if (currentValue < 2.5) {
            targetValue = 2;
        } else {
            targetValue = 3;
        }
        
        // Animate snap with easing
        const startValue = currentValue;
        const distance = Math.abs(targetValue - startValue);
        
        // Duration based on distance (closer = slower for magnetic effect)
        const duration = 0.3 + (distance * 0.1);
        
        gsap.to({ value: startValue }, {
            value: targetValue,
            duration: duration,
            ease: 'power2.out',
            onUpdate: function() {
                slider.value = this.targets()[0].value;
                updateDifficulty();
            }
        });
    }
    
    // Track dragging state
    slider.addEventListener('mousedown', () => {
        isDragging = true;
    });
    
    slider.addEventListener('touchstart', () => {
        isDragging = true;
    });
    
    slider.addEventListener('mouseup', () => {
        isDragging = true;
        snapToNearest();
        setTimeout(() => isDragging = false, 100);
    });
    
    slider.addEventListener('touchend', () => {
        isDragging = true;
        snapToNearest();
        setTimeout(() => isDragging = false, 100);
    });
    
    slider.addEventListener('input', updateDifficulty);
    updateDifficulty(); // Set initial state
}

function showGameScreen() {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('game-screen').classList.add('active');
    gsap.from('#game-screen', { opacity: 0, scale: 0.95, duration: 0.8, ease: 'power3.out' });
}

// Start game
async function startGame(mode) {
    try {
        console.log('Starting game in mode:', mode);
        gameMode = mode;
        
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: mode,
                difficulty: 4,
                human_player: 1
            })
        });
        const data = await response.json();
        console.log('Game created:', data);
        
        gameId = data.game_id;
        gameState = data;
        
        showGameScreen();
        
        // Wait for screen to be visible before initializing board
        setTimeout(() => {
            console.log('Initializing board...');
            initBoard();
            updateUI();
        }, 100);
    } catch (error) {
        console.error('Error starting game:', error);
        alert('Error starting game. Check console for details.');
    }
}

async function startAIGame() {
    try {
        console.log('Starting AI game...');
        gameMode = 'ai';
        
        // Get difficulty from slider (1=Easy, 2=Medium, 3=Hard)
        const sliderValue = parseInt(document.getElementById('difficulty-slider').value);
        const difficultyMap = { 1: 2, 2: 4, 3: 6 }; // Easy=depth 2, Medium=4, Hard=6
        const difficulty = difficultyMap[sliderValue];
        
        // Get selected color from active circle
        const activeCircle = document.querySelector('.color-circle.active');
        humanPlayer = parseInt(activeCircle.dataset.color);
        
        console.log('Slider value:', sliderValue, 'Difficulty depth:', difficulty, 'Human player:', humanPlayer);
        
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'ai',
                difficulty: difficulty,
                human_player: humanPlayer
            })
        });
        
        const data = await response.json();
        console.log('AI Game created:', data);
        
        gameId = data.game_id;
        gameState = data;
        
        showGameScreen();
        
        // Wait for screen to be visible before initializing board
        setTimeout(() => {
            console.log('Initializing AI game board...');
            initBoard();
            updateUI();
            
            // If AI goes first
            if (gameState.current_player !== humanPlayer) {
                console.log('AI goes first, making move...');
                setTimeout(() => makeAIMove(), 800);
            }
        }, 100);
    } catch (error) {
        console.error('Error starting AI game:', error);
        alert('Error starting AI game. Check console for details.');
    }
}

async function newGame() {
    // Close modal and restart game
    const modal = document.getElementById('game-over-modal');
    
    gsap.to('.modal-content', {
        scale: 0.8,
        opacity: 0,
        duration: 0.3,
        onComplete: () => {
            modal.classList.remove('active');
            modal.style.display = 'none';
            modalOpen = false;
            document.body.classList.remove('modal-open');
            
            // Now restart the game
            if (gameMode === 'ai') {
                showAISetup();
            } else {
                startGame(gameMode);
            }
        }
    });
}

// Board creation
function initBoard() {
    const board = document.getElementById('board');
    board.innerHTML = '';
    boardInitialized = false;
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            // Single click handler to prevent multiple fires
            cell.addEventListener('click', () => handleCellClick(row, col), { once: false });
            
            // Optimized hover effects
            cell.addEventListener('mouseenter', () => {
                if (!isAnimating && isValidMove(row, col)) {
                    cell.style.transform = 'scale(1.05)';
                }
            });
            cell.addEventListener('mouseleave', () => {
                cell.style.transform = 'scale(1)';
            });
            
            board.appendChild(cell);
        }
    }
    
    boardInitialized = true;
    renderBoard();
}

function renderBoard() {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            const piece = gameState.board[row][col];
            const existingPiece = cell.querySelector('.piece');
            
            cell.classList.remove('valid', 'hint');
            
            // Only update if piece state has changed
            if (piece === 0 && existingPiece) {
                // Remove piece if cell should be empty
                existingPiece.remove();
            } else if (piece !== 0 && !existingPiece) {
                // Add piece if cell should have one but doesn't
                const pieceDiv = document.createElement('div');
                pieceDiv.className = `piece ${piece === 1 ? 'black' : 'white'}`;
                cell.appendChild(pieceDiv);
            } else if (piece !== 0 && existingPiece) {
                // Update piece color if it exists but has wrong color
                const shouldBeBlack = piece === 1;
                const isBlack = existingPiece.classList.contains('black');
                if (shouldBeBlack !== isBlack) {
                    existingPiece.className = `piece ${shouldBeBlack ? 'black' : 'white'}`;
                }
            }
        }
    }
    // After syncing pieces, refresh highlights separately
    renderHighlights();
}

function isValidMove(row, col) {
    if (!gameState.valid_moves) return false;
    return gameState.valid_moves.some(([r, c]) => r === row && c === col);
}

// Handle move with debounce
async function handleCellClick(row, col) {
    // Prevent multiple clicks
    if (modalOpen || isAnimating) {
        console.log('Animation in progress, ignoring click');
        return;
    }
    if (!gameState || gameState.game_over) {
        console.log('Game is over or not initialized');
        return;
    }
    if (gameMode === 'ai' && gameState.current_player !== humanPlayer) {
        console.log('AI turn, ignoring click');
        return;
    }
    if (!isValidMove(row, col)) {
        console.log('Invalid move');
        return;
    }
    // Immediately clear hover/valid markers so the dot disappears on click
    clearHighlights();

    console.log('Making move at', row, col);
    await makeMove(row, col);
}

async function makeMove(row, col) {
    isAnimating = true;
    
    const response = await fetch(`/api/move/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col })
    });
    
    if (!response.ok) {
        isAnimating = false;
        return;
    }
    
    const data = await response.json();
    const playerWhoMoved = gameState.current_player;
    // Compute flips locally from the PREVIOUS board state
    const localFlips = computeFlips(gameState.board, row, col, playerWhoMoved);
    console.log('Local flips:', localFlips);
    
    // Place the new piece visually first
    await animatePlacement(row, col, playerWhoMoved);
    
    // Animate local flips (fallback if backend failed to send any)
    if (localFlips && localFlips.length) {
        await animateFlips(localFlips);
    } else if (data.flipped && data.flipped.length) {
        await animateFlips(data.flipped);
    }
    
    // Update state, end animation, then render
    gameState = data;
    isAnimating = false;
    updateUI(true);
    renderBoard();
    
    // Check if game over
    if (gameState.game_over) {
        setTimeout(() => showGameOver(), 500);
        return;
    }
    
    // Show skip message
    if (data.skipped) {
        showSkipMessage();
    }
    
    // AI turn
    if (gameMode === 'ai' && gameState.current_player !== humanPlayer && !gameState.game_over) {
        if (aiTimeoutId) clearTimeout(aiTimeoutId);
        aiTimeoutId = setTimeout(() => makeAIMove(), 800);
    }
}

async function makeAIMove() {
    if (modalOpen) return;
    if (isAnimating) return;
    if (gameState && gameState.game_over) return;
    
    isAnimating = true;
    document.getElementById('turn-text').textContent = 'AI is thinking...';
    
    // Snapshot board before AI move for local flip computation
    const prevBoard = gameState.board.map(row => row.slice());
    
    const response = await fetch(`/api/ai_move/${gameId}`, {
        method: 'POST'
    });
    
    const data = await response.json();
    
    if (!data.success) {
        isAnimating = false;
        return;
    }
    
    const { row, col } = data.move;
    const playerWhoMoved = gameState.current_player;
    // Compute flips locally from board before AI move applied
    const localFlips = computeFlips(prevBoard, row, col, playerWhoMoved);
    console.log('AI local flips:', localFlips);
    
    // Place piece WITHOUT updating state
    await animatePlacement(row, col, playerWhoMoved);
    
    // Animate flips BEFORE updating state
    if (localFlips && localFlips.length) {
        await animateFlips(localFlips);
    } else if (data.flipped && data.flipped.length) {
        await animateFlips(data.flipped);
    }
    
    // NOW update state
    gameState = data;
    
    // End animation then render
    isAnimating = false;
    updateUI(true);
    renderBoard();
    
    if (gameState.game_over) {
        setTimeout(() => showGameOver(), 500);
        return;
    }
    
    if (data.skipped) {
        showSkipMessage();
    }
    
    // Decide next turn
    ensureNextTurn();
}

// Animations with GSAP - Optimized
async function animatePlacement(row, col, player) {
    return new Promise(resolve => {
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (!cell) {
            resolve();
            return;
        }
        
        const pieceDiv = document.createElement('div');
        pieceDiv.className = `piece ${player === 1 ? 'black' : 'white'}`;
        cell.appendChild(pieceDiv);
        
        // Faster animation
        gsap.from(pieceDiv, {
            scale: 0,
            duration: 0.25,
            ease: 'back.out(1.5)',
            onComplete: resolve
        });
        
        // Quick flash on cell
        gsap.to(cell, {
            backgroundColor: 'rgba(255, 215, 0, 0.4)',
            duration: 0.2,
            yoyo: true,
            repeat: 1,
            onComplete: () => {
                cell.style.backgroundColor = '';
            }
        });
    });
}

async function animateFlips(flipped) {
    if (!flipped || flipped.length === 0) {
        console.log('No pieces to flip');
        return;
    }
    
    console.log('=== FLIP ANIMATION START ===');
    console.log('Flipping', flipped.length, 'pieces');
    
    return new Promise(resolve => {
        const timeline = gsap.timeline({ 
            onComplete: () => {
                console.log('=== FLIP ANIMATION COMPLETE ===');
                resolve();
            }
        });
        
        flipped.forEach(([row, col], index) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (!cell) {
                console.error('Cell not found:', row, col);
                return;
            }
            
            const piece = cell.querySelector('.piece');
            if (!piece) {
                console.error('Piece not found at cell:', row, col);
                return;
            }
            
            console.log(`Flip ${index + 1}: row ${row}, col ${col}`);
            
            // Visible coin flip using vertical squash
            const delay = index * 0.06;
            const isBlack = piece.classList.contains('black');
            const toColor = isBlack ? '#f0f8fb' : '#071d1a';
            
            // First half: squash vertically to thin oval
            timeline.to(piece, {
                scaleY: 0.08,
                borderRadius: '50% / 8%',
                duration: 0.22,
                ease: 'power2.in',
                force3D: true
            }, delay);
            
            // Mid-point: swap color while it's thinnest
            timeline.add(() => {
                piece.classList.toggle('black');
                piece.classList.toggle('white');
                piece.style.background = toColor; // ensure visual change even if classes are cached
            }, delay + 0.22);
            
            // Second half: expand back to full circle
            timeline.to(piece, {
                scaleY: 1,
                borderRadius: '50% / 50%',
                duration: 0.22,
                ease: 'power2.out',
                force3D: true
            }, delay + 0.22);
        });
    });
}

// UI Updates
function updateUI(skipBoardRender = false) {
    // Update turn
    const turnText = gameState.current_player === 1 ? "Black's Turn" : "White's Turn";
    document.getElementById('turn-text').textContent = turnText;
    
    // Animate turn indicator
    gsap.from('#turn-text', { scale: 1.1, duration: 0.3, ease: 'power2.out' });
    
    // Update score with animation
    animateScore('black-score', gameState.score.black);
    animateScore('white-score', gameState.score.white);
    
    // Render board only if not skipped (during animations we skip it)
    if (!skipBoardRender) {
        renderBoard();
    }
}

// Ensure game proceeds after a move, including skip chains
function ensureNextTurn() {
    if (modalOpen) return;
    if (!gameState || gameState.game_over) return;
    const noMoves = !gameState.valid_moves || gameState.valid_moves.length === 0;
    if (gameMode === 'ai') {
        if (gameState.current_player !== humanPlayer) {
            // AI's turn; if no moves, ask server to move (it will handle skip internally)
            if (aiTimeoutId) clearTimeout(aiTimeoutId);
            aiTimeoutId = setTimeout(() => makeAIMove(), 350);
        } else if (noMoves) {
            // Human has no moves; notify and let AI play
            showSkipMessage();
            if (aiTimeoutId) clearTimeout(aiTimeoutId);
            aiTimeoutId = setTimeout(() => makeAIMove(), 350);
        }
    }
}

function animateScore(elementId, newValue) {
    const element = document.getElementById(elementId);
    const currentValue = parseInt(element.textContent) || 0;
    
    if (currentValue !== newValue) {
        gsap.to({ value: currentValue }, {
            value: newValue,
            duration: 0.5,
            ease: 'power2.out',
            onUpdate: function() {
                element.textContent = Math.round(this.targets()[0].value);
            }
        });
        
        gsap.from(element, { scale: 1.2, duration: 0.3, ease: 'elastic.out(1, 0.5)' });
    }
}

function showSkipMessage() {
    const turnText = document.getElementById('turn-text');
    const playerName = gameState.current_player === 1 ? 'Black' : 'White';
    turnText.textContent = `${playerName} has no moves!`;
    
    gsap.to('#turn-indicator', {
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        duration: 0.3,
        yoyo: true,
        repeat: 1
    });
}

// Hint
async function getHint() {
    if (isAnimating || gameState.game_over) return;
    if (gameMode === 'ai' && gameState.current_player !== humanPlayer) return;
    
    const response = await fetch(`/api/hint/${gameId}`);
    
    if (!response.ok) return;
    
    const data = await response.json();
    const { row, col } = data.hint;
    
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    cell.classList.add('hint');
    
    // Animate hint
    gsap.from(cell, {
        scale: 1.15,
        duration: 0.5,
        ease: 'power2.out',
        repeat: 2,
        yoyo: true,
        onComplete: () => {
            setTimeout(() => cell.classList.remove('hint'), 2000);
        }
    });
}

// Game Over
function showGameOver() {
    console.log('=== SHOWING GAME OVER MODAL ===');
    const modal = document.getElementById('game-over-modal');
    const winnerText = document.getElementById('winner-text');
    const finalScore = document.getElementById('final-score');
    
    if (!modal || !winnerText || !finalScore) {
        console.error('Modal elements not found!');
        return;
    }
    
    // Lock UI and cancel any pending AI actions
    modalOpen = true;
    isAnimating = false;
    if (aiTimeoutId) {
        clearTimeout(aiTimeoutId);
        aiTimeoutId = null;
    }
    clearHighlights();
    
    let result;
    if (gameState.winner === 1) {
        result = '🏆 Black Wins!';
    } else if (gameState.winner === 2) {
        result = '🏆 White Wins!';
    } else {
        result = '🤝 Draw!';
    }
    
    console.log('Winner:', result);
    console.log('Score:', gameState.score);
    
    winnerText.textContent = result;
    finalScore.textContent = `Black: ${gameState.score.black} - White: ${gameState.score.white}`;
    
    // Show modal
    modal.style.display = 'flex';
    modal.classList.add('active');
    document.body.classList.add('modal-open');
    
    console.log('Modal displayed');
    
    // Animate content in
    gsap.fromTo('.modal-content', 
        {
            scale: 0.7,
            opacity: 0
        },
        {
            scale: 1,
            opacity: 1,
            duration: 0.6,
            ease: 'back.out(1.7)'
        }
    );
}

function closeModal() {
    const modal = document.getElementById('game-over-modal');
    gsap.to('.modal-content', {
        scale: 0.8,
        opacity: 0,
        duration: 0.3,
        onComplete: () => {
            modal.classList.remove('active');
            modal.style.display = 'none';
            modalOpen = false;
            document.body.classList.remove('modal-open');
            showMenu();
        }
    });
}

// Initialize on load
window.onload = init;
