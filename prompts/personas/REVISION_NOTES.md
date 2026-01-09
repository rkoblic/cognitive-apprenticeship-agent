# Persona Revision Notes

Detailed changelog tracking updates to synthetic learner personas and related evaluation infrastructure.

---

## 2026-01-09

### All personas (amara_CER, bailey_CER, carlos_CER)
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
