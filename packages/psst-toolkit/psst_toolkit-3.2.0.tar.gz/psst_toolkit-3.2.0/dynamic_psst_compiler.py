#!/usr/bin/env python3
"""
Dynamic PSST: Prompt Symbol Standard Technology with Learning
A token-efficient, self-improving AI prompting system.
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


class DynamicPsstCompiler:
    """Dynamic compiler that learns patterns and adapts automatically."""
    
    def __init__(self, glossary_path: str = "core_glossary.json", 
                 learning_data_path: str = "learning_data.pkl"):
        """Initialize dynamic compiler with learning capabilities."""
        self.glossary_path = glossary_path
        self.learning_data_path = learning_data_path
        self.glossary = self._load_glossary()
        self.reverse_glossary = {v: k for k, v in self.glossary.items()}
        
        # Learning components
        self.phrase_patterns = self._load_learning_data()
        self.similarity_threshold = 0.85
        self.min_phrase_length = 3
        self.max_phrase_length = 50
        
        # Dynamic learning stats
        self.compression_history = []
        self.discovered_patterns = defaultdict(int)
        self.failed_compressions = defaultdict(int)
        
    def _load_glossary(self) -> Dict[str, str]:
        """Load glossary from JSON file."""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('glossary', {})
        except FileNotFoundError:
            # Create default glossary if not exists
            default_glossary = {
                "🗣": "respond",
                "💬": "dialog", 
                "🅣": "tone",
                "🧑‍🤝‍🧑": "audience",
                "🕵️": "persona",
                "🔍": "search",
                "📥": "parameters",
                "📤": "specification", 
                "🎯": "intent",
                "📄": "summary",
                "📊": "structured-output",
                "🧾": "template",
                "🧩": "insert",
                "🗃️": "format-type",
                "⚙️": "tool-call",
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
                "⚖️": "fairness",
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
            self._save_glossary(default_glossary)
            return default_glossary
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
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract potential phrases from text using NLP techniques."""
        phrases = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < self.min_phrase_length:
                continue
                
            # Extract noun phrases and verb phrases
            words = sentence.split()
            
            # Generate phrase combinations
            for i in range(len(words)):
                for j in range(i + 1, min(i + 8, len(words) + 1)):  # Max 8 words per phrase
                    phrase = ' '.join(words[i:j])
                    if len(phrase) >= self.min_phrase_length and len(phrase) <= self.max_phrase_length:
                        phrases.append(phrase)
        
        return phrases
    
    def _calculate_semantic_similarity(self, phrase1: str, phrase2: str) -> float:
        """Calculate semantic similarity using multiple metrics."""
        # Normalize phrases
        p1 = phrase1.lower().strip()
        p2 = phrase2.lower().strip()
        
        # Multiple similarity metrics
        sequence_sim = SequenceMatcher(None, p1, p2).ratio()
        jaro_sim = jellyfish.jaro_winkler_similarity(p1, p2)
        levenshtein_sim = 1 - (jellyfish.levenshtein_distance(p1, p2) / max(len(p1), len(p2)))
        
        # Weighted combination
        return (sequence_sim * 0.4 + jaro_sim * 0.4 + levenshtein_sim * 0.2)
    
    def _discover_similar_phrases(self, phrases: List[str]) -> Dict[str, List[str]]:
        """Discover clusters of similar phrases using simple clustering."""
        if len(phrases) < 2:
            return {}
        
        clusters = {}
        cluster_id = 0
        
        # Simple clustering based on similarity
        for i, phrase1 in enumerate(phrases):
            if any(phrase1 in cluster for cluster in clusters.values()):
                continue
                
            current_cluster = [phrase1]
            
            for j, phrase2 in enumerate(phrases[i+1:], i+1):
                if any(phrase2 in cluster for cluster in clusters.values()):
                    continue
                    
                similarity = self._calculate_semantic_similarity(phrase1, phrase2)
                if similarity >= self.similarity_threshold:
                    current_cluster.append(phrase2)
            
            if len(current_cluster) >= 2:
                clusters[cluster_id] = current_cluster
                cluster_id += 1
        
        return clusters
    
    def _generate_symbol_for_phrase(self, phrase: str) -> str:
        """Generate a unique symbol for a phrase."""
        # Use Unicode symbols that are visually distinct
        symbols = ['⚖️', '🔍', '📄', '🎯', '💼', '📊', '🔗', '📱', '🏢', '🎨', 
                  '🧠', '⚡', '🔧', '📝', '🎭', '🎪', '🏛️', '⚔️', '🛡️', '⚖️', 
                  '🔐', '🛑', '🚷', '🎭', '📛', '🧰', '📝', '🔍‍📝', '🄿', '✎', 
                  '🔄', '🚩', '📚', '🧬', '🛰️', '🪄', '⊕', '℧', '⊗', '🔮', '🎪',
                  '🏆', '🎖️', '🏅', '🥇', '🥈', '🥉', '🎗️', '🎟️', '🎫', '🎬']
        
        # Simple hash-based symbol selection
        hash_val = hash(phrase) % len(symbols)
        return symbols[hash_val]
    
    def _learn_from_text(self, text: str):
        """Learn patterns from new text."""
        # Extract phrases
        phrases = self._extract_phrases(text)
        
        # Discover similar phrase clusters
        clusters = self._discover_similar_phrases(phrases)
        
        # Update learning data
        for cluster_id, similar_phrases in clusters.items():
            if len(similar_phrases) >= 2:  # Only consider clusters with multiple phrases
                # Find the most representative phrase (longest or most frequent)
                representative = max(similar_phrases, key=len)
                
                # Generate symbol if not exists
                if representative not in self.reverse_glossary:
                    symbol = self._generate_symbol_for_phrase(representative)
                    
                    # Add to glossary
                    self.glossary[symbol] = representative
                    self.reverse_glossary[representative] = symbol
                    
                    # Track discovery
                    self.discovered_patterns[representative] += 1
    
    def _adaptive_compress(self, text: str) -> str:
        """Adaptive compression that learns from each compression attempt."""
        result = text
        original_length = len(text)
        
        # First, try existing glossary
        result = self.compress(result)
        
        # Learn from this text
        self._learn_from_text(text)
        
        # Try compression again with newly learned patterns
        new_result = self.compress(result)
        
        # Track compression effectiveness
        compression_ratio = (original_length - len(new_result)) / original_length
        self.compression_history.append(compression_ratio)
        
        # Update learning data
        self._save_learning_data()
        
        return new_result
    
    def compress(self, text: str) -> str:
        """Enhanced compression with learning capabilities."""
        result = text
        
        # Sort by length (longest first) to avoid partial matches
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
    
    def expand(self, text: str) -> str:
        """Expand symbols back to full phrases."""
        result = text
        
        # Sort by length (longest symbols first) to handle complex symbols
        sorted_symbols = sorted(self.glossary.keys(), key=len, reverse=True)
        
        for symbol in sorted_symbols:
            if symbol in result:
                phrase = self.glossary[symbol]
                result = result.replace(symbol, phrase)
        
        return result
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learning performance."""
        if not self.compression_history:
            return {}
        
        return {
            'total_compressions': len(self.compression_history),
            'average_compression_ratio': np.mean(self.compression_history),
            'best_compression_ratio': max(self.compression_history),
            'discovered_patterns': len(self.discovered_patterns),
            'failed_patterns': len(self.failed_compressions),
            'glossary_size': len(self.glossary)
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on learning data."""
        suggestions = []
        
        # Analyze failed compressions
        if self.failed_compressions:
            most_failed = sorted(self.failed_compressions.items(), key=lambda x: x[1], reverse=True)[:5]
            suggestions.append(f"Consider adding symbols for frequently failed patterns: {[p[0] for p in most_failed]}")
        
        # Analyze discovered patterns
        if self.discovered_patterns:
            most_discovered = sorted(self.discovered_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            suggestions.append(f"Most discovered patterns: {[p[0] for p in most_discovered]}")
        
        # Compression trend analysis
        if len(self.compression_history) > 10:
            recent_avg = np.mean(self.compression_history[-10:])
            overall_avg = np.mean(self.compression_history)
            if recent_avg > overall_avg:
                suggestions.append("Compression performance is improving over time!")
            else:
                suggestions.append("Consider reviewing and updating the glossary.")
        
        return suggestions
    
    def auto_optimize_glossary(self):
        """Automatically optimize the glossary based on learning data."""
        # Remove rarely used symbols
        usage_counts = defaultdict(int)
        for phrase in self.reverse_glossary:
            usage_counts[phrase] = self.discovered_patterns.get(phrase, 0)
        
        # Remove symbols used less than 2 times
        rarely_used = [phrase for phrase, count in usage_counts.items() if count < 2]
        for phrase in rarely_used:
            symbol = self.reverse_glossary[phrase]
            del self.glossary[symbol]
            del self.reverse_glossary[phrase]
        
        # Add new high-value patterns
        high_value_patterns = [p for p, count in self.discovered_patterns.items() 
                             if count >= 3 and p not in self.reverse_glossary]
        
        for pattern in high_value_patterns[:10]:  # Limit to top 10
            symbol = self._generate_symbol_for_phrase(pattern)
            self.glossary[symbol] = pattern
            self.reverse_glossary[pattern] = symbol
        
        # Save updated glossary
        self._save_glossary()
    
    def batch_learn(self, texts: List[str]):
        """Learn from a batch of texts."""
        print(f"Learning from {len(texts)} texts...")
        
        for i, text in enumerate(texts):
            if i % 10 == 0:
                print(f"Processed {i}/{len(texts)} texts...")
            
            self._learn_from_text(text)
        
        # Auto-optimize after batch learning
        self.auto_optimize_glossary()
        
        print("Batch learning completed!")
        print(f"Glossary size: {len(self.glossary)} symbols")
        print(f"Discovered patterns: {len(self.discovered_patterns)}")


# Enhanced CLI with learning capabilities
def dynamic_compress_file(input_file: str, output_file: str = None, 
                         glossary_path: str = "core_glossary.json",
                         learning_data_path: str = "learning_data.pkl"):
    """Compress a file using dynamic psst symbols."""
    compiler = DynamicPsstCompiler(glossary_path, learning_data_path)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compressed = compiler._adaptive_compress(content)
    
    if output_file is None:
        output_file = Path(input_file).stem + ".psst"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(compressed)
    
    # Show learning stats
    stats = compiler.get_learning_stats()
    if stats:
        print(f"🧠 Learning Stats:")
        print(f"   Average compression: {stats['average_compression_ratio']:.1%}")
        print(f"   Discovered patterns: {stats['discovered_patterns']}")
        print(f"   Glossary size: {stats['glossary_size']}")
    
    return output_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Dynamic Learning PSST Compiler - Self-improving compression with learning",
        epilog="""
Examples:
  # Compress a file with learning
  psst-dynamic compress input.txt --output compressed.psst
  
  # Expand a compressed file
  psst-dynamic expand compressed.psst --output expanded.txt
  
  # Use specific glossary
  psst-dynamic compress input.txt --glossary custom_glossary.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("command", choices=["compress", "expand"], 
                        help="Command to execute")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--glossary", "-g", default="core_glossary.json",
                        help="Glossary file path")
    parser.add_argument("--learning-data", "-l", default="learning_data.pkl",
                        help="Learning data file path")
    
    args = parser.parse_args()
    
    # Initialize compiler
    compiler = DynamicPsstCompiler(args.glossary, args.learning_data)
    
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
        # Use adaptive compression for learning
        result = compiler._adaptive_compress(text)
        print(f"Dynamic Learning Compression:")
        print(f"  Original: {len(text)} characters")
        print(f"  Compressed: {len(result)} characters")
        print(f"  Savings: {len(text) - len(result)} characters")
        print(f"  Compression: {(len(text) - len(result))/len(text)*100:.1f}%")
        print(f"  Glossary size: {len(compiler.glossary)} entries")
        
        # Show learning stats
        stats = compiler.get_learning_stats()
        if stats:
            print(f"  Learning stats: {stats.get('discovered_patterns', 0)} patterns discovered")
        
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