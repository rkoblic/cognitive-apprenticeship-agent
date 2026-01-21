"""
Deploy Dashboard to GitHub Pages
================================

Deploys the evaluation dashboard to GitHub Pages for team sharing.
Copies dashboard.html to docs/index.html and pushes to the repository.

Prerequisites:
- GitHub Pages must be enabled for the repository (Settings > Pages > Source: Deploy from branch > /docs)
- You must have push access to the repository

Usage:
    python deploy_dashboard.py --run eval_results/runs/YYYYMMDD_HHMMSS
    python deploy_dashboard.py  # Uses most recent run
    python deploy_dashboard.py --no-push  # Generate only, don't push
"""

import argparse
import shutil
import subprocess
from pathlib import Path

from generate_dashboard import find_latest_run, generate_dashboard

SCRIPT_DIR = Path(__file__).parent


def get_git_remote_info(repo_dir: Path) -> tuple[str, str] | None:
    """
    Extract username and repo name from git remote URL.

    Returns:
        (username, repo_name) or None if not a git repo
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # Handle SSH format: git@github.com:username/repo.git
        if url.startswith("git@github.com:"):
            path = url.replace("git@github.com:", "").replace(".git", "")
            parts = path.split("/")
            if len(parts) == 2:
                return parts[0], parts[1]

        # Handle HTTPS format: https://github.com/username/repo.git
        if "github.com" in url:
            path = url.split("github.com/")[-1].replace(".git", "")
            parts = path.split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]

    except subprocess.CalledProcessError:
        pass

    return None


def deploy_dashboard(run_dir: Path, repo_dir: Path, push: bool = True) -> str | None:
    """
    Deploy dashboard to GitHub Pages via docs/ folder.

    Args:
        run_dir: Path to the evaluation run directory
        repo_dir: Path to the git repository root
        push: Whether to commit and push changes

    Returns:
        GitHub Pages URL or None if deployment failed
    """
    docs_dir = repo_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Generate dashboard first (in case it's outdated)
    dashboard_path = generate_dashboard(run_dir)
    print(f"Dashboard generated: {dashboard_path}")

    # Copy to docs/index.html
    dest_path = docs_dir / "index.html"
    shutil.copy(dashboard_path, dest_path)
    print(f"Copied to: {dest_path}")

    if not push:
        print("Skipping git push (--no-push specified)")
        return None

    # Get remote info for URL
    remote_info = get_git_remote_info(repo_dir)
    if remote_info is None:
        print("WARNING: Could not determine GitHub remote URL")
        username, repo = "USER", "REPO"
    else:
        username, repo = remote_info

    # Git add, commit, and push
    try:
        # Check if there are changes to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain", "docs/"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if not status_result.stdout.strip():
            print("No changes to deploy (dashboard already up to date)")
            return f"https://{username}.github.io/{repo}/"

        subprocess.run(
            ["git", "add", "docs/"],
            cwd=repo_dir,
            check=True
        )
        print("Staged docs/ for commit")

        subprocess.run(
            ["git", "commit", "-m", f"Update evaluation dashboard ({run_dir.name})"],
            cwd=repo_dir,
            check=True
        )
        print("Committed changes")

        subprocess.run(
            ["git", "push"],
            cwd=repo_dir,
            check=True
        )
        print("Pushed to remote")

        url = f"https://{username}.github.io/{repo}/"
        print(f"\nDashboard deployed!")
        print(f"View at: {url}")
        print("(Note: GitHub Pages may take 1-2 minutes to update)")

        return url

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git operation failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Deploy evaluation dashboard to GitHub Pages"
    )
    parser.add_argument(
        "--run",
        type=str,
        help="Path to evaluation run directory (default: most recent)"
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=str(SCRIPT_DIR),
        help="Path to git repository root (default: script directory)"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Generate and copy dashboard but don't commit/push"
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

    repo_dir = Path(args.repo)
    if not (repo_dir / ".git").exists():
        print(f"ERROR: Not a git repository: {repo_dir}")
        return

    deploy_dashboard(run_dir, repo_dir, push=not args.no_push)


if __name__ == "__main__":
    main()
