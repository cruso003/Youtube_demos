#!/bin/bash

# Universal AI Agent Platform - Setup Script
echo "🚀 Universal AI Agent Platform - Setup"
echo "======================================"

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $python_version"

# Create virtual environment (optional but recommended)
read -p "🤔 Create virtual environment? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask flask-cors python-dotenv

# Optional: Install LiveKit dependencies for full functionality
read -p "🤔 Install LiveKit dependencies for full agent functionality? (y/n): " install_livekit
if [[ $install_livekit == "y" || $install_livekit == "Y" ]]; then
    echo "📦 Installing LiveKit dependencies..."
    pip install "livekit-agents[deepgram,openai,cartesia,silero,turn-detector]~=1.0"
    pip install "livekit-plugins-noise-cancellation~=0.2"
    echo "✅ LiveKit dependencies installed!"
else
    echo "⚠️  LiveKit dependencies skipped. Some features will not work."
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created! Please edit it with your API keys."
else
    echo "📝 .env file already exists."
fi

# Run tests
echo "🧪 Running core tests..."
python test_core.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Start API Gateway: python api_gateway/main.py"
echo "   3. Try demo apps:"
echo "      - python demos/language_learning/app.py"
echo "      - python demos/emergency_services/app.py"
echo ""
echo "📖 Documentation:"
echo "   - API Reference: docs/api.md"
echo "   - Business Adapters: docs/adapters.md" 
echo "   - Client SDKs: docs/sdks.md"