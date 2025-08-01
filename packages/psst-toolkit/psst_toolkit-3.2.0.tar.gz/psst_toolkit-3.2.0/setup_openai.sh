#!/bin/bash

echo "=== PSST OpenAI Integration Setup ==="
echo

# Check if API key is already set
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY is already set"
    echo "Current key: ${OPENAI_API_KEY:0:10}..."
else
    echo "❌ OPENAI_API_KEY not found"
    echo
    echo "To set your OpenAI API key, run one of these commands:"
    echo
    echo "Option 1 - Set for current session:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo
    echo "Option 2 - Add to your shell profile (recommended):"
    echo "echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.zshrc"
    echo "source ~/.zshrc"
    echo
    echo "Option 3 - Create a .env file:"
    echo "echo 'OPENAI_API_KEY=your-api-key-here' > .env"
    echo
    echo "You can get your API key from: https://platform.openai.com/api-keys"
fi

echo
echo "Testing integration..."
python3 test_openai_integration.py
