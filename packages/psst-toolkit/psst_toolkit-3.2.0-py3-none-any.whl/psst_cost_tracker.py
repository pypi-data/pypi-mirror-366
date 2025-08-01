#!/usr/bin/env python3
"""
psst_cost_tracker.py: Cost and usage tracking for PSST OpenAI integration
Usage: python3 psst_cost_tracker.py [--days 7] [--verbose] [--session session_name]
"""

import os
import sys
import argparse
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas library not found. Install with: pip install pandas")
    sys.exit(1)

class PsstCostTracker:
    """Enhanced cost tracking for PSST with session analysis."""
    
    def __init__(self, admin_key: str = None):
        self.admin_key = admin_key or os.environ.get("OPENAI_ADMIN_KEY", "")
        self.enabled = bool(self.admin_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.admin_key}",
                "Content-Type": "application/json",
            }
        else:
            print("⚠️  Warning: No admin key provided. Set OPENAI_ADMIN_KEY environment variable.")
            print("   Cost tracking will be limited to session analysis only.")
    
    def fetch_usage(self, days: int = 7) -> Optional[List[Dict]]:
        """Fetch usage data from OpenAI admin API."""
        if not self.enabled:
            return None
            
        try:
            params = {
                "start_time": int((datetime.now() - timedelta(days=days)).timestamp()),
                "bucket_width": "1d",
                "group_by": ["model"],
                "limit": days
            }
            resp = requests.get(
                "https://api.openai.com/v1/organization/usage/completions",
                headers=self.headers, params=params
            )
            resp.raise_for_status()
            return resp.json()["data"]
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch usage data: {e}")
            return None
    
    def fetch_costs(self, days: int = 7) -> Optional[List[Dict]]:
        """Fetch cost data from OpenAI admin API."""
        if not self.enabled:
            return None
            
        try:
            params = {
                "start_time": int((datetime.now() - timedelta(days=days)).timestamp()),
                "bucket_width": "1d",
                "limit": days
            }
            resp = requests.get(
                "https://api.openai.com/v1/organization/costs",
                headers=self.headers, params=params
            )
            resp.raise_for_status()
            return resp.json()["data"]
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch cost data: {e}")
            return None
    
    def analyze_sessions(self, session_name: Optional[str] = None) -> Dict:
        """Analyze PSST session data for cost insights."""
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
                
                session_info = {
                    "name": session_dir.name,
                    "session_id": metadata.get("session_id", "unknown"),
                    "total_tokens": metadata.get("total_tokens", 0),
                    "message_count": metadata.get("message_count", 0),
                    "model": metadata.get("model", "unknown"),
                    "created": metadata.get("created"),
                    "last_updated": metadata.get("last_updated"),
                    "has_glossary": any(msg["role"] == "system" for msg in messages),
                    "messages": len(messages)
                }
                
                sessions_data.append(session_info)
                total_tokens += session_info["total_tokens"]
                total_messages += session_info["message_count"]
                session_count += 1
                
            except Exception as e:
                print(f"⚠️  Warning: Could not analyze session {session_dir.name}: {e}")
        
        return {
            "sessions": sessions_data,
            "summary": {
                "total_sessions": session_count,
                "total_tokens": total_tokens,
                "total_messages": total_messages,
                "avg_tokens_per_session": total_tokens / session_count if session_count > 0 else 0,
                "avg_tokens_per_message": total_tokens / total_messages if total_messages > 0 else 0
            }
        }
    
    def estimate_costs(self, tokens: int, model: str = "gpt-3.5-turbo") -> float:
        """Estimate costs based on token count and model."""
        # Approximate costs per 1K tokens (as of 2024)
        cost_rates = {
            "gpt-3.5-turbo": 0.002,  # $0.002 per 1K tokens
            "gpt-4": 0.03,            # $0.03 per 1K tokens
            "gpt-4-turbo": 0.01,      # $0.01 per 1K tokens
        }
        
        rate = cost_rates.get(model, cost_rates["gpt-3.5-turbo"])
        return (tokens / 1000) * rate
    
    def print_usage_analysis(self, days: int = 7, verbose: bool = False):
        """Print detailed usage analysis."""
        print(f"📊 Usage Analysis (Last {days} days)")
        print("=" * 50)
        
        usage_data = self.fetch_usage(days)
        cost_data = self.fetch_costs(days)
        
        if usage_data:
            print("✅ OpenAI API Usage Data:")
            for bucket in usage_data:
                if "results" in bucket:
                    for result in bucket["results"]:
                        model = result.get("model", "unknown")
                        tokens = result.get("n_requests", 0)
                        print(f"   Model: {model}, Requests: {tokens}")
        else:
            print("❌ No usage data available (check admin key)")
        
        if cost_data:
            print("\n✅ OpenAI API Cost Data:")
            for bucket in cost_data:
                if "results" in bucket:
                    for result in bucket["results"]:
                        cost = result.get("cost", 0)
                        print(f"   Cost: ${cost:.4f}")
        else:
            print("\n❌ No cost data available (check admin key)")
    
    def print_session_analysis(self, session_name: Optional[str] = None, verbose: bool = False):
        """Print detailed session analysis."""
        print("💬 PSST Session Analysis")
        print("=" * 50)
        
        analysis = self.analyze_sessions(session_name)
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        summary = analysis["summary"]
        sessions = analysis["sessions"]
        
        print(f"📈 Summary:")
        print(f"   Total sessions: {summary['total_sessions']}")
        print(f"   Total tokens: {summary['total_tokens']:,}")
        print(f"   Total messages: {summary['total_messages']}")
        print(f"   Avg tokens per session: {summary['avg_tokens_per_session']:.1f}")
        print(f"   Avg tokens per message: {summary['avg_tokens_per_message']:.1f}")
        
        # Estimate costs
        estimated_cost_gpt35 = self.estimate_costs(summary['total_tokens'], "gpt-3.5-turbo")
        estimated_cost_gpt4 = self.estimate_costs(summary['total_tokens'], "gpt-4")
        
        print(f"\n💰 Estimated Costs:")
        print(f"   GPT-3.5-turbo: ${estimated_cost_gpt35:.4f}")
        print(f"   GPT-4: ${estimated_cost_gpt4:.4f}")
        
        if verbose and sessions:
            print(f"\n📋 Detailed Session List:")
            for session in sessions:
                session_cost_gpt35 = self.estimate_costs(session["total_tokens"], session["model"])
                print(f"   • {session['name']} (ID: {session['session_id']})")
                print(f"     Tokens: {session['total_tokens']:,}, Messages: {session['message_count']}")
                print(f"     Model: {session['model']}, Estimated cost: ${session_cost_gpt35:.4f}")
                if session["has_glossary"]:
                    print(f"     ✅ Glossary included")
                print()
    
    def print_token_validation(self, session_name: str):
        """Print token validation for a specific session."""
        sessions_dir = Path.home() / ".psst-sessions"
        session_file = sessions_dir / session_name / "conversation.json"
        
        if not session_file.exists():
            print(f"❌ Session '{session_name}' not found")
            return
        
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            messages = data.get("messages", [])
            metadata = data.get("metadata", {})
            
            print(f"🔍 Token Validation for Session: {session_name}")
            print("=" * 60)
            
            total_chars = 0
            total_estimated_tokens = 0
            actual_tokens = metadata.get("total_tokens", 0)
            
            for i, msg in enumerate(messages):
                content = msg["content"]
                role = msg["role"]
                chars = len(content)
                estimated_tokens = chars * 0.75  # Rough estimate
                
                total_chars += chars
                total_estimated_tokens += estimated_tokens
                
                print(f"Message {i+1} ({role.upper()}):")
                print(f"   Characters: {chars:,}")
                print(f"   Estimated tokens: {estimated_tokens:.0f}")
                print(f"   Content preview: {content[:80]}{'...' if len(content) > 80 else ''}")
                print()
            
            print(f"📊 Summary:")
            print(f"   Total characters: {total_chars:,}")
            print(f"   Estimated tokens: {total_estimated_tokens:.0f}")
            print(f"   Actual tokens (from API): {actual_tokens:,}")
            
            if actual_tokens > 0:
                accuracy = abs(total_estimated_tokens - actual_tokens) / actual_tokens * 100
                print(f"   Estimation accuracy: {accuracy:.1f}% off")
                
                # Show cost comparison
                cost_gpt35 = self.estimate_costs(actual_tokens, "gpt-3.5-turbo")
                cost_gpt4 = self.estimate_costs(actual_tokens, "gpt-4")
                print(f"   Estimated cost (GPT-3.5): ${cost_gpt35:.4f}")
                print(f"   Estimated cost (GPT-4): ${cost_gpt4:.4f}")
            
        except Exception as e:
            print(f"❌ Error analyzing session: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Cost and usage tracking for PSST OpenAI integration",
        epilog="""
Examples:
  # Analyze all sessions
  python3 psst_cost_tracker.py
  
  # Analyze specific session
  python3 psst_cost_tracker.py --session physics
  
  # Verbose analysis with API data
  python3 psst_cost_tracker.py --verbose --days 30
  
  # Token validation for specific session
  python3 psst_cost_tracker.py --session physics --validate
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--days", "-d", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--session", "-s", help="Analyze specific session only")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed information")
    parser.add_argument("--validate", action="store_true",
                        help="Show token validation for specific session")
    parser.add_argument("--admin-key", help="OpenAI admin API key")
    
    args = parser.parse_args()
    
    # Initialize cost tracker
    tracker = PsstCostTracker(args.admin_key)
    
    if args.validate:
        if not args.session:
            print("❌ Error: --validate requires --session")
            sys.exit(1)
        tracker.print_token_validation(args.session)
    else:
        # Print usage analysis
        tracker.print_usage_analysis(args.days, args.verbose)
        print()
        
        # Print session analysis
        tracker.print_session_analysis(args.session, args.verbose)

if __name__ == "__main__":
    main() 