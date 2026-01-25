"""
Live Dashboard Generator for MentorAI Evaluations
==================================================

Generates a self-contained HTML dashboard with all evaluation data embedded.
The dashboard can be opened locally or deployed to GitHub Pages for team sharing.

By default, aggregates results from runs dated 2026-01-21 onwards in
eval_results/runs/. Use --no-aggregate for single-run mode.

Features:
- Aggregates results from all evaluation runs (deduplicates by conversation ID)
- All data embedded as JSON (no external fetch needed)
- Summary cards: Critical pass rate, Quality average, Progress
- Per-criteria table with pass rates
- Per-conversation table with expandable details

Usage:
    python generate_dashboard.py                    # Aggregate all runs (default)
    python generate_dashboard.py --no-aggregate     # Single run only
    python generate_dashboard.py --run <path>       # Specify output location
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
EVAL_RESULTS_DIR = SCRIPT_DIR / "eval_results"
HUMAN_RATINGS_DIR = EVAL_RESULTS_DIR / "human_ratings"
CONVERSATIONS_DIR = SCRIPT_DIR / "conversations"

# GitHub repo URL for transcript links
GITHUB_BASE_URL = "https://github.com/rkoblic/cognitive-apprenticeship-agent/blob/main"

# Criteria to show in deep-dive section
DEEP_DIVE_CRITERIA = ["B-03", "B-04", "E-02", "F-01"]


def find_latest_run() -> Path | None:
    """Find the most recent evaluation run directory."""
    runs_dir = EVAL_RESULTS_DIR / "runs"
    if not runs_dir.exists():
        return None

    run_dirs = sorted(runs_dir.iterdir(), reverse=True)
    return run_dirs[0] if run_dirs else None


def build_transcript_index(manifest: dict) -> dict:
    """
    Build mapping from langsmith_id to transcript path.

    Uses batch dataset name to find corresponding conversations folder,
    then matches transcripts by persona name.

    Returns:
        Dict mapping langsmith_id to relative transcript path
    """
    index = {}

    if not CONVERSATIONS_DIR.exists():
        return index

    # Group conversations by their source batch
    # The manifest may aggregate multiple batches, so we need to check each run
    aggregated_from = manifest.get("aggregated_from", [])

    # For aggregated manifests, we need to load each source manifest to get the dataset info
    if aggregated_from:
        runs_dir = EVAL_RESULTS_DIR / "runs"
        for run_id in aggregated_from:
            run_manifest_path = runs_dir / run_id / "manifest.json"
            if run_manifest_path.exists():
                try:
                    run_manifest = json.loads(run_manifest_path.read_text())
                    _add_transcripts_from_manifest(run_manifest, index)
                except (json.JSONDecodeError, IOError):
                    pass
    else:
        # Single run manifest
        _add_transcripts_from_manifest(manifest, index)

    return index


def _add_transcripts_from_manifest(manifest: dict, index: dict) -> None:
    """Helper to add transcript mappings from a single manifest."""
    dataset = manifest.get("config", {}).get("dataset", "")

    # Extract batch timestamp from dataset name (batch-YYYYMMDD_HHMMSS)
    if not dataset.startswith("batch-"):
        return

    batch_ts = dataset.replace("batch-", "")

    # Try exact match first, then prefix match (handles truncated timestamps)
    batch_dir = None
    if (CONVERSATIONS_DIR / batch_ts).exists():
        batch_dir = CONVERSATIONS_DIR / batch_ts
    else:
        # Try prefix match for truncated timestamps (e.g., 20260123_1355 vs 20260123_135503)
        for d in CONVERSATIONS_DIR.iterdir():
            if d.is_dir() and d.name.startswith(batch_ts):
                batch_dir = d
                break

    if not batch_dir:
        return

    # Build persona -> list of transcript files mapping
    persona_files = {}
    for md_file in sorted(batch_dir.glob("*.md")):
        # Extract persona from filename like "20260123_120156_daniel_SBI.md"
        parts = md_file.stem.split("_")
        if len(parts) >= 3:
            persona = "_".join(parts[2:])  # e.g., "daniel_SBI"
            if persona not in persona_files:
                persona_files[persona] = []
            persona_files[persona].append(md_file)

    # Match conversations to transcript files
    for conv in manifest.get("conversations", []):
        langsmith_id = conv.get("langsmith_id")
        persona = conv.get("persona")

        if not langsmith_id or not persona or langsmith_id in index:
            continue

        if persona in persona_files and persona_files[persona]:
            # Use first available file for this persona, then remove it from the list
            transcript_file = persona_files[persona].pop(0)
            # Store relative path from repo root
            index[langsmith_id] = str(transcript_file.relative_to(SCRIPT_DIR))


def load_manifest(run_dir: Path) -> dict:
    """Load manifest.json from a run directory."""
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json found in {run_dir}")

    return json.loads(manifest_path.read_text())


def aggregate_all_runs(runs_dir: Path | None = None, date_filter: str | None = "20260121") -> dict:
    """
    Load and merge all manifest.json files from runs directory.

    Args:
        runs_dir: Path to runs directory (defaults to eval_results/runs/)
        date_filter: Filter runs by date prefix:
            - "today": Only runs from today (YYYYMMDD)
            - "YYYYMMDD": Only runs from that date onwards (inclusive)
            - None: Include all runs (no filter)

    Returns:
        Merged manifest with all conversations, deduplicated by langsmith_id
    """
    if runs_dir is None:
        runs_dir = EVAL_RESULTS_DIR / "runs"

    if not runs_dir.exists():
        return {"conversations": [], "status": "no_runs"}

    # Resolve date filter
    if date_filter == "today":
        min_date = datetime.now().strftime("%Y%m%d")
    elif date_filter:
        min_date = date_filter
    else:
        min_date = None

    all_conversations = []
    run_ids = []

    for manifest_path in sorted(runs_dir.glob("*/manifest.json")):
        run_id = manifest_path.parent.name

        # Apply date filter - include runs >= min_date
        if min_date and run_id[:8] < min_date:
            continue

        try:
            manifest = json.loads(manifest_path.read_text())
            conversations = manifest.get("conversations", [])
            all_conversations.extend(conversations)
            run_ids.append(run_id)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {manifest_path}: {e}")

    # Helper to count valid (non-error) quality results
    def count_valid_quality_results(conv):
        quality_results = conv.get("quality_results", {})
        count = 0
        for judge_id, result in quality_results.items():
            # Count if it has 'passed' field (not an error)
            if isinstance(result, dict) and "passed" in result:
                count += 1
        return count

    # Deduplicate by langsmith_id (prefer entries with more complete data)
    seen = {}
    for conv in all_conversations:
        langsmith_id = conv.get("langsmith_id")
        if langsmith_id:
            existing = seen.get(langsmith_id)
            if not existing:
                seen[langsmith_id] = conv
            else:
                # Prefer entry with more complete quality data
                existing_valid = count_valid_quality_results(existing)
                new_valid = count_valid_quality_results(conv)
                if new_valid > existing_valid:
                    seen[langsmith_id] = conv
                # If same completeness, prefer valid persona over Unknown
                elif new_valid == existing_valid:
                    new_persona = conv.get("persona")
                    if existing.get("persona") in [None, "Unknown", "unknown"] and new_persona not in [None, "Unknown", "unknown"]:
                        seen[langsmith_id] = conv
        else:
            # No ID, just append (shouldn't happen but be safe)
            seen[id(conv)] = conv

    deduped_conversations = list(seen.values())

    return {
        "run_id": f"aggregated-from-{min_date}" if min_date else "aggregated-all",
        "timestamp": datetime.now().isoformat(),
        "status": "complete",
        "conversations": deduped_conversations,
        "aggregated_from": run_ids,
        "config": {
            "source": "aggregated",
            "total_runs": len(run_ids),
            "date_filter": date_filter,
        }
    }


def load_human_ratings() -> dict:
    """Load all human rating JSON files from eval_results/human_ratings/."""
    if not HUMAN_RATINGS_DIR.exists():
        return {"ratings": [], "by_langsmith_id": {}, "by_timestamp": {}}

    ratings = []
    by_langsmith_id = {}
    by_timestamp = {}

    for json_path in sorted(HUMAN_RATINGS_DIR.glob("*.json")):
        if json_path.name == "index.json" or json_path.name == "id_mapping.json":
            continue
        try:
            rating = json.loads(json_path.read_text())
            ratings.append(rating)

            # Index by langsmith_id if available
            langsmith_id = rating.get("metadata", {}).get("langsmith_id")
            if langsmith_id:
                by_langsmith_id[langsmith_id] = rating

            # Index by timestamp_persona key
            ts = rating.get("metadata", {}).get("conversation_timestamp", "")
            persona = rating.get("metadata", {}).get("persona", "")
            if ts and persona:
                by_timestamp[f"{ts}_{persona}"] = rating

        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {json_path}: {e}")

    return {
        "ratings": ratings,
        "by_langsmith_id": by_langsmith_id,
        "by_timestamp": by_timestamp,
    }


def get_llm_verdict_for_criterion(conv: dict, criterion_code: str) -> str | None:
    """Extract LLM verdict for a specific criterion code from conversation data."""
    # Check critical criteria first
    critical_json = conv.get("critical_json", {})
    criteria = critical_json.get("criteria", {})
    if criterion_code in criteria:
        return criteria[criterion_code].get("verdict")

    # Check quality results
    quality_results = conv.get("quality_results", {})
    for judge_data in quality_results.values():
        judge_json = judge_data.get("json", {})
        judge_criteria = judge_json.get("criteria", {})
        if criterion_code in judge_criteria:
            return judge_criteria[criterion_code].get("verdict")

    return None


def get_llm_evidence_for_criterion(conv: dict, criterion_code: str) -> str:
    """Extract LLM evidence for a specific criterion code from conversation data."""
    # Check critical criteria first
    critical_json = conv.get("critical_json", {})
    criteria = critical_json.get("criteria", {})
    if criterion_code in criteria:
        return criteria[criterion_code].get("evidence", "")

    # Check quality results
    quality_results = conv.get("quality_results", {})
    for judge_data in quality_results.values():
        judge_json = judge_data.get("json", {})
        judge_criteria = judge_json.get("criteria", {})
        if criterion_code in judge_criteria:
            return judge_criteria[criterion_code].get("evidence", "")

    return ""


def calculate_human_agreement(conv: dict, human_rating: dict) -> dict:
    """Calculate agreement between LLM and human ratings for a conversation."""
    human_criteria = human_rating.get("criteria", {})

    agree = 0
    disagree = 0
    disagreements = []

    for code, human_data in human_criteria.items():
        human_verdict = human_data.get("verdict")
        if human_verdict == "N/A":
            continue  # Skip N/A criteria

        llm_verdict = get_llm_verdict_for_criterion(conv, code)
        if llm_verdict in ["PASS", "FAIL"] and human_verdict in ["PASS", "FAIL"]:
            if llm_verdict == human_verdict:
                agree += 1
            else:
                disagree += 1
                disagreements.append({
                    "code": code,
                    "llm": llm_verdict,
                    "human": human_verdict,
                    "human_evidence": human_data.get("evidence", ""),
                    "llm_evidence": get_llm_evidence_for_criterion(conv, code)
                })

    total = agree + disagree
    return {
        "agree": agree,
        "disagree": disagree,
        "total": total,
        "percentage": round(agree / total * 100, 1) if total > 0 else None,
        "disagreements": disagreements
    }


def calculate_human_metrics(manifest: dict, human_ratings: dict) -> dict:
    """Calculate human spot-check metrics."""
    if not human_ratings.get("ratings"):
        return {
            "has_data": False,
            "total_conversations_rated": 0,
            "total_criteria_compared": 0,
            "total_agree": 0,
            "overall_agreement_pct": None,
            "by_conversation": [],
            "raters": []
        }

    conversations = manifest.get("conversations", [])
    by_conversation = []
    total_agree = 0
    total_criteria = 0
    raters = set()

    # Try to match each human rating to a conversation
    for rating in human_ratings["ratings"]:
        raters.add(rating.get("metadata", {}).get("rater", "Unknown"))

        # Try to find matching conversation by langsmith_id
        langsmith_id = rating.get("metadata", {}).get("langsmith_id")
        matched_conv = None

        if langsmith_id:
            for conv in conversations:
                if conv.get("langsmith_id") == langsmith_id:
                    matched_conv = conv
                    break

        # Calculate agreement even if no LLM match (will have empty disagreements)
        if matched_conv:
            agreement = calculate_human_agreement(matched_conv, rating)
        else:
            # No matching conversation - show human data but no agreement stats
            agreement = {
                "agree": 0,
                "disagree": 0,
                "total": 0,
                "percentage": None,
                "disagreements": [],
                "no_llm_match": True
            }

        by_conversation.append({
            "timestamp": rating.get("metadata", {}).get("conversation_timestamp", ""),
            "persona": rating.get("metadata", {}).get("persona", ""),
            "rater": rating.get("metadata", {}).get("rater", ""),
            "langsmith_id": langsmith_id,
            "human_summary": rating.get("summary", {}),
            "agreement": agreement
        })

        total_agree += agreement["agree"]
        total_criteria += agreement["total"]

    return {
        "has_data": True,
        "total_conversations_rated": len(human_ratings["ratings"]),
        "total_criteria_compared": total_criteria,
        "total_agree": total_agree,
        "overall_agreement_pct": round(total_agree / total_criteria * 100, 1) if total_criteria > 0 else None,
        "by_conversation": by_conversation,
        "raters": sorted(list(raters))
    }


# Persona name to letter mapping
PERSONA_LETTERS = {
    "amara_SBI": "A",
    "bailey_SBI": "B",
    "carlos_SBI": "C",
    "daniel_SBI": "D",
    "elise_SBI": "E",
    "fatou_SBI": "F",
}
PERSONA_ORDER = ["amara_SBI", "bailey_SBI", "carlos_SBI", "daniel_SBI", "elise_SBI", "fatou_SBI"]


def calculate_dashboard_metrics(manifest: dict) -> dict:
    """Calculate metrics for dashboard display."""
    conversations = manifest.get("conversations", [])
    total = len(conversations)

    if total == 0:
        return {
            "total": 0,
            "completed": 0,
            "critical_passed": 0,
            "critical_failed": 0,
            "critical_pass_rate": 0,
            "quality_total_passed": 0,
            "quality_total_criteria": 0,
            "quality_average": 0,
            "per_criteria": {},
            "personas_seen": [],
        }

    # Critical stats
    critical_passed = sum(1 for c in conversations if c.get("critical_verdict") == "PASS")
    critical_failed = sum(1 for c in conversations if c.get("critical_verdict") == "FAIL")
    completed = critical_passed + critical_failed

    # Track which personas we've seen
    personas_seen = set()

    # Quality stats - aggregate across all judges AND individual criteria
    per_criteria = {}
    total_quality_passed = 0
    total_quality_criteria = 0

    for conv in conversations:
        persona = conv.get("persona", "unknown")
        personas_seen.add(persona)

        quality_results = conv.get("quality_results", {})
        for judge_id, result in quality_results.items():
            if judge_id not in per_criteria:
                per_criteria[judge_id] = {
                    "passed": 0,
                    "total": 0,
                    "individual": {},
                    "by_persona": {p: {"passed": 0, "total": 0} for p in PERSONA_ORDER}
                }

            passed = result.get("passed", 0)
            judge_total = result.get("total", 0)

            per_criteria[judge_id]["passed"] += passed
            per_criteria[judge_id]["total"] += judge_total
            total_quality_passed += passed
            total_quality_criteria += judge_total

            # Track per-persona stats for this judge
            if persona in PERSONA_ORDER:
                per_criteria[judge_id]["by_persona"][persona]["passed"] += passed
                per_criteria[judge_id]["by_persona"][persona]["total"] += judge_total

            # Track individual criteria codes (e.g., A-01, B-02)
            if result.get("json") and result["json"].get("criteria"):
                for code, data in result["json"]["criteria"].items():
                    if code not in per_criteria[judge_id]["individual"]:
                        per_criteria[judge_id]["individual"][code] = {
                            "passed": 0,
                            "failed": 0,
                            "by_persona": {p: {"passed": 0, "failed": 0} for p in PERSONA_ORDER}
                        }
                    if data.get("verdict") == "PASS":
                        per_criteria[judge_id]["individual"][code]["passed"] += 1
                        if persona in PERSONA_ORDER:
                            per_criteria[judge_id]["individual"][code]["by_persona"][persona]["passed"] += 1
                    elif data.get("verdict") == "FAIL":
                        per_criteria[judge_id]["individual"][code]["failed"] += 1
                        if persona in PERSONA_ORDER:
                            per_criteria[judge_id]["individual"][code]["by_persona"][persona]["failed"] += 1

    # Calculate percentages
    for judge_id in per_criteria:
        p = per_criteria[judge_id]
        p["percentage"] = round(p["passed"] / p["total"] * 100, 1) if p["total"] > 0 else 0

    # Sort personas seen by defined order
    sorted_personas = [p for p in PERSONA_ORDER if p in personas_seen]

    return {
        "total": total,
        "completed": completed,
        "critical_passed": critical_passed,
        "critical_failed": critical_failed,
        "critical_pass_rate": round(critical_passed / completed * 100, 1) if completed > 0 else 0,
        "quality_total_passed": total_quality_passed,
        "quality_total_criteria": total_quality_criteria,
        "quality_average": round(total_quality_passed / total_quality_criteria * 100, 1) if total_quality_criteria > 0 else 0,
        "per_criteria": per_criteria,
        "personas_seen": sorted_personas,
        "persona_letters": PERSONA_LETTERS,
    }


def generate_html(manifest: dict, metrics: dict, transcript_index: dict | None = None) -> str:
    """Generate self-contained HTML dashboard."""
    run_id = manifest.get("run_id", "Unknown")
    status = manifest.get("status", "unknown")
    timestamp = manifest.get("timestamp", datetime.now().isoformat())
    conversations = manifest.get("conversations", [])

    if transcript_index is None:
        transcript_index = {}

    # Status badge colors
    status_colors = {
        "in_progress": "#f59e0b",  # amber
        "complete": "#10b981",     # green
        "unknown": "#6b7280",      # gray
    }
    status_color = status_colors.get(status, status_colors["unknown"])

    # Serialize manifest and transcript index to embed as JSON
    manifest_json = json.dumps(manifest, indent=2)
    transcript_index_json = json.dumps(transcript_index)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MentorAI Evaluation Dashboard - {run_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f3f4f6;
            color: #1f2937;
            line-height: 1.5;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        h1 {{
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .meta {{
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 0.875rem;
            color: #6b7280;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card-label {{
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }}
        .card-value {{
            font-size: 2rem;
            font-weight: 700;
        }}
        .card-value.pass {{
            color: #10b981;
        }}
        .card-value.fail {{
            color: #ef4444;
        }}
        .section {{
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        .section-header {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            font-weight: 600;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            font-weight: 600;
            font-size: 0.875rem;
            color: #6b7280;
            background: #f9fafb;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        /* Rate colors now use inline styles with gradient colors */
        .verdict {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .verdict.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        .verdict.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .verdict.pending {{
            background: #e5e7eb;
            color: #4b5563;
        }}
        .na-badge {{
            color: #6b7280;
            font-size: 0.85em;
        }}
        .warning-badge {{
            cursor: help;
        }}
        .expandable {{
            cursor: pointer;
        }}
        .expandable:hover {{
            background: #f9fafb;
        }}
        .details {{
            display: none;
            background: #f9fafb;
        }}
        .details.open {{
            display: table-row;
        }}
        .details-content {{
            padding: 1rem;
            font-size: 0.875rem;
        }}
        .quality-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem 1.5rem;
            background: #f9fafb;
            padding: 1rem;
            border-radius: 0.375rem;
            border: 1px solid #e5e7eb;
        }}
        .quality-item {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        .quality-item span:first-child {{
            font-weight: 500;
            color: #374151;
            text-transform: capitalize;
        }}
        .quality-item span:last-child {{
            font-size: 0.875rem;
            color: #10b981;
            font-weight: 600;
        }}
        .timestamp {{
            font-size: 0.75rem;
            color: #9ca3af;
        }}
        footer {{
            text-align: center;
            padding: 1rem;
            color: #9ca3af;
            font-size: 0.75rem;
        }}
        /* Evidence display styles */
        .evidence-section {{
            margin-top: 1rem;
            border-top: 1px solid #e5e7eb;
            padding-top: 1rem;
        }}
        .evidence-section h4 {{
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #374151;
        }}
        .criterion-item {{
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 0.375rem;
            border-left: 3px solid;
        }}
        .criterion-item.pass {{
            background: #f0fdf4;
            border-left-color: #10b981;
        }}
        .criterion-item.fail {{
            background: #fef2f2;
            border-left-color: #ef4444;
        }}
        .criterion-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .criterion-code {{
            font-weight: 600;
            font-size: 0.875rem;
        }}
        .criterion-item.pass .criterion-code {{
            color: #065f46;
        }}
        .criterion-item.fail .criterion-code {{
            color: #991b1b;
        }}
        .evidence-text {{
            font-size: 0.8125rem;
            color: #4b5563;
            line-height: 1.6;
            font-style: italic;
        }}
        .evidence-text::before {{
            content: '"';
        }}
        .evidence-text::after {{
            content: '"';
        }}
        .judge-section {{
            margin-top: 1.5rem;
        }}
        .judge-section h5 {{
            font-size: 0.8125rem;
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .failed-summary {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 0.375rem;
            padding: 0.75rem;
            margin-bottom: 1rem;
        }}
        .failed-summary-title {{
            font-weight: 600;
            color: #991b1b;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }}
        .toggle-evidence {{
            font-size: 0.75rem;
            color: #6b7280;
            cursor: pointer;
            text-decoration: underline;
        }}
        .toggle-evidence:hover {{
            color: #374151;
        }}
        .criteria-list {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        .criteria-list.expanded {{
            max-height: 2000px;
        }}
        /* Expandable criteria rows */
        .criteria-expand-row {{
            cursor: pointer;
        }}
        .criteria-expand-row:hover {{
            background: #f9fafb;
        }}
        .criteria-expand-row td:first-child::before {{
            content: '\u25B6';
            display: inline-block;
            margin-right: 0.5rem;
            font-size: 0.625rem;
            transition: transform 0.2s ease;
            color: #9ca3af;
        }}
        .criteria-expand-row.open td:first-child::before {{
            transform: rotate(90deg);
        }}
        .criteria-details-row {{
            display: none;
            background: #f9fafb;
        }}
        .criteria-details-row.open {{
            display: table-row;
        }}
        .persona-tag {{
            font-size: 0.75rem;
            background: #e0e7ff;
            color: #4338ca;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-weight: 500;
        }}
        /* Tooltip styles */
        .criterion-code-tooltip {{
            position: relative;
            cursor: help;
            border-bottom: 1px dotted #9ca3af;
        }}
        .criterion-code-tooltip:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            left: 0;
            top: 100%;
            margin-top: 0.25rem;
            padding: 0.5rem 0.75rem;
            background: #1f2937;
            color: white;
            font-size: 0.75rem;
            font-weight: normal;
            border-radius: 0.375rem;
            white-space: normal;
            width: max-content;
            max-width: 300px;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            line-height: 1.4;
        }}
        /* Persona filter styles */
        .filter-bar {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-bar label {{
            font-size: 0.875rem;
            color: #6b7280;
            margin-right: 0.5rem;
        }}
        .filter-btn {{
            padding: 0.375rem 0.75rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            background: white;
            font-size: 0.8125rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .filter-btn:hover {{
            border-color: #4338ca;
            color: #4338ca;
        }}
        .filter-btn.active {{
            background: #4338ca;
            color: white;
            border-color: #4338ca;
        }}
        .persona-group {{
            margin-bottom: 1.5rem;
        }}
        .persona-group-header {{
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f3f4f6;
            border-bottom: 1px solid #e5e7eb;
            cursor: pointer;
            user-select: none;
        }}
        .persona-group-header:hover {{
            background: #e5e7eb;
        }}
        .persona-group-header h3 {{
            font-size: 0.9375rem;
            font-weight: 600;
            margin: 0;
            flex: 1;
        }}
        .persona-group-header .toggle-icon {{
            font-size: 0.75rem;
            color: #6b7280;
            transition: transform 0.2s ease;
        }}
        .persona-group-header.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        .persona-group-content {{
            display: block;
        }}
        .persona-group-content.collapsed {{
            display: none;
        }}
        .persona-stats {{
            font-size: 0.8125rem;
            color: #6b7280;
            margin-left: 1rem;
        }}
        /* Deep-dive section styles */
        .deep-dive-btn {{
            padding: 0.375rem 0.75rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            background: white;
            font-size: 0.8125rem;
            cursor: pointer;
            transition: all 0.15s ease;
            margin-right: 0.5rem;
        }}
        .deep-dive-btn:hover {{
            border-color: #ef4444;
            color: #ef4444;
        }}
        .deep-dive-btn.active {{
            background: #fef2f2;
            color: #991b1b;
            border-color: #fecaca;
        }}
        .count-badge {{
            display: inline-block;
            background: #fee2e2;
            color: #991b1b;
            padding: 0.125rem 0.375rem;
            border-radius: 9999px;
            font-size: 0.6875rem;
            font-weight: 600;
            margin-left: 0.25rem;
        }}
        .deep-dive-btn.active .count-badge {{
            background: #991b1b;
            color: white;
        }}
        .evidence-cell {{
            max-width: 400px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .evidence-cell:hover {{
            white-space: normal;
            overflow: visible;
            position: relative;
            z-index: 10;
            background: #f9fafb;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 0.25rem;
            padding: 0.5rem;
        }}
        .transcript-link {{
            color: #4338ca;
            text-decoration: none;
            font-weight: 500;
        }}
        .transcript-link:hover {{
            text-decoration: underline;
        }}
        .no-link {{
            color: #9ca3af;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>MentorAI Evaluation Dashboard</h1>
            <div class="meta">
                <span>Run: <strong>{run_id}</strong></span>
                <span class="badge" style="background: {status_color}">{status.replace("_", " ").title()}</span>
                <span class="timestamp">Updated: {timestamp}</span>
            </div>
        </header>

        <div class="cards">
            <div class="card">
                <div class="card-label">Critical Pass Rate</div>
                <div class="card-value {"pass" if metrics["critical_pass_rate"] >= 80 else "fail"}">{metrics["critical_pass_rate"]}%</div>
                <div class="card-label">{metrics["critical_passed"]}/{metrics["completed"]} passed</div>
            </div>
            <div class="card">
                <div class="card-label">Quality Average</div>
                <div class="card-value">{metrics["quality_average"]}%</div>
                <div class="card-label">{metrics["quality_total_passed"]}/{metrics["quality_total_criteria"]} criteria</div>
            </div>
            <div class="card">
                <div class="card-label">Progress</div>
                <div class="card-value">{metrics["completed"]}/{metrics["total"]}</div>
                <div class="card-label">conversations evaluated</div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Per-Criteria Results</div>
            <table>
                <thead id="criteria-header">
                </thead>
                <tbody id="criteria-table">
                </tbody>
            </table>
        </div>

        <div class="section" id="human-spot-check-section" style="display: none;">
            <div class="section-header">Human Spot-Check Agreement</div>
            <div class="cards" style="padding: 1rem 1.5rem;">
                <div class="card">
                    <div class="card-label">Overall Agreement</div>
                    <div class="card-value" id="human-agreement-pct">-</div>
                    <div class="card-label" id="human-agreement-detail">-</div>
                </div>
                <div class="card">
                    <div class="card-label">Conversations Rated</div>
                    <div class="card-value" id="human-conv-count">-</div>
                    <div class="card-label" id="human-raters">-</div>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Conversation</th>
                        <th>Persona</th>
                        <th>Rater</th>
                        <th>Agreement</th>
                        <th>Disagreements</th>
                    </tr>
                </thead>
                <tbody id="human-spot-check-table">
                </tbody>
            </table>
        </div>

        <div class="section" id="criterion-deep-dive-section">
            <div class="section-header">Criterion Deep-Dive</div>
            <div class="filter-bar" style="padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;">
                <label>Show failures for:</label>
                <button class="deep-dive-btn active" data-criterion="B-03">B-03 <span class="count-badge">0</span></button>
                <button class="deep-dive-btn active" data-criterion="B-04">B-04 <span class="count-badge">0</span></button>
                <button class="deep-dive-btn active" data-criterion="E-02">E-02 <span class="count-badge">0</span></button>
                <button class="deep-dive-btn active" data-criterion="F-01">F-01 <span class="count-badge">0</span></button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Persona</th>
                        <th>Criterion</th>
                        <th>Evidence</th>
                        <th>Transcript</th>
                    </tr>
                </thead>
                <tbody id="deep-dive-table">
                </tbody>
            </table>
        </div>

        <div class="section">
            <div class="section-header">Per-Conversation Results</div>
            <div class="filter-bar" style="padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;">
                <label>Filter by persona:</label>
                <button class="filter-btn active" data-persona="all">All</button>
                <span id="persona-filters"></span>
                <span style="margin-left: auto; font-size: 0.8125rem; color: #6b7280;">
                    <label><input type="checkbox" id="group-by-persona" style="margin-right: 0.25rem;"> Group by persona</label>
                </span>
            </div>
            <div id="conversations-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Persona</th>
                            <th>Critical</th>
                            <th>Quality Score</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="conversations">
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            Last generated: {datetime.now().isoformat()}
        </footer>
    </div>

    <script>
        const manifest = {manifest_json};
        const metrics = {json.dumps(metrics)};

        // Transcript index for linking to GitHub
        const transcriptIndex = {transcript_index_json};
        const GITHUB_BASE_URL = '{GITHUB_BASE_URL}';
        const DEEP_DIVE_CRITERIA = ['B-03', 'B-04', 'E-02', 'F-01'];

        // Criterion descriptions for tooltips
        const CRITERION_DESCRIPTIONS = {{
            "A-01": "Goal Clarity: Mentor confirms the session goal is drafting SBI feedback and names what success looks like.",
            "A-02": "Phase Signaling: Mentor explicitly marks transitions between phases (modeling, practice, coaching).",
            "A-03": "Realistic Scenario: The practice scenario feels like a real workplace situation with plausible dynamics.",
            "B-01": "Shows, Not Tells: Mentor demonstrates an actual complete SBI example as a model.",
            "B-02": "Thinking Out Loud: During modeling, mentor explains why they made each choice, not just what the components are.",
            "B-03": "Visible Decision-Making: Mentor shows at least one choice point where they consider alternatives.",
            "B-04": "Self-Checking: Mentor models checking their own work against criteria.",
            "B-05": "Heuristic Offered: Mentor provides at least one reusable rule of thumb the learner can apply independently.",
            "C-01": "Specific Feedback: Mentor points to exact language and names the specific issue with that language.",
            "C-02": "Actionable Direction: When giving feedback, mentor includes what to do next, not just what's wrong.",
            "C-03": "Revision Requested: After giving feedback, mentor explicitly asks the learner to revise or try again.",
            "C-04": "Revision Checked: When learner revises, mentor evaluates the revision specifically.",
            "C-05": "Productive Struggle: When learner errs, mentor explores it before correcting rather than immediately providing the fix.",
            "C-06": "Elicits Articulation: Mentor asks learner to explain reasoning behind an SBI choice.",
            "C-07": "Prompts Reflection: Mentor asks learner to reflect on their learning process.",
            "D-01": "Catches Vague Situations: When learner uses vague time references, mentor prompts for specific time and place.",
            "D-02": "Catches Judgment Leakage: When behavior contains interpretation, mentor prompts for observable actions.",
            "D-03": "Catches Accusatory Impact: When learner uses blame language, mentor prompts for owned 'I' statements.",
            "D-04": "Tests Distinctions: Mentor probes the observable vs. interpretive line to test learner understanding.",
            "D-05": "Scaffolds the Stuck: When learner struggles, mentor offers targeted help rather than full answer or generic encouragement.",
            "D-06": "Reusable Scaffold: Mentor provides tools the learner can reuse independently (camera test, self-check, etc.).",
            "E-01": "Checks Before Advancing: Before moving to next phase, mentor checks learner's readiness.",
            "E-02": "Fades Support: After learner shows competence, mentor pulls back and gives less detailed guidance.",
            "E-03": "Protects Productive Struggle: When learner asks for answer, mentor requires at least one attempt first.",
            "F-01": "Varied Turn Structure: Mentor doesn't follow the same formula every turn; there's variety in rhythm.",
            "F-02": "Has a Voice: Mentor shows some personality—reactions, opinions, humor, or human touch.",
            "F-03": "Responds to Negative Affect: When learner shows anxiety/frustration, mentor acknowledges and responds supportively."
        }};

        function escapeHtml(text) {{
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // Calculate color based on percentage thresholds
        // ≤40% = red, 41-79% = orange, ≥80% = green
        function getRateColor(pct) {{
            if (pct === '-' || pct === null || pct === undefined) return '#6b7280';  // gray for no data
            if (pct <= 40) return 'hsl(0, 85%, 40%)';     // red
            if (pct < 80) return 'hsl(35, 85%, 45%)';    // orange
            return 'hsl(120, 85%, 35%)';                  // green
        }}

        function getRateStyle(pct) {{
            return `color: ${{getRateColor(pct)}}; font-weight: 600;`;
        }}

        function extractPersona(conv) {{
            // Try persona field first (if valid)
            if (conv.persona && conv.persona !== 'Unknown' && conv.persona !== 'unknown') {{
                return conv.persona;
            }}
            // Try run_name pattern
            if (conv.run_name) {{
                const match = conv.run_name.match(/([a-z]+_SBI)/i);
                if (match) return match[1].toLowerCase().replace('_sbi', '_SBI');
            }}
            // Try dataset_name (batch datasets include persona)
            if (conv.dataset_name) {{
                const match = conv.dataset_name.match(/([a-z]+_SBI)/i);
                if (match) return match[1].toLowerCase().replace('_sbi', '_SBI');
            }}
            return 'Unknown';
        }}

        function renderCriteriaTable() {{
            const thead = document.getElementById('criteria-header');
            const tbody = document.getElementById('criteria-table');
            const perCriteria = metrics.per_criteria || {{}};
            const personasSeen = metrics.personas_seen || [];
            const personaLetters = metrics.persona_letters || {{}};
            const numPersonaCols = personasSeen.length;
            const totalCols = 4 + numPersonaCols;
            const conversations = manifest.conversations || [];

            // Calculate per-persona conversation counts
            const personaCounts = {{}};
            conversations.forEach(conv => {{
                const persona = extractPersona(conv);
                personaCounts[persona] = (personaCounts[persona] || 0) + 1;
            }});

            // Render header with counts
            let headerHtml = '<tr><th>Criterion</th><th>Passed</th><th>Pass Rate</th>';
            personasSeen.forEach(p => {{
                const count = personaCounts[p] || 0;
                headerHtml += `<th style="width: 55px; text-align: center" title="${{p}}">${{personaLetters[p] || p[0].toUpperCase()}} (${{count}})</th>`;
            }});
            headerHtml += '</tr>';
            thead.innerHTML = headerHtml;

            Object.entries(perCriteria).forEach(([judgeId, data], index) => {{
                const percentage = data.percentage || 0;
                const progressClass = percentage >= 80 ? 'high' : percentage >= 50 ? 'medium' : 'low';
                const byPersona = data.by_persona || {{}};

                // Main row
                const row = document.createElement('tr');
                row.className = 'criteria-expand-row';
                row.onclick = (e) => toggleCriteriaDetails(index, e);
                let rowHtml = `
                    <td>${{judgeId.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}}</td>
                    <td>${{data.passed}}/${{data.total}}</td>
                    <td style="${{getRateStyle(percentage)}}">${{percentage}}%</td>
                `;
                // Add persona columns
                personasSeen.forEach(p => {{
                    const pData = byPersona[p] || {{passed: 0, total: 0}};
                    const pPct = pData.total > 0 ? Math.round(pData.passed / pData.total * 100) : '-';
                    const style = pPct === '-' ? '' : getRateStyle(pPct);
                    rowHtml += `<td style="text-align: center; ${{style}}">${{pPct}}${{pPct !== '-' ? '%' : ''}}</td>`;
                }});
                row.innerHTML = rowHtml;
                tbody.appendChild(row);

                // Details row with individual criteria
                const detailsRow = document.createElement('tr');
                detailsRow.className = 'criteria-details-row';
                detailsRow.id = `criteria-details-${{index}}`;

                const individual = data.individual || {{}};
                const sortedCriteria = Object.entries(individual).sort((a, b) => a[0].localeCompare(b[0]));

                // Add individual criteria as sub-rows (same format as main rows)
                sortedCriteria.forEach(([code, stats]) => {{
                    const total = stats.passed + stats.failed;
                    const pct = total > 0 ? Math.round(stats.passed / total * 100) : 0;
                    const cByPersona = stats.by_persona || {{}};
                    const tooltip = CRITERION_DESCRIPTIONS[code] || code;

                    const subRow = document.createElement('tr');
                    subRow.className = 'criteria-details-row';
                    subRow.id = `criteria-details-${{index}}-${{code}}`;

                    let subRowHtml = `
                        <td style="padding-left: 2rem;"><span class="criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{code}}</span></td>
                        <td>${{stats.passed}}/${{total}}</td>
                        <td style="${{getRateStyle(pct)}}">${{pct}}%</td>
                    `;
                    // Add persona columns
                    personasSeen.forEach(p => {{
                        const ps = cByPersona[p] || {{passed: 0, failed: 0}};
                        const pTotal = ps.passed + ps.failed;
                        const pPct = pTotal > 0 ? Math.round(ps.passed / pTotal * 100) : '-';
                        const style = pPct === '-' ? '' : getRateStyle(pPct);
                        subRowHtml += `<td style="text-align: center; ${{style}}">${{pPct}}${{pPct !== '-' ? '%' : ''}}</td>`;
                    }});
                    subRow.innerHTML = subRowHtml;
                    tbody.appendChild(subRow);
                }});
            }});
        }}

        function toggleCriteriaDetails(index, event) {{
            if (event) event.stopPropagation();
            const row = document.querySelectorAll('.criteria-expand-row')[index];
            row.classList.toggle('open');
            // Toggle all sub-rows for this index
            document.querySelectorAll(`[id^="criteria-details-${{index}}-"]`).forEach(el => {{
                el.classList.toggle('open');
            }});
            saveState();
        }}

        function renderCriteriaEvidence(criteria, showAll = false) {{
            if (!criteria || Object.keys(criteria).length === 0) {{
                return '<em>No criteria data available</em>';
            }}

            // Separate failed and passed criteria
            const failed = [];
            const passed = [];
            for (const [code, data] of Object.entries(criteria)) {{
                if (data.verdict === 'FAIL') {{
                    failed.push({{ code, ...data }});
                }} else if (data.verdict === 'PASS') {{
                    passed.push({{ code, ...data }});
                }}
            }}

            let html = '';

            // Always show failed criteria first and prominently
            if (failed.length > 0) {{
                html += '<div class="failed-summary"><div class="failed-summary-title">Failed Criteria (' + failed.length + ')</div>';
                failed.forEach(item => {{
                    const tooltip = CRITERION_DESCRIPTIONS[item.code] || item.code;
                    html += `<div class="criterion-item fail">
                        <div class="criterion-header">
                            <span class="criterion-code criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{item.code}}</span>
                            <span class="verdict fail">FAIL</span>
                        </div>
                        <div class="evidence-text">${{escapeHtml(item.evidence)}}</div>
                    </div>`;
                }});
                html += '</div>';
            }}

            // Show passed criteria (collapsed by default if there are many)
            if (passed.length > 0 && showAll) {{
                html += '<div class="passed-criteria">';
                passed.forEach(item => {{
                    const tooltip = CRITERION_DESCRIPTIONS[item.code] || item.code;
                    html += `<div class="criterion-item pass">
                        <div class="criterion-header">
                            <span class="criterion-code criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{item.code}}</span>
                            <span class="verdict pass">PASS</span>
                        </div>
                        <div class="evidence-text">${{escapeHtml(item.evidence)}}</div>
                    </div>`;
                }});
                html += '</div>';
            }} else if (passed.length > 0) {{
                html += `<div class="toggle-evidence" onclick="this.nextElementSibling.classList.toggle('expanded'); this.textContent = this.nextElementSibling.classList.contains('expanded') ? 'Hide ${{passed.length}} passed criteria' : 'Show ${{passed.length}} passed criteria'">Show ${{passed.length}} passed criteria</div>`;
                html += '<div class="criteria-list">';
                passed.forEach(item => {{
                    const tooltip = CRITERION_DESCRIPTIONS[item.code] || item.code;
                    html += `<div class="criterion-item pass">
                        <div class="criterion-header">
                            <span class="criterion-code criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{item.code}}</span>
                            <span class="verdict pass">PASS</span>
                        </div>
                        <div class="evidence-text">${{escapeHtml(item.evidence)}}</div>
                    </div>`;
                }});
                html += '</div>';
            }}

            return html;
        }}

        // State persistence helpers
        const STATE_KEY = 'mentorDashboardState';

        function saveState() {{
            // Get indices of collapsed groups by checking ALL headers
            const allGroupHeaders = document.querySelectorAll('.persona-group-header');
            const collapsedGroupIndices = [];
            allGroupHeaders.forEach((el, idx) => {{
                if (el.classList.contains('collapsed')) collapsedGroupIndices.push(idx);
            }});

            // Get indices of expanded criteria by checking ALL criteria rows
            const allCriteriaRows = document.querySelectorAll('.criteria-expand-row');
            const expandedCriteriaIndices = [];
            allCriteriaRows.forEach((el, idx) => {{
                if (el.classList.contains('open')) expandedCriteriaIndices.push(idx);
            }});

            const state = {{
                personaFilter: currentPersonaFilter,
                groupByPersona: groupByPersona,
                expandedDetails: Array.from(document.querySelectorAll('.details.open')).map(el => el.id),
                collapsedGroups: collapsedGroupIndices,
                expandedCriteria: expandedCriteriaIndices
            }};
            try {{
                localStorage.setItem(STATE_KEY, JSON.stringify(state));
            }} catch (e) {{ /* ignore storage errors */ }}
        }}

        function loadState() {{
            try {{
                const saved = localStorage.getItem(STATE_KEY);
                return saved ? JSON.parse(saved) : null;
            }} catch (e) {{
                return null;
            }}
        }}

        function restoreExpandedState() {{
            const state = loadState();
            if (!state) return;

            // Restore expanded details
            (state.expandedDetails || []).forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.add('open');
            }});

            // Restore collapsed persona groups
            (state.collapsedGroups || []).forEach(idx => {{
                const headers = document.querySelectorAll('.persona-group-header');
                if (headers[idx]) {{
                    headers[idx].classList.add('collapsed');
                    if (headers[idx].nextElementSibling) {{
                        headers[idx].nextElementSibling.classList.add('collapsed');
                    }}
                }}
            }});

            // Restore expanded criteria rows
            (state.expandedCriteria || []).forEach(idx => {{
                const rows = document.querySelectorAll('.criteria-expand-row');
                if (rows[idx]) {{
                    rows[idx].classList.add('open');
                    document.querySelectorAll(`[id^="criteria-details-${{idx}}-"]`).forEach(el => {{
                        el.classList.add('open');
                    }});
                }}
            }});
        }}

        // Current filter state (restored from localStorage if available)
        const savedState = loadState();
        let currentPersonaFilter = savedState?.personaFilter || 'all';
        let groupByPersona = savedState?.groupByPersona || false;

        function initFilters() {{
            const personaFiltersContainer = document.getElementById('persona-filters');
            const personasSeen = metrics.personas_seen || [];
            const personaLetters = metrics.persona_letters || {{}};

            // Add filter buttons for each persona
            personasSeen.forEach(persona => {{
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.dataset.persona = persona;
                btn.textContent = personaLetters[persona] || persona;
                btn.title = persona;
                btn.onclick = () => setPersonaFilter(persona);
                personaFiltersContainer.appendChild(btn);
            }});

            // "All" button handler
            document.querySelector('.filter-btn[data-persona="all"]').onclick = () => setPersonaFilter('all');

            // Group by persona checkbox
            document.getElementById('group-by-persona').onchange = (e) => {{
                groupByPersona = e.target.checked;
                renderConversations();
                restoreExpandedState();
                saveState();
            }};

            // Restore saved filter state
            if (currentPersonaFilter !== 'all') {{
                setPersonaFilter(currentPersonaFilter);
            }}
            if (groupByPersona) {{
                document.getElementById('group-by-persona').checked = true;
            }}
        }}

        function setPersonaFilter(persona) {{
            currentPersonaFilter = persona;
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.persona === persona);
            }});
            renderConversations();
            restoreExpandedState();
            saveState();
        }}

        function renderConversations() {{
            const container = document.getElementById('conversations-container');
            const conversations = manifest.conversations || [];
            const personasSeen = metrics.personas_seen || [];
            const personaLetters = metrics.persona_letters || {{}};

            // Filter conversations
            const filtered = conversations.filter(conv => {{
                if (currentPersonaFilter === 'all') return true;
                return extractPersona(conv) === currentPersonaFilter;
            }});

            if (groupByPersona) {{
                // Group by persona
                const groups = {{}};
                filtered.forEach(conv => {{
                    const persona = extractPersona(conv);
                    if (!groups[persona]) groups[persona] = [];
                    groups[persona].push(conv);
                }});

                let html = '';
                // Sort groups by persona order
                const sortedPersonas = [...personasSeen, ...Object.keys(groups).filter(p => !personasSeen.includes(p))];
                sortedPersonas.forEach(persona => {{
                    const convs = groups[persona];
                    if (!convs || convs.length === 0) return;

                    const letter = personaLetters[persona] || persona[0].toUpperCase();
                    const critPassed = convs.filter(c => c.critical_verdict === 'PASS').length;
                    const critTotal = convs.filter(c => c.critical_verdict === 'PASS' || c.critical_verdict === 'FAIL').length;

                    html += `
                        <div class="persona-group">
                            <div class="persona-group-header" onclick="togglePersonaGroup(this, event)">
                                <span class="toggle-icon">▼</span>
                                <h3 style="margin-left: 0.5rem;"><span class="persona-tag">${{letter}}</span> ${{persona}}</h3>
                                <span class="persona-stats">${{convs.length}} conversation${{convs.length !== 1 ? 's' : ''}} · Critical: ${{critPassed}}/${{critTotal}}</span>
                            </div>
                            <div class="persona-group-content">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Critical</th>
                                            <th>Quality Score</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;
                    convs.forEach((conv, idx) => {{
                        html += renderConversationRow(conv, `${{persona}}-${{idx}}`, false);
                    }});
                    html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }});
                container.innerHTML = html;
            }} else {{
                // Flat table view
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Persona</th>
                                <th>Critical</th>
                                <th>Quality Score</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filtered.forEach((conv, idx) => {{
                    html += renderConversationRow(conv, idx, true);
                }});
                html += '</tbody></table>';
                container.innerHTML = html;
            }}
        }}

        function renderConversationRow(conv, index, showPersona) {{
            const criticalVerdict = conv.critical_verdict || 'PENDING';
            const criticalJson = conv.critical_json || {{}};
            const qualityResults = conv.quality_results || {{}};

            // Calculate quality score
            let qualityPassed = 0;
            let qualityTotal = 0;
            let qualityNA = 0;
            let hasParseIssue = false;
            const EXPECTED_TOTAL = 20;

            for (const [judge, result] of Object.entries(qualityResults)) {{
                qualityPassed += result.passed || 0;
                qualityTotal += result.total || 0;
                qualityNA += result.na_count || (result.json && result.json.overall && result.json.overall.na_count) || 0;
            }}

            const actualTotal = qualityTotal + qualityNA;
            if (qualityTotal > 0 && actualTotal < EXPECTED_TOTAL) {{
                hasParseIssue = true;
            }}

            let qualityScore = '-';
            if (qualityTotal > 0) {{
                qualityScore = `${{qualityPassed}}/${{qualityTotal}}`;
                if (qualityNA > 0) {{
                    qualityScore += ` <span class="na-badge" title="${{qualityNA}} criteria N/A">(${{qualityNA}} N/A)</span>`;
                }}
                if (hasParseIssue) {{
                    qualityScore += ` <span class="warning-badge" title="Some criteria failed to parse">⚠️</span>`;
                }}
            }}

            const persona = extractPersona(conv);
            const personaCol = showPersona ? `<td><span class="persona-tag">${{persona}}</span></td>` : '';

            let html = `
                <tr class="expandable" onclick="toggleDetails('${{index}}', event)">
                    <td>${{conv.short_id}}</td>
                    ${{personaCol}}
                    <td><span class="verdict ${{criticalVerdict.toLowerCase()}}">${{criticalVerdict}}</span></td>
                    <td>${{qualityScore}}</td>
                    <td><span class="verdict ${{criticalVerdict === 'PENDING' ? 'pending' : 'pass'}}">
                        ${{criticalVerdict === 'PENDING' ? 'Pending' : 'Complete'}}
                    </span></td>
                </tr>
            `;

            // Details row
            const colspan = showPersona ? 5 : 4;
            let detailsHtml = `<tr class="details" id="details-${{index}}"><td colspan="${{colspan}}"><div class="details-content">`;

            // Quality summary grid
            if (Object.keys(qualityResults).length > 0) {{
                detailsHtml += '<div class="quality-grid" style="margin-bottom: 1rem;">';
                for (const [judge, result] of Object.entries(qualityResults)) {{
                    const passed = result.passed || 0;
                    const total = result.total || 0;
                    const pct = total > 0 ? Math.round(passed / total * 100) : 0;
                    detailsHtml += `<div class="quality-item"><span>${{judge.replace(/_/g, ' ')}}</span><span>${{passed}}/${{total}} (${{pct}}%)</span></div>`;
                }}
                detailsHtml += '</div>';
            }}

            // Critical criteria evidence
            if (criticalJson.criteria) {{
                detailsHtml += '<div class="evidence-section">';
                detailsHtml += '<h4>Critical Criteria Evidence</h4>';
                detailsHtml += renderCriteriaEvidence(criticalJson.criteria);
                detailsHtml += '</div>';
            }}

            // Quality judges evidence
            for (const [judgeName, result] of Object.entries(qualityResults)) {{
                if (result.json && result.json.criteria) {{
                    detailsHtml += '<div class="judge-section">';
                    detailsHtml += `<h5>${{judgeName.replace(/_/g, ' ')}}</h5>`;
                    detailsHtml += renderCriteriaEvidence(result.json.criteria);
                    detailsHtml += '</div>';
                }}
            }}

            if (!criticalJson.criteria && Object.keys(qualityResults).length === 0) {{
                detailsHtml += '<em>No evaluation data yet</em>';
            }}

            detailsHtml += '</div></td></tr>';
            html += detailsHtml;

            return html;
        }}

        function togglePersonaGroup(header, event) {{
            if (event) event.stopPropagation();
            header.classList.toggle('collapsed');
            header.nextElementSibling.classList.toggle('collapsed');
            saveState();
        }}

        function toggleDetails(index, event) {{
            if (event) event.stopPropagation();
            const details = document.getElementById(`details-${{index}}`);
            if (details) {{
                details.classList.toggle('open');
                saveState();
            }}
        }}

        function renderHumanSpotCheck() {{
            const humanMetrics = metrics.human;
            if (!humanMetrics || !humanMetrics.has_data) {{
                return; // Section stays hidden
            }}

            // Show the section
            document.getElementById('human-spot-check-section').style.display = 'block';

            // Update summary cards
            if (humanMetrics.overall_agreement_pct !== null) {{
                const pct = humanMetrics.overall_agreement_pct;
                const pctEl = document.getElementById('human-agreement-pct');
                pctEl.textContent = pct + '%';
                pctEl.style.color = getRateColor(pct);
            }}
            document.getElementById('human-agreement-detail').textContent =
                `${{humanMetrics.total_agree}}/${{humanMetrics.total_criteria_compared}} criteria`;

            document.getElementById('human-conv-count').textContent = humanMetrics.total_conversations_rated;
            document.getElementById('human-raters').textContent =
                humanMetrics.raters.length > 0 ? `Rater${{humanMetrics.raters.length > 1 ? 's' : ''}}: ${{humanMetrics.raters.join(', ')}}` : '-';

            // Render table
            const tbody = document.getElementById('human-spot-check-table');
            let html = '';

            humanMetrics.by_conversation.forEach((item, idx) => {{
                const agreement = item.agreement;
                const hasMatch = !agreement.no_llm_match;

                let agreementDisplay = '-';
                let agreementStyle = '';
                if (hasMatch && agreement.percentage !== null) {{
                    agreementDisplay = `${{agreement.percentage}}% (${{agreement.agree}}/${{agreement.total}})`;
                    agreementStyle = getRateStyle(agreement.percentage);
                }} else if (!hasMatch) {{
                    agreementDisplay = '<span class="na-badge" title="No matching LLM evaluation found">No LLM match</span>';
                }}

                let disagreementDisplay = '-';
                if (agreement.disagreements && agreement.disagreements.length > 0) {{
                    const codes = agreement.disagreements.map(d => d.code).join(', ');
                    disagreementDisplay = `<span style="color: #ef4444;">${{agreement.disagreements.length}}</span> (${{codes}})`;
                }} else if (hasMatch && agreement.total > 0) {{
                    disagreementDisplay = '<span style="color: #10b981;">None</span>';
                }}

                // Main row
                html += `
                    <tr class="expandable" onclick="toggleHumanDetails('human-${{idx}}', event)">
                        <td>${{item.timestamp}}</td>
                        <td><span class="persona-tag">${{item.persona}}</span></td>
                        <td>${{item.rater}}</td>
                        <td style="${{agreementStyle}}">${{agreementDisplay}}</td>
                        <td>${{disagreementDisplay}}</td>
                    </tr>
                `;

                // Details row (disagreements)
                if (agreement.disagreements && agreement.disagreements.length > 0) {{
                    html += `
                        <tr class="details" id="details-human-${{idx}}">
                            <td colspan="5">
                                <div class="details-content">
                                    <div class="failed-summary">
                                        <div class="failed-summary-title">Human vs LLM Disagreements</div>
                    `;
                    agreement.disagreements.forEach(d => {{
                        const tooltip = CRITERION_DESCRIPTIONS[d.code] || d.code;
                        html += `
                                        <div style="margin: 0.75rem 0; padding: 0.75rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 0.375rem;">
                                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                                <span class="criterion-code-tooltip" style="font-weight: 600;" data-tooltip="${{escapeHtml(tooltip)}}">${{d.code}}</span>
                                                <span>LLM: <span class="verdict ${{d.llm.toLowerCase()}}">${{d.llm}}</span></span>
                                                <span>Human: <span class="verdict ${{d.human.toLowerCase()}}">${{d.human}}</span></span>
                                            </div>
                                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.8125rem;">
                                                <div>
                                                    <div style="font-weight: 600; color: #6b7280; margin-bottom: 0.25rem;">LLM Rationale:</div>
                                                    <div style="color: #4b5563; font-style: italic;">${{escapeHtml(d.llm_evidence) || '-'}}</div>
                                                </div>
                                                <div>
                                                    <div style="font-weight: 600; color: #6b7280; margin-bottom: 0.25rem;">Human Notes:</div>
                                                    <div style="color: #4b5563; font-style: italic;">${{escapeHtml(d.human_evidence) || '-'}}</div>
                                                </div>
                                            </div>
                                        </div>
                        `;
                    }});
                    html += `
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                }}
            }});

            tbody.innerHTML = html;
        }}

        function toggleHumanDetails(id, event) {{
            if (event) event.stopPropagation();
            const details = document.getElementById(`details-${{id}}`);
            if (details) {{
                details.classList.toggle('open');
                saveState();
            }}
        }}

        // Deep-dive section for specific criteria failures
        let activeDeepDiveCriteria = new Set(DEEP_DIVE_CRITERIA);

        function extractCriterionFailures() {{
            // Extract all failures for deep-dive criteria from conversations
            const failures = [];
            const conversations = manifest.conversations || [];

            conversations.forEach(conv => {{
                const langsmithId = conv.langsmith_id;
                const shortId = conv.short_id;
                const persona = extractPersona(conv);

                // Check critical criteria
                const criticalJson = conv.critical_json || {{}};
                const criticalCriteria = criticalJson.criteria || {{}};
                for (const [code, data] of Object.entries(criticalCriteria)) {{
                    if (DEEP_DIVE_CRITERIA.includes(code) && data.verdict === 'FAIL') {{
                        failures.push({{
                            langsmithId,
                            shortId,
                            persona,
                            criterion: code,
                            evidence: data.evidence || ''
                        }});
                    }}
                }}

                // Check quality results
                const qualityResults = conv.quality_results || {{}};
                for (const [judgeName, result] of Object.entries(qualityResults)) {{
                    const criteria = result.json?.criteria || {{}};
                    for (const [code, data] of Object.entries(criteria)) {{
                        if (DEEP_DIVE_CRITERIA.includes(code) && data.verdict === 'FAIL') {{
                            failures.push({{
                                langsmithId,
                                shortId,
                                persona,
                                criterion: code,
                                evidence: data.evidence || ''
                            }});
                        }}
                    }}
                }}
            }});

            return failures;
        }}

        function countFailuresByCriterion(failures) {{
            const counts = {{}};
            DEEP_DIVE_CRITERIA.forEach(c => counts[c] = 0);
            failures.forEach(f => {{
                if (counts[f.criterion] !== undefined) {{
                    counts[f.criterion]++;
                }}
            }});
            return counts;
        }}

        function renderCriterionDeepDive() {{
            const failures = extractCriterionFailures();
            const counts = countFailuresByCriterion(failures);

            // Update count badges
            document.querySelectorAll('.deep-dive-btn').forEach(btn => {{
                const criterion = btn.dataset.criterion;
                const badge = btn.querySelector('.count-badge');
                if (badge && counts[criterion] !== undefined) {{
                    badge.textContent = counts[criterion];
                }}
            }});

            // Setup button click handlers
            document.querySelectorAll('.deep-dive-btn').forEach(btn => {{
                btn.onclick = () => {{
                    btn.classList.toggle('active');
                    const criterion = btn.dataset.criterion;
                    if (btn.classList.contains('active')) {{
                        activeDeepDiveCriteria.add(criterion);
                    }} else {{
                        activeDeepDiveCriteria.delete(criterion);
                    }}
                    updateDeepDiveTable(failures);
                }};
            }});

            // Initial render
            updateDeepDiveTable(failures);
        }}

        function updateDeepDiveTable(failures) {{
            const tbody = document.getElementById('deep-dive-table');

            // Filter to active criteria
            const filtered = failures.filter(f => activeDeepDiveCriteria.has(f.criterion));

            if (filtered.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #6b7280; padding: 2rem;">No failures for selected criteria</td></tr>';
                return;
            }}

            let html = '';
            filtered.forEach(f => {{
                const tooltip = CRITERION_DESCRIPTIONS[f.criterion] || f.criterion;
                const transcriptPath = transcriptIndex[f.langsmithId];
                let transcriptLink = '<span class="no-link">-</span>';
                if (transcriptPath) {{
                    const githubUrl = `${{GITHUB_BASE_URL}}/${{transcriptPath}}`;
                    transcriptLink = `<a href="${{githubUrl}}" target="_blank" class="transcript-link">View</a>`;
                }}

                html += `
                    <tr>
                        <td>${{f.shortId}}</td>
                        <td><span class="persona-tag">${{f.persona}}</span></td>
                        <td><span class="criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{f.criterion}}</span></td>
                        <td class="evidence-cell" title="${{escapeHtml(f.evidence)}}">${{escapeHtml(f.evidence)}}</td>
                        <td>${{transcriptLink}}</td>
                    </tr>
                `;
            }});

            tbody.innerHTML = html;
        }}

        renderCriteriaTable();
        renderHumanSpotCheck();
        renderCriterionDeepDive();
        initFilters();
        renderConversations();
        restoreExpandedState();
    </script>
</body>
</html>'''

    return html


def generate_dashboard(run_dir: Path, output_path: Path | None = None, aggregate: bool = True) -> Path:
    """
    Generate dashboard HTML for a run directory.

    Args:
        run_dir: Path to the evaluation run directory (used for output location)
        output_path: Optional output path (defaults to run_dir/dashboard.html)
        aggregate: If True, aggregate results from ALL runs (default: True)

    Returns:
        Path to the generated dashboard file
    """
    if aggregate:
        # Aggregate all runs for a complete view
        manifest = aggregate_all_runs()
    else:
        # Single run mode
        manifest = load_manifest(run_dir)

    # Load human spot-check ratings
    human_ratings = load_human_ratings()
    human_metrics = calculate_human_metrics(manifest, human_ratings)

    # Build transcript index for linking to GitHub
    transcript_index = build_transcript_index(manifest)

    metrics = calculate_dashboard_metrics(manifest)
    metrics["human"] = human_metrics
    html = generate_html(manifest, metrics, transcript_index)

    if output_path is None:
        output_path = run_dir / "dashboard.html"

    output_path.write_text(html)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate evaluation dashboard from manifest.json"
    )
    parser.add_argument(
        "--run",
        type=str,
        help="Path to evaluation run directory (default: most recent)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for dashboard.html (default: <run_dir>/dashboard.html)"
    )
    parser.add_argument(
        "--no-aggregate",
        action="store_true",
        help="Only show results from the specified run (default: aggregate all runs)"
    )

    args = parser.parse_args()

    # Determine run directory
    if args.run:
        run_dir = Path(args.run)
    else:
        run_dir = find_latest_run()
        if run_dir is None:
            print("ERROR: No evaluation runs found. Run an evaluation first.")
            return

    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        return

    output_path = Path(args.output) if args.output else None
    aggregate = not args.no_aggregate

    try:
        dashboard_path = generate_dashboard(run_dir, output_path, aggregate=aggregate)
        if aggregate:
            print(f"Dashboard generated (aggregated from all runs): {dashboard_path}")
        else:
            print(f"Dashboard generated (single run): {dashboard_path}")
        print(f"Open in browser: file://{dashboard_path.absolute()}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
