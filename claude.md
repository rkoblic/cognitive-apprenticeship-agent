# MentorAI Evaluation Project

Automated evaluation framework for testing MentorAI (a tutoring agent) against synthetic learner personas.

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
eval_results/               # Judge evaluation outputs
```

## Running Evaluations

### Generate Conversations
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

See `docs/llm-as-judge-notes.md` for full documentation.

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
