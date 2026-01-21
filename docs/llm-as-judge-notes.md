# LLM-as-Judge Evaluation Notes

This document tracks our process for setting up automated evaluation of MentorAI tutoring conversations using LLM judges.

## Overview

We use LLM judges (Claude) to evaluate tutoring conversations between MentorAI and synthetic learner personas. The evaluation uses a two-stage pipeline:

1. **Stage 1: Critical Criteria** - Fast-fail gate (7 criteria, must pass all)
2. **Stage 2: Quality Criteria** - Detailed assessment (20 criteria across 6 domains)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  run_eval.py    │────▶│   LangSmith     │────▶│ run_judge_eval  │
│  (conversations)│     │   (storage)     │     │  (evaluation)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  eval_results/  │
                                               │  - manifest.json│
                                               │  - critical/*.md│
                                               │  - quality/*.md │
                                               └─────────────────┘
```

## File Organization

```
prompts/judges/                      # Judge prompts as markdown files
├── critical_criteria.md             # Stage 1: Critical gate (7 criteria)
├── session_setup.md                 # Stage 2A: Session Setup (3 criteria)
├── modeling_quality.md              # Stage 2B: Modeling Quality (4 criteria)
├── coaching_quality.md              # (future)
├── sbi_content.md                   # (future)
├── adaptive_pacing.md               # (future)
└── conversational_quality.md        # (future)

eval_results/
├── validation/                      # Validation-phase results
│   └── 20260113_v1/
│       ├── manifest.json
│       ├── critical/
│       │   ├── {short_id}.md
│       │   └── {short_id}.json
│       └── quality/
│           ├── {short_id}_session_setup.md
│           └── {short_id}_session_setup.json
└── runs/                            # Production run results
    └── 20260113_143000/
        └── ...
```

## Running Evaluations

```bash
# Full pipeline (critical + quality for passing conversations)
python run_judge_eval.py --project MentorAI-Eval --limit 10

# Validation mode (separate output location for manual review)
python run_judge_eval.py --project MentorAI-Eval --validation --limit 3

# Filter by tag (tag runs in LangSmith UI first)
python run_judge_eval.py --tag eval-batch-1 --limit 50

# Run only critical criteria
python run_judge_eval.py --stage critical --limit 10

# Run specific quality judge
python run_judge_eval.py --stage quality --judge session_setup

# Use different model
python run_judge_eval.py --model claude-sonnet-4-20250514 --limit 5
```

### Using Datasets (Recommended)

Datasets let you curate a specific set of conversations for evaluation. This is better than tag filtering because you can select examples after they're created.

```bash
# Step 1: Create a dataset from runs
python create_dataset.py --name eval-batch-jan13 --limit 10

# Step 2: Run evaluation on the dataset
python run_judge_eval.py --dataset eval-batch-jan13

# Other dataset commands
python create_dataset.py --list                           # List existing datasets
python create_dataset.py --name my-dataset --append       # Add more runs to existing
python create_dataset.py --name my-dataset --tag my-tag   # Only runs with tag
```

**Benefits of datasets:**
- Curate examples after conversations are generated
- Reproducible evaluation sets
- Version your test data
- Can add examples from LangSmith Playground (as of April 2025)

### Filtering by Tag (Alternative)

If you prefer to tag runs directly:
1. In LangSmith UI, select the runs you want to evaluate
2. Click "Add tags" and enter a tag name (e.g., `eval-batch-1`)
3. Run with `--tag eval-batch-1`

**Note:** Tags must be added at trace time or via code—the LangSmith UI doesn't support adding tags to existing traces retroactively.

## Two-Stage Pipeline

### Stage 1: Critical Criteria (Fast-Fail Gate)

| Code | Criterion | What It Checks |
|------|-----------|----------------|
| B-01 | Shows, Not Tells | Mentor demonstrates a complete SBI example |
| C-01 | Specific Feedback | Mentor quotes exact problematic language |
| C-03 | Revision Requested | Mentor asks learner to revise after feedback |
| D-01 | Catches Vague Situations | Mentor catches "lately," "sometimes," etc. |
| D-02 | Catches Judgment Leakage | Mentor catches "dismissive," "rude," etc. |
| D-03 | Catches Accusatory Impact | Mentor catches "You made everyone..." |
| E-03 | Protects Productive Struggle | Mentor requires attempt before giving answers |

**N/A Handling:** D-01, D-02, D-03, and E-03 can be marked N/A if the learner never produces the error type that would trigger them.

### Stage 2: Quality Criteria

Only conversations that PASS critical criteria proceed to quality evaluation.

| Judge | Criteria | Status |
|-------|----------|--------|
| session_setup | A-01, A-02, A-03 | Implemented |
| modeling_quality | B-02, B-03, B-04, B-05 | Implemented |
| coaching_quality | C-02, C-04, C-05, C-06, C-07 | Implemented |
| sbi_content | D-04, D-05, D-06 | Implemented |
| adaptive_pacing | E-01, E-02 | Implemented |
| conversational_quality | F-01, F-02, F-03 | Implemented |

## Pass Thresholds

For a conversation to pass evaluation, it must meet the following thresholds:

### Critical Criteria: 100%

All applicable critical criteria must pass. These represent fundamental SBI coaching behaviors—a mentor that misses these isn't doing SBI coaching.

- **7 critical criteria** total (B-01, C-01, C-03, D-01, D-02, D-03, E-03)
- Some criteria can be **N/A** if the learner never triggers the condition (e.g., D-01 is N/A if learner never uses vague situation language)
- Threshold applies to **scorable criteria only** (PASS or FAIL verdicts, excluding N/A)

### Quality Criteria: 85%

At least 85% of applicable quality criteria must pass per conversation. This allows for minor imperfections while maintaining a high bar.

- **20 quality criteria** total across 6 domains
- 85% = at most **3 failures** out of 20 (or proportionally fewer if some are N/A)
- Evaluated **per conversation**, not aggregated across a batch

### Summary

| Criteria Type | Count | Threshold | Interpretation |
|---------------|-------|-----------|----------------|
| Critical | 7 | 100% | Must pass all (N/A excluded) |
| Quality | 20 | 85% | Allow up to 3 misses per conversation |

**Note:** These thresholds are starting points. Adjust based on data from initial eval runs if needed.

## Output Format

Each evaluation produces:
- **Markdown file** (.md) - Human-readable with transcript and verdicts
- **JSON file** (.json) - Machine-readable structured data
- **manifest.json** - Run metadata and summary statistics

### JSON Schema (example)

```json
{
  "criteria": {
    "B-01": {"verdict": "PASS", "evidence": "..."},
    "C-01": {"verdict": "PASS", "evidence": "..."}
  },
  "overall": {
    "verdict": "PASS",
    "passed_count": 6,
    "failed_count": 0,
    "na_count": 1,
    "failed_criteria": []
  }
}
```

## Model Selection

| Model | Use Case | Notes |
|-------|----------|-------|
| `claude-opus-4-5-20251101` | Production evaluation | Best reasoning, catches subtle issues |
| `claude-sonnet-4-20250514` | Development/testing | Good balance of quality and cost |
| `claude-haiku-4-20250414` | Quick iteration | Too light for nuanced judgment calls |

**Recommendation:** Use Opus 4.5 for final evaluations.

## Transcript Processing

### Inner Monologue Stripping

Synthetic learners output two parts:
- `[INNER THOUGHT]` - Internal reasoning (for evaluation diagnostics)
- `[RESPONSE]` - What the mentor sees

The judge should only evaluate what the mentor could see, so we strip both markers.

### Run Filtering

Important: We filter by run name (`MentorAI Evaluation Conversation`) to avoid evaluating the judge's own API calls.

### LangSmith Tracing

The judge script disables LangSmith tracing (`LANGCHAIN_TRACING_V2=false`) so judge API calls aren't logged to LangSmith. This:
- Prevents judge runs from appearing in your project
- Avoids incurring LangSmith token costs for judge calls
- Keeps your project clean with only tutor conversations

## Issues Encountered

### 1. LangChain Template Escaping
**Problem:** JSON examples in prompts with `{}` were interpreted as template variables.
**Solution:** Escape with double braces `{{}}` in prompt files.

### 2. Wrong Runs Being Evaluated
**Problem:** Judge script picked up its own LangSmith-logged API calls.
**Solution:** Filter by run name with `--run-filter` flag.

### 3. API Key Environment Variables
**Problem:** Script checked for `LANGSMITH_API_KEY` but environment used `LANGCHAIN_API_KEY`.
**Solution:** Accept either variable name.

### 4. Model ID Format
**Problem:** Initial model ID `claude-opus-4-5-20250514` returned 404.
**Solution:** Correct Opus 4.5 model ID is `claude-opus-4-5-20251101`.

## Validation Process

1. Run `python run_judge_eval.py --validation --limit 3`
2. Review each verdict in `eval_results/validation/` - do you agree?
3. Check evidence accuracy - did judge quote real transcript sections?
4. Note disagreements for prompt refinement
5. Scale up once judge is trusted on validation set

## Generating Reports

Generate HTML and CSV reports for easy sharing with colleagues:

```bash
# Generate from most recent run
python generate_report.py

# Generate from specific run
python generate_report.py --run eval_results/validation/20260113_v3

# Output to custom location
python generate_report.py --output reports/
```

**Output files:**
- `report.html` - Visual report with summary stats, progress bars, expandable details
- `results.csv` - Spreadsheet with all criteria verdicts and evidence

The HTML report includes:
- Summary statistics (conversations evaluated, pass rates)
- Per-judge breakdown with progress bars
- Expandable conversation details with full evidence

## Next Steps

- [x] Create multi-judge architecture
- [x] Implement critical criteria judge
- [x] Implement all 6 quality judges
- [x] Add JSON output alongside markdown
- [x] Add tag filtering for selective evaluation
- [x] Disable LangSmith tracing for judge calls
- [x] Add aggregate reporting (HTML + CSV)
- [x] Add dataset-based evaluation workflow
- [ ] Document disagreements with judge verdicts
- [ ] Validate judges on larger sample

---

## Changelog

### 2026-01-19: SBI Fidelity Criteria V2 Update

Updated judge prompts to align with SBI Fidelity Criteria V2. Key changes:

**Critical Criteria (critical_criteria.md)**
- Renamed E-04 → E-03 (Protects Productive Struggle)
- Criteria list now: B-01, C-01, C-03, D-01, D-02, D-03, E-03

**Adaptive Pacing (adaptive_pacing.md)**
- Removed E-03 "Adjusts to Struggle" (criterion removed from V2)
- Reduced from 3 criteria to 2 (E-01, E-02)
- E-03 "Protects Productive Struggle" moved to critical criteria

**Coaching Quality (coaching_quality.md)**
- Updated C-07 "Prompts Reflection" description
- Old: focused on comparing draft to modeled example
- New: emphasizes stepping back from task to reflect on learning process (what was difficult, what clicked, how thinking changed) rather than justifying specific draft choices

**Conversational Quality (conversational_quality.md)**
- Major reduction from 6 criteria to 3
- Kept F-01 "Varied Turn Structure" (unchanged)
- Moved F-05 "Has a Voice" → F-02 (same content)
- Added new F-03 "Responds to Negative Affect" (from V2)
- Removed: F-02 "Genuine Curiosity", F-03 "Room to Breathe", F-04 "Dwells on Difficulty", F-06 "Questions Over Corrections"

**Total criteria count**: 27 (7 critical + 20 quality)

---

### 2026-01-21: Dashboard Enhancements & Persona Tracking

**Dashboard Improvements (generate_dashboard.py)**
- Added per-persona columns (A, B, C, D, E, F) to Per-Criteria Results table
- Shows pass rates broken down by persona (Amara, Bailey, Carlos, Daniel, Elise, Fatou)
- Changed individual criteria display from card grid to table rows matching category format
- Reordered columns: Criterion | Passed | Pass Rate | Persona Columns | Progress
- Expandable criteria rows now show individual criterion results

**Persona Tracking Fix (run_judge_eval.py)**
- Added automatic persona extraction from LangSmith dataset examples
- Extracts `persona_name` from `example.inputs` and stores in manifest
- Dashboard now correctly displays persona instead of "Unknown"

**Environment Variable Fix**
- Added `load_dotenv(override=True)` to all scripts (run_eval.py, run_judge_eval.py, create_dataset.py)
- Ensures `.env` file values take precedence over shell environment variables
- Fixes API key authentication issues when env vars are set differently in shell

---

*Last updated: 2026-01-21*
