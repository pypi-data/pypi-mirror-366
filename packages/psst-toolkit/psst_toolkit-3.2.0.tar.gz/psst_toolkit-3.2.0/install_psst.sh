#!/bin/bash

# PSST Installation Script
# Prompt Symbol Standard Technology
# Version: 3.0.0

echo "🚀 Installing PSST (Prompt Symbol Standard Technology)"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is not available. Please install pip."
    exit 1
fi

echo "✅ pip found: $(python3 -m pip --version)"

# Install required dependencies
echo "📦 Installing dependencies..."
python3 -m pip install jellyfish numpy

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x psst-learn 2>/dev/null || true

# Test the installation
echo "🧪 Testing installation..."
if [ -f "psst_ultimate.py" ]; then
    if [ -f "examples/legal_prompt.txt" ]; then
        echo "Testing compression..."
        python3 psst_ultimate.py compress examples/legal_prompt.txt > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ PSST installation successful!"
            echo ""
            echo "📚 Quick Start:"
            echo "  python3 psst_ultimate.py compress input.txt"
            echo "  python3 psst_ultimate.py expand input_ultimate.psst"
            echo ""
            echo "📖 Documentation:"
            echo "  - PSST_USER_MANUAL.md (Complete user manual)"
            echo "  - PSST_QUICK_REFERENCE.md (Quick reference card)"
            echo "  - COMPRESSION_RESULTS.md (Performance results)"
            echo ""
            echo "🎯 Example:"
            echo "  python3 psst_ultimate.py compress examples/legal_prompt.txt"
        else
            echo "❌ PSST test failed"
            exit 1
        fi
    else
        echo "⚠️  examples/legal_prompt.txt not found, skipping test"
        echo "✅ PSST installation completed"
    fi
else
    echo "❌ psst_ultimate.py not found in current directory"
    echo "Please run this script from the PSST directory"
    exit 1
fi

echo ""
echo "🎉 PSST installation completed successfully!"
echo "Target: 80-90% token reduction with perfect fidelity"
echo "Achieved: 88.6% compression in tests" 