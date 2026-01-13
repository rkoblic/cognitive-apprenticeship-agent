"""
Critical Criteria Evaluator for SBI Tutoring Conversations
===========================================================

This script:
1. Fetches tutoring conversations from LangSmith
2. Strips synthetic learner inner monologue (so judge sees what tutor saw)
3. Runs each through the critical criteria judge
4. Saves results as markdown files for manual review

Setup required:
- pip install langsmith langchain langchain-anthropic
- Set environment variables (see below)
"""

import os
import re
from datetime import datetime
from pathlib import Path

from langsmith import Client
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# =============================================================================
# CONFIGURATION - Edit these values
# =============================================================================

# LangSmith settings
LANGSMITH_PROJECT = "MentorAI-Eval"  # Replace with your project name

# Filter settings - adjust to match your runs
RUN_NAME_FILTER = "MentorAI Evaluation Conversation"  # Filter to only get tutor-learner conversations
TAG_FILTER = None       # e.g., "sbi_eval" or None for all
LIMIT = 2              # Max conversations to evaluate

# Judge model
# Options: claude-opus-4-5-20251101 (best), claude-sonnet-4-20250514 (balanced), claude-haiku-4-20250414 (fast/cheap)
JUDGE_MODEL = "claude-opus-4-5-20251101"

# Output directory
OUTPUT_DIR = Path("eval_results")

# =============================================================================
# CRITICAL CRITERIA JUDGE PROMPT
# =============================================================================

JUDGE_PROMPT = """# Critical Criteria Evaluation

## Role

You are an expert evaluator of cognitive apprenticeship tutoring for SBI (Situation-Behavior-Impact) feedback skills. Your task is to determine whether a tutoring conversation meets minimum fidelity requirements.

## Task

Review the tutoring transcript below and evaluate whether it passes or fails each of the 7 critical criteria. A conversation must pass ALL critical criteria to proceed to full evaluation. Failure on any single criterion indicates fundamental fidelity problems.

## Critical Criteria

Evaluate each criterion as PASS or FAIL. A criterion only passes if there is clear evidence in the transcript.

### B-01: Shows, Not Tells
- **PASS**: Mentor demonstrates an actual SBI example—writes out or speaks a complete Situation-Behavior-Impact statement as a model.
- **FAIL**: Mentor only explains what SBI is, describes the framework, or tells the learner what good SBI looks like without actually showing one.

### C-01: Specific Feedback
- **PASS**: When the learner produces a draft, mentor points to exact language (quotes or references specific words) and names the specific issue with that language.
- **FAIL**: Mentor gives generic feedback ("that's not quite right," "try to be more specific") without identifying which words are problematic and why.

### C-03: Revision Requested
- **PASS**: After giving feedback on a learner's draft, mentor explicitly asks the learner to revise or try again.
- **FAIL**: Mentor provides feedback but then moves on, fixes it for the learner, or only asks "does that make sense?" without requesting a revision attempt.

### D-01: Catches Vague Situations
- **PASS**: When learner uses vague time references ("lately," "sometimes," "recently," "often"), mentor identifies this and prompts for specific time and place.
- **FAIL**: Mentor accepts vague situation language without comment, or this error type does not appear in the learner's drafts (mark N/A).

### D-02: Catches Judgment Leakage
- **PASS**: When learner's behavior description contains interpretation or judgment words (e.g., "dismissive," "rude," "lazy," "didn't care," "hostile," "unprofessional"), mentor identifies this and prompts for observable actions.
- **FAIL**: Mentor accepts interpretive language in behavior without comment, or this error type does not appear in the learner's drafts (mark N/A).

### D-03: Catches Accusatory Impact
- **PASS**: When learner uses blame language in impact (e.g., "You made everyone uncomfortable," "You ruined the meeting"), mentor identifies this and prompts for owned experience using "I" statements.
- **FAIL**: Mentor accepts accusatory impact language without comment, or this error type does not appear in the learner's drafts (mark N/A).

### E-04: Protects Productive Struggle
- **PASS**: When learner asks mentor to just give them the answer or do it for them, mentor requires at least one attempt from the learner before providing the solution.
- **FAIL**: Mentor immediately provides answers when learner expresses difficulty or asks for help, without requiring an attempt first. If learner never asks for answers to be given, mark N/A.

## Special Handling: N/A Criteria

For D-01, D-02, D-03, and E-04: These criteria test the mentor's response to specific learner behaviors. If the learner never produces the error type or behavior that would trigger the criterion, mark it N/A (Not Applicable). N/A does not count as a failure.

A conversation passes the critical gate if:
- All applicable criteria are marked PASS
- No applicable criteria are marked FAIL

## Output Format

For each criterion, provide:
1. **Verdict**: PASS, FAIL, or N/A
2. **Evidence**: A brief quote or description from the transcript supporting your verdict (1-2 sentences)

Then provide an overall PASS/FAIL determination.

---

## Transcript to Evaluate

{transcript}

---

## Evaluation

### B-01: Shows, Not Tells
**Verdict**: 
**Evidence**: 

### C-01: Specific Feedback
**Verdict**: 
**Evidence**: 

### C-03: Revision Requested
**Verdict**: 
**Evidence**: 

### D-01: Catches Vague Situations
**Verdict**: 
**Evidence**: 

### D-02: Catches Judgment Leakage
**Verdict**: 
**Evidence**: 

### D-03: Catches Accusatory Impact
**Verdict**: 
**Evidence**: 

### E-04: Protects Productive Struggle
**Verdict**: 
**Evidence**: 

---

## Overall Determination

**Result**: [PASS / FAIL]
**Summary**: [One sentence explaining the result]
**Failed Criteria**: [List any failed criteria, or "None"]"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def strip_inner_monologue(transcript: str) -> str:
    """
    Remove synthetic learner inner thoughts from transcript.
    The judge should only see what the tutor saw.
    
    Adjust the pattern if your inner monologue format differs.
    """
    # Pattern 1: [INNER THOUGHT] ... (until next speaker or double newline)
    pattern1 = r'\[INNER THOUGHT\].*?(?=\n\n|\n[A-Z][a-z]+:|\Z)'
    
    # Pattern 2: <inner_thought> ... </inner_thought>
    pattern2 = r'<inner_thought>.*?</inner_thought>'
    
    # Pattern 3: *thinking* ... *end thinking* or similar
    pattern3 = r'\*thinking\*.*?\*end thinking\*'
    
    cleaned = transcript
    for pattern in [pattern1, pattern2, pattern3]:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Remove [RESPONSE] tags (leave the content, just strip the marker)
    cleaned = re.sub(r'\[RESPONSE\]\s*', '', cleaned, flags=re.IGNORECASE)

    # Clean up extra whitespace left behind
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()


def format_run_as_transcript(run) -> str:
    """
    Convert a LangSmith run into a readable transcript.

    Expected format: run.outputs['transcript'] is a list of dicts:
    [{'role': 'MentorAI', 'content': '...'}, {'role': 'LEARNER', 'content': '...'}]
    """
    # Primary format: transcript as list of role/content dicts
    if hasattr(run, 'outputs') and run.outputs:
        if 'transcript' in run.outputs:
            transcript = run.outputs['transcript']
            if isinstance(transcript, list):
                messages = []
                for msg in transcript:
                    role = msg.get('role', 'Unknown')
                    content = msg.get('content', '')
                    messages.append(f"{role}: {content}")
                return '\n\n'.join(messages)
            elif isinstance(transcript, str):
                return transcript

    # Fallback: return string representation of outputs
    return str(run.outputs) if run.outputs else "No transcript found"


def save_result(run_id: str, run_name: str, transcript: str, evaluation: str, output_dir: Path):
    """Save evaluation result as a markdown file."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w\-]', '_', run_name or 'unnamed')[:50]
    filename = f"{timestamp}_{safe_name}_{run_id[:8]}.md"
    
    content = f"""# Evaluation Result

**Run ID**: {run_id}
**Run Name**: {run_name}
**Evaluated**: {datetime.now().isoformat()}

---

## Transcript (Inner Monologue Stripped)

{transcript}

---

## Judge Evaluation

{evaluation}
"""
    
    filepath = output_dir / filename
    filepath.write_text(content)
    return filepath


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================

def run_evaluation():
    """Main function to fetch conversations and run evaluations."""
    
    # Check for required environment variables
    # LangSmith accepts either LANGSMITH_API_KEY or LANGCHAIN_API_KEY
    if not os.environ.get('LANGSMITH_API_KEY') and not os.environ.get('LANGCHAIN_API_KEY'):
        print("ERROR: LANGSMITH_API_KEY or LANGCHAIN_API_KEY environment variable not set")
        print("Set it with: export LANGSMITH_API_KEY='your-key-here'")
        return
    
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Initialize clients
    print("Connecting to LangSmith...")
    ls_client = Client()
    
    print(f"Initializing judge model ({JUDGE_MODEL})...")
    judge_llm = ChatAnthropic(model=JUDGE_MODEL, temperature=0)
    judge_prompt = ChatPromptTemplate.from_template(JUDGE_PROMPT)
    judge_chain = judge_prompt | judge_llm
    
    # Fetch runs from LangSmith
    print(f"Fetching runs from project: {LANGSMITH_PROJECT}")
    
    filter_kwargs = {
        "project_name": LANGSMITH_PROJECT,
        "limit": LIMIT,
    }
    
    if RUN_NAME_FILTER:
        filter_kwargs["filter"] = f'eq(name, "{RUN_NAME_FILTER}")'
    
    runs = list(ls_client.list_runs(**filter_kwargs))
    
    if TAG_FILTER:
        runs = [r for r in runs if TAG_FILTER in (r.tags or [])]
    
    print(f"Found {len(runs)} runs to evaluate")
    
    if not runs:
        print("No runs found. Check your project name and filters.")
        return
    
    # Process each run
    results_summary = []
    
    for i, run in enumerate(runs, 1):
        print(f"\n[{i}/{len(runs)}] Evaluating run: {run.name} ({run.id})")
        
        # Format transcript
        raw_transcript = format_run_as_transcript(run)
        
        # Strip inner monologue
        clean_transcript = strip_inner_monologue(raw_transcript)
        
        if len(clean_transcript) < 100:
            print(f"  WARNING: Transcript seems too short ({len(clean_transcript)} chars)")
            print(f"  You may need to adjust format_run_as_transcript() for your data structure")
        
        # Run judge
        print("  Running critical criteria evaluation...")
        try:
            response = judge_chain.invoke({"transcript": clean_transcript})
            evaluation = response.content
        except Exception as e:
            print(f"  ERROR: {e}")
            evaluation = f"Error during evaluation: {e}"
        
        # Save result
        filepath = save_result(
            run_id=str(run.id),
            run_name=run.name,
            transcript=clean_transcript,
            evaluation=evaluation,
            output_dir=OUTPUT_DIR
        )
        print(f"  Saved to: {filepath}")
        
        # Quick summary
        if "**Result**: PASS" in evaluation:
            results_summary.append((run.name, "PASS"))
            print("  Result: PASS ✓")
        elif "**Result**: FAIL" in evaluation:
            results_summary.append((run.name, "FAIL"))
            print("  Result: FAIL ✗")
        else:
            results_summary.append((run.name, "UNCLEAR"))
            print("  Result: Could not parse")
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results_summary if r == "PASS")
    failed = sum(1 for _, r in results_summary if r == "FAIL")
    unclear = sum(1 for _, r in results_summary if r == "UNCLEAR")
    
    print(f"Total evaluated: {len(results_summary)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Unclear: {unclear}")
    print(f"\nResults saved to: {OUTPUT_DIR.absolute()}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_evaluation()
