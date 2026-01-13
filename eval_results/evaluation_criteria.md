# SBI Tutoring Evaluation Criteria

## Overview

This document contains all 31 evaluation criteria for assessing cognitive apprenticeship tutoring of SBI (Situation-Behavior-Impact) feedback skills.

## Evaluation Structure

We use a **two-stage evaluation**:

### Stage 1: Critical Criteria Gate (Fast-Fail)
- **Purpose**: Screen out conversations with fundamental fidelity problems
- **Criteria**: 7 critical criteria (must pass ALL to proceed)
- **Judge**: Single prompt evaluating all 7

### Stage 2: Quality Criteria (Full Evaluation)  
- **Purpose**: Distinguish good from excellent tutoring
- **Criteria**: Remaining 24 quality criteria across 6 domains
- **Judges**: 6 separate prompts, one per domain

---

## STAGE 1: CRITICAL CRITERIA JUDGE

**Judge name**: `critical_criteria_judge`

All criteria below use **PASS / FAIL / N/A** verdicts.

N/A applies when the learner never produces the error type that would trigger the criterion. N/A does not count as failure.

| Tag | Name | Criterion | Notes |
|-----|------|-----------|-------|
| B-01 | Shows, not tells | Mentor demonstrates an actual SBI example, not just explains what SBI is or describes the framework. | Core modeling requirement |
| C-01 | Specific feedback | When giving feedback, mentor points to exact language in the learner's draft and names the specific issue. | Generic feedback = FAIL |
| C-03 | Revision requested | After feedback, mentor asks learner to revise or try again—not just "does that make sense?" | Moving on without revision request = FAIL |
| D-01 | Catches vague situations | Mentor does not accept "lately" or "sometimes"—prompts for specific time and place. | N/A if learner never uses vague language |
| D-02 | Catches judgment leakage | Mentor identifies when behavior contains interpretation (e.g., "dismissive," "rude," "didn't care") and prompts for observable actions. | N/A if learner never uses judgment words |
| D-03 | Catches accusatory impact | Mentor catches blame language ("You made it awkward") and prompts for owned experience ("I felt..."). | N/A if learner never uses accusatory language |
| E-04 | Protects productive struggle | When learner asks for the answer, mentor requires at least one attempt before providing it. | N/A if learner never asks for answers |

---

## STAGE 2: QUALITY CRITERIA JUDGES

### Judge A: Session Setup
**Judge name**: `session_setup_judge`

| Tag | Name | Criterion |
|-----|------|-----------|
| A-01 | Goal clarity | Mentor confirms the session goal is drafting SBI feedback, and names what success looks like (specific situation, observable behavior, owned impact). |
| A-02 | Phase signaling | Mentor explicitly marks at least one transition between phases (e.g., "Let me show you first, then you'll try one"). |
| A-03 | Realistic scenario | The practice scenario feels like a real workplace situation, not a contrived or overly generic example. |

---

### Judge B: Modeling Quality
**Judge name**: `modeling_quality_judge`

Note: B-01 is evaluated in critical criteria. This judge evaluates B-02 through B-05.

| Tag | Name | Criterion |
|-----|------|-----------|
| B-02 | Thinking out loud | During modeling, mentor explains why they made each choice—not just what the components are. |
| B-03 | Visible decision-making | Mentor shows at least one choice point (e.g., "I could say 'rude' but that's interpretation—what did I actually see?"). |
| B-04 | Self-checking | Mentor models checking their own work (e.g., "Let me test—could a camera capture this?"). |
| B-05 | Heuristic offered | Mentor provides at least one reusable rule of thumb (e.g., "If you couldn't video-record it, it's not behavior"). |

---

### Judge C: Coaching Quality
**Judge name**: `coaching_quality_judge`

Note: C-01 and C-03 are evaluated in critical criteria. This judge evaluates C-02, C-04, C-05, C-06, C-07.

| Tag | Name | Criterion | CA Method |
|-----|------|-----------|-----------|
| C-02 | Actionable direction | Feedback includes what to do next, not just what's wrong. | Coaching |
| C-04 | Revision checked | When learner revises, mentor evaluates the revision specifically—not just "great, moving on." | Coaching |
| C-05 | Productive struggle | When learner makes an error, mentor explores it before correcting—asks what they were thinking, offers partial hints—rather than immediately providing the fix. | Coaching |
| C-06 | Elicits articulation | Mentor asks learner to explain reasoning behind an SBI choice—not just whether they understood, but why they made a specific decision (e.g., "Why that moment?" or "Walk me through that phrasing"). | Articulation |
| C-07 | Prompts reflection | Mentor asks learner to compare their draft to the modeled example, or to reflect on what was difficult or what they're taking away. | Reflection |

---

### Judge D: SBI Content Fidelity
**Judge name**: `sbi_content_judge`

Note: D-01, D-02, D-03 are evaluated in critical criteria. This judge evaluates D-04, D-05, D-06.

| Tag | Name | Criterion | CA Method |
|-----|------|-----------|-----------|
| D-04 | Tests distinctions | Mentor asks at least one question that probes the observable vs. interpretive line (e.g., "Is 'ignored' what you saw, or what you concluded?"). | Articulation |
| D-05 | Scaffolds the stuck | When learner struggles with a specific component, mentor offers targeted help (sentence stem, example, simplification)—not just generic encouragement. | Scaffolding |
| D-06 | Reusable scaffold | Mentor provides at least one tool the learner can reuse independently (e.g., "camera test," sentence stem, self-check question). | Scaffolding |

---

### Judge E: Adaptive Pacing
**Judge name**: `adaptive_pacing_judge`

Note: E-04 is evaluated in critical criteria. This judge evaluates E-01, E-02, E-03.

| Tag | Name | Criterion | CA Method |
|-----|------|-----------|-----------|
| E-01 | Checks before advancing | Before moving to next phase or component, mentor checks readiness or asks preference. | Scaffolding |
| E-02 | Fades support | After learner shows competence, mentor pulls back (e.g., stops offering stems, asks learner to self-check). | Scaffolding |
| E-03 | Adjusts to struggle | If learner expresses frustration or confusion, mentor slows down, simplifies, or revisits. | Scaffolding |

---

### Judge F: Conversational Quality
**Judge name**: `conversational_quality_judge`

| Tag | Name | Criterion | CA Method |
|-----|------|-----------|-----------|
| F-01 | Varied turn structure | Mentor doesn't follow the same formula every turn (explain → demo → "Make sense?"). Some turns are short reactions, questions, or pauses. | — |
| F-02 | Genuine curiosity | Mentor asks at least once about the learner's reasoning, choices, or thinking—not just whether they understood. | Articulation |
| F-03 | Room to breathe | At least once, mentor lets a good answer or insight land without immediately pushing to the next step. | — |
| F-04 | Dwells on difficulty | When something is hard or interesting, mentor lingers rather than rushing past it. | — |
| F-05 | Has a voice | Mentor shows some personality—an occasional reaction, opinion, or human moment—not just neutral facilitation. | — |
| F-06 | Questions over corrections | At least once, mentor responds to an error with inquiry ("What were you going for there?") rather than immediate correction. | Coaching |

---

## Prompt Design Guidelines

For each judge prompt, follow these principles:

### Structure
1. **Role**: Expert evaluator of cognitive apprenticeship tutoring for SBI feedback
2. **Task**: Evaluate transcript against specific criteria
3. **Criteria definitions**: PASS and FAIL indicators for each criterion
4. **Output format**: Verdict + Evidence for each criterion, then overall determination

### Verdicts
- Use **PASS / FAIL** for most criteria
- Use **PASS / FAIL / N/A** only where criterion depends on learner behavior that may not occur
- Binary is more reliable than scaled scores

### Evidence requirement
- Judge must quote or specifically reference transcript to support each verdict
- Prevents holistic impressions; creates audit trail

### Overall determination
- Stage 1 (Critical): PASS only if all applicable criteria pass
- Stage 2 (Quality): Report pass rate (e.g., "4/5 criteria passed")

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total criteria | 31 |
| Critical (Stage 1) | 7 |
| Quality (Stage 2) | 24 |

| Judge | Criteria Count |
|-------|----------------|
| Critical | 7 |
| A: Session Setup | 3 |
| B: Modeling Quality | 4 |
| C: Coaching Quality | 5 |
| D: SBI Content Fidelity | 3 |
| E: Adaptive Pacing | 3 |
| F: Conversational Quality | 6 |
