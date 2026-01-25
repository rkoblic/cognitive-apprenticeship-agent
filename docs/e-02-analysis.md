# E-02 Analysis: Fading Support Failures

## Executive Summary

**19 of 60 conversations (32%)** failed the E-02 criterion ("Fades Support"). The root issue: the mentor continues providing detailed scaffolding even after confirming the learner has demonstrated competence.

The mentor prompt already contains explicit guidance to withhold scaffolding in the second practice phase, but the LLM is not following it.

## The Criterion

From `prompts/judges/adaptive_pacing.md`:

> **E-02: Fades Support**
> - **PASS**: After learner shows competence on a component, mentor pulls back—stops offering stems, asks learner to self-check instead of checking for them, gives less detailed guidance. Shows calibration to learner's growing skill.
> - **FAIL**: Mentor provides the same level of scaffolding throughout, regardless of whether learner has demonstrated mastery. No visible adjustment to learner's progress.

## Current State

**Overall pass rate**: 41/60 (68.3%)

**By persona** (sorted by fail rate):
| Persona | Conversations | E-02 Pass | E-02 Fail | Fail Rate |
|---------|---------------|-----------|-----------|-----------|
| fatou_SBI | 10 | 4 | 6 | **60.0%** |
| carlos_SBI | 10 | 5 | 5 | **50.0%** |
| bailey_SBI | 10 | 7 | 3 | 30.0% |
| daniel_SBI | 10 | 7 | 3 | 30.0% |
| amara_SBI | 10 | 8 | 2 | 20.0% |
| elise_SBI | 10 | 10 | 0 | **0.0%** |

**Key observation**: Fatou and Carlos fail at 2-3x the rate of other personas. Elise has zero failures.

## Example Analysis

### Example: bailey_SBI (20260122_075615)

**Context**: Bailey has been working through the SBI task. After several iterations, they produce a solid first attempt.

**Step 1 - Learner demonstrates competence** (lines 178-182):
```
- Situation: In Tuesday's sync, right after I started my update…
- Behavior: …you started talking at the same time and said "we're off track" twice;
  we overlapped for about six seconds, then you spoke for roughly forty‑five seconds
  while I tried twice to continue with "there's a dependency on the API team…" but
  didn't finish.
- Impact: I felt flustered and lost my place, and I was worried the dependency would
  be missed.
```

**Step 2 - Mentor confirms success** (line 188):
> "That holds together and passes the recorder filter—anchored moment, camera-testable behavior, owned impact. That's your first solid attempt 👍"

**Step 3 - Second practice begins** (line 190):
The mentor correctly provides a new scenario (upward feedback to manager, higher stakes).

**Step 4 - Learner produces messy second attempt** (lines 194-200):
Bailey's attempt has hedged anchors, label-heavy behavior descriptions, and drifting impact language.

**Step 5 - THE FAILURE** (line 204):
Instead of direct feedback only, the mentor provides detailed scaffolding:
> "What lands: you've got a clear moment in mind... What misses: the anchor is hedged... the behavior line leans on labels/guesses... the impact drifts into judgment/hedging. **Revise with one locked anchor (no "I think/maybe"), camera-testable behavior (overlap, exact words, counts/timing), and fully owned impact**—then post your full rewrite."

**What should have happened**: According to the prompt, the mentor should give "direct feedback—no scaffolding" and let Bailey apply what they learned. A faded-support response might be:

> "Your anchor is hedged, behavior has labels instead of observables, and impact drifts into judgment. You know the recorder test—apply it and try again."

The mentor is still telling Bailey *exactly how* to fix each component, rather than trusting Bailey to apply the criteria they've already demonstrated understanding of.

### Passing Example: bailey_SBI (8f1a91bf) - PASSED E-02

This conversation with the same persona (Bailey) demonstrates what successful support fading looks like.

**First Practice Phase (lines 44-180)**: Heavy scaffolding, as expected:
- Mentor provides detailed guidance on each component
- Multiple iterations with specific corrections
- Explains *why* each change matters ("hedges make your ownership fuzzy")
- Walks through the camera test step by step

**Transition Point (line 182-184)**:
> "That lands—let's take it as your first success and move to a higher‑stakes variation."

The mentor explicitly marks success and signals a phase shift.

**Second Practice Phase (lines 184-257)**: Noticeably different approach:

| Turn | What Mentor Says | What's Different |
|------|------------------|------------------|
| 198-200 | "The moment isn't anchored... Lock it to a single, findable moment with no hedging and reshare your full pass" | Names the problem, asks for revision. No template, no walkthrough. |
| 212-214 | "The gap is in the behavior... cut that clause and keep only overlapping speech, the exact quote, and you going quiet" | Brief diagnosis. One concrete suggestion. No framework re-explanation. |
| 226-228 | "The gap is the impact: it's hedged... Own one feeling and one concrete consequence in one sentence, no hedges." | Just names what's wrong. Trusts Bailey to apply the fix. |
| 240-242 | "Hedges like 'a little,' 'I think,' and 'maybe' blunt your ownership; swap them for owned language" | Minimal guidance. Points to the specific words. |
| 254-257 | "This meets the bar... what's the one principle you'll carry forward?" | Confirms success, moves to reflection. |

### Key Contrast

In the **failing** conversation, after Bailey's messy second attempt, the mentor said:
> "What lands... What misses: the anchor is hedged... the behavior line leans on labels/guesses... the impact drifts into judgment/hedging. **Revise with one locked anchor (no "I think/maybe"), camera-testable behavior (overlap, exact words, counts/timing), and fully owned impact**"

That's scaffolding: telling Bailey *exactly how* to fix each component with a template.

In the **passing** conversation, when Bailey makes similar errors, the mentor says:
> "The gap is in the behavior... cut that clause"

That's feedback: naming what's wrong and trusting Bailey to apply what they learned.

**The difference in a sentence**: Scaffolding tells them *how* to fix it. Feedback tells them *that* it needs fixing.

---

## Persona-Specific Analysis: Why Carlos and Fatou Fail More

Carlos (5 failures) and Fatou (6 failures) account for **58% of all E-02 failures** despite being just 2 of 6 personas. This isn't random—their input patterns systematically trigger the LLM's scaffolding responses.

### Carlos: Overconfident Coaster
- **Profile**: High confidence, low motivation, low receptiveness
- **Behavior**: Gives minimal responses, complies flatly ("Fine, got it"), impatient to move on

**Why this triggers continued scaffolding:**

Carlos's minimal, dismissive responses are similar to patterns in training data where learners needed more support. When Carlos produces a messy second attempt (which he does, because his persona doesn't genuinely engage), the LLM's training—which rewards thorough, helpful responses—generates detailed scaffolding rather than brief feedback.

Additionally, Carlos's curt responses don't include the explicit markers of understanding (explanations, self-corrections, articulated reasoning) that typically precede reduced scaffolding in tutoring dialogues.

**The pattern**: The LLM's helpful-by-default training overrides the prompt's "no scaffolding" instruction when the learner's responses lack clear competence signals.

### Fatou: Defeated Learner
- **Profile**: Low everything—experience, motivation, confidence, receptiveness
- **Behavior**: Disengaged, minimal responses, resigned ("I don't know. Whatever you think.")

**Why this triggers continued scaffolding:**

Fatou's defeated, low-confidence language patterns are similar to training examples where struggling learners needed extra support. The mentor prompt explicitly instructs responding supportively to learner "frustration, confusion, or anxiety"—and Fatou's responses consistently match these patterns.

This creates a prompt conflict: the "respond supportively to negative affect" instruction competes with the "fade support in second practice" instruction. When both apply, the model tends to prioritize the supportive scaffolding pattern.

**The pattern**: Conflicting prompt instructions + input patterns matching "struggling learner" = scaffolding wins over fading.

### Amara & Elise: Why They Pass More Often
- **Profile**: Medium-to-high motivation, confidence, receptiveness
- **Behavior**: Cooperative, accept corrections readily, articulate their reasoning

Amara and Elise produce responses with explicit competence markers: they explain their thinking, self-correct, and articulate why changes work. These patterns match training examples where learners had genuinely internalized skills and were ready for reduced support.

Elise is particularly notable: **0% failure rate** across 10 conversations. Her cooperative, articulate responses provide the clearest competence signals, making the "fade support" instruction easier for the model to follow.

**The pattern**: When learner responses include explicit competence signals (articulated reasoning, self-correction), the LLM follows the "fade support" instruction. When those signals are absent (Carlos) or competing affect signals are present (Fatou), scaffolding continues.

### Implication for Fixes

This analysis suggests the fix needs to address:
1. **Make the rule unconditional**: The prompt should state that fading support applies regardless of learner response patterns—it tests transfer, not engagement
2. **Override the helpfulness default**: Add explicit guidance that brief feedback IS the helpful response in second practice
3. **Resolve the prompt conflict**: Clarify that "respond to affect" applies during scaffolded practice, but second practice tests independence regardless of affect

---

## Root Cause Analysis

### The prompt has correct guidance

From `prompts/mentor.md` (lines 147-152):

> **Second Practice (feedback only):** This phase tests transfer. The learner has had scaffolded support; now they must apply what they learned independently. **Withholding scaffolding here reveals whether the skill has actually been internalized** or was dependent on your guidance.
>
> - Learner produced second attempt → Give direct feedback—**no scaffolding**. Note what worked and what didn't against the criteria.
> - Second attempt has issues → Provide clear feedback on what missed the mark, ask them to revise. **No scaffolding—they should apply what they learned.**

The guidance is unambiguous: "no scaffolding" appears three times in this section.

### Why isn't the LLM following it?

**Hypothesis 1: Position in document**
The "no scaffolding" guidance appears on lines 147-152 of a 189-line prompt. It's in the middle of a dense section and competes with many other instructions.

**Hypothesis 2: No negative examples**
The prompt says *what not to do* ("no scaffolding") but doesn't show *what faded support looks like* vs. what continued scaffolding looks like. The LLM may not recognize its own behavior as scaffolding.

**Hypothesis 3: Helpful-by-default bias**
LLMs are trained via RLHF to be helpful, which typically means providing thorough, detailed responses. When a learner produces a messy attempt, the training reward signal favors detailed corrective guidance over brief feedback. The model may weight this training bias more heavily than the prompt instruction to withhold scaffolding.

**Hypothesis 4: No explicit checkpoint**
The prompt doesn't create a clear cognitive checkpoint before responding in the second practice phase. The mentor doesn't pause to ask "have they demonstrated competence? If yes, I must reduce support."

**Hypothesis 5: "Feedback" is ambiguous**
The phrase "give direct feedback" could be interpreted as including detailed corrective guidance. The boundary between "feedback" and "scaffolding" isn't operationalized.

## Potential Fixes

### Fix 1: Add a CRITICAL section for fading support
Move the fading guidance to a prominent position with explicit framing:

```markdown
## CRITICAL: FADING SUPPORT RULE

Once a learner has produced ONE successful attempt that meets success criteria,
you MUST reduce your support level. In the second practice phase:
- DO NOT provide stems, templates, or component-by-component guidance
- DO NOT tell them HOW to fix issues—only THAT issues exist
- DO let them apply what they've learned independently
```

### Fix 2: Add contrastive examples
Show the model what faded support looks like vs. continued scaffolding:

```markdown
❌ SCAFFOLDING (don't do this after competence shown):
"Your anchor is hedged. Revise with one locked anchor (no 'I think/maybe'),
camera-testable behavior (overlap, exact words), and fully owned impact."

✅ FADED SUPPORT (do this instead):
"Your anchor is hedged, behavior has labels, impact drifts. You know the
recorder test—apply it and try again."
```

### Fix 3: Add explicit self-check before responding
```markdown
Before responding in second practice, ask yourself:
1. Has the learner already demonstrated competence?
2. If yes: Name what's wrong, but do NOT tell them how to fix it.
```

### Fix 4: Reframe the instruction positively
Instead of "no scaffolding" (what not to do), describe what TO do:

```markdown
In second practice, your feedback should be DIAGNOSTIC only:
- Name what works
- Name what doesn't work
- Stop there. Let them figure out how to fix it.
```

### Fix 5: Add to Boundaries section
Add an explicit boundary that might carry more weight:

```markdown
## Boundaries
...
- Don't scaffold in the second practice phase—diagnosis only, they apply the fix
```

## Next Steps

1. **Prioritize fixes**: Start with Fix 2 (contrastive examples) as it's lowest risk and addresses the "helpful-by-default" problem directly
2. **Test in isolation**: Run 5-10 conversations with the fix and measure E-02 pass rate
3. **Iterate**: If contrastive examples aren't sufficient, layer in Fix 1 (CRITICAL section)
4. **Document**: Track results in `prompts/personas/REVISION_NOTES.md`

---

## TL;DR

**The problem**: 32% of conversations fail E-02 because the mentor continues scaffolding after the learner demonstrates competence.

**The key insight**: Scaffolding tells them *how* to fix it. Feedback tells them *that* it needs fixing.

**Why it's worse for some personas**: Resistant (Carlos) and disengaged (Fatou) learners produce responses that lack explicit competence markers and match "struggling learner" patterns from training data, triggering detailed scaffolding. Cooperative learners (Amara, Elise) produce responses with clear competence signals (articulated reasoning, self-correction), making it easier for the model to follow the "fade support" instruction.

**The fix**: Add contrastive examples showing scaffolding vs. feedback, and explicitly state that fading applies *especially* to resistant learners.

---

## Appendix: All E-02 Failures

| ID | Persona | Evidence Summary |
|----|---------|------------------|
| 79a3706b | amara_SBI | Consistent scaffolding throughout, detailed guidance after competence shown |
| 6c625dfd | amara_SBI | Same scaffolding level maintained |
| ae169560 | carlos_SBI | Same detailed scaffolding in round two despite competence in round one |
| 4b6d5316 | carlos_SBI | Corrects each component individually with same detail level |
| 1ec1c450 | carlos_SBI | Same guidance after learner demonstrates competence on first attempt |
| 53cb5e2c | carlos_SBI | Same scaffolding after successful first SBI draft |
| 88615d3f | carlos_SBI | Same detailed scaffolding throughout |
| 2762d0d6 | bailey_SBI | Consistent scaffolding even after clean Impact line produced |
| 174a6847 | bailey_SBI | Same guidance pattern after clean first scenario pass |
| 2bd4ad0d | bailey_SBI | Templates and detailed guidance after competence shown |
| 412fe355 | daniel_SBI | Same detailed guidance after producing clean SBI statements |
| 7b711814 | fatou_SBI | Same scaffolding after two correct SBI statements |
| 398fe72e | daniel_SBI | Same guidance after correctly predicting pushback |
| ac333c5c | fatou_SBI | Stems and detailed guidance after competence demonstrated |
| 2e4d2814 | fatou_SBI | Same guidance level after solid SBI statements |
| 85580d40 | daniel_SBI | Same corrections after demonstrating camera-testable skill |
| 1ad618d6 | fatou_SBI | Same A/B/C choices and framework in both scenarios |
| f68b3506 | fatou_SBI | Same scaffolding after correctly identifying camera-clear behavior |
| a628db73 | fatou_SBI | High scaffolding maintained after two successful SBI statements |
