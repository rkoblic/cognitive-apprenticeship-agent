"""
Unified LLM-as-Judge Evaluation Runner
======================================

Runs LLM judges on tutoring conversations stored in LangSmith.

Supports:
- Two-stage evaluation: critical criteria (gate) + quality judges
- Validation mode for manual review
- Both JSON and markdown output
- Selective judge execution

Usage:
    # Full pipeline (critical + quality for passing conversations)
    python run_judge_eval.py --project MentorAI-Eval --limit 10

    # Validation mode (separate output location)
    python run_judge_eval.py --project MentorAI-Eval --validation --limit 3

    # Run only critical criteria
    python run_judge_eval.py --project MentorAI-Eval --stage critical --limit 10

    # Run specific quality judge
    python run_judge_eval.py --project MentorAI-Eval --stage quality --judge session_setup
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Disable LangSmith tracing for judge calls (we only want to trace tutor conversations)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langsmith import Client
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
JUDGES_DIR = SCRIPT_DIR / "prompts" / "judges"
EVAL_RESULTS_DIR = SCRIPT_DIR / "eval_results"

# Default settings
DEFAULT_PROJECT = "MentorAI-Eval"
DEFAULT_RUN_FILTER = "MentorAI Evaluation Conversation"
DEFAULT_MODEL = "claude-opus-4-5-20251101"
DEFAULT_LIMIT = 10

# Available quality judges (Stage 2)
QUALITY_JUDGES = [
    "session_setup",
    "modeling_quality",
    "coaching_quality",
    "sbi_content",
    "adaptive_pacing",
    "conversational_quality",
]


# =============================================================================
# PROMPT LOADING
# =============================================================================

def load_judge_prompt(judge_id: str) -> tuple[str, dict]:
    """
    Load a judge prompt from markdown file.

    Returns:
        (prompt_text, metadata_dict)
    """
    filepath = JUDGES_DIR / f"{judge_id}.md"
    if not filepath.exists():
        raise FileNotFoundError(f"Judge prompt not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")

    # Parse YAML frontmatter if present
    metadata = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Parse arrays
                    if value.startswith("[") and value.endswith("]"):
                        value = [v.strip() for v in value[1:-1].split(",")]
                    # Parse numbers
                    elif value.isdigit():
                        value = int(value)
                    metadata[key] = value
            content = parts[2].strip()

    return content, metadata


# =============================================================================
# TRANSCRIPT PROCESSING
# =============================================================================

def strip_inner_monologue(transcript: str) -> str:
    """
    Remove synthetic learner inner thoughts from transcript.
    The judge should only see what the tutor saw.
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
    """
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

    return str(run.outputs) if run.outputs else "No transcript found"


# =============================================================================
# OUTPUT PARSING
# =============================================================================

def extract_json_from_response(response: str) -> dict | None:
    """
    Extract JSON block from judge response.
    Returns None if no valid JSON found.
    """
    # Look for JSON block in code fence
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    json_match = re.search(r'\{[^{}]*"criteria"[^{}]*\{.*?\}.*?\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def parse_overall_verdict(response: str) -> str:
    """
    Extract overall PASS/FAIL verdict from response.
    """
    if "**Result**: PASS" in response or '"verdict": "PASS"' in response:
        return "PASS"
    elif "**Result**: FAIL" in response or '"verdict": "FAIL"' in response:
        return "FAIL"
    return "UNCLEAR"


# =============================================================================
# RESULT SAVING
# =============================================================================

def save_results(
    run_dir: Path,
    judge_id: str,
    short_id: str,
    transcript: str,
    evaluation: str,
    json_data: dict | None,
    is_critical: bool = False
):
    """
    Save evaluation results as both markdown and JSON files.
    """
    # Determine subdirectory
    if is_critical:
        subdir = run_dir / "critical"
    else:
        subdir = run_dir / "quality"
    subdir.mkdir(parents=True, exist_ok=True)

    # Filename: short_id for critical, short_id_judge_id for quality
    if is_critical:
        base_name = short_id
    else:
        base_name = f"{short_id}_{judge_id}"

    # Save markdown
    md_content = f"""# {judge_id.replace('_', ' ').title()} Evaluation

**Conversation ID**: {short_id}
**Judge**: {judge_id}
**Evaluated**: {datetime.now().isoformat()}

---

## Transcript (Inner Monologue Stripped)

{transcript}

---

## Judge Evaluation

{evaluation}
"""
    md_path = subdir / f"{base_name}.md"
    md_path.write_text(md_content)

    # Save JSON
    if json_data:
        json_data["_metadata"] = {
            "judge_id": judge_id,
            "conversation_id": short_id,
            "evaluated_at": datetime.now().isoformat(),
        }
        json_path = subdir / f"{base_name}.json"
        json_path.write_text(json.dumps(json_data, indent=2))

    return md_path


def save_manifest(run_dir: Path, config: dict, results: list):
    """
    Save manifest.json with run metadata and summary.
    """
    # Calculate summary stats
    critical_passed = sum(1 for r in results if r.get("critical_verdict") == "PASS")
    critical_failed = sum(1 for r in results if r.get("critical_verdict") == "FAIL")

    manifest = {
        "run_id": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "conversations": results,
        "summary": {
            "total_evaluated": len(results),
            "critical_passed": critical_passed,
            "critical_failed": critical_failed,
        }
    }

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


# =============================================================================
# JUDGE EXECUTION
# =============================================================================

def run_judge(
    judge_id: str,
    transcript: str,
    model: str
) -> tuple[str, dict | None]:
    """
    Run a single judge on a transcript.

    Returns:
        (raw_response, parsed_json_or_none)
    """
    prompt_text, metadata = load_judge_prompt(judge_id)

    llm = ChatAnthropic(model=model, temperature=0)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm

    response = chain.invoke({"transcript": transcript})
    response_text = response.content

    json_data = extract_json_from_response(response_text)

    return response_text, json_data


# =============================================================================
# MAIN EVALUATION LOGIC
# =============================================================================

def run_evaluation(args):
    """Main evaluation function."""

    # Check for required environment variables
    if not os.environ.get('LANGSMITH_API_KEY') and not os.environ.get('LANGCHAIN_API_KEY'):
        print("ERROR: LANGSMITH_API_KEY or LANGCHAIN_API_KEY environment variable not set")
        return

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        return

    # Determine output directory
    if args.validation:
        # Find next validation batch number
        validation_dir = EVAL_RESULTS_DIR / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y%m%d")
        existing = list(validation_dir.glob(f"{today}_v*"))
        next_num = len(existing) + 1
        run_dir = validation_dir / f"{today}_v{next_num}"
    else:
        runs_dir = EVAL_RESULTS_DIR / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = runs_dir / timestamp

    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {run_dir}")

    # Initialize LangSmith client
    print("Connecting to LangSmith...")
    ls_client = Client()

    # Fetch runs
    print(f"Fetching runs from project: {args.project}")
    if args.tag:
        print(f"Filtering by tag: {args.tag}")

    filter_kwargs = {
        "project_name": args.project,
        "limit": args.limit,
    }
    if args.run_filter:
        filter_kwargs["filter"] = f'eq(name, "{args.run_filter}")'

    runs = list(ls_client.list_runs(**filter_kwargs))

    # Filter by tag if specified (done client-side since LangSmith API tag filtering is limited)
    if args.tag:
        runs = [r for r in runs if args.tag in (r.tags or [])]

    print(f"Found {len(runs)} conversations to evaluate")

    if not runs:
        print("No runs found. Check your project name and filters.")
        return

    # Determine which judges to run
    run_critical = args.stage in ["critical", "all"]
    run_quality = args.stage in ["quality", "all"]

    if args.judge:
        quality_judges = [args.judge] if args.judge in QUALITY_JUDGES else []
        if args.judge not in QUALITY_JUDGES:
            print(f"WARNING: Unknown judge '{args.judge}'. Available: {QUALITY_JUDGES}")
    else:
        quality_judges = QUALITY_JUDGES

    # Process each conversation
    results = []

    for i, run in enumerate(runs, 1):
        short_id = str(run.id)[:8]
        print(f"\n[{i}/{len(runs)}] Processing conversation: {short_id}")

        # Format and clean transcript
        raw_transcript = format_run_as_transcript(run)
        transcript = strip_inner_monologue(raw_transcript)

        result = {
            "langsmith_id": str(run.id),
            "short_id": short_id,
            "run_name": run.name,
        }

        # Stage 1: Critical Criteria
        critical_passed = True
        if run_critical:
            print("  Running critical criteria judge...")
            try:
                response, json_data = run_judge("critical_criteria", transcript, args.model)
                verdict = parse_overall_verdict(response)

                save_results(
                    run_dir=run_dir,
                    judge_id="critical_criteria",
                    short_id=short_id,
                    transcript=transcript,
                    evaluation=response,
                    json_data=json_data,
                    is_critical=True
                )

                result["critical_verdict"] = verdict
                result["critical_json"] = json_data
                critical_passed = (verdict == "PASS")

                print(f"  Critical: {verdict}")

            except Exception as e:
                print(f"  ERROR in critical criteria: {e}")
                result["critical_verdict"] = "ERROR"
                result["critical_error"] = str(e)
                critical_passed = False

        # Stage 2: Quality Judges (only if critical passed)
        if run_quality and critical_passed and quality_judges:
            result["quality_results"] = {}

            for judge_id in quality_judges:
                print(f"  Running {judge_id} judge...")
                try:
                    response, json_data = run_judge(judge_id, transcript, args.model)

                    save_results(
                        run_dir=run_dir,
                        judge_id=judge_id,
                        short_id=short_id,
                        transcript=transcript,
                        evaluation=response,
                        json_data=json_data,
                        is_critical=False
                    )

                    # Extract pass rate from JSON if available
                    if json_data and "overall" in json_data:
                        overall = json_data["overall"]
                        result["quality_results"][judge_id] = {
                            "passed": overall.get("passed_count", 0),
                            "total": overall.get("passed_count", 0) + overall.get("failed_count", 0),
                            "json": json_data
                        }
                        print(f"    {judge_id}: {overall.get('passed_count', '?')}/{overall.get('passed_count', 0) + overall.get('failed_count', 0)} passed")
                    else:
                        result["quality_results"][judge_id] = {"raw_response": True}
                        print(f"    {judge_id}: completed (no JSON parsed)")

                except Exception as e:
                    print(f"    ERROR in {judge_id}: {e}")
                    result["quality_results"][judge_id] = {"error": str(e)}

        elif run_quality and not critical_passed:
            print("  Skipping quality judges (failed critical criteria)")

        results.append(result)

    # Save manifest
    config = {
        "project": args.project,
        "run_filter": args.run_filter,
        "tag": args.tag,
        "model": args.model,
        "limit": args.limit,
        "stage": args.stage,
        "validation": args.validation,
        "quality_judges": quality_judges if run_quality else [],
    }
    manifest_path = save_manifest(run_dir, config, results)

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    if run_critical:
        passed = sum(1 for r in results if r.get("critical_verdict") == "PASS")
        failed = sum(1 for r in results if r.get("critical_verdict") == "FAIL")
        errors = sum(1 for r in results if r.get("critical_verdict") == "ERROR")
        print(f"Critical Criteria: {passed} passed, {failed} failed, {errors} errors")

    if run_quality:
        with_quality = sum(1 for r in results if r.get("quality_results"))
        print(f"Quality Evaluations: {with_quality} conversations evaluated")

    print(f"\nResults saved to: {run_dir}")
    print(f"Manifest: {manifest_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run LLM-as-judge evaluation on tutoring conversations"
    )

    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help=f"LangSmith project name (default: {DEFAULT_PROJECT})"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Max conversations to evaluate (default: {DEFAULT_LIMIT})"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Judge model (default: {DEFAULT_MODEL})"
    )

    parser.add_argument(
        "--run-filter",
        default=DEFAULT_RUN_FILTER,
        help=f"Filter runs by name (default: {DEFAULT_RUN_FILTER})"
    )

    parser.add_argument(
        "--validation",
        action="store_true",
        help="Run in validation mode (output to validation/ subdirectory)"
    )

    parser.add_argument(
        "--stage",
        choices=["critical", "quality", "all"],
        default="all",
        help="Which stage(s) to run (default: all)"
    )

    parser.add_argument(
        "--judge",
        help=f"Run specific quality judge only. Options: {', '.join(QUALITY_JUDGES)}"
    )

    parser.add_argument(
        "--tag",
        help="Filter runs by tag (e.g., 'eval-batch-1')"
    )

    args = parser.parse_args()
    run_evaluation(args)


if __name__ == "__main__":
    main()
