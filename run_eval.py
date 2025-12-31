"""
MentorAI Evaluation Script
Runs automated conversations between MentorAI (tutor) and a synthetic learner.
Logs all conversations to LangSmith for review and scoring.

Prompts are loaded from markdown files for easy editing:
  - prompts/mentor.md           # MentorAI system prompt
  - prompts/personas/<name>.md  # Synthetic learner personas

Usage:
    python run_eval.py --persona mo --turns 10
    python run_eval.py --persona nell --turns 12
    python run_eval.py --persona chris --turns 10
    python run_eval.py --list-personas  # Show available personas
"""

import argparse
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
    
    Args:
        persona_name: Name of the persona (matches filename in prompts/personas/)
        num_turns: Number of back-and-forth exchanges
    
    Returns:
        Dictionary containing the full conversation transcript
    """
    
    # Load prompts from files
    mentor_prompt = load_mentor_prompt()
    learner_prompt = load_persona_prompt(persona_name)
    
    # Track conversation from both perspectives
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
    transcript.append({"role": "MentorAI", "content": mentor_response})
    print(f"MentorAI: {mentor_response}\n")
    
    # Run the conversation for specified number of turns
    for turn in range(num_turns):
        # Learner responds
        learner_response = call_llm(learner_prompt, learner_messages, persona_name)
        learner_messages.append({"role": "assistant", "content": learner_response})
        mentor_messages.append({"role": "user", "content": learner_response})
        transcript.append({"role": persona_name, "content": learner_response})
        print(f"{persona_name.upper()}: {learner_response}\n")
        
        # MentorAI responds
        mentor_response = call_llm(mentor_prompt, mentor_messages, "MentorAI")
        mentor_messages.append({"role": "assistant", "content": mentor_response})
        learner_messages.append({"role": "user", "content": mentor_response})
        transcript.append({"role": "MentorAI", "content": mentor_response})
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
    python run_eval.py --persona mo --turns 10
    python run_eval.py --persona nell --turns 12
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
