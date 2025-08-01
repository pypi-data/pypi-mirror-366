#!/usr/bin/env python3
"""
PSST Hybrid Integration
Combines system message and expansion approaches for optimal reliability and compression
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Union
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

from psst_ultimate import UltimatePsstCompiler


class PsstHybridIntegration:
    """Hybrid PSST integration that chooses the best approach for each prompt."""
    
    def __init__(self, api_key: str = None, glossary_path: str = "ultimate_glossary.json"):
        """Initialize hybrid PSST integration."""
        self.compiler = UltimatePsstCompiler(glossary_path)
        
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('OPENAI_API_KEY')
        
        # Define complex symbols that might confuse LLMs (use expansion)
        self.complex_symbols = [
            '📜',  # Long legal phrase
            '⚔️',  # Long legal phrase  
            '🏗️',  # Long legal phrase
            '🔍',  # Medium legal phrase
            '⚖️'   # Medium phrase
        ]
        
        # Simple symbols that LLMs handle well (use system message)
        self.simple_symbols = [
            '📄',  # Short phrase
            '🎨',  # Short phrase
            '📋',  # Short phrase
            '⊕summarize',  # Text symbol
            '℧tone_friendly',  # Text symbol
            '⊗legal_brief'  # Text symbol
        ]
        
        # Response symbols for PSST responses
        self.response_symbols = {
            '✅': 'I understand and will proceed as requested.',
            '📝': 'Here is my analysis:',
            '🔍': 'Key findings:',
            '📊': 'Summary:',
            '💡': 'Important insight:',
            '⚠️': 'Note:',
            '🎯': 'Recommendation:',
            '📋': 'Next steps:',
            '🔗': 'Related considerations:',
            '📈': 'Impact assessment:'
        }
    
    def _build_system_message(self, used_symbols: list = None) -> str:
        """Build efficient system message with only needed symbols."""
        
        if used_symbols is None:
            used_symbols = list(self.compiler.glossary.keys())
        
        system_msg = """You are an AI assistant that understands PSST (Prompt Symbol Standard Technology) symbols. 

PSST symbols are Unicode characters that represent longer phrases. Here are the symbols you should understand:

"""
        
        for symbol in used_symbols:
            if symbol in self.compiler.glossary:
                phrase = self.compiler.glossary[symbol]
                system_msg += f"{symbol} = \"{phrase}\"\n"
        
        system_msg += """
When you see these symbols in a prompt, interpret them as their full meanings. For example, if you see "⚖️", treat it as if the user said "You are a legal assistant. Highlight key rulings and arguments in the case below."

Respond naturally as if the user had written the full phrases instead of the symbols."""
        
        return system_msg
    
    def _analyze_prompt_complexity(self, compressed_prompt: str) -> dict:
        """Analyze the complexity of a compressed prompt."""
        
        analysis = {
            'has_complex_symbols': False,
            'has_simple_symbols': False,
            'complex_symbols_found': [],
            'simple_symbols_found': [],
            'total_symbols': 0,
            'recommended_approach': 'system_message'
        }
        
        # Check for complex symbols
        for symbol in self.complex_symbols:
            if symbol in compressed_prompt:
                analysis['has_complex_symbols'] = True
                analysis['complex_symbols_found'].append(symbol)
                analysis['total_symbols'] += 1
        
        # Check for simple symbols
        for symbol in self.simple_symbols:
            if symbol in compressed_prompt:
                analysis['has_simple_symbols'] = True
                analysis['simple_symbols_found'].append(symbol)
                analysis['total_symbols'] += 1
        
        # Determine recommended approach
        if analysis['has_complex_symbols']:
            analysis['recommended_approach'] = 'expansion'
        elif analysis['has_simple_symbols']:
            analysis['recommended_approach'] = 'system_message'
        else:
            analysis['recommended_approach'] = 'system_message'  # Default
        
        return analysis
    
    def _call_openai_api(self, messages: List[Dict], model: str = "gpt-4") -> Dict:
        """Call OpenAI API with error handling."""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def send_hybrid_prompt(self, prompt: str, model: str = "gpt-4", 
                          force_expansion: bool = False, 
                          use_psst_response: bool = False) -> dict:
        """Send prompt using hybrid approach - system message for simple, expansion for complex."""
        
        # Compress the prompt
        compressed_prompt = self.compiler.compress(prompt)
        
        # Analyze complexity
        analysis = self._analyze_prompt_complexity(compressed_prompt)
        
        # Add PSST response instruction if requested
        if use_psst_response:
            psst_instruction = "\n\nIMPORTANT: Respond using PSST symbols where possible. Use these symbols:\n"
            for symbol, meaning in self.response_symbols.items():
                psst_instruction += f"{symbol} = \"{meaning}\"\n"
            psst_instruction += "\nUse these symbols in your response to make it more concise while maintaining clarity."
            prompt += psst_instruction
        
        # Determine approach
        if force_expansion or analysis['recommended_approach'] == 'expansion':
            approach = "expansion"
            expanded_prompt = self.compiler.expand(compressed_prompt)
            
            messages = [{"role": "user", "content": expanded_prompt}]
            
        else:
            approach = "system_message"
            used_symbols = analysis['simple_symbols_found']
            system_message = self._build_system_message(used_symbols)
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": compressed_prompt}
            ]
        
        # Send to OpenAI
        response = self._call_openai_api(messages, model)
        
        if "error" in response:
            return {
                'error': response['error'],
                'approach': approach,
                'compressed_prompt': compressed_prompt,
                'analysis': analysis
            }
        
        result = {
            'approach': approach,
            'compressed_prompt': compressed_prompt,
            'expanded_prompt': expanded_prompt if approach == "expansion" else None,
            'system_message': system_message if approach == "system_message" else None,
            'analysis': analysis,
            'response': response['choices'][0]['message']['content'],
            'usage': response.get('usage', {}),
            'model': model
        }
        
        return result
    
    def send_with_psst_response(self, prompt: str, model: str = "gpt-4") -> dict:
        """Send prompt and ask AI to respond using PSST symbols."""
        
        return self.send_hybrid_prompt(prompt, model, use_psst_response=True)


def demo_hybrid_integration():
    """Demonstrate hybrid PSST integration."""
    
    integration = PsstHybridIntegration()
    
    # Test prompts
    test_prompts = [
        # Simple prompt (should use system message)
        "Summarize the following text in 3 bullet points.",
        
        # Complex prompt (should use expansion)
        "The plaintiff filed a motion for summary judgment claiming breach of contract. The defendant argues that the contract was void due to mutual mistake regarding the property's zoning classification.",
        
        # Mixed prompt (should use system message)
        "Please act as a legal assistant. Highlight key rulings and arguments in the case below. Case Details: The court must determine whether the evidence shows a genuine issue of material fact."
    ]
    
    print("=== PSST Hybrid Integration Demo ===")
    print()
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Test {i}:")
        print(f"Original: {prompt[:100]}...")
        
        result = integration.send_hybrid_prompt(prompt)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Approach: {result['approach']}")
            print(f"📊 Analysis: {result['analysis']['recommended_approach']}")
            print(f"🔍 Complex symbols: {result['analysis']['complex_symbols_found']}")
            print(f"📝 Simple symbols: {result['analysis']['simple_symbols_found']}")
            print(f"💬 Response: {result['response'][:100]}...")
            print(f"📈 Usage: {result['usage']}")
        
        print("-" * 50)
        print()


def demo_psst_response():
    """Demonstrate PSST response functionality."""
    
    integration = PsstHybridIntegration()
    
    # Test prompt with PSST response
    test_prompt = """Please act as a legal assistant. Highlight key rulings and arguments in the case below. 

Case Details:
The plaintiff filed a motion for summary judgment claiming breach of contract. The defendant argues that the contract was void due to mutual mistake regarding the property's zoning classification. The court must determine whether the evidence shows a genuine issue of material fact.

Please provide your analysis using PSST symbols for conciseness."""
    
    print("=== PSST Response Demo ===")
    print()
    print("Original prompt:")
    print(test_prompt)
    print()
    
    result = integration.send_with_psst_response(test_prompt)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ AI Response with PSST symbols:")
        print(result['response'])
        print()
        print(f"📊 Approach used: {result['approach']}")
        print(f"📈 Token usage: {result['usage']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PSST Hybrid Integration Demo")
    parser.add_argument("--demo", choices=["hybrid", "psst-response"], 
                       help="Run specific demo")
    parser.add_argument("--prompt", help="Test with custom prompt")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--force-expansion", action="store_true", 
                       help="Force expansion approach")
    parser.add_argument("--psst-response", action="store_true", 
                       help="Ask AI to respond using PSST symbols")
    
    args = parser.parse_args()
    
    integration = PsstHybridIntegration()
    
    if args.demo == "hybrid":
        demo_hybrid_integration()
    elif args.demo == "psst-response":
        demo_psst_response()
    elif args.prompt:
        # Test with custom prompt
        result = integration.send_hybrid_prompt(
            args.prompt, 
            model=args.model,
            force_expansion=args.force_expansion,
            use_psst_response=args.psst_response
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Approach: {result['approach']}")
            print(f"�� Analysis: {result['analysis']}")
            print(f"💬 Response: {result['response']}")
            print(f"📈 Usage: {result['usage']}")
    else:
        # Run both demos
        demo_hybrid_integration()
        print("\n" + "="*50 + "\n")
        demo_psst_response()
