#!/usr/bin/env python3
"""
psst_openai.py: Enhanced PSST OpenAI integration with session management
"""

import os
import sys
import argparse
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

from psst_compiler import PsstCompiler

# Default configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_GLOSSARY = "core_glossary.json"
SESSIONS_DIR = Path.home() / ".psst-sessions"

# Cost tracking configuration
COST_TRACKING_ENABLED = False
ADMIN_KEY = ""  # Set this to enable cost tracking

class CostTracker:
    """Tracks costs and usage using OpenAI's admin API."""
    
    def __init__(self, admin_key: str = None):
        self.admin_key = admin_key or ADMIN_KEY
        self.enabled = bool(self.admin_key)
        if self.enabled:
            self.headers = {
                "Authorization": f"Bearer {self.admin_key}",
                "Content-Type": "application/json",
            }
    
    def fetch_usage(self, days: int = 7) -> Optional[Dict]:
        """Fetch usage data from OpenAI admin API."""
        if not self.enabled:
            return None
            
        try:
            params = {
                "start_time": int(datetime.now().timestamp()) - days * 86400,
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
    
    def fetch_costs(self, days: int = 7) -> Optional[Dict]:
        """Fetch cost data from OpenAI admin API."""
        if not self.enabled:
            return None
            
        try:
            params = {
                "start_time": int(datetime.now().timestamp()) - days * 86400,
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

class ConversationSession:
    """Manages conversation sessions with message history."""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.session_dir = SESSIONS_DIR / session_name
        self.session_file = self.session_dir / "conversation.json"
        self.messages: List[Dict] = []
        self.metadata = {
            "created": None,
            "last_updated": None,
            "total_tokens": 0,
            "message_count": 0,
            "model": DEFAULT_MODEL,
            "session_id": self._generate_session_id()
        }
        self._ensure_session_dir()
        self._load_session()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _ensure_session_dir(self):
        """Create session directory if it doesn't exist."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_session(self):
        """Load existing session or create new one."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.messages = data.get("messages", [])
                    self.metadata = data.get("metadata", self.metadata)
                    # Ensure session_id exists for old sessions
                    if "session_id" not in self.metadata:
                        self.metadata["session_id"] = self._generate_session_id()
            except (json.JSONDecodeError, OSError) as e:
                print(f"⚠️  Warning: Could not load session {self.session_name}: {e}")
                print("   Starting fresh session.")
        else:
            # New session
            self.metadata["created"] = datetime.now().isoformat()
    
    def save_session(self):
        """Save session to disk."""
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        data = {
            "messages": self.messages,
            "metadata": self.metadata
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"⚠️  Warning: Could not save session: {e}")
    
    def add_system_message(self, content: str):
        """Add system message (usually containing glossary)."""
        if not self.has_system_message():
            self.messages.append({"role": "system", "content": content})
    
    def add_user_message(self, content: str):
        """Add user message to conversation."""
        self.messages.append({"role": "user", "content": content})
        self.metadata["message_count"] += 1
    
    def add_assistant_message(self, content: str, usage: Optional[Dict] = None):
        """Add assistant response to conversation."""
        self.messages.append({"role": "assistant", "content": content})
        if usage:
            self.metadata["total_tokens"] += usage.get("total_tokens", 0)
    
    def has_system_message(self) -> bool:
        """Check if session already has a system message (with glossary)."""
        return any(msg["role"] == "system" for msg in self.messages)
    
    def get_messages(self) -> List[Dict]:
        """Get all messages for API call."""
        return self.messages.copy()
    
    def is_new_session(self) -> bool:
        """Check if this is a brand new session."""
        return len(self.messages) == 0
    
    def get_session_id(self) -> str:
        """Get the unique session identifier."""
        return self.metadata.get("session_id", "unknown")
    
    @classmethod
    def list_sessions(cls) -> List[str]:
        """List all available sessions."""
        if not SESSIONS_DIR.exists():
            return []
        
        sessions = []
        for session_dir in SESSIONS_DIR.iterdir():
            if session_dir.is_dir() and (session_dir / "conversation.json").exists():
                sessions.append(session_dir.name)
        return sorted(sessions)
    
    @classmethod
    def delete_session(cls, session_name: str) -> bool:
        """Delete a session."""
        session_dir = SESSIONS_DIR / session_name
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
            return True
        return False

def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.environ.get(DEFAULT_API_KEY_ENV)
    if not api_key:
        print(f"❌ Error: OpenAI API key not found.")
        print(f"   Set the {DEFAULT_API_KEY_ENV} environment variable:")
        print(f"   export {DEFAULT_API_KEY_ENV}=your_api_key_here")
        sys.exit(1)
    return api_key

def call_openai_api(
    messages: List[Dict],
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None
) -> Dict:
    """Send messages to OpenAI API and return response."""
    if api_key is None:
        api_key = get_api_key()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages
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
        print(f"❌ API call failed: {e}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"   Response: {e.response.text}")
        sys.exit(1)

def build_system_prompt(
    custom_system_prompt: Optional[str] = None,
    glossary: Optional[Dict[str, str]] = None
) -> str:
    """Build the system prompt with glossary and custom instructions."""
    enhanced_system_prompt = ""
    
    # Add glossary definitions if provided
    if glossary:
        enhanced_system_prompt += "You will receive messages containing special symbols. Here are their meanings:\n\n"
        for symbol, meaning in sorted(glossary.items()):
            enhanced_system_prompt += f"• {symbol}: {meaning}\n"
        enhanced_system_prompt += "\nPlease interpret these symbols according to their meanings when responding.\n"
    
    # Add user's system prompt if provided
    if custom_system_prompt:
        if enhanced_system_prompt:
            enhanced_system_prompt += "\n" + custom_system_prompt
        else:
            enhanced_system_prompt = custom_system_prompt
    
    return enhanced_system_prompt

def compress_prompt(prompt: str, glossary_path: str = DEFAULT_GLOSSARY) -> tuple[str, int, Dict[str, str]]:
    """Compress prompt using psst compiler. Returns (compressed_prompt, savings, glossary)."""
    try:
        compiler = PsstCompiler(glossary_path)
        original_length = len(prompt)
        compressed = compiler.compress(prompt)
        compressed_length = len(compressed)
        savings = original_length - compressed_length
        return compressed, savings, compiler.glossary
    except Exception as e:
        print(f"❌ Compression failed: {e}")
        sys.exit(1)

def read_prompt_from_stdin() -> str:
    """Read prompt from stdin if available."""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""

def format_response(response_data: Dict, show_usage: bool = False) -> str:
    """Format the OpenAI response for display."""
    try:
        content = response_data["choices"][0]["message"]["content"]
        result = content.strip()
        
        if show_usage and "usage" in response_data:
            usage = response_data["usage"]
            result += f"\n\n📊 Token Usage:"
            result += f"\n   Prompt: {usage.get('prompt_tokens', 0)} tokens"
            result += f"\n   Response: {usage.get('completion_tokens', 0)} tokens"
            result += f"\n   Total: {usage.get('total_tokens', 0)} tokens"
        
        return result
    except (KeyError, IndexError) as e:
        print(f"❌ Failed to extract response content: {e}")
        print("Raw response:", json.dumps(response_data, indent=2))
        sys.exit(1)

def show_session_info(session: ConversationSession):
    """Display session information."""
    print(f"💬 Session: {session.session_name}")
    print(f"   ID: {session.get_session_id()}")
    if session.is_new_session():
        print("   Status: New session")
    else:
        print(f"   Messages: {len(session.messages)}")
        print(f"   User messages: {session.metadata['message_count']}")
        print(f"   Total tokens used: {session.metadata['total_tokens']}")
        print(f"   Model: {session.metadata.get('model', DEFAULT_MODEL)}")
        if session.metadata.get('created'):
            print(f"   Created: {session.metadata['created'][:19].replace('T', ' ')}")
        
        # Check if glossary was already sent
        if session.has_system_message():
            print("   💰 Glossary: Already sent (no additional token cost)")
        else:
            print("   💰 Glossary: Will be sent this session")

def print_verbose_tokens(messages: List[Dict], verbose: bool = False):
    """Print the actual tokens/words being sent to the API."""
    if not verbose:
        return
    
    print("\n🔍 VERBOSE: Tokens being sent to API:")
    print("=" * 50)
    
    for i, msg in enumerate(messages):
        role = msg["role"]
        content = msg["content"]
        
        # Estimate tokens (rough approximation)
        words = content.split()
        estimated_tokens = len(words) * 1.3  # Rough estimate
        
        print(f"Message {i+1} ({role.upper()}):")
        print(f"   Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        print(f"   Length: {len(content)} characters, ~{estimated_tokens:.0f} tokens")
        print()
    
    total_chars = sum(len(msg["content"]) for msg in messages)
    total_estimated_tokens = total_chars * 0.75  # Rough estimate
    print(f"📊 Total estimated tokens: ~{total_estimated_tokens:.0f}")
    print("=" * 50)

def validate_response(response: Dict, sent_messages: List[Dict], verbose: bool = False):
    """Validate and show what was sent vs received."""
    if not verbose:
        return
    
    print("\n✅ RESPONSE VALIDATION:")
    print("=" * 50)
    
    try:
        received_content = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})
        
        print(f"📤 Sent: {len(sent_messages)} messages")
        print(f"📥 Received: {len(received_content)} characters")
        print(f"🔢 Actual tokens used: {usage.get('total_tokens', 'unknown')}")
        
        # Show first 100 chars of response
        print(f"📝 Response preview: {received_content[:100]}{'...' if len(received_content) > 100 else ''}")
        
        # Compare with estimated tokens
        total_sent_chars = sum(len(msg["content"]) for msg in sent_messages)
        estimated_tokens = total_sent_chars * 0.75
        actual_tokens = usage.get('total_tokens', 0)
        
        if actual_tokens > 0:
            accuracy = abs(estimated_tokens - actual_tokens) / actual_tokens * 100
            print(f"📊 Token estimation accuracy: {accuracy:.1f}% off")
        
    except (KeyError, IndexError) as e:
        print(f"⚠️  Could not validate response: {e}")
    
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Send psst-compressed prompts to OpenAI API with conversation sessions",
        epilog="""
Examples:
  # Start new conversation
  psst-openai "Explain quantum computing" --session physics

  # Continue existing conversation  
  psst-openai "Can you elaborate?" --session physics
  
  # Force new session (replaces existing)
  psst-openai "Start fresh" --session physics --new-session
  
  # List all sessions
  psst-openai --list-sessions
  
  # Use default session
  psst-openai "Hello" 
  
  # Read from stdin
  cat prompt.txt | psst-openai --session analysis
  
  # Verbose mode with token validation
  psst-openai "Analyze this" --verbose --cost-tracking
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("prompt", nargs="?", help="Prompt text (omit to read from stdin)")
    parser.add_argument("--session", "-S", default="default", 
                        help="Session name for conversation continuity (default: 'default')")
    parser.add_argument("--new-session", "-N", action="store_true",
                        help="Start a new session (replacing existing if same name)")
    parser.add_argument("--list-sessions", "-L", action="store_true",
                        help="List all available sessions and exit")
    parser.add_argument("--delete-session", metavar="NAME",
                        help="Delete specified session and exit")
    parser.add_argument("--session-info", "-I", action="store_true",
                        help="Show session information before processing")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, 
                        help=f"OpenAI model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--glossary", "-g", default=DEFAULT_GLOSSARY,
                        help=f"Glossary file to use (default: {DEFAULT_GLOSSARY})")
    parser.add_argument("--show-tokens", "-t", action="store_true", 
                        help="Show compression and token usage information")
    parser.add_argument("--raw", "-r", action="store_true",
                        help="Don't compress the prompt (send as is)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Return raw JSON response")
    parser.add_argument("--usage", "-u", action="store_true",
                        help="Show token usage statistics")
    parser.add_argument("--no-glossary", action="store_true",
                        help="Don't include symbol definitions in system prompt")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed token information and validation")
    parser.add_argument("--cost-tracking", "-c", action="store_true",
                        help="Enable cost tracking using admin API (requires admin key)")
    parser.add_argument("--admin-key", help="OpenAI admin API key for cost tracking")
    
    args = parser.parse_args()
    
    # Initialize cost tracker if requested
    cost_tracker = None
    if args.cost_tracking or args.admin_key:
        admin_key = args.admin_key or os.environ.get("OPENAI_ADMIN_KEY", "")
        if admin_key:
            cost_tracker = CostTracker(admin_key)
            print("💰 Cost tracking enabled")
        else:
            print("⚠️  Warning: Cost tracking requested but no admin key provided")
            print("   Set OPENAI_ADMIN_KEY environment variable or use --admin-key")
    
    # Handle session management commands
    if args.list_sessions:
        sessions = ConversationSession.list_sessions()
        if sessions:
            print("Available sessions:")
            for session_name in sessions:
                session = ConversationSession(session_name)
                status = "empty" if session.is_new_session() else f"{len(session.messages)} messages"
                tokens = f", {session.metadata['total_tokens']} tokens" if session.metadata['total_tokens'] > 0 else ""
                session_id = f" (ID: {session.get_session_id()})"
                print(f"  • {session_name} ({status}{tokens}){session_id}")
        else:
            print("No sessions found.")
        return
    
    if args.delete_session:
        if ConversationSession.delete_session(args.delete_session):
            print(f"✅ Deleted session: {args.delete_session}")
        else:
            print(f"❌ Session not found: {args.delete_session}")
        return
    
    # Load or create session
    session = ConversationSession(args.session)
    
    # Handle new session flag
    if args.new_session and not session.is_new_session():
        ConversationSession.delete_session(args.session)
        session = ConversationSession(args.session)
        print(f"🆕 Started new session: {args.session}")
    
    # Show session info if requested
    if args.session_info:
        show_session_info(session)
        print()
    
    # Read from stdin if no prompt argument and stdin has data
    stdin_prompt = read_prompt_from_stdin()
    if args.prompt is None and not stdin_prompt:
        parser.print_help()
        sys.exit(1)
    
    # Combine arguments and stdin
    prompt = args.prompt or stdin_prompt
    
    if not prompt.strip():
        print("❌ Error: Empty prompt provided")
        sys.exit(1)
    
    # Update session model
    session.metadata["model"] = args.model
    
    # Compress prompt unless raw mode
    glossary = None
    if not args.raw:
        compressed, savings, glossary = compress_prompt(prompt, args.glossary)
        
        if args.show_tokens:
            original_length = len(prompt)
            compressed_length = len(compressed)
            symbols_used = sum(1 for symbol in glossary.keys() if symbol in compressed)
            print(f"🗜️  Compression Results:")
            print(f"   Original: {original_length} characters")
            print(f"   Compressed: {compressed_length} characters")
            print(f"   Savings: {savings} characters ({savings/original_length*100:.1f}% reduction)")
            print(f"   Symbols used: {symbols_used}")
            print(f"   Session: {session.session_name} (ID: {session.get_session_id()})")
            print(f"   Using model: {args.model}")
            
            # Show glossary cost info
            if not args.no_glossary:
                if session.has_system_message():
                    print("   💰 Glossary cost: FREE (already sent in this session)")
                else:
                    glossary_tokens = len(build_system_prompt(args.system, glossary).split())
                    print(f"   💰 Glossary cost: ~{glossary_tokens} tokens (one-time per session)")
            
            print("=" * 50)
        
        prompt_to_send = compressed
    else:
        prompt_to_send = prompt
        if args.show_tokens:
            print(f"📝 Sending uncompressed prompt ({len(prompt)} characters)")
            print(f"   Session: {session.session_name} (ID: {session.get_session_id()})")
            print(f"   Using model: {args.model}")
            print("=" * 50)
    
    # Add system message if this is a new session and we need glossary
    if not session.has_system_message() and not args.no_glossary:
        system_prompt = build_system_prompt(args.system, glossary)
        if system_prompt:
            session.add_system_message(system_prompt)
    elif not session.has_system_message() and args.system:
        # Add user's system prompt even without glossary
        session.add_system_message(args.system)
    
    # Add user message to session
    session.add_user_message(prompt_to_send)
    
    # Get messages for API call
    messages = session.get_messages()
    
    # Print verbose token information if requested
    print_verbose_tokens(messages, args.verbose)
    
    # Send to API
    print("🤖 Calling OpenAI API...", end="", flush=True)
    response = call_openai_api(
        messages=messages,
        model=args.model
    )
    print(" ✅")
    print()
    
    # Validate response if verbose mode
    validate_response(response, messages, args.verbose)
    
    # Add assistant response to session
    try:
        assistant_content = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})
        session.add_assistant_message(assistant_content, usage)
        
        # Save session
        session.save_session()
        
    except (KeyError, IndexError) as e:
        print(f"⚠️  Warning: Could not save assistant response: {e}")
    
    # Show cost tracking information if enabled
    if cost_tracker:
        print("\n💰 Cost Tracking:")
        print("=" * 30)
        usage_data = cost_tracker.fetch_usage(1)  # Last 1 day
        cost_data = cost_tracker.fetch_costs(1)   # Last 1 day
        
        if usage_data:
            print("📊 Recent usage data available")
        if cost_data:
            print("💵 Recent cost data available")
        
        print("   (Use --verbose for detailed cost analysis)")
    
    # Process response
    if args.json:
        print(json.dumps(response, indent=2))
    else:
        formatted_response = format_response(response, args.usage)
        print(formatted_response)

if __name__ == "__main__":
    main() 