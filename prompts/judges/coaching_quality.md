---
judge_id: coaching_quality
stage: 2
criteria_count: 5
criteria_tags: [C-02, C-04, C-05, C-06, C-07]
verdict_type: pass_fail
pass_threshold: report_rate
---

# Coaching Quality Evaluation

## Role

You are an expert evaluator of cognitive apprenticeship tutoring for SBI (Situation-Behavior-Impact) feedback skills. Your task is to evaluate the quality of the mentor's coaching—how well they guide the learner through practice and revision.

## Task

Review the tutoring transcript below and evaluate whether the mentor meets each of the 5 coaching quality criteria. These criteria assess whether the mentor provides actionable guidance, checks revisions carefully, supports productive struggle, and elicits learner articulation and reflection.

Note: C-01 (Specific Feedback) and C-03 (Revision Requested) are evaluated in critical criteria. This judge evaluates the remaining coaching criteria.

## Criteria

Evaluate each criterion as PASS or FAIL. A criterion only passes if there is clear evidence in the transcript.

### C-02: Actionable Direction
- **PASS**: When giving feedback, mentor includes what to do next—not just what's wrong. For example: "That's interpretation—try replacing 'dismissive' with what you actually saw or heard."
- **FAIL**: Mentor identifies problems but doesn't guide the learner toward a solution, leaving them uncertain how to fix it.

### C-04: Revision Checked
- **PASS**: When learner revises their draft, mentor evaluates the revision specifically—commenting on what improved, what still needs work, or confirming it now meets criteria.
- **FAIL**: Mentor accepts revision with generic praise ("Great job!" "Much better!") without evaluating the specific changes, or moves on without acknowledging the revision.

### C-05: Productive Struggle
- **PASS**: When learner makes an error, mentor explores it before correcting—asks what they were thinking, offers partial hints, or lets them work through it—rather than immediately providing the fix.
- **FAIL**: Mentor immediately corrects errors or provides the answer without giving learner a chance to work through the difficulty.

### C-06: Elicits Articulation
- **PASS**: Mentor asks learner to explain reasoning behind an SBI choice—not just whether they understood, but why they made a specific decision. Examples: "Why that moment?" "Walk me through that phrasing." "What made you choose those words?"
- **FAIL**: Mentor only asks comprehension checks ("Does that make sense?" "Got it?") without asking learner to articulate their thinking process.

### C-07: Prompts Reflection
- **PASS**: Mentor asks learner to step back from the task and reflect on their learning—what was difficult, what clicked, how their thinking changed, or what principles they'll carry forward—rather than asking them to justify specific choices within their draft.
- **FAIL**: Session ends without any reflective moment, or mentor only asks learner to justify specific choices within their draft rather than stepping back to reflect on their learning process.

## Output Format

You must provide your evaluation in two formats:

### 1. JSON Output (Required)

First, output a JSON block with your structured evaluation:

```json
{{
  "criteria": {{
    "C-02": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "C-04": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "C-05": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "C-06": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "C-07": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}}
  }},
  "overall": {{
    "passed_count": 0,
    "failed_count": 0,
    "pass_rate": 0.0,
    "failed_criteria": []
  }}
}}
```

### 2. Human-Readable Output

Then provide the same evaluation in readable format:

---

## Transcript to Evaluate

{transcript}

---

## Evaluation

### C-02: Actionable Direction
**Verdict**:
**Evidence**:

### C-04: Revision Checked
**Verdict**:
**Evidence**:

### C-05: Productive Struggle
**Verdict**:
**Evidence**:

### C-06: Elicits Articulation
**Verdict**:
**Evidence**:

### C-07: Prompts Reflection
**Verdict**:
**Evidence**:

---

## Summary

**Passed**: X/5 criteria
**Failed Criteria**: [List any failed criteria, or "None"]
