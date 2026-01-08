"""
MentorAI Evaluation Script
Runs automated conversations between MentorAI (tutor) and a synthetic learner.
Logs all conversations to LangSmith for review and scoring.

Prompts are loaded from markdown files for easy editing:
  - prompts/mentor.md           # MentorAI system prompt
  - prompts/personas/<name>.md  # Synthetic learner personas

The script maintains three views of learner responses:
  - Full output (with [INNER THOUGHT]): logged for evaluation/diagnostics
  - Visible response only: what the mentor agent sees
  - Learner's own history: includes inner thoughts for continuity

Usage:
    python run_eval.py --persona amara --turns 10
    python run_eval.py --persona carlos --turns 12
    python run_eval.py --persona daniel --turns 10
    python run_eval.py --list-personas  # Show available personas
"""

import argparse
import re
from pathlib import Path
from openai import OpenAI
from langsmith import traceable

# Initialize OpenAI client
client = OpenAI()

# Directory containing prompts (relative to this script)
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"
PERSONAS_DIR = PROMPTS_DIR / "personas"


# =============================================================================
# PROMPT LOADING
# =============================================================================

def load_prompt(filepath: Path) -> str:
    """Load a prompt from a markdown file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    return filepath.read_text(encoding="utf-8")


def load_mentor_prompt() -> str:
    """Load the MentorAI system prompt."""
    return load_prompt(PROMPTS_DIR / "mentor.md")


def load_persona_prompt(persona_name: str) -> str:
    """Load a synthetic learner persona prompt."""
    filepath = PERSONAS_DIR / f"{persona_name}.md"
    return load_prompt(filepath)


def get_available_personas() -> list[str]:
    """Return list of available persona names (without .md extension)."""
    if not PERSONAS_DIR.exists():
        return []
    return sorted([f.stem for f in PERSONAS_DIR.glob("*.md")])


# =============================================================================
# RESPONSE PROCESSING
# =============================================================================

def extract_visible_response(learner_output: str) -> str:
    """
    Strip inner thought block, returning only the visible response.
    
    The mentor should only see what a human tutor would see—the learner's
    actual spoken response, not their internal reasoning process.
    
    Args:
        learner_output: Full learner output including [INNER THOUGHT] block
        
    Returns:
        Only the [RESPONSE] portion, or cleaned output if tags are malformed
    """
    # Primary: Look for [RESPONSE] block and extract everything after it
    response_match = re.search(
        r'\[RESPONSE\]\s*\n?(.*)', 
        learner_output, 
        re.DOTALL | re.IGNORECASE
    )
    if response_match:
        return response_match.group(1).strip()
    
    # Fallback: Strip [INNER THOUGHT] block if [RESPONSE] tag is missing
    # This handles cases where the model omits the [RESPONSE] label
    cleaned = re.sub(
        r'\[INNER THOUGHT\].*?(?=\[RESPONSE\]|\Z)', 
        '', 
        learner_output, 
        flags=re.DOTALL | re.IGNORECASE
    )
    cleaned = cleaned.strip()
    
    # If we still have content, return it; otherwise return original
    # (prevents returning empty string if format is completely unexpected)
    return cleaned if cleaned else learner_output.strip()


def extract_inner_thought(learner_output: str) -> str | None:
    """
    Extract the inner thought block for diagnostic purposes.
    
    Args:
        learner_output: Full learner output including [INNER THOUGHT] block
        
    Returns:
        The inner thought content, or None if not found
    """
    thought_match = re.search(
        r'\[INNER THOUGHT\]\s*\n?(.*?)(?=\[RESPONSE\]|\Z)',
        learner_output,
        re.DOTALL | re.IGNORECASE
    )
    if thought_match:
        return thought_match.group(1).strip()
    return None


# =============================================================================
# CONVERSATION FUNCTIONS
# =============================================================================

def call_llm(system_prompt: str, messages: list, role_name: str) -> str:
    """Call OpenAI API and return the response."""
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.8,
        messages=[{"role": "system", "content": system_prompt}] + messages
    )
    return response.choices[0].message.content


@traceable(name="MentorAI Evaluation Conversation")
def run_conversation(persona_name: str, num_turns: int = 10) -> dict:
    """
    Run a conversation between MentorAI and a synthetic learner.
    
    Maintains three separate views of the conversation:
    - mentor_messages: What mentor sees (visible responses only)
    - learner_messages: What learner sees (includes own inner thoughts)
    - transcript: Full record for evaluation (both views preserved)
    
    Args:
        persona_name: Name of the persona (matches filename in prompts/personas/)
        num_turns: Number of back-and-forth exchanges
    
    Returns:
        Dictionary containing the full conversation transcript with diagnostic data
    """
    
    # Load prompts from files
    mentor_prompt = load_mentor_prompt()
    learner_prompt = load_persona_prompt(persona_name)
    
    # Track conversation from both perspectives
    # Key insight: these diverge because mentor shouldn't see inner thoughts
    mentor_messages = []
    learner_messages = []
    transcript = []
    
    print(f"\n{'='*60}")
    print(f"Starting conversation: MentorAI <-> {persona_name.upper()}")
    print(f"{'='*60}\n")
    
    # MentorAI opens the conversation
    mentor_response = call_llm(mentor_prompt, mentor_messages, "MentorAI")
    mentor_messages.append({"role": "assistant", "content": mentor_response})
    learner_messages.append({"role": "user", "content": mentor_response})
    transcript.append({
        "role": "MentorAI", 
        "content": mentor_response
    })
    print(f"MentorAI: {mentor_response}\n")
    
    # Run the conversation for specified number of turns
    for turn in range(num_turns):
        # Learner responds
        learner_response_full = call_llm(learner_prompt, learner_messages, persona_name)
        visible_response = extract_visible_response(learner_response_full)
        inner_thought = extract_inner_thought(learner_response_full)
        
        # Learner sees their own full output (maintains reasoning continuity)
        learner_messages.append({"role": "assistant", "content": learner_response_full})
        
        # Mentor sees ONLY the visible response (simulates real tutoring)
        mentor_messages.append({"role": "user", "content": visible_response})
        
        # Transcript preserves everything for evaluation
        transcript.append({
            "role": persona_name,
            "content": learner_response_full,      # Full output for LLM-as-Judge
            "visible_to_mentor": visible_response,  # What mentor actually saw
            "inner_thought": inner_thought          # Extracted for analysis
        })
        
        # Console shows what mentor sees (the realistic view)
        print(f"{persona_name.upper()}: {visible_response}\n")
        
        # MentorAI responds (based only on visible responses)
        mentor_response = call_llm(mentor_prompt, mentor_messages, "MentorAI")
        mentor_messages.append({"role": "assistant", "content": mentor_response})
        learner_messages.append({"role": "user", "content": mentor_response})
        transcript.append({
            "role": "MentorAI", 
            "content": mentor_response
        })
        print(f"MentorAI: {mentor_response}\n")
    
    print(f"\n{'='*60}")
    print(f"Conversation complete: {num_turns} turns")
    print(f"{'='*60}\n")
    
    return {
        "persona": persona_name,
        "num_turns": num_turns,
        "transcript": transcript
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run MentorAI evaluation conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_eval.py --persona amara --turns 10
    python run_eval.py --persona carlos --turns 12
    python run_eval.py --list-personas
        """
    )
    parser.add_argument("--persona", type=str, 
                        help="Which synthetic learner to use (see --list-personas)")
    parser.add_argument("--turns", type=int, default=10,
                        help="Number of conversation turns (default: 10)")
    parser.add_argument("--list-personas", action="store_true",
                        help="List available personas and exit")
    
    args = parser.parse_args()
    
    # Handle --list-personas
    if args.list_personas:
        personas = get_available_personas()
        if personas:
            print("Available personas:")
            for p in personas:
                print(f"  - {p}")
        else:
            print(f"No personas found in {PERSONAS_DIR}")
        exit(0)
    
    # Require --persona if not listing
    if not args.persona:
        parser.error("--persona is required (use --list-personas to see options)")
    
    # Validate persona exists
    available = get_available_personas()
    if args.persona not in available:
        print(f"Error: Unknown persona '{args.persona}'")
        print(f"Available: {', '.join(available)}")
        exit(1)
    
    result = run_conversation(args.persona, args.turns)
    
    print("\nConversation logged to LangSmith!")
    print("Go to smith.langchain.com to review and score the trace.")
