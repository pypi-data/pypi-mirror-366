#!/usr/bin/env python3
"""
psst_token_estimator.py: Token estimation for high-volume PSST scenarios
Usage: python3 psst_token_estimator.py [--prompts 10000000] [--glossary-cost 242]
"""

import os
import sys
import argparse
import json
from typing import Dict, List, Optional
from pathlib import Path

class PsstTokenEstimator:
    """Estimates token usage for high-volume PSST scenarios."""
    
    def __init__(self):
        self.glossary_tokens = 242  # Default glossary size in tokens
        self.avg_response_tokens = 150  # Average response tokens
        self.avg_prompt_tokens = 50   # Average prompt tokens
        
    def estimate_with_glossary(self, prompt_tokens: int, response_tokens: int = None) -> int:
        """Estimate total tokens including glossary."""
        if response_tokens is None:
            response_tokens = self.avg_response_tokens
        return self.glossary_tokens + prompt_tokens + response_tokens
    
    def estimate_without_glossary(self, prompt_tokens: int, response_tokens: int = None) -> int:
        """Estimate total tokens without glossary (for comparison)."""
        if response_tokens is None:
            response_tokens = self.avg_response_tokens
        return prompt_tokens + response_tokens
    
    def calculate_compression_ratio(self, original_tokens: int, compressed_tokens: int) -> float:
        """Calculate compression ratio."""
        return (original_tokens - compressed_tokens) / original_tokens * 100
    
    def estimate_high_volume_scenario(self, 
                                    total_prompts: int = 10000000,
                                    avg_prompt_tokens: int = 50,
                                    avg_response_tokens: int = 150,
                                    glossary_tokens: int = 242,
                                    compression_ratio: float = 88.6) -> Dict:
        """Estimate token usage for high-volume scenarios."""
        
        # Calculate compressed prompt tokens
        compressed_prompt_tokens = int(avg_prompt_tokens * (1 - compression_ratio / 100))
        
        # Calculate tokens per request
        tokens_with_glossary = glossary_tokens + compressed_prompt_tokens + avg_response_tokens
        tokens_without_glossary = avg_prompt_tokens + avg_response_tokens
        
        # Calculate total tokens for all prompts
        total_tokens_with_glossary = tokens_with_glossary * total_prompts
        total_tokens_without_glossary = tokens_without_glossary * total_prompts
        
        # Calculate cost savings
        cost_gpt35_with_glossary = (total_tokens_with_glossary / 1000) * 0.002
        cost_gpt35_without_glossary = (total_tokens_without_glossary / 1000) * 0.002
        cost_gpt4_with_glossary = (total_tokens_with_glossary / 1000) * 0.03
        cost_gpt4_without_glossary = (total_tokens_without_glossary / 1000) * 0.03
        
        # Calculate glossary overhead
        glossary_overhead_tokens = glossary_tokens * total_prompts
        glossary_overhead_cost_gpt35 = (glossary_overhead_tokens / 1000) * 0.002
        glossary_overhead_cost_gpt4 = (glossary_overhead_tokens / 1000) * 0.03
        
        return {
            "scenario": {
                "total_prompts": total_prompts,
                "avg_prompt_tokens": avg_prompt_tokens,
                "avg_response_tokens": avg_response_tokens,
                "glossary_tokens": glossary_tokens,
                "compression_ratio": compression_ratio
            },
            "per_request": {
                "tokens_with_glossary": tokens_with_glossary,
                "tokens_without_glossary": tokens_without_glossary,
                "compressed_prompt_tokens": compressed_prompt_tokens,
                "glossary_overhead": glossary_tokens
            },
            "total_tokens": {
                "with_glossary": total_tokens_with_glossary,
                "without_glossary": total_tokens_without_glossary,
                "glossary_overhead": glossary_overhead_tokens
            },
            "costs": {
                "gpt35_with_glossary": cost_gpt35_with_glossary,
                "gpt35_without_glossary": cost_gpt35_without_glossary,
                "gpt4_with_glossary": cost_gpt4_with_glossary,
                "gpt4_without_glossary": cost_gpt4_without_glossary,
                "glossary_overhead_gpt35": glossary_overhead_cost_gpt35,
                "glossary_overhead_gpt4": glossary_overhead_cost_gpt4
            },
            "savings": {
                "tokens_saved": total_tokens_without_glossary - total_tokens_with_glossary,
                "cost_saved_gpt35": cost_gpt35_without_glossary - cost_gpt35_with_glossary,
                "cost_saved_gpt4": cost_gpt4_without_glossary - cost_gpt4_with_glossary
            }
        }
    
    def analyze_session_data(self, session_name: str = None) -> Dict:
        """Analyze actual session data to get real token usage patterns."""
        sessions_dir = Path.home() / ".psst-sessions"
        if not sessions_dir.exists():
            return {"error": "No sessions directory found"}
        
        sessions_data = []
        total_tokens = 0
        total_messages = 0
        session_count = 0
        
        # Get list of sessions to analyze
        if session_name:
            session_dirs = [sessions_dir / session_name] if (sessions_dir / session_name).exists() else []
        else:
            session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
        
        for session_dir in session_dirs:
            session_file = session_dir / "conversation.json"
            if not session_file.exists():
                continue
            
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                messages = data.get("messages", [])
                
                # Calculate tokens per message type
                system_tokens = 0
                user_tokens = 0
                assistant_tokens = 0
                
                for msg in messages:
                    content = msg.get("content", "")
                    chars = len(content)
                    estimated_tokens = chars * 0.75  # Rough estimate
                    
                    if msg["role"] == "system":
                        system_tokens += estimated_tokens
                    elif msg["role"] == "user":
                        user_tokens += estimated_tokens
                    elif msg["role"] == "assistant":
                        assistant_tokens += estimated_tokens
                
                session_info = {
                    "name": session_dir.name,
                    "total_tokens": metadata.get("total_tokens", 0),
                    "message_count": metadata.get("message_count", 0),
                    "system_tokens": system_tokens,
                    "user_tokens": user_tokens,
                    "assistant_tokens": assistant_tokens,
                    "messages": len(messages)
                }
                
                sessions_data.append(session_info)
                total_tokens += session_info["total_tokens"]
                total_messages += session_info["message_count"]
                session_count += 1
                
            except Exception as e:
                print(f"⚠️  Warning: Could not analyze session {session_dir.name}: {e}")
        
        if session_count == 0:
            return {"error": "No sessions found"}
        
        # Calculate averages
        avg_tokens_per_session = total_tokens / session_count
        avg_tokens_per_message = total_tokens / total_messages if total_messages > 0 else 0
        avg_system_tokens = sum(s["system_tokens"] for s in sessions_data) / session_count
        avg_user_tokens = sum(s["user_tokens"] for s in sessions_data) / session_count
        avg_assistant_tokens = sum(s["assistant_tokens"] for s in sessions_data) / session_count
        
        return {
            "sessions": sessions_data,
            "summary": {
                "total_sessions": session_count,
                "total_tokens": total_tokens,
                "total_messages": total_messages,
                "avg_tokens_per_session": avg_tokens_per_session,
                "avg_tokens_per_message": avg_tokens_per_message,
                "avg_system_tokens": avg_system_tokens,
                "avg_user_tokens": avg_user_tokens,
                "avg_assistant_tokens": avg_assistant_tokens
            }
        }
    
    def print_high_volume_analysis(self, total_prompts: int = 10000000, 
                                  avg_prompt_tokens: int = 50,
                                  avg_response_tokens: int = 150,
                                  glossary_tokens: int = 242,
                                  compression_ratio: float = 88.6):
        """Print detailed high-volume analysis."""
        
        print(f"🚀 High-Volume Token Estimation Analysis")
        print("=" * 60)
        print(f"📊 Scenario: {total_prompts:,} prompts per day")
        print(f"   Average prompt: {avg_prompt_tokens} tokens")
        print(f"   Average response: {avg_response_tokens} tokens")
        print(f"   Glossary size: {glossary_tokens} tokens")
        print(f"   Compression ratio: {compression_ratio}%")
        print()
        
        # Calculate estimates
        estimates = self.estimate_high_volume_scenario(
            total_prompts, avg_prompt_tokens, avg_response_tokens, 
            glossary_tokens, compression_ratio
        )
        
        # Per request analysis
        print("📈 Per Request Analysis:")
        print(f"   Without PSST: {estimates['per_request']['tokens_without_glossary']} tokens")
        print(f"   With PSST: {estimates['per_request']['tokens_with_glossary']} tokens")
        print(f"   Glossary overhead: {estimates['per_request']['glossary_overhead']} tokens")
        print(f"   Compression savings: {estimates['per_request']['tokens_without_glossary'] - estimates['per_request']['tokens_with_glossary']} tokens")
        print()
        
        # Total daily analysis
        print("📊 Daily Totals:")
        print(f"   Without PSST: {estimates['total_tokens']['without_glossary']:,} tokens")
        print(f"   With PSST: {estimates['total_tokens']['with_glossary']:,} tokens")
        print(f"   Glossary overhead: {estimates['total_tokens']['glossary_overhead']:,} tokens")
        print(f"   Net savings: {estimates['savings']['tokens_saved']:,} tokens")
        print()
        
        # Cost analysis
        print("💰 Cost Analysis (Daily):")
        print("   GPT-3.5-turbo:")
        print(f"     Without PSST: ${estimates['costs']['gpt35_without_glossary']:,.2f}")
        print(f"     With PSST: ${estimates['costs']['gpt35_with_glossary']:,.2f}")
        print(f"     Savings: ${estimates['savings']['cost_saved_gpt35']:,.2f}")
        print("   GPT-4:")
        print(f"     Without PSST: ${estimates['costs']['gpt4_without_glossary']:,.2f}")
        print(f"     With PSST: ${estimates['costs']['gpt4_with_glossary']:,.2f}")
        print(f"     Savings: ${estimates['savings']['cost_saved_gpt4']:,.2f}")
        print()
        
        # Glossary overhead analysis
        print("📋 Glossary Overhead Analysis:")
        print(f"   Total glossary tokens per day: {estimates['total_tokens']['glossary_overhead']:,}")
        print(f"   Glossary cost (GPT-3.5): ${estimates['costs']['glossary_overhead_gpt35']:,.2f}")
        print(f"   Glossary cost (GPT-4): ${estimates['costs']['glossary_overhead_gpt4']:,.2f}")
        print(f"   Glossary overhead %: {estimates['total_tokens']['glossary_overhead'] / estimates['total_tokens']['with_glossary'] * 100:.1f}%")
        print()
        
        # Efficiency metrics
        efficiency = estimates['savings']['tokens_saved'] / estimates['total_tokens']['without_glossary'] * 100
        print(f"🎯 Efficiency Metrics:")
        print(f"   Overall token reduction: {efficiency:.1f}%")
        print(f"   Cost reduction (GPT-3.5): {estimates['savings']['cost_saved_gpt35'] / estimates['costs']['gpt35_without_glossary'] * 100:.1f}%")
        print(f"   Cost reduction (GPT-4): {estimates['savings']['cost_saved_gpt4'] / estimates['costs']['gpt4_without_glossary'] * 100:.1f}%")
        print()
        
        # Monthly and yearly projections
        monthly_prompts = total_prompts * 30
        yearly_prompts = total_prompts * 365
        
        print("📅 Projections:")
        print(f"   Monthly prompts: {monthly_prompts:,}")
        print(f"   Yearly prompts: {yearly_prompts:,}")
        print(f"   Monthly savings (GPT-3.5): ${estimates['savings']['cost_saved_gpt35'] * 30:,.2f}")
        print(f"   Yearly savings (GPT-3.5): ${estimates['savings']['cost_saved_gpt35'] * 365:,.2f}")
        print(f"   Monthly savings (GPT-4): ${estimates['savings']['cost_saved_gpt4'] * 30:,.2f}")
        print(f"   Yearly savings (GPT-4): ${estimates['savings']['cost_saved_gpt4'] * 365:,.2f}")

    def estimate_session_based_scenario(self, 
                                      total_prompts: int = 10000000,
                                      avg_prompts_per_session: int = 5,
                                      avg_prompt_tokens: int = 500,
                                      avg_response_tokens: int = 200,
                                      glossary_tokens: int = 242,
                                      compression_ratio: float = 88.6) -> Dict:
        """Estimate token usage with session-based glossary caching."""
        
        # Calculate number of sessions
        total_sessions = total_prompts // avg_prompts_per_session
        
        # Calculate compressed prompt tokens
        compressed_prompt_tokens = int(avg_prompt_tokens * (1 - compression_ratio / 100))
        
        # Calculate tokens per request
        tokens_with_glossary = glossary_tokens + compressed_prompt_tokens + avg_response_tokens
        tokens_without_glossary = avg_prompt_tokens + avg_response_tokens
        
        # Calculate total tokens with session caching
        # Glossary sent once per session, not per request
        total_glossary_tokens = total_sessions * glossary_tokens
        total_compressed_prompts = total_prompts * compressed_prompt_tokens
        total_responses = total_prompts * avg_response_tokens
        total_tokens_with_session_caching = total_glossary_tokens + total_compressed_prompts + total_responses
        
        # Calculate costs
        cost_gpt35_with_session = (total_tokens_with_session_caching / 1000) * 0.002
        cost_gpt35_without_psst = (total_prompts * tokens_without_glossary / 1000) * 0.002
        cost_gpt4_with_session = (total_tokens_with_session_caching / 1000) * 0.03
        cost_gpt4_without_psst = (total_prompts * tokens_without_glossary / 1000) * 0.03
        
        return {
            "scenario": {
                "total_prompts": total_prompts,
                "total_sessions": total_sessions,
                "avg_prompts_per_session": avg_prompts_per_session,
                "avg_prompt_tokens": avg_prompt_tokens,
                "avg_response_tokens": avg_response_tokens,
                "glossary_tokens": glossary_tokens,
                "compression_ratio": compression_ratio
            },
            "per_request": {
                "tokens_without_psst": tokens_without_glossary,
                "tokens_with_psst": tokens_with_glossary,
                "compressed_prompt_tokens": compressed_prompt_tokens,
                "glossary_overhead_per_request": glossary_tokens
            },
            "total_tokens": {
                "without_psst": total_prompts * tokens_without_glossary,
                "with_session_caching": total_tokens_with_session_caching,
                "glossary_tokens_total": total_glossary_tokens,
                "compressed_prompts_total": total_compressed_prompts,
                "responses_total": total_responses
            },
            "costs": {
                "gpt35_without_psst": cost_gpt35_without_psst,
                "gpt35_with_session": cost_gpt35_with_session,
                "gpt4_without_psst": cost_gpt4_without_psst,
                "gpt4_with_session": cost_gpt4_with_session
            },
            "savings": {
                "tokens_saved": (total_prompts * tokens_without_glossary) - total_tokens_with_session_caching,
                "cost_saved_gpt35": cost_gpt35_without_psst - cost_gpt35_with_session,
                "cost_saved_gpt4": cost_gpt4_without_psst - cost_gpt4_with_session
            }
        }
    
    def print_session_based_analysis(self, total_prompts: int = 10000000,
                                   avg_prompts_per_session: int = 5,
                                   avg_prompt_tokens: int = 500,
                                   avg_response_tokens: int = 200,
                                   glossary_tokens: int = 242,
                                   compression_ratio: float = 88.6):
        """Print session-based analysis showing glossary caching benefits."""
        
        print(f"🚀 Session-Based Token Estimation Analysis")
        print("=" * 60)
        print(f"📊 Scenario: {total_prompts:,} prompts per day")
        print(f"   Sessions: {total_prompts // avg_prompts_per_session:,}")
        print(f"   Prompts per session: {avg_prompts_per_session}")
        print(f"   Average prompt: {avg_prompt_tokens} tokens")
        print(f"   Average response: {avg_response_tokens} tokens")
        print(f"   Glossary size: {glossary_tokens} tokens")
        print(f"   Compression ratio: {compression_ratio}%")
        print()
        
        # Calculate estimates
        estimates = self.estimate_session_based_scenario(
            total_prompts, avg_prompts_per_session, avg_prompt_tokens, 
            avg_response_tokens, glossary_tokens, compression_ratio
        )
        
        # Per request analysis
        print("📈 Per Request Analysis:")
        print(f"   Without PSST: {estimates['per_request']['tokens_without_psst']} tokens")
        print(f"   With PSST: {estimates['per_request']['tokens_with_psst']} tokens")
        print(f"   Glossary overhead per request: {estimates['per_request']['glossary_overhead_per_request']} tokens")
        print(f"   Compression savings per request: {estimates['per_request']['tokens_without_psst'] - estimates['per_request']['tokens_with_psst']} tokens")
        print()
        
        # Session analysis
        print("📊 Session Analysis:")
        print(f"   Total sessions: {estimates['scenario']['total_sessions']:,}")
        print(f"   Glossary sent once per session")
        print(f"   Glossary tokens per session: {estimates['scenario']['glossary_tokens']}")
        print(f"   Total glossary tokens: {estimates['total_tokens']['glossary_tokens_total']:,}")
        print()
        
        # Daily totals
        print("📊 Daily Totals:")
        print(f"   Without PSST: {estimates['total_tokens']['without_psst']:,} tokens")
        print(f"   With session caching: {estimates['total_tokens']['with_session_caching']:,} tokens")
        print(f"   Glossary tokens: {estimates['total_tokens']['glossary_tokens_total']:,}")
        print(f"   Compressed prompts: {estimates['total_tokens']['compressed_prompts_total']:,}")
        print(f"   Responses: {estimates['total_tokens']['responses_total']:,}")
        print(f"   Net savings: {estimates['savings']['tokens_saved']:,} tokens")
        print()
        
        # Cost analysis
        print("💰 Cost Analysis (Daily):")
        print("   GPT-3.5-turbo:")
        print(f"     Without PSST: ${estimates['costs']['gpt35_without_psst']:,.2f}")
        print(f"     With session caching: ${estimates['costs']['gpt35_with_session']:,.2f}")
        print(f"     Savings: ${estimates['savings']['cost_saved_gpt35']:,.2f}")
        print("   GPT-4:")
        print(f"     Without PSST: ${estimates['costs']['gpt4_without_psst']:,.2f}")
        print(f"     With session caching: ${estimates['costs']['gpt4_with_session']:,.2f}")
        print(f"     Savings: ${estimates['savings']['cost_saved_gpt4']:,.2f}")
        print()
        
        # Efficiency metrics
        efficiency = estimates['savings']['tokens_saved'] / estimates['total_tokens']['without_psst'] * 100
        print(f"🎯 Efficiency Metrics:")
        print(f"   Overall token reduction: {efficiency:.1f}%")
        print(f"   Cost reduction (GPT-3.5): {estimates['savings']['cost_saved_gpt35'] / estimates['costs']['gpt35_without_psst'] * 100:.1f}%")
        print(f"   Cost reduction (GPT-4): {estimates['savings']['cost_saved_gpt4'] / estimates['costs']['gpt4_without_psst'] * 100:.1f}%")
        print()
        
        # Monthly and yearly projections
        monthly_prompts = total_prompts * 30
        yearly_prompts = total_prompts * 365
        
        print("📅 Projections:")
        print(f"   Monthly prompts: {monthly_prompts:,}")
        print(f"   Yearly prompts: {yearly_prompts:,}")
        print(f"   Monthly savings (GPT-3.5): ${estimates['savings']['cost_saved_gpt35'] * 30:,.2f}")
        print(f"   Yearly savings (GPT-3.5): ${estimates['savings']['cost_saved_gpt35'] * 365:,.2f}")
        print(f"   Monthly savings (GPT-4): ${estimates['savings']['cost_saved_gpt4'] * 30:,.2f}")
        print(f"   Yearly savings (GPT-4): ${estimates['savings']['cost_saved_gpt4'] * 365:,.2f}")

def main():
    parser = argparse.ArgumentParser(
        description="Token estimation for high-volume PSST scenarios",
        epilog="""
Examples:
  # Default 10M prompts analysis
  python3 psst_token_estimator.py
  
  # Custom scenario
  python3 psst_token_estimator.py --prompts 5000000 --avg-prompt 100
  
  # Analyze real session data
  python3 psst_token_estimator.py --analyze-sessions
  
  # Session-based analysis
  python3 psst_token_estimator.py --session-based
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--prompts", "-p", type=int, default=10000000,
                        help="Total prompts per day (default: 10,000,000)")
    parser.add_argument("--avg-prompt", "-a", type=int, default=50,
                        help="Average prompt tokens (default: 50)")
    parser.add_argument("--avg-response", "-r", type=int, default=150,
                        help="Average response tokens (default: 150)")
    parser.add_argument("--glossary", "-g", type=int, default=242,
                        help="Glossary tokens (default: 242)")
    parser.add_argument("--compression", "-c", type=float, default=88.6,
                        help="Compression ratio %% (default: 88.6)")
    parser.add_argument("--analyze-sessions", "-s", action="store_true",
                        help="Analyze real session data for estimates")
    parser.add_argument("--session-based", "-b", action="store_true",
                        help="Use session-based glossary caching analysis")
    parser.add_argument("--prompts-per-session", type=int, default=5,
                        help="Average prompts per session (default: 5)")
    
    args = parser.parse_args()
    
    estimator = PsstTokenEstimator()
    
    if args.analyze_sessions:
        print("📊 Analyzing Real Session Data...")
        print("=" * 50)
        
        analysis = estimator.analyze_session_data()
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        summary = analysis["summary"]
        print(f"📈 Real Session Analysis:")
        print(f"   Sessions analyzed: {summary['total_sessions']}")
        print(f"   Average tokens per session: {summary['avg_tokens_per_session']:.1f}")
        print(f"   Average tokens per message: {summary['avg_tokens_per_message']:.1f}")
        print(f"   Average system tokens: {summary['avg_system_tokens']:.1f}")
        print(f"   Average user tokens: {summary['avg_user_tokens']:.1f}")
        print(f"   Average assistant tokens: {summary['avg_assistant_tokens']:.1f}")
        print()
        
        # Use real data for high-volume estimation
        real_avg_prompt = summary['avg_user_tokens']
        real_avg_response = summary['avg_assistant_tokens']
        real_glossary = summary['avg_system_tokens']
        
        print("🚀 High-Volume Estimation (Based on Real Data):")
        estimator.print_high_volume_analysis(
            args.prompts, real_avg_prompt, real_avg_response, 
            real_glossary, args.compression
        )
    elif args.session_based:
        # Use session-based analysis
        estimator.print_session_based_analysis(
            args.prompts, args.prompts_per_session, args.avg_prompt, 
            args.avg_response, args.glossary, args.compression
        )
    else:
        # Use provided parameters
        estimator.print_high_volume_analysis(
            args.prompts, args.avg_prompt, args.avg_response,
            args.glossary, args.compression
        )

if __name__ == "__main__":
    main() 