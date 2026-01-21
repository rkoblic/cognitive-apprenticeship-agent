"""
Live Dashboard Generator for MentorAI Evaluations
==================================================

Generates a self-contained HTML dashboard with all evaluation data embedded.
The dashboard can be opened locally or deployed to GitHub Pages for team sharing.

Features:
- All data embedded as JSON (no external fetch needed)
- Summary cards: Critical pass rate, Quality average, Progress
- Per-criteria table with pass rates
- Per-conversation table with expandable details
- Auto-refresh support when hosted

Usage:
    python generate_dashboard.py --run eval_results/runs/YYYYMMDD_HHMMSS
    python generate_dashboard.py  # Uses most recent run
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
        }

    # Critical stats
    critical_passed = sum(1 for c in conversations if c.get("critical_verdict") == "PASS")
    critical_failed = sum(1 for c in conversations if c.get("critical_verdict") == "FAIL")
    completed = critical_passed + critical_failed

    # Quality stats - aggregate across all judges
    per_criteria = {}
    total_quality_passed = 0
    total_quality_criteria = 0

    for conv in conversations:
        quality_results = conv.get("quality_results", {})
        for judge_id, result in quality_results.items():
            if judge_id not in per_criteria:
                per_criteria[judge_id] = {"passed": 0, "total": 0}

            passed = result.get("passed", 0)
            judge_total = result.get("total", 0)

            per_criteria[judge_id]["passed"] += passed
            per_criteria[judge_id]["total"] += judge_total
            total_quality_passed += passed
            total_quality_criteria += judge_total

    # Calculate percentages
    for judge_id in per_criteria:
        p = per_criteria[judge_id]
        p["percentage"] = round(p["passed"] / p["total"] * 100, 1) if p["total"] > 0 else 0

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
        .progress-bar {{
            width: 100%;
            height: 0.5rem;
            background: #e5e7eb;
            border-radius: 9999px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.3s ease;
        }}
        .progress-fill.high {{
            background: #10b981;
        }}
        .progress-fill.medium {{
            background: #f59e0b;
        }}
        .progress-fill.low {{
            background: #ef4444;
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
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.5rem;
        }}
        .quality-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.25rem 0;
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
                <thead>
                    <tr>
                        <th>Criterion</th>
                        <th>Passed</th>
                        <th>Pass Rate</th>
                        <th style="width: 40%">Progress</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'''
                    <tr>
                        <td>{judge_id.replace("_", " ").title()}</td>
                        <td>{data["passed"]}/{data["total"]}</td>
                        <td>{data["percentage"]}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill {"high" if data["percentage"] >= 80 else "medium" if data["percentage"] >= 50 else "low"}" style="width: {data["percentage"]}%"></div>
                            </div>
                        </td>
                    </tr>
                    ''' for judge_id, data in metrics["per_criteria"].items())}
                </tbody>
            </table>
        </div>

        <div class="section">
            <div class="section-header">Per-Conversation Results</div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Critical</th>
                        <th>Quality Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="conversations">
                </tbody>
            </table>
        </div>

        <footer>
            Auto-refreshes every 30 seconds when hosted. Last generated: {datetime.now().isoformat()}
        </footer>
    </div>

    <script>
        const manifest = {manifest_json};

        function renderConversations() {{
            const tbody = document.getElementById('conversations');
            const conversations = manifest.conversations || [];

            conversations.forEach((conv, index) => {{
                const criticalVerdict = conv.critical_verdict || 'PENDING';
                const qualityResults = conv.quality_results || {{}};

                // Calculate quality score
                let qualityPassed = 0;
                let qualityTotal = 0;
                for (const [judge, result] of Object.entries(qualityResults)) {{
                    qualityPassed += result.passed || 0;
                    qualityTotal += result.total || 0;
                }}
                const qualityScore = qualityTotal > 0 ? `${{qualityPassed}}/${{qualityTotal}}` : '-';

                // Main row
                const row = document.createElement('tr');
                row.className = 'expandable';
                row.onclick = () => toggleDetails(index);
                row.innerHTML = `
                    <td>${{conv.short_id}}</td>
                    <td><span class="verdict ${{criticalVerdict.toLowerCase()}}">${{criticalVerdict}}</span></td>
                    <td>${{qualityScore}}</td>
                    <td><span class="verdict ${{criticalVerdict === 'PENDING' ? 'pending' : 'pass'}}">
                        ${{criticalVerdict === 'PENDING' ? 'Pending' : 'Complete'}}
                    </span></td>
                `;
                tbody.appendChild(row);

                // Details row
                const detailsRow = document.createElement('tr');
                detailsRow.className = 'details';
                detailsRow.id = `details-${{index}}`;

                let detailsHtml = '<td colspan="4"><div class="details-content">';
                if (Object.keys(qualityResults).length > 0) {{
                    detailsHtml += '<div class="quality-grid">';
                    for (const [judge, result] of Object.entries(qualityResults)) {{
                        const passed = result.passed || 0;
                        const total = result.total || 0;
                        const pct = total > 0 ? Math.round(passed / total * 100) : 0;
                        detailsHtml += `<div class="quality-item"><span>${{judge.replace(/_/g, ' ')}}</span><span>${{passed}}/${{total}} (${{pct}}%)</span></div>`;
                    }}
                    detailsHtml += '</div>';
                }} else {{
                    detailsHtml += '<em>No quality evaluation data yet</em>';
                }}
                detailsHtml += '</div></td>';
                detailsRow.innerHTML = detailsHtml;
                tbody.appendChild(detailsRow);
            }});
        }}

        function toggleDetails(index) {{
            const details = document.getElementById(`details-${{index}}`);
            details.classList.toggle('open');
        }}

        renderConversations();
    </script>
</body>
</html>'''

    return html


def generate_dashboard(run_dir: Path, output_path: Path | None = None) -> Path:
    """
    Generate dashboard HTML for a run directory.

    Args:
        run_dir: Path to the evaluation run directory
        output_path: Optional output path (defaults to run_dir/dashboard.html)

    Returns:
        Path to the generated dashboard file
    """
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

    try:
        dashboard_path = generate_dashboard(run_dir, output_path)
        print(f"Dashboard generated: {dashboard_path}")
        print(f"Open in browser: file://{dashboard_path.absolute()}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
