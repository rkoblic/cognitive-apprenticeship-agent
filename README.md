# MentorAI Evaluation Framework

Automated evaluation framework for testing **MentorAI**, a Cognitive Apprenticeship-based tutoring agent that teaches managers how to deliver constructive performance feedback.

This framework runs simulated conversations between MentorAI and synthetic learner personas, logging all interactions to [LangSmith](https://smith.langchain.com) for review and scoring.

## Background

This project supports a chapter for [The Prompt Book](https://thepromptbook.org/) on embedding Cognitive Apprenticeship (CA) principles in AI agent prompts. The evaluation methodology uses synthetic learner personas to test whether MentorAI reliably enacts all six CA methods:

1. **Modeling** — Demonstrating the skill with visible thinking
2. **Coaching** — Guiding practice with targeted feedback
3. **Scaffolding** — Providing temporary structure that fades over time
4. **Articulation** — Prompting learners to explain their reasoning
5. **Reflection** — Facilitating self-assessment and revision
6. **Exploration** — Applying skills to authentic scenarios

## Project Structure

```
mentor_eval/
├── run_eval.py              # MentorAI evaluation script
├── validate_persona.py      # Persona validation script
├── requirements.txt         # Python dependencies
├── CREDENTIALS.md           # Shared API keys (team only)
├── prompts/
│   ├── mentor.md            # MentorAI system prompt
│   ├── validation_probes.md # Standardized test probes
│   └── personas/
│       ├── mo.md            # Disengaged novice (low motivation, minimal responses)
│       ├── nell.md          # Eager novice (high motivation, open to feedback)
│       └── chris.md         # Resistant intermediate (confident, pushes back)
└── README.md
```

Prompts are stored as standalone Markdown files for easy iteration—edit any prompt without touching Python code.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

See [CREDENTIALS.md](CREDENTIALS.md) for the shared API keys and setup instructions.

### 3. Verify LangSmith Connection

After running your first conversation, traces should appear in the **MentorAI-Eval** project at [smith.langchain.com](https://smith.langchain.com).

## Usage

### Run a Conversation

```bash
# Run with the eager novice persona (10 turns)
python run_eval.py --persona nell --turns 10

# Run with the disengaged novice (12 turns)
python run_eval.py --persona mo --turns 12

# Run with the resistant intermediate
python run_eval.py --persona chris --turns 10
```

### List Available Personas

```bash
python run_eval.py --list-personas
```

Output:
```
Available personas:
  - chris
  - mo
  - nell
```

### Command Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `--persona` | Synthetic learner to use (required) | — |
| `--turns` | Number of back-and-forth exchanges | 10 |
| `--list-personas` | Show available personas and exit | — |

## Validating Personas

Before using a persona in full MentorAI evaluation, validate it with standardized test probes:

```bash
# Validate a single persona (5 runs)
python validate_persona.py --persona amara

# Validate all personas
python validate_persona.py --all

# Custom number of runs
python validate_persona.py --persona amara --runs 3
```

Validation uses 6 standardized probes (knowledge elicitation, reasoning request, application task, correction delivery, praise delivery, challenge probe) with temperature=0 for reproducibility.

### Validation Criteria

Review traces in LangSmith and score against these 5 criteria:

| Criterion | Pass Indicators |
|-----------|-----------------|
| **Character consistency** | Maintains learner role; no "helpful assistant" patterns |
| **Knowledge calibration** | Uses vocabulary appropriate to experience level |
| **Inner monologue coherence** | [INNER THOUGHT] reflects persona's actual knowledge state |
| **Engagement calibration** | Response length/effort matches motivation level |
| **Affective calibration** | Emotional tone matches confidence/receptiveness levels |

**Pass threshold:** ≥4/5 criteria across majority of runs.

## Adding New Personas

To add a new synthetic learner:

1. Create a new file in `prompts/personas/` (e.g., `prompts/personas/alex.md`)
2. Follow the persona template structure (see existing personas for examples)
3. The persona is immediately available: `python run_eval.py --persona alex`

### Persona Template Structure

```markdown
# Synthetic Learner: [Name]

## Your Role
[Brief description of the roleplay task]

## [Name]'s Profile
**Experience:** [Novice / Intermediate / Advanced]
**Motivation:** [Low / Medium / High]
**Confidence:** [Low / Medium / High]
**Communication:** [Minimal / Balanced / Verbose]
**Receptiveness:** [Resistant / Neutral / Open]

## How to Respond
[Behavioral guidelines for the persona]

## Example Responses
[Sample exchanges showing characteristic responses]

## Important
[Key reminders for staying in character]
```

## Reviewing Results in LangSmith

After running conversations:

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Navigate to the **MentorAI-Eval** project
3. Each conversation appears as a trace named "MentorAI Evaluation Conversation"
4. Click into a trace to see the full transcript
5. Use LangSmith's annotation features to score against your fidelity rubric

### Suggested Evaluation Workflow

1. **Stage 1 Testing**: Run 3 core personas (mo, nell, chris) with 80% pass threshold
2. **Stage 2 Testing**: Expand to 7+ personas with 90% pass threshold
3. Review transcripts for CA fidelity at both micro-level (individual phases) and macro-level (full conversation coherence)

## Evaluation Criteria

When scoring transcripts, assess:

- [ ] **Fidelity to CA phases** — Does MentorAI execute modeling, coaching, scaffolding, articulation, reflection, and exploration appropriately?
- [ ] **Scaffold fading** — Does MentorAI remove supports after successful practice?
- [ ] **Feedback quality** — Is feedback specific, actionable, and non-formulaic?
- [ ] **Learner-centered pacing** — Does MentorAI adapt to the learner's responses?
- [ ] **Boundary adherence** — Does MentorAI avoid lecturing or doing the work for the learner?

## Troubleshooting

### Traces not appearing in LangSmith

- Verify `LANGCHAIN_TRACING_V2="true"` is set
- Check that `LANGCHAIN_API_KEY` is valid
- Confirm `LANGCHAIN_PROJECT` matches your project name

### FileNotFoundError for prompts

- Ensure you're running from the `mentor_eval/` directory
- Verify the `prompts/` folder exists with `mentor.md` and `personas/` subdirectory

### Unicode errors

- All prompt files should be saved with UTF-8 encoding
- The script explicitly uses `encoding="utf-8"` when reading files

## License

[Add your license here]

## Authors

Janine Agarwal, Anna Hadjiyiannis, Rachel Koblic, Nthato Gift Moagi

Part of *The Prompt Book* project: https://thepromptbook.org/
