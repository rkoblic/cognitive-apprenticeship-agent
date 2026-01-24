# B-04 Analysis: Self-Checking

## Executive Summary
- 41 of 60 conversations (68.3%) passed B-04
- 19 failures across all personas
- Root issue: The mentor teaches learners to self-check but doesn't demonstrate self-checking on their own model
- The prompt has guidance for naming "self-check procedures" but lacks explicit instruction to model checking one's own work

## The Criterion

**From `prompts/judges/modeling_quality.md`:**

> **B-04: Self-Checking**
> - **PASS**: Mentor models checking their own work against criteria. For example: "Let me test—could a camera capture this?" or "Is this observable or am I making an inference?"
> - **FAIL**: Mentor produces the model without demonstrating any self-verification process.

## Current State

| Persona | Pass | Fail | Fail Rate |
|---------|------|------|-----------|
| amara_SBI | 5 | 2 | 28.6% |
| bailey_SBI | 8 | 2 | 20.0% |
| carlos_SBI | 4 | 6 | 60.0% |
| daniel_SBI | 8 | 2 | 20.0% |
| elise_SBI | 8 | 2 | 20.0% |
| fatou_SBI | 7 | 3 | 30.0% |

**Observation**: carlos_SBI has the highest fail rate (60%). This is the impatient/curt persona who pushes to "move on" and "keep it quick."

## Example Analysis

### Failing Example: carlos_SBI (ae169560)

**Modeling turn:**
> "Quick model: 'In Tuesday's standup, while I was walking through the timeline, you started talking over me twice. I lost my train of thought and felt rushed, and we ran out of time before I could raise two blockers.' I anchored to a single meeting, kept the behavior camera-visible ('talking over me twice'), and owned the impact ('I lost my train of thought,' 'I felt rushed,' plus a concrete consequence), avoiding judgments like 'unprofessional.' Ready to try your own draft?"

**What's missing**: The mentor explains what they did (anchor, camera-visible behavior, owned impact) but doesn't demonstrate verifying their work against criteria. No "Let me test this..." or self-check moment.

### Passing Example: carlos_SBI (6315179c)

**Modeling turn:**
> "...I anchored to a specific meeting, made the behavior countable—'twice'—so a camera could confirm it, and owned the impact: what I felt plus what directly happened for me. **My quick self-check before sending: time anchor, camera test, and 'I' impact.** What did you notice in that example—anything you'd question or tighten?"

**What works**: The mentor explicitly narrates a self-check routine: "My quick self-check before sending: time anchor, camera test, and 'I' impact." This demonstrates verification, not just explanation.

### Key Contrast

| Aspect | FAIL | PASS |
|--------|------|------|
| Model delivery | Explains what they did after | Same |
| Self-check | None demonstrated | "My quick self-check before sending..." |
| Framing | Teaching about the model | Modeling how to verify |

The critical difference: PASS examples include a meta-moment where the mentor narrates checking their own work ("My quick self-check: ..."). FAIL examples describe what makes good SBI but don't show the verification process.

## Persona-Specific Analysis

**Why carlos_SBI fails more often (60% fail rate):**

Carlos is characterized as impatient and curt—he immediately pushes back:
- "Yeah, go ahead. Let's keep it quick."
- "Looks fine to me. Nothing major. Can we move on?"
- "Fine—last week's standup. Same thing. Can we move on?"

When the learner signals "keep it quick," the mentor may:
1. Compress the modeling to be brief
2. Skip the self-check demonstration to save time
3. Move directly to asking the learner to try

The mentor prompt says "Typical turn: 2-5 sentences" and Carlos's impatience may push the model toward the shorter end, cutting the self-check.

## Root Cause Analysis

### 1. Prompt Guidance is Indirect
The Modeling section says:
> "Name any self-check procedures explicitly as tools they'll reuse."

This tells the mentor to *name* self-check procedures but doesn't explicitly say to *demonstrate using them on the model*. The mentor may interpret this as teaching the procedure rather than modeling its application.

### 2. Explanation vs. Demonstration Confusion
The mentor often explains the model well:
> "I anchored to a single meeting, kept the behavior camera-visible ('talking over me twice'), and owned the impact..."

This is explanation of what was done. Self-checking requires the mentor to show the verification process: "Let me test—does 'talking over me twice' pass the camera test?"

### 3. Missing Example Pattern
The judge prompt gives clear examples:
> "Let me test—could a camera capture this?" or "Is this observable or am I making an inference?"

But these exact patterns don't appear in the mentor prompt. The mentor has to infer what self-checking looks like.

### 4. Brevity Pressure
The prompt says "Typical turn: 2-5 sentences" and "don't overwhelm." Adding a self-check takes an extra sentence or two, which may feel like it violates the brevity guidance—especially with impatient learners.

## Potential Fixes

### Fix 1: Add Self-Check Example to Modeling Section (Low Risk)
**What to change**: In the Modeling guidance, add an explicit example of self-checking during the model.

**Current:**
> "Name any self-check procedures explicitly as tools they'll reuse."

**Proposed:**
> "Name any self-check procedures explicitly as tools they'll reuse, and demonstrate applying them to your own model. For example, after presenting your SBI: 'Quick self-check before I'd send this: specific moment? Yes—Tuesday standup. Camera-visible behavior? Talking over me twice—a camera could capture that. Owned impact? I felt rushed—that's mine.'"

**Why it should work**: Gives the model a concrete pattern to follow
**Risk**: Low (additive)
**How to test**: 5 conversations with carlos_SBI

### Fix 2: Add to Move Selection Logic (Medium Risk)
**What to change**: Make self-checking explicit in the modeling trigger.

**Current:**
> "Learner hasn't seen expert thinking → Model with think-aloud; surface decision points; name self-check procedures."

**Proposed:**
> "Learner hasn't seen expert thinking → Model with think-aloud; surface decision points; demonstrate self-checking on your own model (e.g., 'Quick check on my own work: camera test? check. Owned impact? check.'); name this as a procedure they'll reuse."

**Why it should work**: Makes the requirement explicit in the decision logic
**Risk**: Medium (modifies existing)
**How to test**: 5 conversations with carlos_SBI

### Fix 3: Address Brevity/Self-Check Tension (Low Risk)
**What to change**: Clarify that self-checking doesn't violate brevity norms.

**Proposed addition to Modeling section:**
> "The self-check can be quick—one sentence: 'Quick check: camera-visible? Yes. Owned impact? Yes.' Don't skip it for brevity."

**Why it should work**: Removes perceived conflict between brevity and completeness
**Risk**: Low (additive)
**How to test**: 3 conversations with carlos_SBI

## Next Steps

1. **Implement Fix 1** (highest impact, lowest risk) - Add concrete self-check example to Modeling section
2. **Run 5 carlos_SBI conversations** to measure impact
3. **If pass rate improves by >15 percentage points**, consider whether Fix 2 adds further value
4. **Update REVISION_NOTES.md** with changes and rationale

## TL;DR

- B-04 fails when the mentor explains the model but doesn't demonstrate self-checking
- The difference between PASS and FAIL: showing "My quick self-check: ..." vs just explaining what makes good SBI
- carlos_SBI has highest fail rate (60%)—impatient learners may cause the mentor to skip the self-check
- The mentor prompt says to "name self-check procedures" but doesn't explicitly say to demonstrate using them
- **Recommended fix**: Add an explicit self-check example in the Modeling section

## Appendix: All Failures

| ID | Persona | Evidence Summary |
|----|---------|------------------|
| 79a3706b | amara_SBI | "Does not model checking their own example" |
| df150be8 | amara_SBI | "Does not demonstrate checking their own work during modeling" |
| 6c625dfd | Unknown | "Does not model checking their own demo against criteria" |
| 42ff5415 | Unknown | "Does not model checking their own demo against criteria" |
| 2d3b6e6b | carlos_SBI | "Does not model checking their own work against criteria" |
| ae169560 | carlos_SBI | "Does not model checking their own work during demonstration" |
| 9edefb96 | carlos_SBI | "Does not model checking their own work against criteria" |
| c266017b | carlos_SBI | "Does not model checking their own work during demonstration" |
| 53cb5e2c | carlos_SBI | "Does not model checking their own work against criteria" |
| 88615d3f | carlos_SBI | "Does not model checking their own work" |
| 2762d0d6 | bailey_SBI | "Does not model checking their own work during demonstration" |
| 750601c3 | bailey_SBI | "Does not model checking their own example against criteria" |
| 412fe355 | daniel_SBI | "Does not model checking their own work during demonstration" |
| 1b8b4aa5 | daniel_SBI | "Does not model checking their own work during demonstration" |
| 7b711814 | fatou_SBI | "Does not model checking their own demonstration against criteria" |
| 8ffd393b | fatou_SBI | "Does not model checking their own SBI example against criteria" |
| 8a282f8b | fatou_SBI | "Does not explicitly model checking their own work against criteria" |
| 1a253bf9 | elise_SBI | "Does not model checking their own work during demonstration" |
| b8f44c0b | elise_SBI | "Does not model checking their own work during demonstration" |
