# MentorAI Evaluation Project

Automated evaluation framework for testing MentorAI (a tutoring agent) against synthetic learner personas.

## Project Structure

```
prompts/
  mentor.md                 # MentorAI system prompt
  personas/
    *.md                    # Synthetic learner personas
    REVISION_NOTES.md       # Changelog for persona/eval updates
docs/
  prompt-engineering-notes.md  # Lessons learned, patterns
run_eval.py                 # Main evaluation script
```

## Running Evaluations

```bash
python run_eval.py --persona <name> --turns <n>
python run_eval.py --list-personas  # Show available personas
```

Conversations are logged to LangSmith for review and scoring.

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
