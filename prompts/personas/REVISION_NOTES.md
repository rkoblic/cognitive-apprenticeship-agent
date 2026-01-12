# Persona Revision Notes

Detailed changelog tracking updates to synthetic learner personas and related evaluation infrastructure.

---

## 2026-01-12

### mentor.md - Learner provides their own practice scenario
- Changed practice flow: mentor asks learner for their situation instead of providing a scenario
- Updated "Who provides the case" section: modeling uses mentor scenario, practice uses learner's real situation
- Updated "Scenario generation guidelines" to clarify it's for modeling only
- Updated "Mastery criteria" with new practice flow: ask for situation → unpack what's observable → draft SBI
- **Rationale:** When mentor provides scenarios with all the details ("Sam interrupted you twice, checked their phone"), the learner just reformats given information. The cognitive work of identifying observable vs. judgment is skipped. Now the learner brings their own (likely judgment-laden) situation and the mentor helps unpack it.

### mentor.md - Natural session close, not scripted exit ticket
- Replaced formulaic 3-bullet exit ticket (reuse/watch for/transfer) with personalized wrap-up
- Exit should connect to what learner said was hard in reflection, not deliver a generic checklist
- Added explicit "Don't ask implementation intentions questions" guidance
- **Rationale:** Exit ticket felt scripted—like checking boxes on research rather than responding to the learner. A real mentor would build on what the learner just said was difficult, not ignore it and deliver a template.

### mentor.md - Productive struggle over giving answers
- Rewrote Coaching method: "Ask before telling. If something is vague or wrong, ask what they meant—don't show them what they should have written. Let them sit in the discomfort of not knowing."
- Rewrote Scaffolding method: "Offer a partial cue or question, not a complete template. If they get it wrong twice, explore why before giving more support."
- Added explicit practice guidance: pick ONE problem, ask what they meant, let them struggle, only then offer partial cue
- Added DO NOT list: no templates with blanks, no rewriting their answer, no listing all problems at once
- Updated turn count to 15 max (was 7-10)
- **Rationale:** Mentor was giving away answers with templates like "In [specific time/place], you [observable action]..." The goal is productive struggle, not transcription. Ask before telling, explore repeated mistakes.

### mentor.md - 2-turn modeling (structure + judgment-check)
- Changed from 1-turn to 2-turn modeling to stay truer to cognitive apprenticeship
- Turn 1: Model full SBI structure with inline annotations, end with "What do you notice about how I described the behavior?"
- Turn 2: Model the judgment-check explicitly ("Could a camera capture this?"), end with "What questions before you try?"
- Situation anchor is easy; the hard parts are observable behavior and catching judgment — focus modeling there
- Updated target turn count to 7-10 (was 6-10)
- **Rationale:** One-turn modeling compressed too much. CA emphasizes making expert thinking visible in chunks. Two turns allows learner to process the structure before adding the judgment-check skill, while still keeping conversations short.

### mentor.md - Remove over-labeling of pedagogical moves
- Added explicit rule to Turn Structure: "Never label or announce your pedagogical move. Don't say 'Hint:', 'Scaffold:', 'Let me model this:', 'Step 3:', or 'Demo:'"
- Added note to CA Toolkit section: "(These categories guide your internal decision-making. Never name them in your response.)"
- Replaced all "hint" references with "suggestion" to reduce likelihood of "Hint:" labels in output
- **Rationale:** Mentor was outputting meta-labels like "Step 3 (demo):", "Scaffold:", "Hint:" which made conversations feel like reading a manual. Skilled human tutors do scaffolding without announcing it.

### mentor.md - Compressed conversation structure
- Rewrote "Modeling-first approach" section: model complete SBI in ONE turn with inline annotations instead of 5 separate steps with check-ins
- Rewrote "Mastery criteria" section: learner attempts FULL SBI at once, not piece-by-piece (situation → behavior → impact as separate turns)
- Updated "When to close" section: target 6-10 turns total instead of 15-20
- Added explicit guidance against step-by-step scaffolding that inflates conversation length
- **Rationale:** Conversations were running 15-20 turns, making evaluation review impractical. Compressed modeling (1 turn vs 5-10) and chunked practice (full attempt vs step-by-step) maintains cognitive apprenticeship approach while targeting 6-10 turn conversations.

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
