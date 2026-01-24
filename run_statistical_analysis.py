"""
Statistical Significance Testing for MentorAI Evaluation
=========================================================

Analyzes evaluation results to determine whether observed differences
in pass/fail rates are statistically significant.

Tests performed:
1. Chi-square test for overall persona effect on each criterion
2. Fisher's exact test for pairwise persona comparisons
3. Benjamini-Hochberg FDR correction for multiple comparisons

Usage:
    python run_statistical_analysis.py
    python run_statistical_analysis.py --criteria B-03,B-04,F-01
    python run_statistical_analysis.py --output stats_report.md

Requirements:
    pip install scipy statsmodels
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    from scipy.stats import fisher_exact, chi2_contingency
    from statsmodels.stats.multitest import multipletests
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install scipy statsmodels")
    exit(1)

SCRIPT_DIR = Path(__file__).parent
EVAL_RESULTS_DIR = SCRIPT_DIR / "eval_results"

PERSONAS = ['amara_SBI', 'bailey_SBI', 'carlos_SBI',
            'daniel_SBI', 'elise_SBI', 'fatou_SBI']

DEFAULT_CRITERIA = ['B-03', 'B-04', 'E-02', 'F-01']

ALL_CRITERIA = [
    'A-01', 'A-02', 'A-03',  # Session setup
    'B-01', 'B-02', 'B-03', 'B-04', 'B-05',  # Modeling quality
    'C-01', 'C-02', 'C-03', 'C-04', 'C-05',  # Coaching quality
    'D-01', 'D-02', 'D-03',  # SBI content
    'E-01', 'E-02', 'E-03',  # Adaptive pacing
    'F-01', 'F-02', 'F-03',  # Conversational quality
]


def load_evaluation_data(min_date: str = '20260121') -> list[dict]:
    """
    Load and deduplicate conversations from all manifest files.

    Args:
        min_date: Only include runs from this date onwards (YYYYMMDD)

    Returns:
        List of conversation dicts, deduplicated by langsmith_id
    """
    runs_dir = EVAL_RESULTS_DIR / "runs"
    if not runs_dir.exists():
        print(f"Error: {runs_dir} not found")
        return []

    seen = {}

    for manifest_path in sorted(runs_dir.glob('*/manifest.json')):
        run_id = manifest_path.parent.name
        if run_id[:8] < min_date:
            continue

        try:
            data = json.loads(manifest_path.read_text())
            for conv in data.get('conversations', []):
                lid = conv.get('langsmith_id')
                if lid and lid not in seen:
                    seen[lid] = conv
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {manifest_path}: {e}")

    return list(seen.values())


def extract_criterion_results(conversations: list[dict], criterion: str) -> dict:
    """
    Extract pass/fail counts by persona for a specific criterion.

    Args:
        conversations: List of conversation dicts
        criterion: Criterion code (e.g., 'B-03')

    Returns:
        Dict mapping persona to {'pass': n, 'fail': n, 'na': n}
    """
    results = defaultdict(lambda: {'pass': 0, 'fail': 0, 'na': 0})

    for conv in conversations:
        persona = conv.get('persona', 'Unknown')

        # Check quality_results
        for judge, result in conv.get('quality_results', {}).items():
            criteria = result.get('json', {}).get('criteria', {})
            if criterion in criteria:
                verdict = criteria[criterion].get('verdict')
                if verdict == 'PASS':
                    results[persona]['pass'] += 1
                elif verdict == 'FAIL':
                    results[persona]['fail'] += 1
                elif verdict == 'N/A':
                    results[persona]['na'] += 1

        # Check critical_json
        critical_json = conv.get('critical_json')
        if critical_json:
            criteria = critical_json.get('criteria', {})
            if criterion in criteria:
                verdict = criteria[criterion].get('verdict')
                if verdict == 'PASS':
                    results[persona]['pass'] += 1
                elif verdict == 'FAIL':
                    results[persona]['fail'] += 1
                elif verdict == 'N/A':
                    results[persona]['na'] += 1

    return dict(results)


def chi_square_test(results: dict) -> tuple[float | None, float | None, int]:
    """
    Chi-square test for independence: does persona affect pass/fail?

    Args:
        results: Dict mapping persona to {'pass': n, 'fail': n}

    Returns:
        Tuple of (chi2 statistic, p-value, degrees of freedom)
        Returns (None, None, 0) if test cannot be performed
    """
    table = []
    valid_personas = []

    for p in PERSONAS:
        if p in results:
            passes = results[p]['pass']
            fails = results[p]['fail']
            # Only include if there's at least one observation
            if passes + fails > 0:
                table.append([passes, fails])
                valid_personas.append(p)

    if len(table) < 2:
        return None, None, 0

    # Check for zero marginals (chi-square requires expected counts > 0)
    col_sums = [sum(row[i] for row in table) for i in range(2)]
    if 0 in col_sums:
        return None, None, 0

    try:
        chi2, p_value, dof, expected = chi2_contingency(table)
        return chi2, p_value, dof
    except ValueError:
        return None, None, 0


def fisher_exact_test(results: dict, persona1: str, persona2: str) -> tuple[float | None, float | None]:
    """
    Fisher's exact test for comparing two personas.

    Args:
        results: Dict mapping persona to {'pass': n, 'fail': n}
        persona1: First persona to compare
        persona2: Second persona to compare

    Returns:
        Tuple of (odds ratio, p-value)
        Returns (None, None) if test cannot be performed
    """
    if persona1 not in results or persona2 not in results:
        return None, None

    table = [
        [results[persona1]['pass'], results[persona1]['fail']],
        [results[persona2]['pass'], results[persona2]['fail']]
    ]

    # Check for valid table (need at least one observation per row)
    if any(sum(row) == 0 for row in table):
        return None, None

    try:
        odds_ratio, p_value = fisher_exact(table)
        return odds_ratio, p_value
    except ValueError:
        return None, None


def find_extreme_personas(results: dict) -> tuple[str | None, str | None]:
    """
    Find personas with highest and lowest fail rates.

    Returns:
        Tuple of (highest_fail_persona, lowest_fail_persona)
    """
    fail_rates = {}

    for persona, counts in results.items():
        total = counts['pass'] + counts['fail']
        if total > 0:
            fail_rates[persona] = counts['fail'] / total

    if len(fail_rates) < 2:
        return None, None

    sorted_personas = sorted(fail_rates.items(), key=lambda x: x[1])
    lowest = sorted_personas[0][0]
    highest = sorted_personas[-1][0]

    return highest, lowest


def run_analysis(criteria: list[str], alpha: float = 0.05) -> dict:
    """
    Run full statistical analysis on specified criteria.

    Args:
        criteria: List of criterion codes to analyze
        alpha: Significance level (default 0.05)

    Returns:
        Dict with analysis results
    """
    conversations = load_evaluation_data()

    if not conversations:
        return {'error': 'No conversations loaded'}

    print(f"Loaded {len(conversations)} conversations")
    print(f"Analyzing criteria: {', '.join(criteria)}")
    print("=" * 60)

    all_tests = []
    results_by_criterion = {}

    for criterion in criteria:
        results = extract_criterion_results(conversations, criterion)
        results_by_criterion[criterion] = results

        # Summary stats
        total_pass = sum(r['pass'] for r in results.values())
        total_fail = sum(r['fail'] for r in results.values())
        total = total_pass + total_fail

        if total == 0:
            print(f"\n{criterion}: No data")
            continue

        pass_rate = total_pass / total * 100
        print(f"\n{criterion}: {total_pass}/{total} passed ({pass_rate:.1f}%)")

        # Per-persona breakdown
        print("  By persona:")
        for p in PERSONAS:
            if p in results:
                ps = results[p]['pass']
                fl = results[p]['fail']
                t = ps + fl
                if t > 0:
                    fr = fl / t * 100
                    print(f"    {p}: {ps}/{t} pass ({fr:.1f}% fail)")

        # Chi-square test
        chi2, p_chi, dof = chi_square_test(results)
        if chi2 is not None:
            sig = "**" if p_chi < alpha else ""
            print(f"  Chi-square test: χ²={chi2:.2f}, df={dof}, p={p_chi:.4f} {sig}")
            all_tests.append({
                'criterion': criterion,
                'test': 'chi_square',
                'comparison': 'all_personas',
                'statistic': chi2,
                'p_value': p_chi
            })

        # Pairwise comparison of extreme personas
        highest, lowest = find_extreme_personas(results)
        if highest and lowest and highest != lowest:
            odds, p_fisher = fisher_exact_test(results, highest, lowest)
            if odds is not None:
                sig = "**" if p_fisher < alpha else ""
                print(f"  Fisher's exact ({highest} vs {lowest}): OR={odds:.2f}, p={p_fisher:.4f} {sig}")
                all_tests.append({
                    'criterion': criterion,
                    'test': 'fisher_exact',
                    'comparison': f'{highest}_vs_{lowest}',
                    'statistic': odds,
                    'p_value': p_fisher
                })

    # Multiple comparison correction
    if all_tests:
        print("\n" + "=" * 60)
        print("Multiple Comparison Correction (Benjamini-Hochberg FDR)")
        print("=" * 60)

        p_values = [t['p_value'] for t in all_tests]
        rejected, corrected_p, _, _ = multipletests(p_values, method='fdr_bh', alpha=alpha)

        for test, orig_p, corr_p, sig in zip(all_tests, p_values, corrected_p, rejected):
            test['corrected_p'] = corr_p
            test['significant'] = sig

            status = "SIGNIFICANT" if sig else "not significant"
            label = f"{test['criterion']} ({test['test']}, {test['comparison']})"
            print(f"  {label}")
            print(f"    p={orig_p:.4f} → corrected p={corr_p:.4f} ({status})")

    return {
        'n_conversations': len(conversations),
        'criteria_analyzed': criteria,
        'alpha': alpha,
        'tests': all_tests,
        'results_by_criterion': results_by_criterion
    }


def generate_report(analysis: dict, output_path: Path | None = None) -> str:
    """
    Generate markdown report from analysis results.
    """
    lines = [
        "# Statistical Analysis Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Summary",
        "",
        f"- **Conversations analyzed**: {analysis.get('n_conversations', 0)}",
        f"- **Criteria tested**: {', '.join(analysis.get('criteria_analyzed', []))}",
        f"- **Significance level (α)**: {analysis.get('alpha', 0.05)}",
        f"- **Multiple comparison correction**: Benjamini-Hochberg FDR",
        "",
        "## Results by Criterion",
        ""
    ]

    for criterion, results in analysis.get('results_by_criterion', {}).items():
        total_pass = sum(r['pass'] for r in results.values())
        total_fail = sum(r['fail'] for r in results.values())
        total = total_pass + total_fail

        if total == 0:
            continue

        pass_rate = total_pass / total * 100
        lines.append(f"### {criterion}")
        lines.append("")
        lines.append(f"**Overall**: {total_pass}/{total} passed ({pass_rate:.1f}%)")
        lines.append("")
        lines.append("| Persona | Pass | Fail | Fail Rate |")
        lines.append("|---------|------|------|-----------|")

        for p in PERSONAS:
            if p in results:
                ps = results[p]['pass']
                fl = results[p]['fail']
                t = ps + fl
                if t > 0:
                    fr = fl / t * 100
                    lines.append(f"| {p} | {ps} | {fl} | {fr:.1f}% |")

        lines.append("")

    # Statistical tests
    lines.append("## Statistical Tests")
    lines.append("")
    lines.append("| Criterion | Test | Comparison | Statistic | p-value | Corrected p | Significant |")
    lines.append("|-----------|------|------------|-----------|---------|-------------|-------------|")

    for test in analysis.get('tests', []):
        sig = "Yes" if test.get('significant') else "No"
        lines.append(
            f"| {test['criterion']} | {test['test']} | {test['comparison']} | "
            f"{test['statistic']:.2f} | {test['p_value']:.4f} | "
            f"{test.get('corrected_p', 'N/A'):.4f} | {sig} |"
        )

    lines.append("")
    lines.append("## Interpretation Notes")
    lines.append("")
    lines.append("- **Chi-square test**: Tests whether pass/fail rates differ across all personas")
    lines.append("- **Fisher's exact test**: Compares the two personas with most extreme fail rates")
    lines.append("- **Corrected p-values**: Adjusted for multiple comparisons using FDR")
    lines.append("- **Significant**: Corrected p-value < α after FDR adjustment")
    lines.append("")
    lines.append("### Caveats")
    lines.append("")
    lines.append("1. Small sample sizes (~10 per persona) limit statistical power")
    lines.append("2. Multiple criteria per conversation violate independence assumptions")
    lines.append("3. Results should be treated as exploratory, not confirmatory")

    report = "\n".join(lines)

    if output_path:
        output_path.write_text(report)
        print(f"\nReport saved to: {output_path}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Run statistical significance tests on MentorAI evaluation data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_statistical_analysis.py
    python run_statistical_analysis.py --criteria B-03,B-04,F-01
    python run_statistical_analysis.py --all-criteria
    python run_statistical_analysis.py --output stats_report.md
        """
    )

    parser.add_argument(
        '--criteria',
        type=str,
        help=f"Comma-separated list of criteria to analyze (default: {','.join(DEFAULT_CRITERIA)})"
    )

    parser.add_argument(
        '--all-criteria',
        action='store_true',
        help="Analyze all criteria"
    )

    parser.add_argument(
        '--alpha',
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)"
    )

    parser.add_argument(
        '--output',
        type=str,
        help="Output path for markdown report"
    )

    args = parser.parse_args()

    # Determine criteria to analyze
    if args.all_criteria:
        criteria = ALL_CRITERIA
    elif args.criteria:
        criteria = [c.strip() for c in args.criteria.split(',')]
    else:
        criteria = DEFAULT_CRITERIA

    # Run analysis
    analysis = run_analysis(criteria, alpha=args.alpha)

    # Generate report if output specified
    if args.output:
        output_path = Path(args.output)
        generate_report(analysis, output_path)

    # Print significant findings summary
    significant = [t for t in analysis.get('tests', []) if t.get('significant')]
    if significant:
        print("\n" + "=" * 60)
        print("SIGNIFICANT FINDINGS (after correction)")
        print("=" * 60)
        for t in significant:
            print(f"  {t['criterion']}: {t['comparison']} (p={t['corrected_p']:.4f})")
    else:
        print("\nNo statistically significant findings after correction.")


if __name__ == '__main__':
    main()
