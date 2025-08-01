#!/usr/bin/env python3
"""
test_enhanced_features.py: Test the new enhanced PSST features
"""

import os
import sys
import subprocess
from pathlib import Path

def test_verbose_mode():
    """Test the new verbose mode with token validation."""
    print("🧪 Testing Enhanced PSST Features")
    print("=" * 50)
    
    # Test 1: Basic verbose mode
    print("\n1️⃣ Testing verbose mode with token validation...")
    try:
        result = subprocess.run([
            "python3", "psst-openai", 
            "Explain quantum computing in simple terms",
            "--session", "test_verbose",
            "--verbose",
            "--show-tokens"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Verbose mode test passed")
            print("📝 Output preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ Verbose mode test failed")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_cost_tracker():
    """Test the new cost tracking functionality."""
    print("\n2️⃣ Testing cost tracker...")
    try:
        result = subprocess.run([
            "python3", "psst_cost_tracker.py",
            "--session", "test_verbose",
            "--verbose"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Cost tracker test passed")
            print("📊 Analysis preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ Cost tracker test failed")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_session_management():
    """Test enhanced session management with unique IDs."""
    print("\n3️⃣ Testing enhanced session management...")
    try:
        # List sessions to see the new ID format
        result = subprocess.run([
            "python3", "psst-openai",
            "--list-sessions"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Session management test passed")
            print("📋 Sessions with IDs:")
            print(result.stdout)
        else:
            print("❌ Session management test failed")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_token_validation():
    """Test token validation for a specific session."""
    print("\n4️⃣ Testing token validation...")
    try:
        result = subprocess.run([
            "python3", "psst_cost_tracker.py",
            "--session", "test_verbose",
            "--validate"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Token validation test passed")
            print("🔍 Validation preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ Token validation test failed")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_feature_summary():
    """Show a summary of the new features."""
    print("\n🎉 Enhanced Features Summary")
    print("=" * 50)
    print("✅ Added Features:")
    print("   • Unique session identifiers (UUID-based)")
    print("   • Verbose token tracking and validation")
    print("   • Cost tracking integration with OpenAI admin API")
    print("   • Detailed token analysis and estimation")
    print("   • Response validation (sent vs received)")
    print("   • Enhanced session management with IDs")
    print("   • Cost estimation for different models")
    print("   • Token accuracy validation")
    
    print("\n🔧 New Commands:")
    print("   • psst-openai --verbose (show detailed token info)")
    print("   • psst-openai --cost-tracking (enable cost tracking)")
    print("   • psst_cost_tracker.py (standalone cost analysis)")
    print("   • psst_cost_tracker.py --validate (token validation)")
    
    print("\n📊 What's Missing (Now Implemented):")
    print("   ✅ Integration of cost tracking API")
    print("   ✅ Verbose mode to show actual tokens/words")
    print("   ✅ Response validation showing sent vs received")
    print("   ✅ Unique conversation thread identifiers")
    print("   ✅ Token validation and accuracy checking")

def main():
    """Run all tests."""
    print("🚀 Testing Enhanced PSST Features")
    print("=" * 50)
    
    # Check if required files exist
    required_files = ["psst-openai", "psst_cost_tracker.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file not found: {file}")
            return
    
    # Run tests
    test_verbose_mode()
    test_cost_tracker()
    test_session_management()
    test_token_validation()
    
    # Show summary
    show_feature_summary()
    
    print("\n🎯 All tests completed!")
    print("💡 Try these commands to explore the new features:")
    print("   python3 psst-openai 'Hello' --verbose --show-tokens")
    print("   python3 psst_cost_tracker.py --verbose")
    print("   python3 psst_cost_tracker.py --session default --validate")

if __name__ == "__main__":
    main() 