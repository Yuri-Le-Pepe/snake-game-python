#!/usr/bin/env python3
"""
Snake Game - Classic Snake Game Implementation
Use arrow keys to control the snake and eat the red food to grow!
"""

import pygame
import random
import sys
import json
import os
from datetime import datetime
import math
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 128, 0)
GRAY = (128, 128, 128)

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_WIDTH = WINDOW_WIDTH // CELL_SIZE
CELL_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Game speed (frames per second)
INITIAL_FPS = 5  # Start slower
MAX_FPS = 20     # Maximum speed
CURRENT_FPS = INITIAL_FPS

# High score file
HIGHSCORE_FILE = 'snake_highscores.json'

# Audio settings
SOUND_ENABLED = True
MUSIC_VOLUME = 0.3
SFX_VOLUME = 0.5

class Snake:
    def __init__(self):
        """Initialize the snake"""
        self.positions = [(CELL_WIDTH // 2, CELL_HEIGHT // 2)]  # Start in center
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        
    def move(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= CELL_WIDTH or
            new_head[1] < 0 or new_head[1] >= CELL_HEIGHT):
            return False  # Game over
        
        # Check self collision
        if new_head in self.positions:
            return False  # Game over
        
        self.positions.insert(0, new_head)
        
        # Remove tail unless growing
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
    
    def change_direction(self, new_direction):
        """Change snake direction, preventing 180-degree turns"""
        dx, dy = self.direction
        new_dx, new_dy = new_direction
        
        # Prevent moving in opposite direction
        if (dx, dy) != (-new_dx, -new_dy):
            self.direction = new_direction
    
    def grow_snake(self):
        """Make the snake grow on next move"""
        self.grow = True
    
    def draw(self, screen):
        """Draw the snake on the screen"""
        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Head is brighter green, body is darker green
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, rect)
            # Add border to snake segments
            pygame.draw.rect(screen, BLACK, rect, 1)

class Food:
    def __init__(self, snake_positions):
        """Initialize food at a random position not occupied by snake"""
        self.position = self.generate_position(snake_positions)
    
    def generate_position(self, snake_positions):
        """Generate a random position for food"""
        while True:
            x = random.randint(0, CELL_WIDTH - 1)
            y = random.randint(0, CELL_HEIGHT - 1)
            if (x, y) not in snake_positions:
                return (x, y)
    
    def draw(self, screen):
        """Draw the food on the screen"""
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)
        # Add a small border
        pygame.draw.rect(screen, BLACK, rect, 1)

class HighScoreManager:
    def __init__(self, filename=HIGHSCORE_FILE):
        """Initialize high score manager"""
        self.filename = filename
        self.high_scores = self.load_high_scores()
    
    def load_high_scores(self):
        """Load high scores from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    scores = json.load(f)
                    # Ensure we have the right format (backward compatibility)
                    if isinstance(scores, list) and all('score' in s and 'date' in s for s in scores):
                        # Add default name for old scores without names
                        for score in scores:
                            if 'name' not in score:
                                score['name'] = 'Anonymous'
                        return scores
            except (json.JSONDecodeError, KeyError):
                pass
        # Return empty list if file doesn't exist or is corrupted
        return []
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def add_score(self, score, name="Anonymous"):
        """Add a new score and return True if it's a high score"""
        is_high_score = len(self.high_scores) < 5 or score > min(s['score'] for s in self.high_scores)
        
        if is_high_score:
            # Add new score with name and timestamp
            new_score = {
                'score': score,
                'name': name[:12],  # Limit name to 12 characters
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            self.high_scores.append(new_score)
            # Sort by score (highest first) and keep only top 5
            self.high_scores.sort(key=lambda x: x['score'], reverse=True)
            self.high_scores = self.high_scores[:5]
            self.save_high_scores()
        
        return is_high_score
    
    def get_top_scores(self, count=5):
        """Get top scores"""
        return self.high_scores[:count]
    
    def is_high_score(self, score):
        """Check if score would be a high score"""
        return len(self.high_scores) < 5 or score > min(s['score'] for s in self.high_scores)

class AudioManager:
    def __init__(self):
        """Initialize audio manager with generated sounds"""
        self.sound_enabled = SOUND_ENABLED
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.sounds = {}
        self.generate_sounds()
        self.start_background_music()
    
    def generate_sounds(self):
        """Generate sound effects programmatically"""
        if not HAS_NUMPY:
            print("Warning: NumPy not available - audio disabled")
            self.sound_enabled = False
            return
            
        try:
            # Food eat sound - upward chirp
            eat_sound = self.create_tone_sequence([
                (400, 0.1), (600, 0.1), (800, 0.1)
            ])
            if eat_sound:
                self.sounds['eat'] = eat_sound
            
            # Game over sound - downward tone
            game_over_sound = self.create_tone_sequence([
                (400, 0.3), (300, 0.3), (200, 0.4)
            ])
            if game_over_sound:
                self.sounds['game_over'] = game_over_sound
            
            # High score sound - victory fanfare
            high_score_sound = self.create_tone_sequence([
                (523, 0.2), (659, 0.2), (784, 0.2), (1047, 0.4)
            ])
            if high_score_sound:
                self.sounds['high_score'] = high_score_sound
            
            # Level up sound - ascending notes
            level_up_sound = self.create_tone_sequence([
                (440, 0.15), (554, 0.15), (659, 0.2)
            ])
            if level_up_sound:
                self.sounds['level_up'] = level_up_sound
            
        except Exception as e:
            print(f"Warning: Could not generate sounds: {e}")
            self.sound_enabled = False
    
    def create_tone_sequence(self, notes):
        """Create a sequence of tones"""
        if not HAS_NUMPY:
            return None
            
        sample_rate = 22050
        total_duration = sum(duration for _, duration in notes)
        total_frames = int(sample_rate * total_duration)
        
        # Create stereo sound array using numpy
        sound_array = np.zeros((total_frames, 2), dtype=np.int16)
        
        frame_pos = 0
        for frequency, duration in notes:
            frames = int(sample_rate * duration)
            for i in range(frames):
                if frame_pos + i < total_frames:
                    # Generate sine wave with fade in/out
                    t = i / sample_rate
                    fade = min(1.0, min(i / (sample_rate * 0.01), (frames - i) / (sample_rate * 0.01)))
                    amplitude = int(fade * 16000 * math.sin(2 * math.pi * frequency * t))
                    sound_array[frame_pos + i] = [amplitude, amplitude]
            frame_pos += frames
        
        # Convert to pygame sound
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume)
        return sound
    
    def start_background_music(self):
        """Start simple background music"""
        try:
            # Create a simple looping melody
            notes = [
                (330, 0.5), (392, 0.5), (440, 0.5), (392, 0.5),
                (330, 0.5), (294, 0.5), (330, 1.0),
                (392, 0.5), (440, 0.5), (494, 0.5), (440, 0.5),
                (392, 0.5), (330, 0.5), (392, 1.0)
            ]
            
            background_music = self.create_background_melody(notes)
            # Note: pygame.mixer.music is better for long music files,
            # but for our generated music, we'll use a different approach
            self.background_channel = pygame.mixer.Channel(0)
            
        except Exception as e:
            print(f"Warning: Could not create background music: {e}")
    
    def create_background_melody(self, notes):
        """Create background melody"""
        if not HAS_NUMPY:
            return None
            
        sample_rate = 22050
        total_duration = sum(duration for _, duration in notes)
        total_frames = int(sample_rate * total_duration)
        
        # Create stereo sound array using numpy
        sound_array = np.zeros((total_frames, 2), dtype=np.int16)
        
        frame_pos = 0
        for frequency, duration in notes:
            frames = int(sample_rate * duration)
            for i in range(frames):
                if frame_pos + i < total_frames:
                    t = i / sample_rate
                    # Soft sine wave for background
                    amplitude = int(8000 * math.sin(2 * math.pi * frequency * t))
                    sound_array[frame_pos + i] = [amplitude, amplitude]
            frame_pos += frames
        
        sound = pygame.sndarray.make_sound(sound_array)
        sound.set_volume(self.music_volume)
        return sound
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.sound_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Warning: Could not play sound {sound_name}: {e}")
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            pygame.mixer.stop()
        return self.sound_enabled
    
    def adjust_music_volume(self, change):
        """Adjust music volume"""
        self.music_volume = max(0.0, min(1.0, self.music_volume + change))
        return self.music_volume
    
    def adjust_sfx_volume(self, change):
        """Adjust sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + change))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
        return self.sfx_volume

class Game:
    def __init__(self):
        """Initialize the game"""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Use Arrow Keys to Play!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.medium_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.high_score_manager = HighScoreManager()
        self.audio_manager = AudioManager()
        self.show_high_scores = False
        self.new_high_score = False
        self.entering_name = False
        self.player_name = ""
        self.name_cursor_visible = True
        self.cursor_timer = 0
        self.show_audio_settings = False
        self.last_speed_level = 1
        self.reset_game()
    
    def reset_game(self):
        """Reset the game to initial state"""
        global CURRENT_FPS
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.show_high_scores = False
        self.new_high_score = False
        self.entering_name = False
        self.player_name = ""
        self.show_audio_settings = False
        self.last_speed_level = 1
        CURRENT_FPS = INITIAL_FPS  # Reset speed to initial slow speed
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if self.entering_name:
                        # Handle name input
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            # Submit the name
                            name = self.player_name.strip() if self.player_name.strip() else "Anonymous"
                            self.high_score_manager.add_score(self.score, name)
                            self.entering_name = False
                            self.new_high_score = True
                            # Play high score celebration sound again
                            self.audio_manager.play_sound('high_score')
                        elif event.key == pygame.K_BACKSPACE:
                            # Remove last character
                            self.player_name = self.player_name[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            # Cancel name entry, use Anonymous
                            self.high_score_manager.add_score(self.score, "Anonymous")
                            self.entering_name = False
                            self.new_high_score = True
                        elif len(self.player_name) < 12:  # Limit name length
                            # Add character to name
                            if event.unicode.isprintable() and event.unicode not in ['\r', '\n']:
                                self.player_name += event.unicode
                    else:
                        if event.key == pygame.K_SPACE:
                            if self.show_high_scores:
                                self.show_high_scores = False
                            else:
                                self.reset_game()
                        elif event.key == pygame.K_h:
                            self.show_high_scores = not self.show_high_scores
                        elif event.key == pygame.K_m:
                            self.show_audio_settings = not self.show_audio_settings
                        elif event.key == pygame.K_ESCAPE:
                            return False
                else:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_m:
                        self.show_audio_settings = not self.show_audio_settings
                    elif event.key == pygame.K_s and self.show_audio_settings:
                        enabled = self.audio_manager.toggle_sound()
                        print(f"Sound {'enabled' if enabled else 'disabled'}")
                    elif event.key == pygame.K_UP and self.show_audio_settings:
                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            vol = self.audio_manager.adjust_sfx_volume(0.1)
                            print(f"SFX Volume: {vol:.1f}")
                        else:
                            vol = self.audio_manager.adjust_music_volume(0.1)
                            print(f"Music Volume: {vol:.1f}")
                    elif event.key == pygame.K_DOWN and self.show_audio_settings:
                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            vol = self.audio_manager.adjust_sfx_volume(-0.1)
                            print(f"SFX Volume: {vol:.1f}")
                        else:
                            vol = self.audio_manager.adjust_music_volume(-0.1)
                            print(f"Music Volume: {vol:.1f}")
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True
    
    def update(self):
        """Update game state"""
        if not self.game_over and not self.paused:
            # Move snake
            if not self.snake.move():
                self.game_over = True
                # Play game over sound
                self.audio_manager.play_sound('game_over')
                
                # Check if it's a potential high score
                if self.high_score_manager.is_high_score(self.score):
                    self.entering_name = True
                    self.player_name = ""
                    self.new_high_score = False  # Will be set to True after name entry
                    self.audio_manager.play_sound('high_score')
                else:
                    self.new_high_score = False
                return
            
            # Check if snake ate food
            if self.snake.positions[0] == self.food.position:
                self.snake.grow_snake()
                self.score += 10
                self.food = Food(self.snake.positions)
                
                # Play eat sound
                self.audio_manager.play_sound('eat')
                
                # Increase speed gradually as score increases
                global CURRENT_FPS
                # Increase speed every 30 points (every 3 food items)
                speed_increase = self.score // 30
                new_speed_level = speed_increase + 1
                
                # Play level up sound if speed increased
                if new_speed_level > self.last_speed_level:
                    self.audio_manager.play_sound('level_up')
                    self.last_speed_level = new_speed_level
                
                CURRENT_FPS = min(MAX_FPS, INITIAL_FPS + speed_increase)
    
    def draw(self):
        """Draw everything on the screen"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Update cursor blink timer
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 30 frames
            self.name_cursor_visible = not self.name_cursor_visible
            self.cursor_timer = 0
        
        # Draw grid (optional, for visual appeal)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        if not self.game_over:
            # Draw snake and food
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw speed and level
            speed_level = (CURRENT_FPS - INITIAL_FPS) + 1
            speed_text = self.font.render(f"Speed: {CURRENT_FPS} (Level {speed_level})", True, WHITE)
            self.screen.blit(speed_text, (10, 50))
            
            # Draw next speed up indicator
            points_needed = 30 - (self.score % 30)
            if CURRENT_FPS < MAX_FPS:
                next_speed_text = pygame.font.Font(None, 24).render(f"Next speed up in {points_needed} points", True, YELLOW)
                self.screen.blit(next_speed_text, (10, 85))
            else:
                max_speed_text = pygame.font.Font(None, 24).render("Maximum speed reached!", True, YELLOW)
                self.screen.blit(max_speed_text, (10, 85))
            
            if self.paused:
                # Draw pause message
                pause_text = self.large_font.render("PAUSED", True, YELLOW)
                pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
                
                resume_text = self.font.render("Press SPACE to resume", True, WHITE)
                resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
                self.screen.blit(resume_text, resume_rect)
        else:
            if self.entering_name:
                # Draw name entry screen
                self.draw_name_entry_screen()
            elif self.show_audio_settings:
                # Draw audio settings screen
                self.draw_audio_settings_screen()
            elif self.show_high_scores:
                # Draw high scores screen
                self.draw_high_scores_screen()
            else:
                # Draw game over screen
                y_offset = -80 if self.new_high_score else -50
                
                game_over_text = self.large_font.render("GAME OVER", True, RED)
                game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
                self.screen.blit(game_over_text, game_over_rect)
                
                # Show new high score message if applicable
                if self.new_high_score:
                    new_high_text = self.medium_font.render("🎉 NEW HIGH SCORE! 🎉", True, YELLOW)
                    new_high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
                    self.screen.blit(new_high_text, new_high_rect)
                
                final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
                final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(final_score_text, final_score_rect)
                
                # Show current high score
                top_scores = self.high_score_manager.get_top_scores(1)
                if top_scores:
                    best_score_text = self.small_font.render(f"Best Score: {top_scores[0]['score']} by {top_scores[0]['name']}", True, YELLOW)
                    best_score_rect = best_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
                    self.screen.blit(best_score_text, best_score_rect)
                
                restart_text = self.font.render("Press SPACE to play again", True, WHITE)
                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
                self.screen.blit(restart_text, restart_rect)
                
                controls_text = [
                    "Press H for High Scores | M for Audio Settings",
                    "ESC to quit"
                ]
                for i, text in enumerate(controls_text):
                    control_text = self.small_font.render(text, True, WHITE)
                    control_rect = control_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90 + i * 20))
                    self.screen.blit(control_text, control_rect)
        
        # Draw instructions
        if not self.game_over and not self.paused:
            instructions = [
                "Arrow Keys: Move",
                "Space: Pause",
                "M: Audio Settings",
                "ESC: Quit"
            ]
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 24).render(instruction, True, WHITE)
                self.screen.blit(text, (WINDOW_WIDTH - 150, 10 + i * 25))
        
        # Draw audio status indicator
        if not self.game_over:
            sound_status = "♪" if self.audio_manager.sound_enabled else "♪̸"
            sound_text = self.small_font.render(f"Sound: {sound_status}", True, YELLOW if self.audio_manager.sound_enabled else GRAY)
            self.screen.blit(sound_text, (10, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def draw_audio_settings_screen(self):
        """Draw the audio settings screen"""
        # Title
        title_text = self.large_font.render("♪ AUDIO SETTINGS ♪", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Current settings
        y_pos = 200
        settings = [
            f"Sound Effects: {'ON' if self.audio_manager.sound_enabled else 'OFF'}",
            f"Music Volume: {self.audio_manager.music_volume:.1f}",
            f"SFX Volume: {self.audio_manager.sfx_volume:.1f}"
        ]
        
        for setting in settings:
            setting_text = self.font.render(setting, True, WHITE)
            setting_rect = setting_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(setting_text, setting_rect)
            y_pos += 40
        
        # Controls
        y_pos += 40
        controls = [
            "S: Toggle Sound Effects",
            "↑/↓: Adjust Music Volume",
            "Shift + ↑/↓: Adjust SFX Volume",
            "SPACE: Back to Game Over",
            "ESC: Quit Game"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, WHITE)
            control_rect = control_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(control_text, control_rect)
            y_pos += 30
        
        # Test sound button hint
        test_hint = "Move in-game to test sound effects!"
        test_text = self.small_font.render(test_hint, True, GRAY)
        test_rect = test_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(test_text, test_rect)
    
    def draw_name_entry_screen(self):
        """Draw the name entry screen"""
        # Title
        title_text = self.large_font.render("🎉 NEW HIGH SCORE! 🎉", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Score
        score_text = self.font.render(f"Score: {self.score:,} points", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        instruction_text = self.font.render("Enter your name:", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Name input box
        input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, 290, 300, 50)
        pygame.draw.rect(self.screen, WHITE, input_box, 2)
        pygame.draw.rect(self.screen, BLACK, input_box.inflate(-4, -4))
        
        # Name text
        display_name = self.player_name
        if self.name_cursor_visible and len(display_name) < 12:
            display_name += "|"
        
        name_text = self.font.render(display_name, True, WHITE)
        # Center the text in the input box
        name_x = input_box.centerx - name_text.get_width() // 2
        name_y = input_box.centery - name_text.get_height() // 2
        self.screen.blit(name_text, (name_x, name_y))
        
        # Character limit indicator
        char_count = f"{len(self.player_name)}/12"
        char_text = self.small_font.render(char_count, True, GRAY)
        self.screen.blit(char_text, (input_box.right - 50, input_box.bottom + 5))
        
        # Controls
        controls = [
            "ENTER: Submit name",
            "BACKSPACE: Delete character",
            "ESC: Use 'Anonymous'"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, WHITE)
            control_rect = control_text.get_rect(center=(WINDOW_WIDTH // 2, 380 + i * 25))
            self.screen.blit(control_text, control_rect)
    
    def draw_high_scores_screen(self):
        """Draw the high scores screen"""
        # Title
        title_text = self.large_font.render("🏆 HIGH SCORES 🏆", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Get top scores
        top_scores = self.high_score_manager.get_top_scores(5)
        
        if not top_scores:
            no_scores_text = self.font.render("No high scores yet!", True, WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(no_scores_text, no_scores_rect)
            
            play_text = self.font.render("Play a game to set the first score!", True, WHITE)
            play_rect = play_text.get_rect(center=(WINDOW_WIDTH // 2, 240))
            self.screen.blit(play_text, play_rect)
        else:
            # Draw scores
            start_y = 180
            for i, score_data in enumerate(top_scores):
                rank = i + 1
                score = score_data['score']
                name = score_data.get('name', 'Anonymous')
                date = score_data['date']
                
                # Rank and score
                if rank == 1:
                    color = YELLOW  # Gold for first place
                    rank_text = f"🥇 {rank}."
                elif rank == 2:
                    color = WHITE   # Silver for second
                    rank_text = f"🥈 {rank}."
                elif rank == 3:
                    color = (205, 127, 50)  # Bronze for third
                    rank_text = f"🥉 {rank}."
                else:
                    color = WHITE
                    rank_text = f"   {rank}."
                
                score_line = f"{rank_text} {score:,} points - {name}"
                score_text = self.font.render(score_line, True, color)
                self.screen.blit(score_text, (120, start_y + i * 50))
                
                # Date
                date_text = self.small_font.render(date, True, GRAY)
                self.screen.blit(date_text, (120, start_y + i * 50 + 25))
        
        # Instructions
        back_text = self.font.render("Press SPACE to go back", True, WHITE)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))
        self.screen.blit(back_text, back_rect)
        
        play_again_text = self.small_font.render("Press ESC to quit game", True, WHITE)
        play_again_rect = play_again_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(play_again_text, play_again_rect)
    
    def run(self):
        """Main game loop"""
        print("🐍 Snake Game Started!")
        print("Use arrow keys to move, SPACE to pause, ESC to quit")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(CURRENT_FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    print("🐍 Welcome to Snake Game!")
    print("=" * 40)
    print("Controls:")
    print("  ↑ ↓ ← → : Move snake")
    print("  SPACE   : Pause/Resume")
    print("  ESC     : Quit game")
    print("=" * 40)
    print("Starting game...")
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
# this is just a test for programming
#Author- Yuri