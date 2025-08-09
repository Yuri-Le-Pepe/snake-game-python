#!/usr/bin/env python3
"""
Basic tests for Snake Game components
"""

import unittest
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from snake_game import Snake, Food, HighScoreManager, CELL_WIDTH, CELL_HEIGHT
except ImportError:
    print("Warning: Could not import game modules. Make sure pygame and numpy are installed.")
    Snake = Food = HighScoreManager = None
    CELL_WIDTH = CELL_HEIGHT = 40  # Default values for testing


class TestSnake(unittest.TestCase):
    """Test Snake class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if Snake is None:
            self.skipTest("Snake class not available")
        self.snake = Snake()
    
    def test_snake_initialization(self):
        """Test snake starts in correct position"""
        self.assertEqual(len(self.snake.positions), 1)
        self.assertEqual(self.snake.positions[0], (CELL_WIDTH // 2, CELL_HEIGHT // 2))
        self.assertEqual(self.snake.direction, (1, 0))  # Moving right
        self.assertFalse(self.snake.grow)
    
    def test_snake_movement(self):
        """Test basic snake movement"""
        initial_pos = self.snake.positions[0]
        result = self.snake.move()
        self.assertTrue(result)  # Movement should be successful
        
        # Snake should move one cell right
        expected_pos = (initial_pos[0] + 1, initial_pos[1])
        self.assertEqual(self.snake.positions[0], expected_pos)
    
    def test_direction_change(self):
        """Test direction changes"""
        # Test valid direction change
        self.snake.change_direction((0, -1))  # Up
        self.assertEqual(self.snake.direction, (0, -1))
        
        # Test invalid reverse direction (should not change)
        self.snake.change_direction((0, 1))  # Down (opposite of up)
        self.assertEqual(self.snake.direction, (0, -1))  # Should stay up
    
    def test_snake_growth(self):
        """Test snake growing mechanism"""
        initial_length = len(self.snake.positions)
        self.snake.grow_snake()
        self.assertTrue(self.snake.grow)
        
        # After moving, snake should be longer
        self.snake.move()
        self.assertEqual(len(self.snake.positions), initial_length + 1)
        self.assertFalse(self.snake.grow)  # Grow flag should reset


class TestFood(unittest.TestCase):
    """Test Food class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if Food is None:
            self.skipTest("Food class not available")
        self.snake_positions = [(20, 15), (19, 15), (18, 15)]  # Sample snake
        self.food = Food(self.snake_positions)
    
    def test_food_initialization(self):
        """Test food is created in valid position"""
        self.assertIsNotNone(self.food.position)
        self.assertIsInstance(self.food.position, tuple)
        self.assertEqual(len(self.food.position), 2)
    
    def test_food_not_on_snake(self):
        """Test food doesn't spawn on snake"""
        self.assertNotIn(self.food.position, self.snake_positions)
    
    def test_food_position_valid(self):
        """Test food position is within game bounds"""
        x, y = self.food.position
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)
        self.assertLess(x, CELL_WIDTH)
        self.assertLess(y, CELL_HEIGHT)


class TestHighScoreManager(unittest.TestCase):
    """Test HighScoreManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if HighScoreManager is None:
            self.skipTest("HighScoreManager class not available")
        # Use a test file to avoid affecting real high scores
        self.test_file = "test_highscores.json"
        self.manager = HighScoreManager(self.test_file)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_empty_high_scores(self):
        """Test manager with no existing scores"""
        self.assertEqual(len(self.manager.high_scores), 0)
        self.assertEqual(len(self.manager.get_top_scores()), 0)
    
    def test_add_score(self):
        """Test adding a new high score"""
        result = self.manager.add_score(100, "TestPlayer")
        self.assertTrue(result)  # Should be a high score (empty list)
        
        scores = self.manager.get_top_scores()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['score'], 100)
        self.assertEqual(scores[0]['name'], "TestPlayer")
    
    def test_is_high_score(self):
        """Test high score detection"""
        # Empty list - any score is high
        self.assertTrue(self.manager.is_high_score(10))
        
        # Add some scores
        for score in [100, 80, 60, 40, 20]:
            self.manager.add_score(score, f"Player{score}")
        
        # Test high score detection
        self.assertTrue(self.manager.is_high_score(90))   # Better than 80
        self.assertTrue(self.manager.is_high_score(25))   # Better than 20
        self.assertFalse(self.manager.is_high_score(15))  # Not better than any
    
    def test_top_5_limit(self):
        """Test that only top 5 scores are kept"""
        # Add 7 scores
        for i, score in enumerate([100, 90, 80, 70, 60, 50, 40]):
            self.manager.add_score(score, f"Player{i}")
        
        scores = self.manager.get_top_scores()
        self.assertEqual(len(scores), 5)  # Should only keep 5
        self.assertEqual(scores[0]['score'], 100)  # Highest first
        self.assertEqual(scores[-1]['score'], 60)  # 5th highest


class TestGameConstants(unittest.TestCase):
    """Test game configuration constants"""
    
    def test_game_dimensions(self):
        """Test game dimensions are reasonable"""
        self.assertGreater(CELL_WIDTH, 0)
        self.assertGreater(CELL_HEIGHT, 0)
        self.assertLessEqual(CELL_WIDTH, 100)  # Reasonable upper bound
        self.assertLessEqual(CELL_HEIGHT, 100)


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestSnake))
    suite.addTest(unittest.makeSuite(TestFood))
    suite.addTest(unittest.makeSuite(TestHighScoreManager))
    suite.addTest(unittest.makeSuite(TestGameConstants))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🐍 Snake Game Tests")
    print("==================")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
