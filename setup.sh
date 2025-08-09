#!/bin/bash
# Snake Game Setup Script for VS Code

echo "🐍 Snake Game - VS Code Setup"
echo "=============================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 To run the Snake game:"
echo "   1. Open this folder in VS Code: code ."
echo "   2. Select Python interpreter: Ctrl+Shift+P → 'Python: Select Interpreter' → Choose ./venv/bin/python"
echo "   3. Press F5 to run, or use Ctrl+Shift+B to build"
echo ""
echo "🎮 Enjoy your Snake game!"
