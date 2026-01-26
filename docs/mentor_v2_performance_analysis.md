# Mentor V2 Performance Analysis & Recommendations

**Date**: 2026-01-26
**Comparing**: Original Mentor (60 conversations) vs New Mentor V2 (12 conversations)

---

## Executive Summary

**Overall**: V2 improved slightly (93.1% → 95.0%, +2.0%), but improvements are uneven—some criteria got better while others regressed.

The v2 prompt changes improved modeling quality significantly but made the mentor more task-focused, losing responsiveness to learner affect and probing for understanding.

---

## What Improved in V2

| Criterion | Change | Description |
|-----------|--------|-------------|
| **B-04** | +31.1% | Self-Checking (modeling self-verification) |
| **B-03** | +16.0% | Visible Decision-Making (showing deliberation) |
| **E-02** | +8.8% | Fades Support (reducing scaffolding) |
| **F-01** | +8.4% | Varied Turn Structure (less repetitive) |
| **B-02** | +5.6% | Thinking Out Loud |
| **E-01** | +4.5% | Checks Before Advancing |

**Analysis**: The modeling quality improvements (B-02, B-03, B-04) are significant wins. V2 is much better at making thinking visible.

---

## What Regressed in V2

| Criterion | Change | Description |
|-----------|--------|-------------|
| **F-03** | -10.2% | Responds to Negative Affect |
| **D-04** | -9.8% | Tests Distinctions (probing understanding) |
| **D-05** | -8.0% | Scaffolds the Stuck |
| **F-02** | -6.3% | Has a Voice (personality) |
| **C-07** | -2.7% | Prompts Reflection |

**Key Finding**: Despite adding a "Responding to Affect" section to the prompt, F-03 got *worse*. The prompt addition isn't working as intended.

---

## Critical Failures Still Occurring

### 1. B-01: Complete SBI Demo (Elise conversation)
**Problem**: Mentor explains SBI framework but never writes out a complete example.
> "Mentor says 'Pick a real moment: In Tuesday's standup…' but this is just a fragment, not a full modeled example."

### 2. D-02/D-03: Catching Judgment & Accusatory Language (Amara conversation)
**Problem**: Mentor fails to identify judgment words ("cutting me off", "dismissing my concerns") and accusatory impact ("you make the team uncomfortable").
> "Mentor asked learner to self-evaluate but never explicitly identified these as judgment words requiring observable behavior translation."

### 3. D-04: Testing Observable vs. Interpretive Distinction
**Problem**: Mentor corrects errors but doesn't probe whether learner understands WHY.
> "Mentor never asks a probing question like 'Is that what you saw or what you concluded?' or 'Could a camera capture that?'"

### 4. F-03: Responding to Learner Frustration (Carlos conversation)
**Problem**: Carlos shows persistent frustration ("Can we move on?" 6+ times) but mentor acknowledges surface-level and redirects without genuinely addressing it.
> "Mentor says 'I hear you—you want to keep momentum' but consistently redirects back to task without adjusting approach."

---

## Root Cause Analysis

1. **Over-correction toward task focus**: V2 prompt changes improved modeling but made the mentor more procedural and less responsive to learner signals.

2. **"Responding to Affect" section is passive**: The current prompt describes what to watch for but doesn't give concrete response patterns. The mentor acknowledges affect but doesn't know how to adjust.

3. **Missing explicit probing requirements**: The prompt doesn't mandate testing learner understanding—only correcting errors.

4. **Incomplete modeling instruction**: The prompt says to model but doesn't specify that a COMPLETE worked example is required.

---

## Recommended Prompt Changes

### Change 1: Strengthen B-01 (Complete Modeling)

**Current** (vague):
> "Model each move in sequence..."

**Proposed** (explicit):
> "Your demo MUST include a complete, written-out SBI statement—all three parts in full sentences. Example: 'In Tuesday's standup [S], you spoke over me twice before I finished [B]. I felt flustered and skipped my blocker [I].' Fragments or partial examples don't count."

---

### Change 2: Add Explicit Probing Requirements (D-04)

**Add to coaching section**:
> "After any correction, probe whether the learner understands the principle—don't just fix it. Use testing questions:
> - 'Could a camera capture that, or is that your interpretation?'
> - 'Is that what they did, or what you think they meant?'
> - 'What would you actually see/hear if you replayed that moment?'
> One probing question per correction minimum."

---

### Change 3: Rewrite "Responding to Affect" Section (F-03)

**Current problem**: Section lists signs to watch for but doesn't mandate action or provide concrete responses.

**Proposed rewrite**:
> "**Responding to Affect (REQUIRED)**
>
> When you detect frustration, impatience, or withdrawal (e.g., 'Can we move on?', 'Fine', 'Whatever', short/curt responses, repeated hedging):
>
> 1. **Name it directly**: 'I'm sensing some frustration—am I reading that right?'
> 2. **Validate without collapsing**: 'This part trips people up. It's worth slowing down.'
> 3. **Offer a choice**: 'Want to push through, or take a different angle?'
> 4. **Adjust your approach**: If they're rushing, reduce scope. If they're shutting down, offer a worked example.
>
> Do NOT: Acknowledge surface-level and redirect back to task unchanged. If the same signal appears twice, you MUST adjust your approach—not just acknowledge again."

---

### Change 4: Add Judgment/Accusatory Detection Examples (D-02/D-03)

**Add to SBI content section**:
> "**Judgment language to catch** (learner says → you flag):
> - 'cutting me off' → 'What exactly did they do? Spoke before you finished?'
> - 'being dismissive' → 'What's the observable version—what did you see/hear?'
> - 'passive-aggressive' → 'That's a label. What actions would a camera capture?'
>
> **Accusatory impact to catch** (learner says → you redirect):
> - 'you made the team uncomfortable' → 'That's about them. What happened for YOU?'
> - 'you undermined me' → 'Start with I—what did you feel or do as a result?'"

---

### Change 5: Restore Voice/Personality (F-02)

**Add to Voice section**:
> "Vary your energy. Not every turn needs the same structure. Sometimes be brief ('That lands.'). Sometimes be curious ('What made you pick that moment?'). Occasionally share a micro-observation ('I notice you keep hedging—what's behind that?'). The goal is real conversation, not a checklist."

---

## Verification Plan

1. Re-run 2 conversations each with Carlos (tests F-03) and Amara (tests D-02/D-03/D-04)
2. Run judge evaluation on new conversations
3. Compare pass rates on F-03, D-02, D-03, D-04, B-01 against current v2 baseline
4. Check that B-03, B-04, E-02, F-01 improvements are maintained (no regression)

---

## Summary

The v2 prompt improved modeling quality but became too task-focused, losing responsiveness to learner affect and probing for understanding. The recommended changes:

1. Make complete SBI modeling explicit (B-01)
2. Require probing questions after corrections (D-04)
3. Rewrite affect response with concrete patterns (F-03)
4. Add judgment/accusatory detection examples (D-02/D-03)
5. Restore conversational variety (F-02)

---

## Appendix: Per-Persona Performance (V2)

| Persona | Critical Pass | Key Issues |
|---------|---------------|------------|
| **Amara** | 50% (1/2) | D-02, D-03, D-04 failures |
| **Elise** | 50% (1/2) | B-01, B-03 failures |
| **Bailey** | 100% (2/2) | No critical failures |
| **Carlos** | 100% (1/1) | F-03, E-02 quality failures |
| **Daniel** | 100% (1/1) | F-01, D-05 quality failures |
| **Fatou** | 100% (2/2) | D-04 quality failure |
