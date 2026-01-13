"""
Aggregate Report Generator for LLM-as-Judge Evaluations
========================================================

Generates HTML and CSV reports from evaluation results.

Usage:
    # Generate from most recent run
    python generate_report.py

    # Generate from specific run
    python generate_report.py --run eval_results/validation/20260113_v3

    # Generate from all runs in a directory
    python generate_report.py --all-runs eval_results/validation/
"""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
EVAL_RESULTS_DIR = SCRIPT_DIR / "eval_results"

# Criteria names for display
CRITERIA_NAMES = {
    "B-01": "Shows, Not Tells",
    "C-01": "Specific Feedback",
    "C-03": "Revision Requested",
    "D-01": "Catches Vague Situations",
    "D-02": "Catches Judgment Leakage",
    "D-03": "Catches Accusatory Impact",
    "E-04": "Protects Productive Struggle",
    "A-01": "Goal Clarity",
    "A-02": "Phase Signaling",
    "A-03": "Realistic Scenario",
    "B-02": "Thinking Out Loud",
    "B-03": "Visible Decision-Making",
    "B-04": "Self-Checking",
    "B-05": "Heuristic Offered",
    "C-02": "Actionable Direction",
    "C-04": "Revision Checked",
    "C-05": "Productive Struggle",
    "C-06": "Elicits Articulation",
    "C-07": "Prompts Reflection",
    "D-04": "Tests Distinctions",
    "D-05": "Scaffolds the Stuck",
    "D-06": "Reusable Scaffold",
    "E-01": "Checks Before Advancing",
    "E-02": "Fades Support",
    "E-03": "Adjusts to Struggle",
    "F-01": "Varied Turn Structure",
    "F-02": "Genuine Curiosity",
    "F-03": "Room to Breathe",
    "F-04": "Dwells on Difficulty",
    "F-05": "Has a Voice",
    "F-06": "Questions Over Corrections",
}

JUDGE_NAMES = {
    "critical_criteria": "Critical Criteria",
    "session_setup": "Session Setup",
    "modeling_quality": "Modeling Quality",
    "coaching_quality": "Coaching Quality",
    "sbi_content": "SBI Content Fidelity",
    "adaptive_pacing": "Adaptive Pacing",
    "conversational_quality": "Conversational Quality",
}


def load_manifest(run_dir: Path) -> dict:
    """Load manifest.json from a run directory."""
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json found in {run_dir}")
    return json.loads(manifest_path.read_text())


def find_latest_run(base_dir: Path) -> Path:
    """Find the most recently modified run directory."""
    runs = []
    for subdir in ["validation", "runs"]:
        search_dir = base_dir / subdir
        if search_dir.exists():
            for run_dir in search_dir.iterdir():
                if run_dir.is_dir() and (run_dir / "manifest.json").exists():
                    runs.append(run_dir)

    if not runs:
        raise FileNotFoundError(f"No evaluation runs found in {base_dir}")

    return max(runs, key=lambda p: p.stat().st_mtime)


def extract_criteria_results(manifest: dict) -> list[dict]:
    """Extract all criteria results into flat list for CSV."""
    results = []
    run_id = manifest["run_id"]
    timestamp = manifest["timestamp"]

    for conv in manifest["conversations"]:
        conv_id = conv["short_id"]

        # Critical criteria
        if "critical_json" in conv and conv["critical_json"]:
            criteria = conv["critical_json"].get("criteria", {})
            for crit_id, data in criteria.items():
                results.append({
                    "run_id": run_id,
                    "timestamp": timestamp,
                    "conversation_id": conv_id,
                    "judge": "critical_criteria",
                    "criterion": crit_id,
                    "criterion_name": CRITERIA_NAMES.get(crit_id, crit_id),
                    "verdict": data.get("verdict", ""),
                    "evidence": data.get("evidence", ""),
                })

        # Quality judges
        for judge_id, judge_data in conv.get("quality_results", {}).items():
            if "json" in judge_data and judge_data["json"]:
                criteria = judge_data["json"].get("criteria", {})
                for crit_id, data in criteria.items():
                    results.append({
                        "run_id": run_id,
                        "timestamp": timestamp,
                        "conversation_id": conv_id,
                        "judge": judge_id,
                        "criterion": crit_id,
                        "criterion_name": CRITERIA_NAMES.get(crit_id, crit_id),
                        "verdict": data.get("verdict", ""),
                        "evidence": data.get("evidence", ""),
                    })

    return results


def calculate_stats(manifest: dict) -> dict:
    """Calculate summary statistics from manifest."""
    stats = {
        "total_conversations": len(manifest["conversations"]),
        "critical_passed": 0,
        "critical_failed": 0,
        "judges": {},
    }

    for conv in manifest["conversations"]:
        if conv.get("critical_verdict") == "PASS":
            stats["critical_passed"] += 1
        elif conv.get("critical_verdict") == "FAIL":
            stats["critical_failed"] += 1

        for judge_id, judge_data in conv.get("quality_results", {}).items():
            if judge_id not in stats["judges"]:
                stats["judges"][judge_id] = {"passed": 0, "total": 0, "criteria": {}}

            if "json" in judge_data and judge_data["json"]:
                overall = judge_data["json"].get("overall", {})
                passed = overall.get("passed_count", 0)
                failed = overall.get("failed_count", 0)
                stats["judges"][judge_id]["passed"] += passed
                stats["judges"][judge_id]["total"] += passed + failed

                # Track per-criteria stats
                for crit_id, data in judge_data["json"].get("criteria", {}).items():
                    if crit_id not in stats["judges"][judge_id]["criteria"]:
                        stats["judges"][judge_id]["criteria"][crit_id] = {"pass": 0, "fail": 0, "na": 0}
                    verdict = data.get("verdict", "").upper()
                    if verdict == "PASS":
                        stats["judges"][judge_id]["criteria"][crit_id]["pass"] += 1
                    elif verdict == "FAIL":
                        stats["judges"][judge_id]["criteria"][crit_id]["fail"] += 1
                    elif verdict == "N/A":
                        stats["judges"][judge_id]["criteria"][crit_id]["na"] += 1

    return stats


def generate_csv(results: list[dict], output_path: Path):
    """Generate CSV file from results."""
    if not results:
        return

    fieldnames = ["run_id", "timestamp", "conversation_id", "judge", "criterion",
                  "criterion_name", "verdict", "evidence"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def generate_html(manifest: dict, stats: dict, results: list[dict], output_path: Path):
    """Generate HTML report."""

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluation Report - {manifest['run_id']}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1, h2, h3 {{ color: #333; }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2563eb;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .pass {{ color: #16a34a; font-weight: bold; }}
        .fail {{ color: #dc2626; font-weight: bold; }}
        .na {{ color: #6b7280; }}
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: #16a34a;
            height: 100%;
            transition: width 0.3s;
        }}
        .evidence {{
            font-size: 0.85em;
            color: #555;
            max-width: 500px;
        }}
        details {{
            margin: 10px 0;
        }}
        summary {{
            cursor: pointer;
            font-weight: 500;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        summary:hover {{
            background: #e5e7eb;
        }}
        .conversation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .badge-pass {{ background: #dcfce7; color: #16a34a; }}
        .badge-fail {{ background: #fee2e2; color: #dc2626; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Evaluation Report</h1>
    <p class="meta">
        Run ID: <strong>{manifest['run_id']}</strong> |
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
        Model: {manifest['config'].get('model', 'N/A')}
    </p>

    <div class="card">
        <h2>Summary</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{stats['total_conversations']}</div>
                <div class="stat-label">Conversations</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{stats['critical_passed']}</div>
                <div class="stat-label">Passed Critical</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{stats['critical_failed']}</div>
                <div class="stat-label">Failed Critical</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Judge Results</h2>
        <table>
            <tr>
                <th>Judge</th>
                <th>Pass Rate</th>
                <th>Progress</th>
            </tr>
"""

    # Add judge rows
    for judge_id, judge_stats in stats["judges"].items():
        total = judge_stats["total"]
        passed = judge_stats["passed"]
        rate = (passed / total * 100) if total > 0 else 0
        judge_name = JUDGE_NAMES.get(judge_id, judge_id)

        html += f"""            <tr>
                <td>{judge_name}</td>
                <td>{passed}/{total} ({rate:.0f}%)</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {rate}%"></div>
                    </div>
                </td>
            </tr>
"""

    html += """        </table>
    </div>

    <div class="card">
        <h2>Detailed Results by Conversation</h2>
"""

    # Add conversation details
    for conv in manifest["conversations"]:
        conv_id = conv["short_id"]
        critical_verdict = conv.get("critical_verdict", "N/A")
        badge_class = "badge-pass" if critical_verdict == "PASS" else "badge-fail"

        html += f"""
        <details>
            <summary>
                <span class="conversation-header">
                    <span>Conversation {conv_id}</span>
                    <span class="badge {badge_class}">{critical_verdict}</span>
                </span>
            </summary>
            <div style="padding: 15px;">
"""

        # Critical criteria table
        if "critical_json" in conv and conv["critical_json"]:
            html += """                <h4>Critical Criteria</h4>
                <table>
                    <tr><th>Criterion</th><th>Verdict</th><th>Evidence</th></tr>
"""
            for crit_id, data in conv["critical_json"].get("criteria", {}).items():
                verdict = data.get("verdict", "")
                evidence = data.get("evidence", "")[:200] + "..." if len(data.get("evidence", "")) > 200 else data.get("evidence", "")
                verdict_class = verdict.lower().replace("/", "")
                crit_name = CRITERIA_NAMES.get(crit_id, crit_id)
                html += f"""                    <tr>
                        <td>{crit_id}: {crit_name}</td>
                        <td class="{verdict_class}">{verdict}</td>
                        <td class="evidence">{evidence}</td>
                    </tr>
"""
            html += """                </table>
"""

        # Quality judges
        for judge_id, judge_data in conv.get("quality_results", {}).items():
            if "json" in judge_data and judge_data["json"]:
                judge_name = JUDGE_NAMES.get(judge_id, judge_id)
                overall = judge_data["json"].get("overall", {})
                passed = overall.get("passed_count", 0)
                failed = overall.get("failed_count", 0)

                html += f"""                <h4>{judge_name} ({passed}/{passed + failed})</h4>
                <table>
                    <tr><th>Criterion</th><th>Verdict</th><th>Evidence</th></tr>
"""
                for crit_id, data in judge_data["json"].get("criteria", {}).items():
                    verdict = data.get("verdict", "")
                    evidence = data.get("evidence", "")[:200] + "..." if len(data.get("evidence", "")) > 200 else data.get("evidence", "")
                    verdict_class = verdict.lower().replace("/", "")
                    crit_name = CRITERIA_NAMES.get(crit_id, crit_id)
                    html += f"""                    <tr>
                        <td>{crit_id}: {crit_name}</td>
                        <td class="{verdict_class}">{verdict}</td>
                        <td class="evidence">{evidence}</td>
                    </tr>
"""
                html += """                </table>
"""

        html += """            </div>
        </details>
"""

    html += """    </div>
</body>
</html>
"""

    output_path.write_text(html)


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML and CSV reports from evaluation results"
    )

    parser.add_argument(
        "--run",
        type=Path,
        help="Path to specific run directory (default: most recent)"
    )

    parser.add_argument(
        "--all-runs",
        type=Path,
        help="Generate combined report from all runs in directory"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: same as input run)"
    )

    args = parser.parse_args()

    # Determine run directory
    if args.run:
        run_dir = args.run
    elif args.all_runs:
        # TODO: Implement multi-run aggregation
        print("Multi-run aggregation not yet implemented. Using most recent run.")
        run_dir = find_latest_run(EVAL_RESULTS_DIR)
    else:
        run_dir = find_latest_run(EVAL_RESULTS_DIR)

    print(f"Loading results from: {run_dir}")

    # Load and process data
    manifest = load_manifest(run_dir)
    results = extract_criteria_results(manifest)
    stats = calculate_stats(manifest)

    # Determine output location
    output_dir = args.output or run_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    csv_path = output_dir / "results.csv"
    html_path = output_dir / "report.html"

    generate_csv(results, csv_path)
    print(f"CSV saved to: {csv_path}")

    generate_html(manifest, stats, results, html_path)
    print(f"HTML saved to: {html_path}")

    print(f"\nReport generated with {len(results)} criteria results from {stats['total_conversations']} conversations")


if __name__ == "__main__":
    main()
