# 🐍 Snake Game project made by Yuri-André

A feature-rich Snake game built with Python and Pygame, complete with sound effects, high scores, and smooth gameplay.

## 🎮 Features

- **Classic Snake Gameplay** - Control the snake with arrow keys
- **Progressive Difficulty** - Speed increases as you score more points  
- **High Score System** - Top 5 leaderboard with player names and dates
- **Audio Effects** - Sound effects for eating, level up, game over, and high scores
- **Audio Settings** - Customizable volume controls and sound toggle
- **Smooth Animation** - 60 FPS gameplay with visual polish
- **Name Entry** - Personal high score entries with name input

## 🎯 Game Controls

### During Gameplay
- **↑ ↓ ← →** - Move snake
- **SPACE** - Pause/Resume  
- **M** - Audio settings menu
- **ESC** - Quit game

### Audio Settings
- **S** - Toggle sound effects on/off
- **↑/↓** - Adjust music volume
- **Shift + ↑/↓** - Adjust SFX volume

### High Scores
- **H** - View high scores leaderboard (when game over)

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Visual Studio Code
- Python extension for VS Code

### Installation

1. **Clone/Download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd snake-game-vscode
   ```

2. **Open in Visual Studio Code**
   ```bash
   code .
   ```

3. **Set up Virtual Environment** (Method 1: Using VS Code Tasks)
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Tasks: Run Task"
   - Select "Setup Virtual Environment"
   - Then select "Install Dependencies"

4. **Set up Virtual Environment** (Method 2: Manual)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

5. **Select Python Interpreter in VS Code**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter" 
   - Choose `./venv/bin/python`

## 🚀 Running the Game

### Method 1: VS Code Debug/Run
- Press `F5` or click the "Run and Debug" button
- Select "Python: Snake Game" configuration

### Method 2: VS Code Tasks
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Tasks: Run Task"
- Select "Run Snake Game"

### Method 3: Terminal
```bash
# Make sure virtual environment is activated
source venv/bin/activate
python snake_game.py
```

### Method 4: Build Task (Default)
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Tasks: Run Build Task" or press `Ctrl+Shift+B`

## 🎵 Audio System

The game features a complete audio system with:
- **Eat Sound** - Pleasant upward chirp when eating food
- **Game Over** - Dramatic descending tone sequence  
- **High Score** - Victory fanfare for new records
- **Level Up** - Ascending celebration when speed increases

All sounds are programmatically generated using mathematical sine waves - no external audio files needed!

## 📁 Project Structure

```
snake-game-vscode/
├── .vscode/
│   ├── settings.json      # VS Code workspace settings
│   ├── launch.json        # Debug configurations  
│   └── tasks.json         # Custom tasks
├── snake_game.py          # Main game file
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── venv/                  # Virtual environment (created during setup)
```

## 🐛 Debugging

The project includes VS Code debug configurations:

1. **Python: Snake Game** - Normal execution
2. **Python: Snake Game (Debug Mode)** - Extended debugging with DEBUG=1

Set breakpoints in VS Code and use F5 to debug!

## 🧹 Code Formatting

Format your code using Black:
- **Manual**: Run the "Format Code" task
- **Automatic**: Code formats on save (configured in settings.json)

## 🏆 High Scores

High scores are automatically saved to `snake_highscores.json` in the game directory. The file includes:
- Player names (up to 12 characters)
- Scores 
- Date and time achieved
- Top 5 scores maintained automatically

## 🎨 Customization

You can customize the game by modifying constants at the top of `snake_game.py`:
- `WINDOW_WIDTH/HEIGHT` - Game window size
- `CELL_SIZE` - Snake and food block size  
- `INITIAL_FPS/MAX_FPS` - Speed settings
- `MUSIC_VOLUME/SFX_VOLUME` - Default audio levels
- Colors (RGB tuples)

## 🤝 Contributing

Feel free to contribute improvements:
1. Fork the project
2. Create a feature branch
3. Make your changes  
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source. Feel free to use and modify as needed.

## 🎮 Enjoy Playing!

Have fun with your Snake game! Try to beat the high scores and experiment with the code to add your own features.

---
*Built with Python 3.13, Pygame 2.6.1*

//-Creator tag

// This was all done on VScode then pushed to github //

// In all honesty this is just a way for me to start getting back in to programming after 2-3 years in hopes to land future jobs in the tech industry //


// If anyone sees this hopefully you can give me pointers as the routes I want to get into are, Business/Data Analyst, Software Engineer, Database Admin, Cloud Engineer //
