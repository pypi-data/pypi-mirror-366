#!/usr/bin/env python3
"""
psst: Prompt Symbol Standard Technology Compiler
A token-efficient, centrally-controllable AI prompting system.
"""

import json
import re
import argparse
import os
from typing import Dict, List, Tuple
from pathlib import Path


class PsstCompiler:
    """Core compiler for psst symbol compression and expansion."""
    
    def __init__(self, glossary_path: str = "core_glossary.json"):
        """Initialize compiler with glossary."""
        self.glossary_path = glossary_path
        self.glossary = self._load_glossary()
        self.reverse_glossary = {v: k for k, v in self.glossary.items()}
    
    def _load_glossary(self) -> Dict[str, str]:
        """Load glossary from JSON file."""
        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('glossary', {})
        except FileNotFoundError:
            raise FileNotFoundError(f"Glossary file not found: {self.glossary_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in glossary file: {self.glossary_path}")
    
    def compress(self, text: str) -> str:
        """Compress text by replacing phrases with symbols."""
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
    
    def annotate(self, text: str) -> List[Tuple[str, str, str]]:
        """Annotate text with symbol-phrase mappings."""
        annotations = []
        
        for symbol in self.glossary:
            if symbol in text:
                phrase = self.glossary[symbol]
                annotations.append((symbol, phrase, text))
        
        return annotations
    
    def validate_glossary(self) -> List[str]:
        """Validate glossary format and return any issues."""
        issues = []
        
        # Check for duplicate phrases
        phrases = list(self.glossary.values())
        duplicates = set([p for p in phrases if phrases.count(p) > 1])
        if duplicates:
            issues.append(f"Duplicate phrases found: {duplicates}")
        
        # Check for very short symbols (might cause false matches)
        short_symbols = [s for s in self.glossary.keys() if len(s) == 1]
        if short_symbols:
            issues.append(f"Single-character symbols (may cause conflicts): {short_symbols}")
        
        return issues


def compress_file(input_file: str, output_file: str = None, glossary_path: str = "core_glossary.json"):
    """Compress a file using psst symbols."""
    compiler = PsstCompiler(glossary_path)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    compressed = compiler.compress(content)
    
    if output_file is None:
        output_file = Path(input_file).stem + ".psst"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(compressed)
    
    return output_file


def expand_file(input_file: str, output_file: str = None, glossary_path: str = "core_glossary.json"):
    """Expand a psst file back to natural language."""
    compiler = PsstCompiler(glossary_path)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    expanded = compiler.expand(content)
    
    if output_file is None:
        base_name = Path(input_file).stem
        if base_name.endswith('.psst'):
            base_name = base_name[:-5]  # Remove .psst extension
        output_file = base_name + "_expanded.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(expanded)
    
    return output_file


def compare_glossaries(old_file: str, new_file: str):
    """Compare two glossary files and show differences."""
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    with open(new_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    old_glossary = old_data.get('glossary', {})
    new_glossary = new_data.get('glossary', {})
    
    # Find added, removed, and modified entries
    old_keys = set(old_glossary.keys())
    new_keys = set(new_glossary.keys())
    
    added = new_keys - old_keys
    removed = old_keys - new_keys
    common = old_keys & new_keys
    
    modified = set()
    for key in common:
        if old_glossary[key] != new_glossary[key]:
            modified.add(key)
    
    print(f"Glossary Comparison: {old_file} → {new_file}")
    print(f"Version: {old_data.get('version', 'unknown')} → {new_data.get('version', 'unknown')}")
    print(f"Added symbols: {len(added)}")
    for symbol in sorted(added):
        print(f"  + {symbol}: {new_glossary[symbol]}")
    
    print(f"Removed symbols: {len(removed)}")
    for symbol in sorted(removed):
        print(f"  - {symbol}: {old_glossary[symbol]}")
    
    print(f"Modified symbols: {len(modified)}")
    for symbol in sorted(modified):
        print(f"  ~ {symbol}: {old_glossary[symbol]} → {new_glossary[symbol]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="psst Compiler - Prompt Symbol Standard Technology")
    parser.add_argument("command", choices=["compress", "expand", "compare", "validate"], 
                       help="Command to execute")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--glossary", "-g", default="core_glossary.json", 
                       help="Glossary file path (default: core_glossary.json)")
    parser.add_argument("--second", help="Second file for comparison")
    
    args = parser.parse_args()
    
    try:
        if args.command == "compress":
            output = compress_file(args.input, args.output, args.glossary)
            print(f"Compressed: {args.input} → {output}")
        
        elif args.command == "expand":
            output = expand_file(args.input, args.output, args.glossary)
            print(f"Expanded: {args.input} → {output}")
        
        elif args.command == "compare":
            if not args.second:
                print("Error: --second file required for compare command")
                exit(1)
            compare_glossaries(args.input, args.second)
        
        elif args.command == "validate":
            compiler = PsstCompiler(args.glossary)
            issues = compiler.validate_glossary()
            if issues:
                print("Glossary validation issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("Glossary validation passed!")
    
    except Exception as e:
        print(f"Error: {e}")
        exit(1) 