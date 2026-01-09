# Persona Revision Notes

Detailed changelog tracking updates to synthetic learner personas and related evaluation infrastructure.

---

## 2026-01-09

### All personas - CRITICAL PERFORMANCE REQUIREMENT restructure
- Moved mistake requirements to absolute top of each prompt as "CRITICAL PERFORMANCE REQUIREMENT — READ THIS FIRST"
- Formatted as clear tables specifying exact mistake type for each task (claim, evidence, reasoning, gap)
- Updated inner monologue to reference top-level requirement first
- Removed duplicate MISTAKE MANDATE sections (now consolidated at top)
- **Rationale:** Previous MISTAKE MANDATE section (placed mid-prompt) was ineffective—models still optimized for correctness. Positioning critical constraints at the very top, before role frame, overrides the model's default helpful behavior.

### run_eval.py - Model change
- Switched from GPT-4o to GPT-5
- Removed temperature parameter (GPT-5 only supports default temperature)
- **Rationale:** GPT-5 better follows role instructions when mistake requirements are positioned at top

### run_eval.py - Early termination fix
- Fixed false positive in `detect_conversation_end()` that triggered when mentor mentioned "exit tickets" in scenario descriptions
- Previous check (`"exit ticket" in mentor_lower`) matched any occurrence, including "digital exit tickets" in program descriptions
- Now uses specific patterns: "exit ticket:", "your exit ticket", "here's your exit ticket", etc.
- **Rationale:** Conversations were terminating after 1 turn when the mentor's scenario included programs that use exit tickets as a practice

### All personas - MISTAKE MANDATE addition (superseded)
- Added "MISTAKE MANDATE" section with explicit instructions to make mistakes on first attempts
- Updated INNER MONOLOGUE REQUIREMENT to include explicit mistake selection step
- **Rationale:** Previous changes (common mistakes section, failure-mode examples) weren't effective—personas still performed too well. The model was optimizing for correctness over role authenticity. New mandate makes mistake-making a hard requirement, not just a description.

Key changes:
- Amara: Must make vague claims, conflate evidence/reasoning, give superficial gaps on first attempts
- Bailey: Must second-guess into wrong answers, refuse to commit, produce circular reasoning
- Carlos: Must give two-word vague claims, say reasoning is "obvious," resist corrections for 2-3 exchanges

### All personas (earlier today)
- Added "COMMON MISTAKES" section defining 4-5 characteristic errors per persona
- Rewrote all few-shot examples to show actual mistakes and failures, not just hedged correct answers
- Added guidance on how each persona handles correction (resistance level, recovery patterns)
- **Rationale:** Personas were performing too well—expressing uncertainty or resistance but not making actual mistakes that require tutor correction

**Amara's common mistakes:**
- Conflates evidence and reasoning
- Makes vague, indefensible claims
- Picks related-but-not-supporting evidence
- Superficial gap identification
- Accepts corrections quickly but may repeat mistakes later

**Bailey's common mistakes:**
- Second-guesses correct answers into wrong ones
- Overthinks to paralysis
- Seeks validation instead of committing
- Circular reasoning from anxiety
- Overcorrects after feedback

**Carlos's common mistakes:**
- Vague claims disguised as decisive
- "Obvious" reasoning with gaps
- Grabs convenient evidence without checking fit
- Dismisses gap identification as unnecessary
- Resists correction for 2-3 exchanges before complying minimally

### All personas (earlier change)
- Added `[INNER THOUGHT]` and `[RESPONSE]` format to all few-shot examples
- **Rationale:** Examples weren't demonstrating the required output format, which may have contributed to inconsistent formatting from the model

### run_eval.py
- Added `extract_visible_response()` and `extract_inner_thought()` functions
- Mentor now only sees visible responses (not inner thoughts)
- Transcript preserves full output for LLM-as-Judge evaluation
- **Rationale:** More realistic simulation—a human tutor wouldn't see the learner's internal reasoning

- Added early termination detection (`detect_conversation_end()`)
- Conversations now stop before max turns when exit ticket is delivered or mutual farewells occur
- **Rationale:** Prevents excessive goodbye loops; ensures complete but not padded conversations

---

## 2026-01-08

### New personas created for CER task
- Created `amara_CER.md` - Baseline novice (medium motivation, straightforward engagement)
- Created `bailey_CER.md` - Anxious striver (high motivation, low confidence, seeks reassurance)
- Created `carlos_CER.md` - Skeptical practitioner (medium motivation, resistant, prefers efficiency)

### Removed old feedback-task personas
- Removed `amara.md`, `bailey.md`, `carlos.md`, `chris.md`, `mo.md`, `nell.md`
- **Rationale:** Task changed from "delivering constructive feedback" to "CER recommendations"

### mentor.md
- Rewrote for CER (Claim-Evidence-Reasoning) recommendation task
- Updated scenario generation guidelines for program/initiative recommendations
- Updated mastery criteria for CER drafting
- **Rationale:** New learning task required complete prompt revision

### validation_probes.md
- Rewrote all 8 probes for CER task context
- **Rationale:** Old probes referenced feedback delivery scenarios

---

## Template for Future Entries

```
## YYYY-MM-DD

### filename.md
- What changed
- **Rationale:** Why the change was made
```
