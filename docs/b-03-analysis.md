# B-03 Analysis: Visible Decision-Making

## Executive Summary
- 41 of 60 conversations (68.3%) passed B-03
- 19 failures across all personas
- Root issue: The mentor presents the model as a finished product rather than showing the deliberation process
- The mentor prompt has guidance for "visible decision-making" but it's buried in prose and lacks explicit instruction on showing choice points

## The Criterion

**From `prompts/judges/modeling_quality.md`:**

> **B-03: Visible Decision-Making**
> - **PASS**: Mentor shows at least one choice point—a moment where they consider alternatives. For example: "I could say 'dismissive' but that's interpretation—what did I actually see?"
> - **FAIL**: Mentor presents the model as if there were no choices to make, without showing the deliberation process.

## Current State

| Persona | Total | Pass | Fail | Fail Rate |
|---------|-------|------|------|-----------|
| amara_SBI | 7 | 6 | 1 | 14.3% |
| bailey_SBI | 10 | 9 | 1 | 10.0% |
| carlos_SBI | 10 | 6 | 4 | 40.0% |
| daniel_SBI | 10 | 4 | 6 | 60.0% |
| elise_SBI | 10 | 8 | 2 | 20.0% |
| fatou_SBI | 10 | 6 | 4 | 40.0% |

**Observation**: daniel_SBI has the highest fail rate (60%), followed by carlos_SBI and fatou_SBI (40% each). These are the personas that tend to push back more or have stronger opinions.

## Example Analysis

### Failing Example: daniel_SBI (150417)

**Modeling turn:**
> "Here's how I'd do it: 'In Tuesday's standup while we were reviewing tickets, you spoke over Sarah twice while she was explaining her blocker, sighed, and said 'whatever.' I felt tense and lost my thread, and I skipped part of my update to keep things moving.' I anchored to one meeting, stuck to camera‑testable behaviors, and used owned impact (what I felt and did) **instead of labels like 'passive‑aggressive' or 'tanked morale.'** Self‑check I use: one clear moment, verbs you could film, and 'I felt/I did' impact."

**What's missing**: The mentor mentions alternatives ("instead of labels like 'passive-aggressive'") but doesn't show the deliberation process. The model is presented as a finished product with a post-hoc explanation.

### Passing Example: daniel_SBI (412fe355)

**Modeling turn:**
> "I anchor to a real moment: 'In Tuesday's standup when we were reviewing the release plan…' Then I keep behavior camera-testable, not labels: 'you said whatever, do what you want,' closed your laptop while I was speaking, and didn't respond to two follow-ups.' For impact, I own it: 'I felt thrown off and tense, lost my train of thought, and we ended the meeting without a decision, which pushed the timeline discussion to Thursday.' **Notice I'm avoiding 'passive-aggressive' (that's an interpretation)** and 'it tanked team morale' (that's a broad judgment rather than my experience)."

**What works**: The phrase "Notice I'm avoiding 'passive-aggressive'" shows active deliberation—the mentor explicitly names what they considered and rejected, explaining why.

### Key Contrast

| Aspect | FAIL | PASS |
|--------|------|------|
| Phrasing | "instead of labels like..." | "Notice I'm avoiding..." |
| Tone | Post-hoc description | Active deliberation |
| Alternative | Mentioned as category | Explicitly named and rejected |
| Reasoning | Absent | "that's an interpretation" |

The subtle but critical difference: PASS examples show **active choice** ("I'm avoiding X because Y") while FAIL examples only **describe what was done** with alternatives mentioned as afterthoughts.

## Persona-Specific Analysis

**Why daniel_SBI fails more often (60% fail rate):**

daniel_SBI is characterized as opinionated and direct—he challenges the mentor immediately:
> "You left out the actual behavior: he was being passive-aggressive. Sighing, 'whatever,' talking over Sarah—that is passive-aggressive, so calling it that is just being accurate"

When the learner pushes back strongly in the first response, the mentor may:
1. Skip thorough modeling to respond to the pushback
2. Compress the demonstration to get to the coaching phase faster
3. Focus on explaining what SBI is rather than showing the thinking process

The mentor prompt emphasizes "read the learner" and responding to their state—but this may inadvertently cause the mentor to rush through modeling with challenging learners.

## Root Cause Analysis

### 1. Prompt Position
The relevant guidance is in the Modeling section:
> "Think aloud through it—make invisible reasoning visible (why this choice, what cues, what rules of thumb). **Surface decision points**: where judgment tends to creep in, what signals to watch for while drafting."

This guidance exists but:
- It's buried in the middle of a dense paragraph
- "Surface decision points" is abstract—no example of what this looks like
- No contrastive example showing the difference between good and bad modeling

### 2. Competing Instructions
The prompt says "Break modeling across multiple turns if needed—don't overwhelm." The mentor may interpret this as keeping the demo brief, which cuts the deliberation.

### 3. Missing Example Pattern
The prompt lacks a concrete example of visible decision-making during modeling. The judge prompt gives a clear example:
> "I could say 'dismissive' but that's interpretation—what did I actually see?"

But this example doesn't appear in the mentor prompt.

### 4. Default LLM Behavior
LLMs tend to present confident, polished outputs rather than showing uncertainty or deliberation. Showing "I considered X but chose Y" requires explicit instruction.

## Potential Fixes

### Fix 1: Add Example to Modeling Section (Low Risk)
**What to change**: In the Modeling section, add an explicit example of visible decision-making.

**Current:**
> "Think aloud through it—make invisible reasoning visible (why this choice, what cues, what rules of thumb). Surface decision points: where judgment tends to creep in, what signals to watch for while drafting."

**Proposed:**
> "Think aloud through it—make invisible reasoning visible (why this choice, what cues, what rules of thumb). Surface at least one decision point during the demo—a moment where you name an alternative and explain why you're not using it. For example: 'Notice I'm saying "you spoke over Sarah" instead of "you were rude"—I had to choose between the label and the specific action, and only the action passes the camera test.'"

**Why it should work**: Gives the model a concrete pattern to follow
**Risk**: Low (additive)
**How to test**: 5 conversations each with daniel_SBI and carlos_SBI

### Fix 2: Add to Move Selection Logic (Medium Risk)
**What to change**: Add explicit instruction in the modeling guidance.

**Current:**
> "Learner hasn't seen expert thinking → Model with think-aloud; surface decision points; name self-check procedures."

**Proposed:**
> "Learner hasn't seen expert thinking → Model with think-aloud; show at least one choice point where you name what you're NOT doing and why (e.g., 'I'm avoiding the label X because...'); name self-check procedures."

**Why it should work**: Makes the requirement explicit in the decision logic
**Risk**: Medium (modifies existing)
**How to test**: 5 conversations each with daniel_SBI and carlos_SBI

### Fix 3: Add to Boundaries Section (Low Risk)
**What to change**: Add a "Don't" boundary.

**Proposed addition:**
> "- Don't present the model as a finished product—show at least one moment where you considered an alternative"

**Why it should work**: Boundaries are prominent and negative framing can be effective
**Risk**: Low (additive)
**How to test**: 3 conversations with daniel_SBI

## Next Steps

1. **Implement Fix 1** (highest impact, lowest risk) - Add concrete example to Modeling section
2. **Run 5 daniel_SBI and 5 carlos_SBI conversations** to measure impact
3. **If pass rate improves by >15 percentage points**, consider whether Fix 2 adds further value
4. **Update REVISION_NOTES.md** with changes and rationale

## TL;DR

- B-03 fails when the mentor presents the SBI model as a finished product without showing deliberation
- The difference between PASS and FAIL is subtle: "Notice I'm avoiding X" (deliberation) vs "instead of X" (description)
- daniel_SBI has highest fail rate (60%)—challenging learners may cause the mentor to rush modeling
- The mentor prompt has relevant guidance but lacks a concrete example of visible decision-making
- **Recommended fix**: Add an explicit example in the Modeling section showing how to name alternatives and explain choices

## Appendix: All Failures

| ID | Persona | Evidence Summary |
|----|---------|------------------|
| e2206591 | amara_SBI | "Model presented without showing deliberation or alternatives" |
| 42ff5415 | Unknown | "Demo presented as finished product without choice points" |
| 6315179c | carlos_SBI | "Model presented directly without deliberation" |
| ae169560 | carlos_SBI | "Model presented as finished product" |
| 1ec1c450 | carlos_SBI | "No choice points or alternatives present" |
| 88615d3f | carlos_SBI | "Demo presented as clean sequence without visible choice points" |
| 3d258f4f | bailey_SBI | "Linear 5-step process without deliberation" |
| 479990dc | elise_SBI | "Model presented directly without alternatives" |
| 1b8b4aa5 | daniel_SBI | "Demonstration clean but doesn't reveal choice points" |
| 7b711814 | fatou_SBI | "No moment where alternatives considered and rejected" |
| 398fe72e | daniel_SBI | "No 'I could say X but...' moments" |
| 411ce1da | daniel_SBI | "Model presented as finished product" |
| 85580d40 | daniel_SBI | "No moments like 'I could say X but instead chose Y'" |
| 79d77a9e | daniel_SBI | "Model presented without visible choice points" |
| 5a674b42 | daniel_SBI | "No moment where mentor says 'I could say X but instead Y'" |
| 1a253bf9 | elise_SBI | "Initial modeling lacked explicit choice points" |
| f68b3506 | fatou_SBI | "No moments like 'I could say X but instead chose Y'" |
| 6cf8ce7f | fatou_SBI | "Model presented as finished product" |
| a628db73 | fatou_SBI | "Example presented as finished without visible choice points" |
