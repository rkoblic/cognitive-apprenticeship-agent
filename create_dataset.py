"""
Create LangSmith Dataset from Runs
==================================

Utility to create a dataset from LangSmith runs for curated evaluation.

Usage:
    # Create dataset from recent runs
    python create_dataset.py --name eval-batch-jan13 --limit 10

    # Create from runs with specific tag
    python create_dataset.py --name eval-batch-jan13 --tag my-tag

    # List existing datasets
    python create_dataset.py --list

    # Add more runs to existing dataset
    python create_dataset.py --name eval-batch-jan13 --append --limit 5
"""

import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file (override existing)
load_dotenv(override=True)

from langsmith import Client

# Default settings
DEFAULT_PROJECT = "MentorAI-Eval"
DEFAULT_RUN_FILTER = "MentorAI Evaluation Conversation"


def list_datasets(client: Client):
    """List all datasets in the workspace."""
    print("\nExisting datasets:")
    print("-" * 50)
    datasets = list(client.list_datasets())
    if not datasets:
        print("  No datasets found.")
        return

    for ds in datasets:
        examples = list(client.list_examples(dataset_id=ds.id, limit=1000))
        print(f"  {ds.name}: {len(examples)} examples")


def create_dataset_from_runs(args):
    """Create or append to a dataset from LangSmith runs."""

    # Check for required environment variables
    if not os.environ.get('LANGSMITH_API_KEY') and not os.environ.get('LANGCHAIN_API_KEY'):
        print("ERROR: LANGSMITH_API_KEY or LANGCHAIN_API_KEY environment variable not set")
        return

    client = Client()

    if args.list:
        list_datasets(client)
        return

    if not args.name:
        print("ERROR: --name is required to create a dataset")
        return

    # Check if dataset exists
    existing_dataset = None
    try:
        existing_dataset = client.read_dataset(dataset_name=args.name)
    except Exception:
        pass  # Dataset doesn't exist

    if existing_dataset and not args.append:
        print(f"ERROR: Dataset '{args.name}' already exists. Use --append to add more examples.")
        return

    # Fetch runs
    print(f"Fetching runs from project: {args.project}")
    filter_kwargs = {
        "project_name": args.project,
        "limit": args.limit,
    }
    if args.run_filter:
        filter_kwargs["filter"] = f'eq(name, "{args.run_filter}")'

    runs = list(client.list_runs(**filter_kwargs))

    # Filter by tag if specified
    if args.tag:
        print(f"Filtering by tag: {args.tag}")
        runs = [r for r in runs if args.tag in (r.tags or [])]

    print(f"Found {len(runs)} runs")

    if not runs:
        print("No runs found. Check your project name and filters.")
        return

    # Create or get dataset
    if existing_dataset:
        dataset = existing_dataset
        print(f"Appending to existing dataset: {args.name}")
    else:
        dataset = client.create_dataset(
            dataset_name=args.name,
            description=f"Evaluation dataset created from {args.project} runs"
        )
        print(f"Created new dataset: {args.name}")

    # Add examples
    added = 0
    skipped = 0

    for run in runs:
        # Skip runs without transcript output
        if not run.outputs or 'transcript' not in run.outputs:
            print(f"  Skipping {str(run.id)[:8]} (no transcript)")
            skipped += 1
            continue

        try:
            client.create_example(
                inputs=run.inputs or {},
                outputs=run.outputs,
                dataset_id=dataset.id,
                metadata={
                    "source_run_id": str(run.id),
                    "source_run_name": run.name,
                    "source_project": args.project,
                }
            )
            print(f"  Added {str(run.id)[:8]}")
            added += 1
        except Exception as e:
            print(f"  Error adding {str(run.id)[:8]}: {e}")
            skipped += 1

    print(f"\nDone! Added {added} examples, skipped {skipped}")
    print(f"Dataset: {args.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Create LangSmith dataset from runs"
    )

    parser.add_argument(
        "--name",
        help="Dataset name to create or append to"
    )

    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help=f"LangSmith project name (default: {DEFAULT_PROJECT})"
    )

    parser.add_argument(
        "--run-filter",
        default=DEFAULT_RUN_FILTER,
        help=f"Filter runs by name (default: {DEFAULT_RUN_FILTER})"
    )

    parser.add_argument(
        "--tag",
        help="Only include runs with this tag"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max runs to add (default: 50)"
    )

    parser.add_argument(
        "--append",
        action="store_true",
        help="Add to existing dataset instead of creating new"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing datasets"
    )

    args = parser.parse_args()
    create_dataset_from_runs(args)


if __name__ == "__main__":
    main()
