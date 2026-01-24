#!/usr/bin/env python3
"""
Convert human spot-check CSV files to JSON format.

Usage:
    python convert_spot_checks.py                    # Convert all CSVs
    python convert_spot_checks.py --input <csv>      # Convert specific file
    python convert_spot_checks.py --dry-run          # Show what would be converted
"""

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path

SPOT_CHECK_DIR = Path("eval_results/spot_check")
OUTPUT_DIR = Path("eval_results/human_ratings")
MAPPING_FILE = OUTPUT_DIR / "id_mapping.json"

# Valid criteria tags (V2 rubric)
VALID_CRITERIA = [
    "A-01", "A-02", "A-03",
    "B-01", "B-02", "B-03", "B-04", "B-05",
    "C-01", "C-02", "C-03", "C-04", "C-05", "C-06", "C-07",
    "D-01", "D-02", "D-03", "D-04", "D-05", "D-06",
    "E-01", "E-02", "E-03",
    "F-01", "F-02", "F-03"
]


def parse_filename(filename: str) -> dict:
    """Extract metadata from CSV filename.

    Expected formats:
    - {Rater}_SBI_Fidelity_Criteria_Spot Checks - {timestamp}_{persona}.csv
    - {Rater}_SBI_Spot_Checks - {timestamp}_{persona}.csv
    - {Rater}_SBI_Spot_Checks - {emoji_prefix} {timestamp}_{persona}.csv
    """
    # Pattern 1: Full format with "Fidelity_Criteria"
    match = re.match(
        r'^(\w+)_SBI_Fidelity_Criteria_Spot Checks - (\d{8}_\d{6})_(\w+)\.csv$',
        filename
    )
    if match:
        return {
            "rater": match.group(1),
            "conversation_timestamp": match.group(2),
            "persona": match.group(3)
        }

    # Pattern 2: Short format without "Fidelity_Criteria"
    match = re.match(
        r'^(\w+)_SBI_Spot_Checks - (\d{8}_\d{6})_(\w+)\.csv$',
        filename
    )
    if match:
        return {
            "rater": match.group(1),
            "conversation_timestamp": match.group(2),
            "persona": match.group(3)
        }

    # Pattern 3: Short format with emoji/symbol prefix before timestamp
    match = re.match(
        r'^(\w+)_SBI_Spot_Checks - [^\d]*(\d{8}_\d{6})_(\w+)\.csv$',
        filename
    )
    if match:
        return {
            "rater": match.group(1),
            "conversation_timestamp": match.group(2),
            "persona": match.group(3)
        }

    raise ValueError(f"Filename doesn't match expected pattern: {filename}")


def normalize_verdict(value: str) -> str:
    """Normalize verdict values to PASS/FAIL/N/A."""
    if not value:
        return None
    value = value.strip().upper()
    if value in ['PASS', 'P']:
        return 'PASS'
    elif value in ['FAIL', 'F', 'FAILL']:  # Handle typos
        return 'FAIL'
    elif value in ['N/A', 'NA']:
        return 'N/A'
    return None  # Skip invalid/empty


def load_id_mapping() -> dict:
    """Load the timestamp-to-LangSmith-ID mapping."""
    if not MAPPING_FILE.exists():
        return {}
    with open(MAPPING_FILE) as f:
        return json.load(f)


def parse_csv(csv_path: Path, id_mapping: dict) -> dict:
    """Parse CSV file into structured data."""
    metadata = parse_filename(csv_path.name)
    criteria = {}

    # Build the key used in id_mapping
    mapping_key = f"{metadata['conversation_timestamp']}_{metadata['persona']}"
    langsmith_id = id_mapping.get(mapping_key)

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = row.get('Tag', '').strip()

            # Skip header rows, summaries, etc.
            skip_prefixes = ['DOMAIN', 'SUMMARY', 'CRITICAL CRITERIA', 'LEGEND',
                           'Total Criteria', 'Critical', 'Quality']
            if not tag or any(tag.startswith(p) for p in skip_prefixes):
                continue

            # Validate tag format
            if tag not in VALID_CRITERIA:
                print(f"  Warning: Unknown criterion tag '{tag}' in {csv_path.name}")
                continue

            verdict = normalize_verdict(row.get('Pass/Fail', ''))
            if verdict is None:
                continue

            evidence = row.get('Evidence/Notes', '').strip()

            criteria[tag] = {
                "verdict": verdict,
                "evidence": evidence
            }

    # Calculate summary
    passed = sum(1 for c in criteria.values() if c['verdict'] == 'PASS')
    failed = sum(1 for c in criteria.values() if c['verdict'] == 'FAIL')
    na = sum(1 for c in criteria.values() if c['verdict'] == 'N/A')

    return {
        "metadata": {
            "rater": metadata["rater"],
            "conversation_timestamp": metadata["conversation_timestamp"],
            "persona": metadata["persona"],
            "langsmith_id": langsmith_id,
            "source_csv": csv_path.name,
            "converted_at": datetime.now().isoformat()
        },
        "criteria": criteria,
        "summary": {
            "total_criteria": len(criteria),
            "passed": passed,
            "failed": failed,
            "na": na
        }
    }


def generate_index(ratings: list) -> dict:
    """Generate an index file for quick loading."""
    raters = set()
    for r in ratings:
        raters.add(r["metadata"]["rater"])

    return {
        "generated_at": datetime.now().isoformat(),
        "total_conversations": len(ratings),
        "raters": sorted(list(raters)),
        "ratings": [
            {
                "id": f"{r['metadata']['conversation_timestamp']}_{r['metadata']['persona']}",
                "rater": r["metadata"]["rater"],
                "persona": r["metadata"]["persona"],
                "langsmith_id": r["metadata"]["langsmith_id"],
                "summary": r["summary"]
            }
            for r in ratings
        ]
    }


def convert_all(dry_run: bool = False):
    """Convert all CSV files in spot_check directory."""
    if not SPOT_CHECK_DIR.exists():
        print(f"ERROR: Spot check directory not found: {SPOT_CHECK_DIR}")
        return

    csv_files = list(SPOT_CHECK_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {SPOT_CHECK_DIR}")
        return

    if not dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load ID mapping
    id_mapping = load_id_mapping()
    if not id_mapping:
        print(f"Warning: No ID mapping found at {MAPPING_FILE}")
        print("  LangSmith IDs will be null. Create the mapping file to enable matching.")

    ratings = []
    for csv_path in sorted(csv_files):
        print(f"Converting: {csv_path.name}")
        try:
            data = parse_csv(csv_path, id_mapping)
            ratings.append(data)

            # Output filename matches conversation identifier
            output_name = f"{data['metadata']['conversation_timestamp']}_{data['metadata']['persona']}.json"
            output_path = OUTPUT_DIR / output_name

            if dry_run:
                print(f"  -> Would write to: {output_path}")
                print(f"     Rater: {data['metadata']['rater']}")
                print(f"     Criteria: {data['summary']['total_criteria']} ({data['summary']['passed']} pass, {data['summary']['failed']} fail, {data['summary']['na']} N/A)")
                if data['metadata']['langsmith_id']:
                    print(f"     LangSmith ID: {data['metadata']['langsmith_id']}")
                else:
                    print(f"     LangSmith ID: NOT MAPPED")
            else:
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"  -> {output_path}")

        except Exception as e:
            print(f"  ERROR: {e}")

    # Generate index
    if ratings and not dry_run:
        index = generate_index(ratings)
        index_path = OUTPUT_DIR / "index.json"
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        print(f"\nIndex generated: {index_path}")

    # Summary
    print(f"\n{'Would convert' if dry_run else 'Converted'} {len(ratings)} files")

    # Warn about missing mappings
    missing = [r for r in ratings if not r['metadata']['langsmith_id']]
    if missing:
        print(f"\nWarning: {len(missing)} files have no LangSmith ID mapping:")
        for r in missing:
            key = f"{r['metadata']['conversation_timestamp']}_{r['metadata']['persona']}"
            print(f"  - {key}")
        print(f"\nAdd mappings to: {MAPPING_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Convert spot-check CSVs to JSON")
    parser.add_argument("--input", help="Specific CSV file to convert")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be converted without writing files")
    args = parser.parse_args()

    if args.input:
        # Convert single file
        id_mapping = load_id_mapping()
        data = parse_csv(Path(args.input), id_mapping)
        print(json.dumps(data, indent=2))
    else:
        convert_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
