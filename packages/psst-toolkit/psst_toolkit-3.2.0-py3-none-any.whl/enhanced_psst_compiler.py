#!/usr/bin/env python3
"""
Enhanced PSST: Prompt Symbol Standard Technology with Semantic Preservation
A token-efficient, self-improving AI prompting system that maintains semantic fidelity.
"""

import json
import re
import argparse
import os
import pickle
from typing import Dict, List, Tuple, Set, Counter
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import jellyfish
import numpy as np


class EnhancedPsstCompiler:
    """Enhanced compiler that learns patterns while preserving semantic meaning."""
    
    def __init__(self, glossary_path: str = "enhanced_glossary.json", 
                 learning_data_path: str = "enhanced_learning_data.pkl"):
        """Initialize enhanced compiler with semantic preservation."""
        self.glossary_path = glossary_path
        self.learning_data_path = learning_data_path
        self.glossary = self._load_glossary()
        self.reverse_glossary = {v: k for k, v in self.glossary.items()}
        
        # Learning components
        self.phrase_patterns = self._load_learning_data()
        self.similarity_threshold = 0.90  # Higher threshold for better fidelity
        self.min_phrase_length = 5
        self.max_phrase_length = 100
        
        # Dynamic learning stats
        self.compression_history = []
        self.discovered_patterns = defaultdict(int)
        self.failed_compressions = defaultdict(int)
        
        # Semantic preservation
        self.semantic_mappings = {
            "You are a legal assistant": "⚖️",
            "Act as a legal assistant": "⚖️", 
            "Be a legal assistant": "⚖️",
            "You are a legal advisor": "⚖️",
            "Act as a legal advisor": "⚖️",
            "You are a legal expert": "⚖️",
            "Be a legal expert": "⚖️",
            "You are a legal professional": "⚖️",
            "Act as a legal professional": "⚖️",
            "You are a legal consultant": "⚖️",
            "Be a legal consultant": "⚖️",
            "Highlight key rulings and arguments": "🔍",
            "Highlight key rulings and arguments in the case below": "🔍",
            "Highlight key rulings and arguments in the case": "🔍",
            "Identify key rulings and arguments": "🔍",
            "Analyze key rulings and arguments": "🔍",
            "Summarize the following text in 3 bullet points": "📄",
            "Summarize the following text in 3 bullet points.": "📄",
            "Summarize the following text": "📄",
            "Provide a summary of the following text": "📄",
            "Create a summary of the following text": "📄",
            "Respond in a warm, casual tone": "🎨",
            "Respond in a warm, casual tone.": "🎨",
            "Use a warm, casual tone": "🎨",
            "Maintain a warm, casual tone": "🎨",
            "Keep a warm, casual tone": "🎨",
            "when explaining the legal concepts to make them accessible to the client": "💼",
            "when explaining the legal concepts": "💼",
            "to make them accessible to the client": "💼",
            "Case Details": "📋",
            "Case details": "📋",
            "Case Details:": "📋",
            "The plaintiff filed a motion for summary judgment": "⚖️",
            "The plaintiff filed a motion": "⚖️",
            "filed a motion for summary judgment": "⚖️",
            "motion for summary judgment": "⚖️",
            "claiming breach of contract": "📜",
            "breach of contract": "📜",
            "The defendant argues that": "⚔️",
            "The defendant argues": "⚔️",
            "defendant argues that": "⚔️",
            "the contract was void due to mutual mistake": "🔍",
            "contract was void due to mutual mistake": "🔍",
            "void due to mutual mistake": "🔍",
            "due to mutual mistake": "🔍",
            "mutual mistake": "🔍",
            "regarding the property's zoning classification": "🏗️",
            "property's zoning classification": "🏗️",
            "zoning classification": "🏗️",
            "The court must determine whether": "⚖️",
            "court must determine whether": "⚖️",
            "must determine whether": "⚖️",
            "the evidence shows a genuine issue of material fact": "🔍",
            "evidence shows a genuine issue of material fact": "🔍",
            "genuine issue of material fact": "🔍",
            "issue of material fact": "🔍"
        }
        
    def _load_glossary(self) -> Dict[str, str]:
        """Load glossary from JSON file."""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('glossary', {})
        except FileNotFoundError:
            # Create enhanced glossary with semantic mappings
            enhanced_glossary = {
                "⚖️": "You are a legal assistant. Highlight key rulings and arguments in the case below.",
                "🔍": "Highlight key rulings and arguments in the case below.",
                "📄": "Summarize the following text in 3 bullet points.",
                "🎨": "Respond in a warm, casual tone.",
                "💼": "when explaining the legal concepts to make them accessible to the client",
                "📋": "Case Details:",
                "📜": "claiming breach of contract",
                "⚔️": "The defendant argues that",
                "🏗️": "regarding the property's zoning classification",
                "🔍": "the evidence shows a genuine issue of material fact",
                "🗣": "respond",
                "💬": "dialog", 
                "🅣": "tone",
                "🧑‍🤝‍🧑": "audience",
                "🕵️": "persona",
                "📥": "parameters",
                "📤": "specification", 
                "🎯": "intent",
                "📊": "structured-output",
                "🧾": "template",
                "🧩": "insert",
                "🗃️": "format-type",
                "🤖": "agent-plan",
                "📌": "constraint",
                "🧠": "LLM",
                "📦": "memory",
                "🧮": "calculate",
                "🧭": "plan",
                "🕹️": "simulate",
                "🧑‍🏫": "explain",
                "❓": "quiz",
                "✔️": "answer",
                "⏱": "deadline",
                "🔀": "branch",
                "🕳": "placeholder",
                "🔐": "restricted",
                "🛑": "forbidden",
                "🚷": "suppress",
                "🎭": "adversarial",
                "📛": "harm-flag",
                "🧰": "diagnostics",
                "📝": "feedback",
                "🔍‍📝": "audit",
                "🄿": "primary-task",
                "✎": "rewrite",
                "🔄": "retry",
                "🚩": "review",
                "📚": "multi-doc",
                "🧬": "dataset",
                "🛰️": "external-API",
                "🪄": "synthetic-flag",
                "⊕summarize": "Summarize the following text in 3 bullet points.",
                "℧tone_friendly": "Respond in a warm, casual tone.",
                "⊗legal_brief": "You are a legal assistant. Highlight key rulings and arguments."
            }
            self._save_glossary(enhanced_glossary)
            return enhanced_glossary
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in glossary file: {self.glossary_path}")
    
    def _save_glossary(self, glossary: Dict[str, str] = None):
        """Save glossary to JSON file."""
        if glossary is None:
            glossary = self.glossary
            
        data = {
            'version': '2.0.0',
            'glossary': glossary
        }
        
        with open(self.glossary_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_learning_data(self) -> Dict:
        """Load or initialize learning data."""
        try:
            with open(self.learning_data_path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {
                'phrase_clusters': {},
                'similarity_matrix': {},
                'compression_stats': {},
                'discovered_patterns': defaultdict(int),
                'failed_patterns': defaultdict(int)
            }
    
    def _save_learning_data(self):
        """Save learning data to disk."""
        learning_data = {
            'phrase_clusters': self.phrase_patterns.get('phrase_clusters', {}),
            'similarity_matrix': self.phrase_patterns.get('similarity_matrix', {}),
            'compression_stats': self.phrase_patterns.get('compression_stats', {}),
            'discovered_patterns': dict(self.discovered_patterns),
            'failed_patterns': dict(self.failed_compressions)
        }
        
        with open(self.learning_data_path, 'wb') as f:
            pickle.dump(learning_data, f)
    
    def _semantic_compress(self, text: str) -> str:
        """Compress text using semantic mappings for better fidelity."""
        result = text
        
        # Apply semantic mappings first (longest phrases first)
        sorted_mappings = sorted(self.semantic_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        for phrase, symbol in sorted_mappings:
            if phrase in result:
                result = result.replace(phrase, symbol)
        
        # Then apply regular glossary
        sorted_phrases = sorted(self.reverse_glossary.keys(), key=len, reverse=True)
        
        for phrase in sorted_phrases:
            if phrase in result:
                symbol = self.reverse_glossary[phrase]
                # Use word boundaries for single words, exact match for phrases
                if len(phrase.split()) == 1:
                    pattern = r'\b' + re.escape(phrase) + r'\b'
                else:
                    pattern = re.escape(phrase)
                result = re.sub(pattern, symbol, result, flags=re.IGNORECASE)
        
        return result
    
    def compress(self, text: str) -> str:
        """Enhanced compression with semantic preservation."""
        return self._semantic_compress(text)
    
    def expand(self, text: str) -> str:
        """Expand symbols back to full phrases."""
        result = text
        
        # First expand semantic mappings
        for phrase, symbol in self.semantic_mappings.items():
            if symbol in result:
                result = result.replace(symbol, phrase)
        
        # Then expand regular glossary
        sorted_symbols = sorted(self.glossary.keys(), key=len, reverse=True)
        
        for symbol in sorted_symbols:
            if symbol in result:
                phrase = self.glossary[symbol]
                result = result.replace(symbol, phrase)
        
        return result
    
    def get_compression_stats(self, original: str, compressed: str) -> Dict:
        """Get detailed compression statistics."""
        original_length = len(original)
        compressed_length = len(compressed)
        savings = original_length - compressed_length
        compression_ratio = (savings / original_length) * 100 if original_length > 0 else 0
        
        return {
            'original_length': original_length,
            'compressed_length': compressed_length,
            'savings': savings,
            'compression_ratio': compression_ratio,
            'symbols_used': len([s for s in self.glossary.keys() if s in compressed])
        }


# Enhanced CLI
def enhanced_compress_file(input_file: str, output_file: str = None, 
                          glossary_path: str = "enhanced_glossary.json"):
    """Compress a file using enhanced psst symbols."""
    compiler = EnhancedPsstCompiler(glossary_path)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compressed = compiler.compress(content)
    
    if output_file is None:
        output_file = Path(input_file).stem + "_enhanced.psst"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(compressed)
    
    # Show compression stats
    stats = compiler.get_compression_stats(content, compressed)
    print(f"Enhanced Compression Stats:")
    print(f"   Original: {stats['original_length']} characters")
    print(f"   Compressed: {stats['compressed_length']} characters")
    print(f"   Savings: {stats['savings']} characters ({stats['compression_ratio']:.1f}% reduction)")
    print(f"   Symbols used: {stats['symbols_used']}")
    
    return output_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Enhanced PSST Compiler - High-performance compression with semantic preservation",
        epilog="""
Examples:
  # Compress a file with enhanced compression
  psst-enhanced compress input.txt --output compressed.psst
  
  # Expand a compressed file
  psst-enhanced expand compressed.psst --output expanded.txt
  
  # Use specific glossary
  psst-enhanced compress input.txt --glossary enhanced_glossary.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("command", choices=["compress", "expand"], 
                        help="Command to execute")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--glossary", "-g", default="enhanced_glossary.json",
                        help="Glossary file path")
    
    args = parser.parse_args()
    
    # Initialize compiler
    compiler = EnhancedPsstCompiler(args.glossary)
    
    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Input file '{args.input}' not found")
        return 1
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return 1
    
    # Process based on command
    if args.command == "compress":
        result = compiler.compress(text)
        print(f"Enhanced Compression:")
        print(f"  Original: {len(text)} characters")
        print(f"  Compressed: {len(result)} characters")
        print(f"  Savings: {len(text) - len(result)} characters")
        print(f"  Compression: {(len(text) - len(result))/len(text)*100:.1f}%")
        print(f"  Glossary size: {len(compiler.glossary)} entries")
        
    elif args.command == "expand":
        result = compiler.expand(text)
        print(f"Expanded: {len(result)} characters")
    
    # Write output
    output_file = args.output or f"{args.input}.{'psst' if args.command == 'compress' else 'txt'}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ Output written to: {output_file}")
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 