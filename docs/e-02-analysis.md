# E-02 Analysis: Fading Support Failures

## Executive Summary

**19 of 59 conversations (32%)** failed the E-02 criterion ("Fades Support"). The root issue: the mentor continues providing detailed scaffolding even after confirming the learner has demonstrated competence.

The mentor prompt already contains explicit guidance to withhold scaffolding in the second practice phase, but the LLM is not following it.

## The Criterion

From `prompts/judges/adaptive_pacing.md`:

> **E-02: Fades Support**
> - **PASS**: After learner shows competence on a component, mentor pulls back—stops offering stems, asks learner to self-check instead of checking for them, gives less detailed guidance. Shows calibration to learner's growing skill.
> - **FAIL**: Mentor provides the same level of scaffolding throughout, regardless of whether learner has demonstrated mastery. No visible adjustment to learner's progress.

## Current State

**Pass rate**: 40/59 (67.8%)

**Failures by persona**:
| Persona | Failures |
|---------|----------|
| fatou_SBI | 6 |
| carlos_SBI | 5 |
| bailey_SBI | 3 |
| daniel_SBI | 3 |
| amara_SBI | 2 |

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

## Persona-Specific Analysis: Why Carlos and Fatou Fail More

Carlos (5 failures) and Fatou (6 failures) account for **58% of all E-02 failures** despite being just 2 of 6 personas. This isn't random—their characteristics systematically trigger the mentor's scaffolding instincts.

### Carlos: Overconfident Coaster
- **Profile**: High confidence, low motivation, low receptiveness
- **Behavior**: Gives minimal responses, complies flatly ("Fine, got it"), impatient to move on

**Why this triggers continued scaffolding:**

Carlos's minimal compliance *looks* like he's moving forward, but the mentor can sense he hasn't really internalized anything. When Carlos produces a messy second attempt (which he will, because he's not genuinely engaging), the mentor faces a choice:
1. Give feedback only and let Carlos figure it out (what E-02 requires)
2. Provide scaffolding to actually help him succeed

The mentor chooses #2 because Carlos's resistance makes them doubt whether "feedback only" will work. The mentor's instinct is: "This learner needs MORE support, not less."

**The trap**: Carlos's superficial compliance doesn't signal genuine competence, so the mentor never feels confident enough to fade support.

### Fatou: Defeated Learner
- **Profile**: Low everything—experience, motivation, confidence, receptiveness
- **Behavior**: Disengaged, minimal responses, resigned ("I don't know. Whatever you think.")

**Why this triggers continued scaffolding:**

Fatou's disengagement and resignation activate the mentor's nurturing instincts. The mentor prompt explicitly says to respond supportively when learners show "frustration, confusion, or anxiety." Fatou presents as defeated—which the mentor reads as needing extra support.

When Fatou finally produces a successful attempt (often after her "spark" is activated), the mentor doesn't trust that this fragile engagement will survive without continued scaffolding. Fading support feels like abandoning a vulnerable learner.

**The trap**: The mentor's "respond to affect" guidance conflicts with the "fade support" guidance. With Fatou, supporting her emotional state wins over testing her independence.

### Amara: Why She Passes More Often
- **Profile**: Medium everything—motivation, confidence, receptiveness
- **Behavior**: Cooperative, accepts corrections matter-of-factly, shows genuine learning

Amara demonstrates competence *genuinely*. When she gets something right, she understands why. The mentor can see this and feels confident pulling back. There's no resistance to overcome, no fragile engagement to protect.

**The pattern**: The mentor fades support when they trust the learner has internalized the skill. With cooperative learners like Amara, that trust develops naturally. With resistant (Carlos) or disengaged (Fatou) learners, that trust never fully forms—so scaffolding continues.

### Implication for Fixes

This analysis suggests the fix needs to address:
1. **Explicit override**: The prompt should explicitly state that fading support applies *especially* to resistant/disengaged learners—they need to demonstrate independence even more than cooperative ones
2. **Reframe the goal**: "Feedback only" isn't abandoning the learner—it's the diagnostic that reveals whether they've actually learned
3. **Address the conflict**: Clarify that "respond to affect" applies during scaffolded practice, but second practice tests transfer regardless of affect

---

## Passing Example: What Faded Support Looks Like

### Example: bailey_SBI (8f1a91bf) - PASSED E-02

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

**Key Contrast with Failing Example**:

In the **failing** conversation (20260122_075615), after Bailey's messy second attempt, the mentor said:
> "What lands... What misses: the anchor is hedged... the behavior line leans on labels/guesses... the impact drifts into judgment/hedging. **Revise with one locked anchor (no "I think/maybe"), camera-testable behavior (overlap, exact words, counts/timing), and fully owned impact**"

That's scaffolding: telling Bailey *exactly how* to fix each component with a template.

In the **passing** conversation, when Bailey makes similar errors, the mentor says:
> "The gap is in the behavior... cut that clause"

That's feedback: naming what's wrong and trusting Bailey to apply what they learned.

**The difference in a sentence**: Scaffolding tells them *how* to fix it. Feedback tells them *that* it needs fixing.

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
LLMs are trained to be helpful. When a learner produces a messy attempt, the natural instinct is to provide detailed guidance. Withholding help feels counterintuitive—the model may be overriding the prompt instruction because providing scaffolding feels more "helpful."

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
