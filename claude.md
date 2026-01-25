# MentorAI Evaluation Project

Automated evaluation framework for testing MentorAI (a tutoring agent) against synthetic learner personas.

## Quick Start

```bash
# Run 5 conversations with a persona and deploy dashboard
python run_batch_eval.py --personas carlos_SBI --count 5 --deploy

# Run multiple personas
python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 5 --deploy
```

Dashboard: https://rkoblic.github.io/cognitive-apprenticeship-agent/

## Available Personas

| Persona | Letter | Characteristics |
|---------|--------|-----------------|
| amara_SBI | A | Cooperative learner, no negative affect |
| bailey_SBI | B | — |
| carlos_SBI | C | Impatient/curt, shows negative affect |
| daniel_SBI | D | — |
| elise_SBI | E | — |
| fatou_SBI | F | — |

## Project Structure

```
prompts/
  mentor.md                 # MentorAI system prompt
  personas/
    *.md                    # Synthetic learner personas
    REVISION_NOTES.md       # Changelog for persona/eval updates
  judges/
    *.md                    # LLM-as-judge evaluation prompts
docs/
  prompt-engineering-notes.md  # Lessons learned, patterns
  llm-as-judge-notes.md     # Judge evaluation setup and notes
run_eval.py                 # Generate tutor-learner conversations
run_judge_eval.py           # Run LLM judges on conversations
create_dataset.py           # Create datasets from LangSmith runs
generate_report.py          # Generate HTML/CSV reports
generate_dashboard.py       # Generate live HTML dashboard
deploy_dashboard.py         # Deploy dashboard to GitHub Pages
run_batch_eval.py           # Full pipeline script (recommended)
convert_spot_checks.py      # Convert human rating CSVs to JSON
eval_results/               # Judge evaluation outputs (local)
  runs/                     # LLM judge results by timestamp
  human_ratings/            # Human spot-check ratings (JSON)
  spot_check/               # Source CSV files from human raters
docs/                       # GitHub Pages dashboard (index.html)
conversations/              # Saved conversation transcripts
```

## Running Evaluations

### Batch Evaluation (Recommended)
```bash
# Full pipeline: generate conversations, run judges, deploy dashboard
python run_batch_eval.py --personas carlos_SBI --count 5 --deploy

# Multiple personas
python run_batch_eval.py --personas amara_SBI,carlos_SBI --count 5 --deploy

# Custom turns per conversation (default: 20)
python run_batch_eval.py --personas carlos_SBI --count 5 --turns 15 --deploy

# Regenerate dashboard from existing local results (no new conversations)
python run_batch_eval.py --eval-only --deploy
```

Each batch creates a separate LangSmith dataset (e.g., `batch-20260121_143000`).
The dashboard aggregates results from all runs created **from 2026-01-21 onwards**.

### Generate Single Conversation
```bash
python run_eval.py --persona <name> --turns <n>
python run_eval.py --list-personas  # Show available personas
```

Conversations are logged to LangSmith for review and scoring.

### Run LLM-as-Judge Evaluation
```bash
python run_judge_eval.py --validation --limit 3   # Validation mode
python run_judge_eval.py --dataset <name>         # Evaluate from dataset
python run_judge_eval.py --stage critical         # Critical criteria only
```

### Create Evaluation Datasets
```bash
python create_dataset.py --name <name> --limit 10  # Create from recent runs
python create_dataset.py --list                    # List existing datasets
```

### Generate Reports
```bash
python generate_report.py                         # From most recent run
python generate_report.py --run <path>            # From specific run
```

Outputs `report.html` (visual) and `results.csv` (data) for sharing.

### Live Dashboard
```bash
python generate_dashboard.py --run <path>         # Generate dashboard HTML
python deploy_dashboard.py --run <path>           # Deploy to GitHub Pages
```

The dashboard shows per-persona pass rates and is automatically regenerated after each evaluation. View at: https://rkoblic.github.io/cognitive-apprenticeship-agent/

See `docs/llm-as-judge-notes.md` for full documentation.

### Human Spot-Check Ratings

To validate LLM judge accuracy, human raters can score conversations and compare against LLM results.

**Adding new spot-check ratings:**

1. **Score conversations** using the CSV template with columns: `Tag, Name, Criterion, Tier, CA Method, Pass/Fail, Evidence/Notes`
2. **Save CSV** to `eval_results/spot_check/` with naming format: `{Rater}_SBI_Fidelity_Criteria_Spot Checks - {timestamp}_{persona}.csv` (alternate format `{Rater}_SBI_Spot_Checks - {timestamp}_{persona}.csv` also supported)
3. **Look up LangSmith ID** for the conversation in the LangSmith UI
4. **Add mapping** to `eval_results/human_ratings/id_mapping.json`:
   ```json
   {
     "20260121_100749_amara_SBI": "e2206591-e8e0-4eac-a481-e66f8b60feba"
   }
   ```
5. **Convert and deploy**:
   ```bash
   python convert_spot_checks.py
   python generate_dashboard.py --output docs/index.html
   git add -A && git commit -m "Add spot-check ratings" && git push
   ```

The dashboard will show overall agreement percentage and highlight disagreements with side-by-side LLM vs human rationale.

## Documentation Conventions

When making changes to personas or evaluation infrastructure:

1. **REVISION_NOTES.md** (`prompts/personas/`) — Log every change with date, file, what changed, and rationale
2. **prompt-engineering-notes.md** (`docs/`) — Document lessons learned, failed approaches, and reusable patterns

## Persona Design Pattern

Personas must make authentic mistakes (not just hedge correct answers). Key pattern:

- Put "CRITICAL PERFORMANCE REQUIREMENT" section at the **top** of the prompt, before role description
- Include a table of specific mistakes to make per task type
- Reference the requirement in the `[INNER THOUGHT]` block

See `docs/prompt-engineering-notes.md` for why this works.

## Output Format

Learner personas use a two-part output format:
- `[INNER THOUGHT]` — Internal reasoning (logged for evaluation, hidden from mentor)
- `[RESPONSE]` — Visible response (what mentor sees)

## Dashboard Details

### Quality Scores
- **20 total criteria** across 6 judges: session_setup (3), modeling_quality (4), coaching_quality (5), sbi_content (3), adaptive_pacing (2), conversational_quality (3)
- **N/A criteria**: Some criteria can be N/A if the learner doesn't trigger the condition (e.g., F-03 "responding to learner frustration" is N/A for amara since she's cooperative)
- **Score display**: Shows `passed/total (X N/A)` when criteria are N/A, and ⚠️ when parsing failed

### Dashboard Features
- **Criterion tooltips**: Hover over any criterion code (A-01, B-02, etc.) to see a description of what that criterion evaluates
- **Persona filtering**: Filter conversations by persona using the letter buttons (A-F), or click "All" to show all
- **Group by persona**: Check the "Group by persona" box to collapse conversations into expandable persona sections with summary stats
- **Color-coded pass rates**: Pass rate percentages are colored green (≥80%), orange (41-79%), or red (≤40%) for quick scanning
- **Human Spot-Check section**: Shows agreement rate between human raters and LLM judges, with expandable disagreement details showing side-by-side rationale

### Aggregation
- Dashboard aggregates all runs from **2026-01-21 onwards** (by date prefix >= 20260121)
- Deduplicates by LangSmith conversation ID, preferring entries with valid persona data
- Results stored in `eval_results/runs/<timestamp>/manifest.json`

### Maintenance

```bash
# Regenerate dashboard from current local results
python generate_dashboard.py

# Deploy to GitHub Pages
python deploy_dashboard.py --run eval_results/runs/<latest_run>

# Clean up old runs (if needed)
rm -rf eval_results/runs/YYYYMMDD_*

# List available LangSmith datasets
python create_dataset.py --list
```

### Troubleshooting
- **Unknown personas**: Check that the batch dataset captured `persona_name` in inputs
- **Duplicate conversations**: Same LangSmith ID evaluated in multiple runs; delete old run directories
- **Missing N/A counts**: Stored in `quality_results.<judge>.json.overall.na_count`
