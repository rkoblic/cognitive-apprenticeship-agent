# Criterion Analysis Template

Use this template when doing a deep-dive analysis on a specific evaluation criterion. See `docs/e-02-analysis.md` for a completed example.

---

## 1. Identify the Criterion

**Criterion code**: [e.g., E-02]
**Criterion name**: [e.g., Fades Support]
**Judge file**: `prompts/judges/[judge_name].md`

Copy the exact PASS/FAIL criteria from the judge prompt:

> **PASS**: [paste criteria]
> **FAIL**: [paste criteria]

---

## 2. Get the Data

### Overall pass/fail rate

```python
python3 -c "
import json
from pathlib import Path

CRITERION = 'E-02'  # Change this

runs_dir = Path('eval_results/runs')
conversations = []

for manifest_path in sorted(runs_dir.glob('*/manifest.json')):
    run_id = manifest_path.parent.name
    if run_id[:8] < '20260121':  # Date filter
        continue
    try:
        data = json.loads(manifest_path.read_text())
        conversations.extend(data.get('conversations', []))
    except:
        pass

# Dedupe by langsmith_id
seen = {}
for conv in conversations:
    lid = conv.get('langsmith_id')
    if lid and lid not in seen:
        seen[lid] = conv

# Count results
passes = fails = 0
for conv in seen.values():
    for judge, result in conv.get('quality_results', {}).items():
        if result.get('json') and result['json'].get('criteria'):
            criteria = result['json']['criteria']
            if CRITERION in criteria:
                if criteria[CRITERION].get('verdict') == 'PASS':
                    passes += 1
                elif criteria[CRITERION].get('verdict') == 'FAIL':
                    fails += 1

total = passes + fails
print(f'{CRITERION}: {passes}/{total} passed ({round(passes/total*100, 1)}%)')
print(f'Failures: {fails}')
"
```

### Pass/fail by persona

```python
python3 -c "
import json
from pathlib import Path
from collections import Counter

CRITERION = 'E-02'  # Change this

runs_dir = Path('eval_results/runs')
conversations = []

for manifest_path in sorted(runs_dir.glob('*/manifest.json')):
    run_id = manifest_path.parent.name
    if run_id[:8] < '20260121':
        continue
    try:
        data = json.loads(manifest_path.read_text())
        conversations.extend(data.get('conversations', []))
    except:
        pass

seen = {}
for conv in conversations:
    lid = conv.get('langsmith_id')
    if lid and lid not in seen:
        seen[lid] = conv

total_by_persona = Counter()
pass_by_persona = Counter()
fail_by_persona = Counter()

for conv in seen.values():
    persona = conv.get('persona', 'Unknown')
    total_by_persona[persona] += 1

    for judge, result in conv.get('quality_results', {}).items():
        if result.get('json') and result['json'].get('criteria'):
            criteria = result['json']['criteria']
            if CRITERION in criteria:
                if criteria[CRITERION].get('verdict') == 'PASS':
                    pass_by_persona[persona] += 1
                elif criteria[CRITERION].get('verdict') == 'FAIL':
                    fail_by_persona[persona] += 1

print('| Persona | Total | Pass | Fail | Fail Rate |')
print('|---------|-------|------|------|-----------|')
for p in ['amara_SBI', 'bailey_SBI', 'carlos_SBI', 'daniel_SBI', 'elise_SBI', 'fatou_SBI']:
    t = total_by_persona.get(p, 0)
    ps = pass_by_persona.get(p, 0)
    f = fail_by_persona.get(p, 0)
    ev = ps + f
    rate = f'{round(f/ev*100, 1)}%' if ev > 0 else 'N/A'
    print(f'| {p} | {t} | {ps} | {f} | {rate} |')
"
```

### List all failures with evidence

```python
python3 -c "
import json
from pathlib import Path

CRITERION = 'E-02'  # Change this

runs_dir = Path('eval_results/runs')
conversations = []

for manifest_path in sorted(runs_dir.glob('*/manifest.json')):
    run_id = manifest_path.parent.name
    if run_id[:8] < '20260121':
        continue
    try:
        data = json.loads(manifest_path.read_text())
        conversations.extend(data.get('conversations', []))
    except:
        pass

seen = {}
for conv in conversations:
    lid = conv.get('langsmith_id')
    if lid and lid not in seen:
        seen[lid] = conv

for conv in seen.values():
    for judge, result in conv.get('quality_results', {}).items():
        if result.get('json') and result['json'].get('criteria'):
            criteria = result['json']['criteria']
            if CRITERION in criteria and criteria[CRITERION].get('verdict') == 'FAIL':
                print(f\"ID: {conv.get('short_id')} | Persona: {conv.get('persona', 'Unknown')}\")
                print(f\"Evidence: {criteria[CRITERION].get('evidence', 'N/A')[:200]}...\")
                print()
"
```

---

## 3. Find Example Transcripts

### Locate a specific conversation

```python
python3 -c "
import json
from pathlib import Path

SHORT_ID = 'xxxxxxxx'  # First 8 chars of conversation ID

runs_dir = Path('eval_results/runs')
for manifest_path in sorted(runs_dir.glob('*/manifest.json')):
    run_id = manifest_path.parent.name
    if run_id[:8] < '20260121':
        continue
    try:
        data = json.loads(manifest_path.read_text())
        for conv in data.get('conversations', []):
            if conv.get('short_id') == SHORT_ID:
                print(f'Run: {run_id}')
                print(f'LangSmith ID: {conv.get(\"langsmith_id\")}')
                print(f'Persona: {conv.get(\"persona\")}')
    except:
        pass
"
```

### Find transcript files

```bash
# List all transcripts for a persona
ls conversations/*/*.md | grep bailey

# Find transcripts by date
ls conversations/20260122_*/*.md
```

Transcripts are stored as: `conversations/{batch_timestamp}/{conversation_timestamp}_{persona}.md`

---

## 4. Analysis Structure

### A. Failing Example
Pick a clear failure case. Document:
1. **Context**: What phase of the conversation?
2. **What the learner did**: Quote the relevant learner turn
3. **What the mentor did wrong**: Quote the mentor response
4. **What should have happened**: Write an example of correct behavior

### B. Passing Example (same persona)
Find a conversation with the same persona that PASSED. Document:
1. **What's different**: How did the mentor behave differently?
2. **Key contrast**: Side-by-side comparison of responses

Using the same persona controls for learner behavior and isolates mentor differences.

### C. Persona Patterns
If certain personas fail more often, analyze why:
- What characteristics trigger the failure?
- What is the mentor prompt saying that conflicts?
- Why might the LLM prioritize one instruction over another?

---

## 5. Root Cause Hypotheses

Common patterns to check:

1. **Position in prompt**: Is the relevant guidance buried or prominent?
2. **Negative vs positive framing**: Does the prompt say what NOT to do without showing what TO do?
3. **Conflicting instructions**: Do other parts of the prompt encourage the opposite behavior?
4. **Missing examples**: Would contrastive examples help the model recognize the pattern?
5. **Ambiguous language**: Are key terms like "feedback" or "scaffolding" clearly defined?
6. **Default model behavior**: Does the failure align with typical LLM tendencies (being helpful, verbose, etc.)?

---

## 6. Proposed Fixes

For each fix, specify:
- **What to change**: Exact location and content
- **Why it should work**: Which root cause it addresses
- **Risk level**: Low (additive) / Medium (modifies existing) / High (restructures)
- **How to test**: Number of conversations, which personas

Prioritize fixes that are:
1. Low risk (additive rather than restructuring)
2. Address the most likely root cause
3. Easy to measure

---

## 7. Document Template

```markdown
# [Criterion Code] Analysis: [Criterion Name]

## Executive Summary
- X of Y conversations (Z%) failed [criterion]
- Root issue: [one sentence]
- The prompt [has/lacks] guidance for this

## The Criterion
[Quote from judge prompt]

## Current State
[Table with pass/fail by persona]

## Example Analysis
### Failing Example: [persona] ([conversation_id])
[Annotated walkthrough]

### Passing Example: [persona] ([conversation_id])
[Annotated walkthrough showing correct behavior]

### Key Contrast
[Side-by-side comparison]

## Persona-Specific Analysis
[If applicable - why certain personas fail more]

## Root Cause Analysis
[Hypotheses for why the LLM isn't following guidance]

## Potential Fixes
[Prioritized list with rationale]

## Next Steps
[Testing plan]

## TL;DR
[4-5 bullet summary]

## Appendix: All Failures
[Table with ID, persona, evidence summary]
```

---

## 8. After Analysis

1. **Save the analysis**: `docs/[criterion]-analysis.md`
2. **Update REVISION_NOTES.md** if you implement fixes: `prompts/personas/REVISION_NOTES.md`
3. **Track in dashboard**: Run new evaluations and compare pass rates
