# F-01 Analysis: Varied Turn Structure

## Executive Summary
- 37 of 59 conversations (62.7%) passed F-01
- 22 failures across most personas (amara_SBI has 0% fail rate)
- Root issue: The mentor follows a predictable formula each turn (validate → instruct → question), creating a robotic feel
- The prompt has guidance for "natural variation" but competing structures encourage uniformity

## The Criterion

**From `prompts/judges/conversational_quality.md`:**

> **F-01: Varied Turn Structure**
> - **PASS**: Mentor doesn't follow the same formula every turn. Some turns are longer explanations, some are short reactions ("Nice catch"), some are questions, some pause to let something land. There's variety in the rhythm.
> - **FAIL**: Mentor follows a predictable pattern on every turn (e.g., explain → demo → "Make sense?" → repeat), creating a robotic feel.

## Current State

| Persona | Pass | Fail | Fail Rate |
|---------|------|------|-----------|
| amara_SBI | 7 | 0 | 0.0% |
| bailey_SBI | 8 | 2 | 20.0% |
| carlos_SBI | 4 | 6 | 60.0% |
| daniel_SBI | 7 | 3 | 30.0% |
| elise_SBI | 5 | 4 | 44.4% |
| fatou_SBI | 3 | 7 | 70.0% |

**Observation**: fatou_SBI has the highest fail rate (70%), followed by carlos_SBI (60%). amara_SBI (the cooperative learner) has 0% fail rate. The pattern suggests challenging or disengaged learners trigger more formulaic responses.

## Example Analysis

### Failing Example: fatou_SBI (1ad618d6)

**Pattern observed across turns:**
1. "Sounds like this is annoying—totally fair. Here's a simplified choice: A or B?"
2. "Got it. Here's the quick version: [explanation]. Type A or B."
3. "Sounds hesitant—totally normal. Here's another choice: 1, 2, or 3?"

**The formula**: acknowledge affect ("Sounds like...") → validate → offer simplified choice (A/B or 1/2/3) → request response

Every turn follows this pattern, creating a predictable rhythm.

### Failing Example: carlos_SBI (88615d3f)

**Pattern observed across turns:**
1. "Anchor and behavior land. The impact misses—[explanation]. Rewrite the impact as..."
2. "That meets the bar. Next fix: [explanation]. Revise..."
3. "Good catch. One more tighten: [explanation]. Share your revised draft..."

**The formula**: brief acknowledgment → identify problem → instruction → request revision

### Passing Example: amara_SBI (e2206591)

**Evidence from judge:**
> "Turn structure varies: short reactions ('Nice catch', 'That's camera-testable—nice', 'Good anchor'), longer explanations with examples, focused questions ('what exact words did they say'), and reflective prompts ('what was the hardest part for you'). Some turns are single sentences, others are multi-part."

**What's different**: The mentor uses genuinely short turns ("Nice catch"), not just abbreviated versions of the formula. There's rhythmic variation—some turns explain, some just react, some ask, some pause.

### Key Contrast

| Aspect | FAIL | PASS |
|--------|------|------|
| Acknowledgment | Every turn starts with acknowledgment | Some turns skip it entirely |
| Turn length | Consistently medium (3-5 sentences) | Varies: 1 sentence to multi-paragraph |
| Ending | Always a question or request | Sometimes just lets things land |
| Formula | validate → feedback → question | Unpredictable—sometimes just "Nice catch." |

The critical difference: PASS examples include genuinely short turns that break the pattern. FAIL examples compress the formula but still follow it.

## Persona-Specific Analysis

**Why fatou_SBI and carlos_SBI fail most (70% and 60%):**

**fatou_SBI** is characterized as disengaged/skeptical:
- Gives minimal responses
- Says things like "I don't know. Whatever you think."
- Shows passive resistance

When the learner is disengaged, the mentor may:
1. Over-explain to fill silence
2. Offer simplified choices (A/B) to reduce friction
3. Validate affect repeatedly to maintain engagement
4. Fall into a "patient teacher" mode that becomes formulaic

**carlos_SBI** is impatient and pushes to move quickly:
- "Can we move on?"
- "Let's keep it quick."

When the learner is impatient, the mentor may:
1. Streamline every turn to the same efficient structure
2. Skip conversational variety to "respect their time"
3. Adopt a consistent rapid-feedback pattern

**Why amara_SBI never fails (0%):**

Amara is cooperative and engaged. When the learner actively participates:
- The mentor can react naturally ("Nice catch!")
- Shorter turns feel appropriate (learner fills the space)
- Less need to scaffold or validate repeatedly
- Conversation flows more like natural dialogue

## Root Cause Analysis

### 1. Competing Prompt Instructions Create Formula
The prompt contains multiple instructions that, combined, create a predictable pattern:

- "End every turn by passing it back to the learner" → Every turn ends with a question
- "Address one issue per turn" → Consistent medium-length turns
- "Don't lecture" → Brief validation + single point + handoff
- "Name what you're seeing without judgment" (affect section) → Validation opener

Each instruction is reasonable alone, but together they create: **[validate] + [one issue] + [question/handoff]**

### 2. No Guidance on Breaking Pattern
The prompt says:
> "Use natural variation—contractions, sentence fragments, occasional interjections"

But this refers to *language* variation (contractions, fragments), not *structural* variation (turn length, whether to include all elements). The mentor varies word choice but not turn architecture.

### 3. Missing Permission for Short Turns
The prompt says "Typical turn: 2-5 sentences." This implies every turn should be 2-5 sentences. The mentor never feels permission to say just "Nice catch." and stop.

### 4. Default LLM Behavior
LLMs tend toward:
- Completeness (including all elements each turn)
- Consistency (maintaining patterns)
- Helpfulness (always adding value)

This creates a pull toward formulaic thoroughness rather than conversational naturalness.

## Potential Fixes

### Fix 1: Explicitly Permit Short Turns (Low Risk)
**What to change**: In the Turn Structure section, add permission for very short turns.

**Current:**
> "Natural and conversational. No headers or bullets unless essential. Never label your move... Typical turn: 2-5 sentences."

**Proposed:**
> "Natural and conversational. No headers or bullets unless essential. Never label your move. **Vary turn length deliberately: some turns can be one sentence ('Nice catch.'), some can be longer explanations. Not every turn needs feedback + question + handoff.** Typical range: 1-5 sentences, but rhythm matters more than consistency."

**Why it should work**: Gives explicit permission to break the formula
**Risk**: Low (additive)
**How to test**: 5 conversations each with fatou_SBI and carlos_SBI

### Fix 2: Add "Let It Land" Guidance (Low Risk)
**What to change**: Add explicit instruction about pausing without a question.

**Proposed addition to Turn Structure:**
> "Sometimes skip the question. After a particularly good learner insight or revision, just acknowledge it briefly and let it land: 'That's it.' No follow-up question. Let them sit with the success."

**Why it should work**: Creates a new pattern the model can use
**Risk**: Low (additive)
**How to test**: 5 conversations with fatou_SBI

### Fix 3: Soften "End Every Turn by Passing It Back" (Medium Risk)
**What to change**: Modify the conversation rule to allow variation.

**Current:**
> "End every turn by passing it back to the learner."

**Proposed:**
> "Usually end by passing it back to the learner, but occasionally just react and let silence do the work."

**Why it should work**: Removes the hard constraint that forces questions every turn
**Risk**: Medium (modifies a core rule)
**How to test**: 5 conversations with fatou_SBI

### Fix 4: Add Structural Variation Examples (Low Risk)
**What to change**: In Voice and Persona, add examples of different turn structures.

**Proposed addition:**
> "Turn structure examples (vary these):
> - Short reaction: 'That lands.'
> - Question only: 'What made you choose that phrasing?'
> - Micro-coaching: 'One thing—swap "felt it was" for what you actually felt.'
> - Reflection pause: 'Good. Take a second with that.'
> - Standard: Feedback + question"

**Why it should work**: Gives concrete patterns to vary between
**Risk**: Low (additive)
**How to test**: 3 conversations with fatou_SBI

## Next Steps

1. **Implement Fix 1** (highest impact, lowest risk) - Add explicit permission for short turns
2. **Implement Fix 2** in same update - Add "let it land" guidance
3. **Run 5 fatou_SBI and 5 carlos_SBI conversations** to measure impact
4. **If pass rate improves by >15 percentage points**, consider whether Fix 3 adds further value
5. **Update REVISION_NOTES.md** with changes and rationale

## TL;DR

- F-01 fails when the mentor follows a predictable validate → feedback → question formula every turn
- The difference between PASS and FAIL: genuine turn variety (including very short turns) vs. compressed but consistent formula
- fatou_SBI (70%) and carlos_SBI (60%) have highest fail rates—challenging learners trigger formulaic responses
- amara_SBI (cooperative) has 0% fail rate—natural conversation emerges when learner is engaged
- Multiple prompt instructions combine to create the formula; no single instruction is wrong
- **Recommended fix**: Add explicit permission for 1-sentence turns and "let it land" moments

## Appendix: All Failures

| ID | Persona | Evidence Summary |
|----|---------|------------------|
| ae169560 | carlos_SBI | "Formula: brief evaluation → identify issue → instruction → 'Your turn'" |
| 4b6d5316 | carlos_SBI | "Pattern: acknowledge → identify issue → ask for revision" |
| c266017b | carlos_SBI | "Pattern: evaluate → identify issue → give instruction → ask for revision" |
| 1ec1c450 | carlos_SBI | "Pattern: brief acknowledgment → identify gap → give instruction → request draft" |
| d833c8de | carlos_SBI | "Pattern: brief validation → identify issue → give directive → request revision" |
| 88615d3f | carlos_SBI | "Pattern: brief acknowledgment, identify problem, give instruction, ask for draft" |
| 174a6847 | bailey_SBI | "Pattern: validate effort → identify issue → give instruction → ask for revision" |
| 55c4baf7 | bailey_SBI | "Pattern: validate concern → provide explanation → end with question" |
| b29a875e | elise_SBI | "Pattern: brief validation → instructional point → question to prompt action" |
| 479990dc | elise_SBI | "Pattern: validate/affirm → provide instruction → end with question" |
| 7b711814 | fatou_SBI | "Pattern: acknowledge state ('Sounds like...') → explanation → question" |
| 411ce1da | daniel_SBI | "Pattern: acknowledge point → identify what needs fixing → ask for revision" |
| ac333c5c | fatou_SBI | "Pattern: validate/acknowledge → explain/feedback → ask question or request draft" |
| 8a282f8b | fatou_SBI | "Pattern: acknowledge input → provide instruction → ask question or request draft" |
| 2e4d2814 | fatou_SBI | "Pattern: acknowledge state ('Sounds like...') → instruction/reframe → question" |
| 85580d40 | daniel_SBI | "Pattern: acknowledge positive → identify 'misses' → ask for revision" |
| 5a1e4f67 | daniel_SBI | "Pattern: acknowledge input → ask question or give directive → request revision" |
| ba6a59e2 | elise_SBI | "Pattern: validate/normalize → provide instruction → ask question" |
| 2f3464af | elise_SBI | "Pattern: validate response → brief instruction → ask question" |
| 1ad618d6 | fatou_SBI | "Pattern: acknowledge affect ('Sounds like...') → offer A/B choice → ask for response" |
| f68b3506 | fatou_SBI | "Pattern: validation/acknowledgment → brief explanation → single question" |
| a628db73 | fatou_SBI | "Pattern: validate/acknowledge → explain or reframe → ask question or give instruction" |
