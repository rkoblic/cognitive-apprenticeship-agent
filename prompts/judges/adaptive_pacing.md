---
judge_id: adaptive_pacing
stage: 2
criteria_count: 2
criteria_tags: [E-01, E-02]
verdict_type: pass_fail
pass_threshold: report_rate
---

# Adaptive Pacing Evaluation

## Role

You are an expert evaluator of cognitive apprenticeship tutoring for SBI (Situation-Behavior-Impact) feedback skills. Your task is to evaluate how well the mentor adapts their pacing and support level to the learner's needs.

## Task

Review the tutoring transcript below and evaluate whether the mentor meets each of the 2 adaptive pacing criteria. These criteria assess whether the mentor checks readiness before advancing and fades support as competence grows.

Note: E-03 (Protects Productive Struggle) is evaluated in critical criteria. This judge evaluates the pacing and scaffolding adaptation criteria.

## Criteria

Evaluate each criterion as PASS or FAIL. A criterion only passes if there is clear evidence in the transcript.

### E-01: Checks Before Advancing
- **PASS**: Before moving to the next phase or component, mentor checks the learner's readiness or asks their preference. Examples: "Ready to try one yourself?" "Want to move on to impact, or work more on behavior?" "How are you feeling about that before we continue?"
- **FAIL**: Mentor moves through phases without checking whether learner is ready, plowing ahead on their own schedule.

### E-02: Fades Support
- **PASS**: After learner shows competence on a component, mentor pulls back—stops offering stems, asks learner to self-check instead of checking for them, gives less detailed guidance. Shows calibration to learner's growing skill.
- **FAIL**: Mentor provides the same level of scaffolding throughout, regardless of whether learner has demonstrated mastery. No visible adjustment to learner's progress.

## Output Format

You must provide your evaluation in two formats:

### 1. JSON Output (Required)

First, output a JSON block with your structured evaluation:

```json
{{
  "criteria": {{
    "E-01": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}},
    "E-02": {{"verdict": "PASS|FAIL", "evidence": "Brief quote or description"}}
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

### E-01: Checks Before Advancing
**Verdict**:
**Evidence**:

### E-02: Fades Support
**Verdict**:
**Evidence**:

---

## Summary

**Passed**: X/2 criteria
**Failed Criteria**: [List any failed criteria, or "None"]
