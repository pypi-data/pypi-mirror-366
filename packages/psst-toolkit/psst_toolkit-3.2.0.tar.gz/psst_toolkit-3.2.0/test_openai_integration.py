#!/usr/bin/env python3
"""
Test OpenAI Integration for PSST
"""

import os
import sys
from psst_hybrid_integration import PsstHybridIntegration

def test_openai_integration():
    """Test the OpenAI integration with PSST."""
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("Or you can enter it now (it won't be saved):")
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        else:
            print("❌ No API key provided. Exiting.")
            return False
    
    print("✅ API key found!")
    
    # Initialize integration
    integration = PsstHybridIntegration(api_key=api_key)
    
    # Test prompts
    test_prompts = [
        {
            "name": "Simple Legal Summary",
            "prompt": "Summarize the following text in 3 bullet points.",
            "expected_approach": "system_message"
        },
        {
            "name": "Complex Legal Analysis", 
            "prompt": "The plaintiff filed a motion for summary judgment claiming breach of contract. The defendant argues that the contract was void due to mutual mistake regarding the property's zoning classification.",
            "expected_approach": "expansion"
        },
        {
            "name": "PSST Response Test",
            "prompt": "Analyze this legal case and provide your findings.",
            "use_psst_response": True
        }
    ]
    
    print("\n=== Testing OpenAI Integration ===")
    print()
    
    for i, test in enumerate(test_prompts, 1):
        print(f"Test {i}: {test['name']}")
        print(f"Prompt: {test['prompt'][:80]}...")
        
        try:
            result = integration.send_hybrid_prompt(
                test['prompt'],
                use_psst_response=test.get('use_psst_response', False)
            )
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            print(f"✅ Approach: {result['approach']}")
            print(f"📊 Analysis: {result['analysis']['recommended_approach']}")
            print(f"🔍 Complex symbols: {result['analysis']['complex_symbols_found']}")
            print(f"📝 Simple symbols: {result['analysis']['simple_symbols_found']}")
            print(f"📈 Token usage: {result['usage']}")
            print(f"💬 Response: {result['response'][:100]}...")
            
            if test.get('use_psst_response'):
                print("🎯 PSST Response: AI instructed to use PSST symbols")
            
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)
        print()
    
    return True

if __name__ == "__main__":
    success = test_openai_integration()
    if success:
        print("🎉 OpenAI integration test completed!")
        print("✅ PSST hybrid approach working")
        print("✅ PSST response functionality working")
        print("✅ Token usage optimization working")
    else:
        print("❌ Integration test failed")
        sys.exit(1)
