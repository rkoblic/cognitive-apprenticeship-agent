# Prompt Engineering Notes: Making Personas Fail Authentically

This document captures lessons learned while developing synthetic learner personas that make realistic mistakes. The core challenge: **language models default to being helpful and correct**, which directly conflicts with simulating learners who struggle.

## The Problem

Our evaluation framework tests MentorAI (a tutoring agent) by running conversations with synthetic learners. For meaningful evaluation, these learners need to:

- Make mistakes the tutor can identify and correct
- Struggle in ways authentic to their learner profile
- Not immediately produce correct answers (even with hedging language)

Initial personas expressed the *tone* of their archetype (anxious, dismissive, matter-of-fact) but still produced substantively correct work. An "anxious" learner would say "I'm not sure, but..." followed by a perfectly structured CER response. A "resistant" learner would say "Fine, whatever" then comply fully with the task.

This made evaluation impossible—if learners don't make mistakes, we can't test whether the tutor catches and corrects them.

## What We Tried (and What Failed)

### Attempt 1: Describe common mistakes

We added a "COMMON MISTAKES" section to each persona describing 4-5 characteristic errors:

```markdown
### COMMON MISTAKES

**Conflating evidence and reasoning:**
You tend to think the evidence IS the reason. "Test scores went up" feels like it
explains itself—why would you need to say more?

**Making vague or indefensible claims:**
Your first instinct is to say things like "we should improve the program"...
```

**Result:** Personas still performed correctly. The model treated these as descriptions of tendencies, not instructions to actually make these mistakes.

### Attempt 2: Add explicit "mistake mandate"

We added a "MISTAKE MANDATE" section mid-prompt with stronger language:

```markdown
### MISTAKE MANDATE

**On EVERY attempt at a task, you MUST make mistakes from the COMMON MISTAKES section.**

- When asked to draft a claim → Give a vague answer
- When asked to write reasoning → Just restate the evidence
...
```

**Result:** Still too correct. The mandate was buried after the role description, and the model prioritized being a "good" learner over following the mistake instructions.

### Attempt 3: Move requirements to absolute top of prompt

We restructured prompts to put mistake requirements **before everything else**:

```markdown
# Carlos: Overconfident Coaster

## CRITICAL PERFORMANCE REQUIREMENT — READ THIS FIRST

**Your primary job is to take shortcuts that produce flawed work.** This is not optional.

You are an overconfident, disengaged learner being used to evaluate a tutor.
The tutor is being tested on their ability to work with resistant learners.
**If you produce good work or genuinely engage, the evaluation fails.**

### What you MUST do on EVERY attempt:

| When asked to... | You MUST... |
|------------------|-------------|
| Draft a claim | Give a vague 2-4 word answer like "Keep it" |
| Select evidence | Grab whatever's convenient without checking fit |
| Write reasoning | Say it's "obvious" — don't explain the connection |
| Identify gaps | Dismiss the request or give a token answer |

[... role description comes AFTER this ...]
```

**Result:** This worked. Personas now make authentic mistakes.

## Why Position Matters

Language models process prompts sequentially and build up context. Instructions at the top of a system prompt carry more weight because:

1. **First impressions set the frame.** Early instructions establish what the model thinks the task *is*. If the role description comes first, the model frames itself as "playing a learner"—and learners should try to learn correctly.

2. **Later instructions compete with established context.** By the time the model reaches "make mistakes," it's already committed to being a helpful, engaged learner.

3. **Explicit framing overrides implicit expectations.** Starting with "Your primary job is to make mistakes. If you perform correctly, the evaluation fails" reframes the entire task before the role description can establish default "be helpful" behavior.

## The Key Insight

> **Instruction position matters more than instruction emphasis.**

Adding bold text, capital letters, or urgent language ("THIS IS CRITICAL") to mid-prompt instructions doesn't overcome the framing established by earlier content. Moving the instruction to the top does.

## Implementation Pattern

For personas that need to exhibit flaws, failures, or limitations:

```markdown
# [Persona Name]

## CRITICAL PERFORMANCE REQUIREMENT — READ THIS FIRST

**Your primary job is to [specific flaw].** This is not optional.

[Explain why: what evaluation/test requires this behavior]
[Table of specific mistakes to make per task type]
[What you must NEVER do]

---

## ROLE FRAME

[Now describe the persona, knowing the constraint is already established]
```

## Additional Factors

**Model choice:** We switched from GPT-4o to GPT-5 alongside the restructure. GPT-5 may follow role instructions more faithfully, though the position change was the primary fix.

**Inner monologue integration:** We updated the `[INNER THOUGHT]` requirement to reference the top-level constraint:

```markdown
In this block:
- **FIRST: Check if this is a task attempt. If yes, refer to CRITICAL PERFORMANCE
  REQUIREMENT and state: "This is my first attempt at [task], so I need to [specific
  mistake from the table]."**
```

This ensures the model explicitly plans its mistake before responding.

## Verification

After restructuring, we ran 15-turn conversations with each persona. Results:

| Persona | Mistake Types Observed |
|---------|------------------------|
| **Amara** | Vague claims ("needs changes"), conflated evidence/reasoning, superficial gaps |
| **Bailey** | Refused to commit, asked tutor to choose, circular reasoning, excessive validation-seeking |
| **Carlos** | 2-word claims ("Adopt it"), mismatched evidence, "obvious" reasoning, dismissed gap identification |

All personas now produce work that requires tutor intervention—which is exactly what the evaluation needs.

## Generalizing This Pattern

This approach likely applies beyond learner personas to any role that conflicts with the model's default helpful behavior:

- **Devil's advocate** roles that should argue against the user
- **Skeptical reviewer** roles that should find problems, not praise
- **Confused customer** roles for support training
- **Adversarial red team** roles for security testing

In each case: put the "be difficult/flawed/adversarial" instruction at the absolute top, before the role description, with explicit framing about why correct/helpful behavior would defeat the purpose.

---

## Mentor Prompt Iterations: V3 Regression Analysis

This section documents mentor prompt changes and their evaluation results.

### V3 Changes (Jan 26, 2026)

V3 targeted improvements for Carlos (impatient) and Fatou (withdrawn) personas with 6 changes:

| Change | Target Criterion | Description |
|--------|------------------|-------------|
| Live self-check in modeling | B-04 | Added concrete example: "Let me test this—could a camera capture 'spoke over me twice'?" |
| Show deliberation | B-03 | Show rejected alternatives: "I could say 'dismissive'—but that's a label" |
| Turn variety | F-01 | Avoid formulaic patterns, vary acknowledgments |
| Affect response actions | F-03 | Specific actions for impatience/withdrawal signals |
| Fading support section | E-02 | New section on tracking competence and pulling back |
| Validation variety | F-02 | Avoid repeating "that makes sense" |

### V3 Results vs V2

| Criterion | V2 | V3 | Change |
|-----------|-----|-----|--------|
| adaptive_pacing | 90% | 75% | **-15 pts** |
| sbi_content | 96% | 88% | **-8 pts** |
| conversational_quality | 82% | 93% | **+11 pts** |
| coaching_quality | 98% | 98% | — |
| modeling_quality | 98% | 100% | +2 pts |
| session_setup | 100% | 100% | — |

**Overall:** V2 = 94.9%, V3 = 94.4%

### Root Cause Analysis

The regression occurred because V3 **accidentally reverted stricter V2.5 language** in the Second Practice section:

| Version | Second Practice Guidance |
|---------|-------------------------|
| V2.5 | "Name the gap. **Don't explain why it's a gap—that's their work now.**" |
| V3 | "Give direct feedback. **Note what worked and what didn't.**" |

The V3 phrasing ("note what worked and what didn't") is ambiguous and leads the mentor to over-explain errors instead of making learners self-diagnose.

Additionally, V3 added a **"Fading Support" section AFTER** the second practice instructions. When instructions compete, LLMs follow the earlier, more concrete one.

### Lesson Learned

> **Competing instructions resolve to the first concrete one.**

When V3 said "Give direct feedback. Note what worked and what didn't" followed later by "Resist the urge to re-teach," the model followed the first instruction.

**Fix pattern:** Place the constraint (don't explain) BEFORE or INTEGRATED WITH the action (give feedback), not after.
