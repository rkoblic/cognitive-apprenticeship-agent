"""
Persona Validation Script
Runs standardized test probes against synthetic learner personas.
Logs all conversations to LangSmith for manual review and scoring.

Validation protocol:
  - 6 standardized probes testing key behavioral markers
  - Temperature 0 for reproducibility
  - 5 runs per persona (configurable)
  - Manual scoring against 5 criteria in LangSmith

Usage:
    python validate_persona.py --persona amara
    python validate_persona.py --persona amara --runs 3
    python validate_persona.py --all
    python validate_persona.py --list-personas
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
PROBES_FILE = PROMPTS_DIR / "validation_probes.md"


# =============================================================================
# PROMPT LOADING
# =============================================================================

def load_prompt(filepath: Path) -> str:
    """Load a prompt from a markdown file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    return filepath.read_text(encoding="utf-8")


def load_persona_prompt(persona_name: str) -> str:
    """Load a synthetic learner persona prompt."""
    filepath = PERSONAS_DIR / f"{persona_name}.md"
    return load_prompt(filepath)


def get_available_personas() -> list[str]:
    """Return list of available persona names (without .md extension)."""
    if not PERSONAS_DIR.exists():
        return []
    return sorted([f.stem for f in PERSONAS_DIR.glob("*.md")])


def load_probes() -> list[dict]:
    """
    Load validation probes from markdown file.
    Returns list of dicts with 'name' and 'text' keys.
    """
    content = load_prompt(PROBES_FILE)
    probes = []

    # Parse probes from markdown format
    # Looking for ### N. Name followed by the probe text
    pattern = r'### \d+\. (.+?)\n(.+?)(?=\n### |\n## |$)'
    matches = re.findall(pattern, content, re.DOTALL)

    for name, text in matches:
        probes.append({
            'name': name.strip(),
            'text': text.strip()
        })

    return probes


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def call_llm(system_prompt: str, messages: list) -> str:
    """Call OpenAI API with temperature=0 for reproducibility."""
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,  # Reproducibility per validation protocol
        messages=[{"role": "system", "content": system_prompt}] + messages
    )
    return response.choices[0].message.content


@traceable(name="Persona Validation")
def run_validation(persona_name: str, run_number: int = 1) -> dict:
    """
    Run a validation session with standardized probes.

    Args:
        persona_name: Name of the persona to validate
        run_number: Which run this is (for logging)

    Returns:
        Dictionary containing the validation transcript
    """

    # Load persona and probes
    persona_prompt = load_persona_prompt(persona_name)
    probes = load_probes()

    # Track conversation
    messages = []
    transcript = []

    print(f"\n{'='*60}")
    print(f"Validation: {persona_name.upper()} (Run {run_number})")
    print(f"{'='*60}\n")

    # Run through each probe
    for i, probe in enumerate(probes, 1):
        print(f"[Probe {i}: {probe['name']}]")
        print(f"TUTOR: {probe['text']}\n")

        # Add probe to conversation
        messages.append({"role": "user", "content": probe['text']})
        transcript.append({
            "role": "tutor",
            "probe_type": probe['name'],
            "content": probe['text']
        })

        # Get persona response
        response = call_llm(persona_prompt, messages)
        messages.append({"role": "assistant", "content": response})
        transcript.append({
            "role": persona_name,
            "content": response
        })
        print(f"{persona_name.upper()}: {response}\n")

    print(f"\n{'='*60}")
    print(f"Validation complete: {len(probes)} probes")
    print(f"{'='*60}\n")

    return {
        "persona": persona_name,
        "run_number": run_number,
        "num_probes": len(probes),
        "transcript": transcript
    }


def validate_persona(persona_name: str, num_runs: int = 5):
    """Run multiple validation sessions for a persona."""
    print(f"\n{'#'*60}")
    print(f"# Validating persona: {persona_name.upper()}")
    print(f"# Runs: {num_runs}")
    print(f"{'#'*60}")

    for run in range(1, num_runs + 1):
        run_validation(persona_name, run_number=run)

    print(f"\nCompleted {num_runs} validation runs for {persona_name}")
    print("Review traces at smith.langchain.com")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate synthetic learner personas with standardized probes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_persona.py --persona amara
    python validate_persona.py --persona amara --runs 3
    python validate_persona.py --all
    python validate_persona.py --list-personas

Validation Criteria (score manually in LangSmith):
    1. Character consistency
    2. Knowledge calibration
    3. Inner monologue coherence
    4. Engagement calibration
    5. Affective calibration

Pass threshold: >= 4/5 criteria across majority of runs
        """
    )
    parser.add_argument("--persona", type=str,
                        help="Which persona to validate")
    parser.add_argument("--runs", type=int, default=5,
                        help="Number of validation runs (default: 5)")
    parser.add_argument("--all", action="store_true",
                        help="Validate all personas")
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

    # Handle --all
    if args.all:
        personas = get_available_personas()
        if not personas:
            print(f"No personas found in {PERSONAS_DIR}")
            exit(1)
        for persona in personas:
            validate_persona(persona, args.runs)
        print(f"\nAll {len(personas)} personas validated!")
        print("Go to smith.langchain.com to review and score traces.")
        exit(0)

    # Require --persona if not using --all or --list-personas
    if not args.persona:
        parser.error("--persona is required (use --list-personas to see options, or --all to validate all)")

    # Validate persona exists
    available = get_available_personas()
    if args.persona not in available:
        print(f"Error: Unknown persona '{args.persona}'")
        print(f"Available: {', '.join(available)}")
        exit(1)

    validate_persona(args.persona, args.runs)
    print("\nValidation logged to LangSmith!")
    print("Go to smith.langchain.com to review and score the traces.")
