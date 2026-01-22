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
- Auto-refresh support when hosted

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


def find_latest_run() -> Path | None:
    """Find the most recent evaluation run directory."""
    runs_dir = EVAL_RESULTS_DIR / "runs"
    if not runs_dir.exists():
        return None

    run_dirs = sorted(runs_dir.iterdir(), reverse=True)
    return run_dirs[0] if run_dirs else None


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

    # Deduplicate by langsmith_id (prefer entries with valid persona)
    seen = {}
    for conv in all_conversations:
        langsmith_id = conv.get("langsmith_id")
        if langsmith_id:
            existing = seen.get(langsmith_id)
            new_persona = conv.get("persona")
            # Prefer entry with valid persona over Unknown/None
            if not existing:
                seen[langsmith_id] = conv
            elif existing.get("persona") in [None, "Unknown", "unknown"] and new_persona not in [None, "Unknown", "unknown"]:
                seen[langsmith_id] = conv
            # Otherwise keep existing (don't overwrite good data with bad)
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


def generate_html(manifest: dict, metrics: dict) -> str:
    """Generate self-contained HTML dashboard."""
    run_id = manifest.get("run_id", "Unknown")
    status = manifest.get("status", "unknown")
    timestamp = manifest.get("timestamp", datetime.now().isoformat())
    conversations = manifest.get("conversations", [])

    # Status badge colors
    status_colors = {
        "in_progress": "#f59e0b",  # amber
        "complete": "#10b981",     # green
        "unknown": "#6b7280",      # gray
    }
    status_color = status_colors.get(status, status_colors["unknown"])

    # Serialize manifest to embed as JSON
    manifest_json = json.dumps(manifest, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
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
        /* Rate color classes */
        .rate-high {{
            color: #059669;
            font-weight: 600;
        }}
        .rate-medium {{
            color: #d97706;
            font-weight: 600;
        }}
        .rate-low {{
            color: #dc2626;
            font-weight: 600;
        }}
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
            Auto-refreshes every 30 seconds when hosted. Last generated: {datetime.now().isoformat()}
        </footer>
    </div>

    <script>
        const manifest = {manifest_json};
        const metrics = {json.dumps(metrics)};

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

            // Render header
            let headerHtml = '<tr><th>Criterion</th><th>Passed</th><th>Pass Rate</th>';
            personasSeen.forEach(p => {{
                headerHtml += `<th style="width: 40px; text-align: center" title="${{p}}">${{personaLetters[p] || p[0].toUpperCase()}}</th>`;
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
                row.onclick = () => toggleCriteriaDetails(index);
                const rateClass = percentage >= 80 ? 'rate-high' : percentage >= 50 ? 'rate-medium' : 'rate-low';
                let rowHtml = `
                    <td>${{judgeId.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}}</td>
                    <td>${{data.passed}}/${{data.total}}</td>
                    <td class="${{rateClass}}">${{percentage}}%</td>
                `;
                // Add persona columns
                personasSeen.forEach(p => {{
                    const pData = byPersona[p] || {{passed: 0, total: 0}};
                    const pPct = pData.total > 0 ? Math.round(pData.passed / pData.total * 100) : '-';
                    const pClass = pPct === '-' ? '' : (pPct >= 80 ? 'rate-high' : pPct >= 50 ? 'rate-medium' : 'rate-low');
                    rowHtml += `<td style="text-align: center" class="${{pClass}}">${{pPct}}${{pPct !== '-' ? '%' : ''}}</td>`;
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
                    const rateClass = pct >= 80 ? 'rate-high' : pct >= 50 ? 'rate-medium' : 'rate-low';
                    const cByPersona = stats.by_persona || {{}};
                    const tooltip = CRITERION_DESCRIPTIONS[code] || code;

                    const subRow = document.createElement('tr');
                    subRow.className = 'criteria-details-row';
                    subRow.id = `criteria-details-${{index}}-${{code}}`;

                    let subRowHtml = `
                        <td style="padding-left: 2rem;"><span class="criterion-code-tooltip" data-tooltip="${{escapeHtml(tooltip)}}">${{code}}</span></td>
                        <td>${{stats.passed}}/${{total}}</td>
                        <td class="${{rateClass}}">${{pct}}%</td>
                    `;
                    // Add persona columns
                    personasSeen.forEach(p => {{
                        const ps = cByPersona[p] || {{passed: 0, failed: 0}};
                        const pTotal = ps.passed + ps.failed;
                        const pPct = pTotal > 0 ? Math.round(ps.passed / pTotal * 100) : '-';
                        const pClass = pPct === '-' ? '' : (pPct >= 80 ? 'rate-high' : pPct >= 50 ? 'rate-medium' : 'rate-low');
                        subRowHtml += `<td style="text-align: center" class="${{pClass}}">${{pPct}}${{pPct !== '-' ? '%' : ''}}</td>`;
                    }});
                    subRow.innerHTML = subRowHtml;
                    tbody.appendChild(subRow);
                }});
            }});
        }}

        function toggleCriteriaDetails(index) {{
            const row = document.querySelectorAll('.criteria-expand-row')[index];
            row.classList.toggle('open');
            // Toggle all sub-rows for this index
            document.querySelectorAll(`[id^="criteria-details-${{index}}-"]`).forEach(el => {{
                el.classList.toggle('open');
            }});
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

        // Current filter state
        let currentPersonaFilter = 'all';
        let groupByPersona = false;

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
            }};
        }}

        function setPersonaFilter(persona) {{
            currentPersonaFilter = persona;
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.persona === persona);
            }});
            renderConversations();
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
                            <div class="persona-group-header" onclick="togglePersonaGroup(this)">
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
                <tr class="expandable" onclick="toggleDetails('${{index}}')">
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

        function togglePersonaGroup(header) {{
            header.classList.toggle('collapsed');
            header.nextElementSibling.classList.toggle('collapsed');
        }}

        function toggleDetails(index) {{
            const details = document.getElementById(`details-${{index}}`);
            if (details) details.classList.toggle('open');
        }}

        renderCriteriaTable();
        initFilters();
        renderConversations();
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

    metrics = calculate_dashboard_metrics(manifest)
    html = generate_html(manifest, metrics)

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
