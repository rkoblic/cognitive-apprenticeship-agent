---
judge_id: session_setup
stage: 2
criteria_count: 3
criteria_tags: [A-01, A-02, A-03]
verdict_type: pass_fail
pass_threshold: report_rate
---

# Session Setup Evaluation

## Role

You are an expert evaluator of cognitive apprenticeship tutoring for SBI (Situation-Behavior-Impact) feedback skills. Your task is to evaluate how well the mentor sets up and frames the tutoring session.

## Task

Review the tutoring transcript below and evaluate whether the mentor meets each of the 3 session setup criteria. These criteria assess whether the mentor establishes clear goals, signals phase transitions, and uses realistic practice scenarios.

## Criteria

Evaluate each criterion as PASS or FAIL. A criterion only passes if there is clear evidence in the transcript.

### A-01: Goal Clarity
- **PASS**: Mentor confirms the session goal is drafting SBI feedback, and names what success looks like (specific situation, observable behavior, owned impact).
- **FAIL**: Mentor jumps into the task without clarifying the goal, or only vaguely mentions "feedback" without specifying success criteria.

### A-02: Phase Signaling
- **PASS**: Mentor explicitly marks at least one transition between phases (e.g., "Let me show you first, then you'll try one" or "Now it's your turn to practice").
- **FAIL**: Mentor moves between modeling, practice, and coaching without signaling the shift, leaving the learner uncertain about what phase they're in.

### A-03: Realistic Scenario
- **PASS**: The practice scenario feels like a real workplace situation—specific enough to be believable, with plausible interpersonal dynamics.
- **FAIL**: The scenario is contrived, overly generic (e.g., "a coworker did something"), or feels like an obvious teaching example rather than a real situation.

## Output Format

You must provide your evaluation in two formats:

### 1. JSON Output (Required)

First, output a JSON block with your structured evaluation:

```json
{{
  "criteria": {{
    "A-01": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "A-02": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "A-03": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}}
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

### A-01: Goal Clarity
**Verdict**:
**Evidence**:

### A-02: Phase Signaling
**Verdict**:
**Evidence**:

### A-03: Realistic Scenario
**Verdict**:
**Evidence**:

---

## Summary

**Passed**: X/3 criteria
**Failed Criteria**: [List any failed criteria, or "None"]
