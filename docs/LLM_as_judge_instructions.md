# How to Run the Critical Criteria Evaluator

## Step 1: Install Dependencies

Open your terminal and run:

```bash
pip install langsmith langchain langchain-anthropic
```

## Step 2: Set Environment Variables

You need two API keys. In your terminal:

```bash
export LANGSMITH_API_KEY='your-langsmith-api-key'
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

**Where to find these:**
- **LangSmith**: Go to smith.langchain.com → Settings → API Keys
- **Anthropic**: Go to console.anthropic.com → API Keys

**Note**: These only last for your current terminal session. To make them permanent, add them to your `~/.bashrc` or `~/.zshrc` file.

## Step 3: Configure the Script

Open `run_critical_eval.py` and edit the configuration section near the top:

```python
# LangSmith settings
LANGSMITH_PROJECT = "MentorAI-Eval"  # <-- Change this

# Filter settings
RUN_NAME_FILTER = None  # e.g., "tutor_conversation" if your runs have names
TAG_FILTER = None       # e.g., "sbi_eval" if you've tagged runs
LIMIT = 10              # Start small for testing
```

**To find your project name**: Go to LangSmith → Projects → copy the exact project name.

## Step 4: Check Your Transcript Format

The script needs to know how your conversations are stored in LangSmith. Look at the `format_run_as_transcript()` function.

**To see how your data is structured:**

```python
from langsmith import Client
client = Client()

# Get one run and inspect it
runs = list(client.list_runs(project_name="your-project-name", limit=1))
run = runs[0]

print("Inputs:", run.inputs)
print("Outputs:", run.outputs)
```

Then adjust `format_run_as_transcript()` to extract the conversation from wherever it lives.

## Step 5: Check Your Inner Monologue Format

The script tries to strip these patterns:
- `[INNER THOUGHT] ... `
- `<inner_thought> ... </inner_thought>`
- `*thinking* ... *end thinking*`

If your synthetic learners use a different format, edit the `strip_inner_monologue()` function.

## Step 6: Run a Test

Start with just 2-3 conversations:

```bash
python run_critical_eval.py
```

The script will:
1. Connect to LangSmith
2. Fetch your conversations
3. Strip inner monologue
4. Run each through the judge
5. Save results to `eval_results/` folder

## Step 7: Review Results

Open the markdown files in `eval_results/`. For each one, check:

1. **Does the transcript look right?** (Inner monologue stripped, conversation intact)
2. **Do you agree with each verdict?** 
3. **Is the evidence accurate?** (Did the judge quote real parts of the transcript?)

If the judge disagrees with your assessment, note which criteria and why. This tells you if the prompt needs refinement.

## Step 8: Scale Up

Once you trust the judge on a few conversations:

```python
LIMIT = 100  # Or however many you have
```

Run again to evaluate your full dataset.

---

## Troubleshooting

### "No runs found"
- Double-check your project name (case-sensitive)
- Try removing filters first to see all runs
- Make sure the runs have completed (not still running)

### "Transcript seems too short"
- Your conversation data is stored differently than expected
- Use the inspection code in Step 4 to see the actual structure
- Update `format_run_as_transcript()` accordingly

### "Error during evaluation"
- Usually an API issue—check your Anthropic key
- Could be rate limiting—add a `time.sleep(1)` between runs

### Inner monologue not stripped
- Check what format your learners actually use
- Print `raw_transcript` vs `clean_transcript` to compare
- Update the regex patterns in `strip_inner_monologue()`

---

## Next Steps After Manual Review

Once you've validated the judge works:

1. **Track disagreements**: Where you disagree with the judge, note why
2. **Refine criteria definitions**: If a criterion is ambiguous, sharpen the PASS/FAIL descriptions
3. **Add JSON output**: For automated pipelines, add structured output parsing
4. **Build the full evaluation**: Create the 6 domain-specific prompts for quality criteria
