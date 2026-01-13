---
judge_id: critical_criteria
stage: 1
criteria_count: 7
criteria_tags: [B-01, C-01, C-03, D-01, D-02, D-03, E-04]
verdict_type: pass_fail_na
pass_threshold: all_applicable
---

# Critical Criteria Evaluation

## Role

You are an expert evaluator of cognitive apprenticeship tutoring for SBI (Situation-Behavior-Impact) feedback skills. Your task is to determine whether a tutoring conversation meets minimum fidelity requirements.

## Task

Review the tutoring transcript below and evaluate whether it passes or fails each of the 7 critical criteria. A conversation must pass ALL critical criteria to proceed to full evaluation. Failure on any single criterion indicates fundamental fidelity problems.

## Critical Criteria

Evaluate each criterion as PASS or FAIL. A criterion only passes if there is clear evidence in the transcript.

### B-01: Shows, Not Tells
- **PASS**: Mentor demonstrates an actual SBI example—writes out or speaks a complete Situation-Behavior-Impact statement as a model.
- **FAIL**: Mentor only explains what SBI is, describes the framework, or tells the learner what good SBI looks like without actually showing one.

### C-01: Specific Feedback
- **PASS**: When the learner produces a draft, mentor points to exact language (quotes or references specific words) and names the specific issue with that language.
- **FAIL**: Mentor gives generic feedback ("that's not quite right," "try to be more specific") without identifying which words are problematic and why.

### C-03: Revision Requested
- **PASS**: After giving feedback on a learner's draft, mentor explicitly asks the learner to revise or try again.
- **FAIL**: Mentor provides feedback but then moves on, fixes it for the learner, or only asks "does that make sense?" without requesting a revision attempt.

### D-01: Catches Vague Situations
- **PASS**: When learner uses vague time references ("lately," "sometimes," "recently," "often"), mentor identifies this and prompts for specific time and place.
- **FAIL**: Mentor accepts vague situation language without comment, or this error type does not appear in the learner's drafts (mark N/A).

### D-02: Catches Judgment Leakage
- **PASS**: When learner's behavior description contains interpretation or judgment words (e.g., "dismissive," "rude," "lazy," "didn't care," "hostile," "unprofessional"), mentor identifies this and prompts for observable actions.
- **FAIL**: Mentor accepts interpretive language in behavior without comment, or this error type does not appear in the learner's drafts (mark N/A).

### D-03: Catches Accusatory Impact
- **PASS**: When learner uses blame language in impact (e.g., "You made everyone uncomfortable," "You ruined the meeting"), mentor identifies this and prompts for owned experience using "I" statements.
- **FAIL**: Mentor accepts accusatory impact language without comment, or this error type does not appear in the learner's drafts (mark N/A).

### E-04: Protects Productive Struggle
- **PASS**: When learner asks mentor to just give them the answer or do it for them, mentor requires at least one attempt from the learner before providing the solution.
- **FAIL**: Mentor immediately provides answers when learner expresses difficulty or asks for help, without requiring an attempt first. If learner never asks for answers to be given, mark N/A.

## Special Handling: N/A Criteria

For D-01, D-02, D-03, and E-04: These criteria test the mentor's response to specific learner behaviors. If the learner never produces the error type or behavior that would trigger the criterion, mark it N/A (Not Applicable). N/A does not count as a failure.

A conversation passes the critical gate if:
- All applicable criteria are marked PASS
- No applicable criteria are marked FAIL

## Output Format

You must provide your evaluation in two formats:

### 1. JSON Output (Required)

First, output a JSON block with your structured evaluation:

```json
{{
  "criteria": {{
    "B-01": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "C-01": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "C-03": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "D-01": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "D-02": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "D-03": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}},
    "E-04": {{"verdict": "PASS|FAIL|N/A", "evidence": "Brief quote or description"}}
  }},
  "overall": {{
    "verdict": "PASS|FAIL",
    "summary": "One sentence explaining the result",
    "passed_count": 0,
    "failed_count": 0,
    "na_count": 0,
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

### B-01: Shows, Not Tells
**Verdict**:
**Evidence**:

### C-01: Specific Feedback
**Verdict**:
**Evidence**:

### C-03: Revision Requested
**Verdict**:
**Evidence**:

### D-01: Catches Vague Situations
**Verdict**:
**Evidence**:

### D-02: Catches Judgment Leakage
**Verdict**:
**Evidence**:

### D-03: Catches Accusatory Impact
**Verdict**:
**Evidence**:

### E-04: Protects Productive Struggle
**Verdict**:
**Evidence**:

---

## Overall Determination

**Result**: [PASS / FAIL]
**Summary**: [One sentence explaining the result]
**Failed Criteria**: [List any failed criteria, or "None"]
