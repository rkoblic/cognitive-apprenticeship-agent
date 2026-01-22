"""
Batch Evaluation Orchestrator
=============================

Single command that handles the full evaluation workflow:
1. Generates N conversations per persona (saves to markdown)
2. Creates a NEW LangSmith dataset for this batch (no re-evaluation of old data)
3. Runs judge evaluation with dashboard updates after each conversation
4. Deploys dashboard to GitHub Pages (optional)

Each batch creates a separate dataset (e.g., batch-20260121_143000). The dashboard
aggregates results from ALL local eval_results/runs/ directories.

Usage:
    # Run 10 conversations for 2 personas (20 turns each), deploy dashboard
    python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 10 --deploy

    # Local only (no deployment)
    python run_batch_eval.py --personas amara_SBI --count 5

    # Single persona with custom turns
    python run_batch_eval.py --personas amara_SBI --count 3 --turns 15

    # Regenerate dashboard from existing local results (no LangSmith calls)
    python run_batch_eval.py --eval-only --deploy
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
EVAL_RESULTS_DIR = SCRIPT_DIR / "eval_results"


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"$ {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    return result.returncode == 0


def generate_conversations(
    personas: list[str],
    count: int,
    turns: int,
    output_dir: Path
) -> bool:
    """
    Generate conversations for each persona.

    Args:
        personas: List of persona names
        count: Number of conversations per persona
        turns: Number of turns per conversation
        output_dir: Directory to save conversation markdown files

    Returns:
        True if all conversations generated successfully
    """
    total = len(personas) * count
    current = 0

    for persona in personas:
        for i in range(count):
            current += 1
            print(f"\n[{current}/{total}] Generating: {persona} (conversation {i+1}/{count})")

            cmd = [
                sys.executable, "run_eval.py",
                "--persona", persona,
                "--turns", str(turns),
                "--save-conversations",
                "--output-dir", str(output_dir)
            ]

            result = subprocess.run(cmd, cwd=SCRIPT_DIR)
            if result.returncode != 0:
                print(f"ERROR: Failed to generate conversation for {persona}")
                return False

    return True


def create_batch_dataset(dataset_name: str, limit: int) -> bool:
    """Create a new dataset for this batch of conversations."""
    cmd = [
        sys.executable, "create_dataset.py",
        "--name", dataset_name,
        "--limit", str(limit)
        # No --append: creates a fresh dataset
    ]
    return run_command(cmd, f"Creating dataset '{dataset_name}' with {limit} conversations")


def run_judge_evaluation(
    dataset: str | None = None,
    limit: int | None = None,
    dashboard: bool = True
) -> Path | None:
    """
    Run judge evaluation on conversations.

    Args:
        dataset: Optional dataset name (if None, uses recent runs)
        limit: Max conversations to evaluate (None = all in dataset)
        dashboard: Whether to generate dashboard updates

    Returns:
        Path to the run directory, or None on failure
    """
    # Create timestamped output directory
    runs_dir = EVAL_RESULTS_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "run_judge_eval.py"]

    if limit:
        cmd.extend(["--limit", str(limit)])
    else:
        # Use a high limit to get all examples
        cmd.extend(["--limit", "1000"])

    if dataset:
        cmd.extend(["--dataset", dataset])

    if dashboard:
        cmd.append("--dashboard")

    success = run_command(cmd, f"Running judge evaluation on {dataset or 'recent runs'}")

    if success:
        # Find the most recent run directory
        run_dirs = sorted(runs_dir.iterdir(), reverse=True)
        return run_dirs[0] if run_dirs else None

    return None


def deploy_dashboard(run_dir: Path) -> bool:
    """Deploy dashboard to GitHub Pages."""
    cmd = [
        sys.executable, "deploy_dashboard.py",
        "--run", str(run_dir)
    ]
    return run_command(cmd, "Deploying dashboard to GitHub Pages")


def main():
    parser = argparse.ArgumentParser(
        description="Run full evaluation workflow: generate conversations, evaluate, and deploy dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Each batch creates a separate LangSmith dataset (e.g., batch-20260121_143000).
The dashboard aggregates results from ALL local eval_results/runs/ directories.

Examples:
    # Generate and evaluate 10 conversations for 2 personas
    python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 10 --deploy

    # Regenerate dashboard from existing local results (no new conversations)
    python run_batch_eval.py --eval-only --deploy

    # Quick test with 2 conversations
    python run_batch_eval.py --personas amara_SBI --count 2
        """
    )

    parser.add_argument(
        "--personas",
        type=str,
        help="Comma-separated list of personas (e.g., 'amara_SBI,carlos_SBI')"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of conversations per persona (default: 5)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=20,
        help="Number of turns per conversation (default: 20)"
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Regenerate dashboard from existing local results (no LangSmith API calls)"
    )
    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip judge evaluation (only generate conversations)"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy dashboard to GitHub Pages after evaluation"
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Disable dashboard generation during evaluation"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.eval_only and not args.personas:
        parser.error("--personas is required unless using --eval-only")

    # Generate timestamp for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dataset = f"batch-{timestamp}"

    print("\n" + "="*60)
    print("  MentorAI Batch Evaluation")
    print("="*60)

    # Parse personas
    personas = []
    if args.personas:
        personas = [p.strip() for p in args.personas.split(",")]
        print(f"  Personas: {', '.join(personas)}")
        print(f"  Conversations per persona: {args.count}")
        print(f"  Turns per conversation: {args.turns}")
        print(f"  New conversations: {len(personas) * args.count}")
        print(f"  Batch dataset: {batch_dataset}")

    # Handle --eval-only: regenerate dashboard from local results only
    if args.eval_only:
        print("\n[--eval-only] Regenerating dashboard from existing local results...")
        from generate_dashboard import generate_dashboard, find_latest_run, aggregate_all_runs

        runs_dir = EVAL_RESULTS_DIR / "runs"
        if not runs_dir.exists() or not any(runs_dir.iterdir()):
            print("ERROR: No evaluation runs found in eval_results/runs/")
            return 1

        # Find the latest run dir (for storing the new aggregated dashboard)
        run_dir = find_latest_run()

        # Generate dashboard (it will aggregate all runs internally)
        dashboard_path = generate_dashboard(run_dir)
        print(f"Dashboard regenerated: {dashboard_path}")

        # Deploy if requested
        if args.deploy:
            print(f"\n[Step 3/3] Deploying dashboard...")
            if not deploy_dashboard(run_dir):
                print("\nWARNING: Dashboard deployment failed")

        print("\n" + "="*60)
        print("  Dashboard Regeneration Complete!")
        print("="*60)
        return 0

    # Step 1: Generate conversations
    conversations_dir = None
    if personas:
        conversations_dir = SCRIPT_DIR / "conversations" / timestamp

        print(f"\n[Step 1/3] Generating conversations...")
        success = generate_conversations(
            personas=personas,
            count=args.count,
            turns=args.turns,
            output_dir=conversations_dir
        )

        if not success:
            print("\nERROR: Conversation generation failed")
            return 1

        print(f"\nConversations saved to: {conversations_dir}")

        # Create batch dataset for these conversations
        total_conversations = len(personas) * args.count
        print(f"\nCreating batch dataset '{batch_dataset}'...")
        if not create_batch_dataset(batch_dataset, total_conversations):
            print("WARNING: Failed to create batch dataset")

    # Step 2: Run judge evaluation on this batch only
    run_dir = None
    if not args.skip_evaluation:
        print(f"\n[Step 2/3] Running judge evaluation on batch '{batch_dataset}'...")
        run_dir = run_judge_evaluation(
            dataset=batch_dataset,
            limit=None,  # Evaluate all in this batch
            dashboard=not args.no_dashboard
        )

        if run_dir is None:
            print("\nERROR: Judge evaluation failed")
            return 1

        print(f"\nResults saved to: {run_dir}")
    else:
        print("\n[Step 2/3] Skipping judge evaluation")

    # Step 3: Deploy dashboard
    if args.deploy and run_dir:
        print(f"\n[Step 3/3] Deploying dashboard...")
        if not deploy_dashboard(run_dir):
            print("\nWARNING: Dashboard deployment failed")
    else:
        print("\n[Step 3/3] Skipping dashboard deployment")

    # Summary
    print("\n" + "="*60)
    print("  Batch Evaluation Complete!")
    print("="*60)

    if conversations_dir and conversations_dir.exists():
        conv_count = len(list(conversations_dir.glob("*.md")))
        print(f"Conversations generated: {conv_count}")
        print(f"Conversations directory: {conversations_dir}")

    if run_dir:
        print(f"Evaluation results: {run_dir}")
        dashboard_path = run_dir / "dashboard.html"
        if dashboard_path.exists():
            print(f"Dashboard: file://{dashboard_path.absolute()}")

    if args.deploy:
        print("\nGitHub Pages dashboard should be live shortly!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
