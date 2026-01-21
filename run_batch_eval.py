"""
Batch Evaluation Orchestrator
=============================

Single command that handles the full evaluation workflow:
1. Generates N conversations per persona (saves to markdown)
2. Creates LangSmith dataset from runs
3. Runs judge evaluation with dashboard updates after each conversation
4. Deploys dashboard to GitHub Pages (optional)

Usage:
    # Run 10 conversations for 2 personas (20 turns each), deploy dashboard
    python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 10 --deploy

    # Local only (no deployment)
    python run_batch_eval.py --personas amara_SBI --count 5

    # Single persona with custom turns
    python run_batch_eval.py --personas amara_SBI --count 3 --turns 15

    # Skip conversation generation, evaluate existing dataset
    python run_batch_eval.py --dataset my-dataset --skip-generation
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


def create_dataset(dataset_name: str, limit: int) -> bool:
    """Create a LangSmith dataset from recent runs."""
    cmd = [
        sys.executable, "create_dataset.py",
        "--name", dataset_name,
        "--limit", str(limit)
    ]
    return run_command(cmd, f"Creating dataset: {dataset_name}")


def run_judge_evaluation(
    dataset: str | None = None,
    limit: int = 10,
    dashboard: bool = True
) -> Path | None:
    """
    Run judge evaluation on conversations.

    Args:
        dataset: Optional dataset name (if None, uses recent runs)
        limit: Max conversations to evaluate
        dashboard: Whether to generate dashboard updates

    Returns:
        Path to the run directory, or None on failure
    """
    # Create timestamped output directory
    runs_dir = EVAL_RESULTS_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = runs_dir / timestamp

    cmd = [
        sys.executable, "run_judge_eval.py",
        "--limit", str(limit)
    ]

    if dataset:
        cmd.extend(["--dataset", dataset])

    if dashboard:
        cmd.append("--dashboard")

    success = run_command(cmd, "Running judge evaluation")

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
Examples:
    # Generate and evaluate 10 conversations for 2 personas
    python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 10 --deploy

    # Evaluate existing dataset (skip generation)
    python run_batch_eval.py --dataset my-dataset --skip-generation

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
        "--dataset",
        type=str,
        help="Use existing LangSmith dataset instead of generating conversations"
    )
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip conversation generation (requires --dataset)"
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
    if args.skip_generation and not args.dataset:
        parser.error("--skip-generation requires --dataset")

    if not args.skip_generation and not args.personas:
        parser.error("--personas is required unless using --skip-generation with --dataset")

    print("\n" + "="*60)
    print("  MentorAI Batch Evaluation")
    print("="*60)

    # Parse personas
    personas = []
    if args.personas:
        personas = [p.strip() for p in args.personas.split(",")]
        print(f"Personas: {', '.join(personas)}")
        print(f"Conversations per persona: {args.count}")
        print(f"Turns per conversation: {args.turns}")
        print(f"Total conversations: {len(personas) * args.count}")

    if args.dataset:
        print(f"Dataset: {args.dataset}")

    # Step 1: Generate conversations
    conversations_dir = None
    if not args.skip_generation and personas:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

        # Create dataset from recent runs
        total_conversations = len(personas) * args.count
        dataset_name = f"batch-{timestamp}"

        print(f"\nCreating dataset '{dataset_name}' from recent runs...")
        if not create_dataset(dataset_name, total_conversations):
            print("WARNING: Dataset creation failed, evaluation will use recent runs")
            dataset_name = None
        else:
            args.dataset = dataset_name
    else:
        print("\n[Step 1/3] Skipping conversation generation")

    # Step 2: Run judge evaluation
    run_dir = None
    if not args.skip_evaluation:
        print(f"\n[Step 2/3] Running judge evaluation...")
        total_to_evaluate = len(personas) * args.count if personas else args.count
        run_dir = run_judge_evaluation(
            dataset=args.dataset,
            limit=total_to_evaluate,
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
