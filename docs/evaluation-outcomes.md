# Evaluation Outcomes

This section summarizes findings from automated evaluation of MentorAI across ~60 tutor-learner conversations with 6 synthetic learner personas.

## Overall Performance Summary

MentorAI was evaluated against 20 criteria organized into 6 evaluation dimensions:

| Dimension | Criteria | Focus |
|-----------|----------|-------|
| Session Setup | A-01, A-02, A-03 | Goal clarity, phase signaling, realistic scenarios |
| Modeling Quality | B-01, B-02, B-03, B-04, B-05 | Demonstration quality and think-aloud |
| Coaching Quality | C-01, C-02, C-03, C-04, C-05 | Feedback specificity and revision cycles |
| SBI Content | D-01, D-02, D-03 | Domain-specific accuracy |
| Adaptive Pacing | E-01, E-02, E-03 | Scaffolding and fading support |
| Conversational Quality | F-01, F-02, F-03 | Natural interaction and affect response |

**Critical criteria** (7 total) represent must-pass behaviors for pedagogical integrity. **Quality criteria** (13 total) represent polish and refinement.

## What the System Does Well

High-pass-rate areas demonstrate strengths in foundational tutoring behaviors:

- **Session Setup (A-01, A-02, A-03)**: MentorAI consistently confirms the learning goal, signals phase transitions, and uses realistic workplace scenarios grounded in specific meetings and colleagues.

- **Specific Feedback (C-01)**: When providing feedback, the mentor points to exact language in the learner's draft and names the specific issue, rather than giving vague guidance.

- **Heuristic Delivery (B-05)**: The mentor reliably provides reusable rules of thumb ("If you couldn't video-record it, it's not behavior") that learners can apply independently.

- **Responding to Negative Affect (F-03)**: When learners show frustration or confusion, the mentor acknowledges the emotional state before continuing with instruction.

## Systematic Weaknesses

Three criteria showed consistent failure patterns with identifiable root causes:

### B-03: Visible Decision-Making (68% pass rate)

**The failure pattern**: The mentor presents the SBI model as a finished product rather than showing the deliberation process.

**Example of failure**:
> "I anchored to a single meeting, kept the behavior camera-visible, and owned the impact."

**Example of success**:
> "Notice I'm avoiding 'passive-aggressive'—that's an interpretation. I had to choose between the label and the specific action."

**Root cause**: The prompt says "surface decision points" but lacks a concrete example of what visible deliberation looks like. The mentor explains *what* it did without showing *why* it chose that over alternatives.

### B-04: Self-Checking (68% pass rate)

**The failure pattern**: The mentor teaches learners a self-check procedure but doesn't demonstrate using it on its own model.

**Example of failure**:
> "Here's the self-check: camera test, owned impact, specific moment. Now try your own."

**Example of success**:
> "Quick check on my own work before handing off: camera-visible? Yes—'talked over me twice' would show on video. Owned impact? Yes—'I felt rushed' is mine."

**Root cause**: The prompt says to "name self-check procedures" but doesn't explicitly instruct the mentor to *demonstrate* applying them. The mentor interprets this as teaching the procedure rather than modeling its use.

### F-01: Varied Turn Structure (63% pass rate)

**The failure pattern**: The mentor follows a predictable formula every turn: validate → identify issue → give instruction → ask question.

**Example of failure**:
> Turn 1: "That's close. The issue is X. Try revising to Y. What's your updated draft?"
> Turn 2: "Good catch. One more thing: Z. Revise that part. Share your draft?"
> Turn 3: "Almost there. The gap is W. Fix that. Your turn?"

**Example of success**: Turns vary genuinely—some are single sentences ("Nice catch."), some are longer explanations, some pause without a question ("That lands. Take a second with that.").

**Root cause**: Multiple prompt instructions combine to create the formula: "End every turn by passing it back to the learner" (forces questions), "Address one issue per turn" (consistent medium length), "Typical turn: 2-5 sentences" (no short turns). Each instruction is reasonable alone, but together they create robotic uniformity.

## Persona-Specific Findings

Evaluation used six synthetic learner personas with varying characteristics. A striking pattern emerged: **the mentor performs well with cooperative learners but degrades with challenging ones**.

| Persona | Characteristics | F-01 Fail Rate | B-04 Fail Rate |
|---------|-----------------|----------------|----------------|
| amara_SBI | Cooperative, engaged | 0% | 29% |
| bailey_SBI | Neutral | 20% | 20% |
| carlos_SBI | Impatient, curt | 60% | 60% |
| fatou_SBI | Disengaged, skeptical | 70% | 30% |

**Interpretation**: When learners push back, express impatience, or disengage:

1. The mentor compresses turns to "respect their time," cutting modeling quality
2. The mentor falls into formulaic patterns as a coping mechanism
3. Scaffolding behaviors like self-check demonstrations get skipped

This reveals a tension between two goals in the prompt:
- **Responsiveness**: "Read the learner, then make one move"
- **Pedagogical completeness**: Demonstrate self-checking, show deliberation

With challenging learners, responsiveness wins—and pedagogical quality suffers.

## LLM-as-Judge Validation

Human raters spot-checked a subset of conversations to validate automated evaluation accuracy. Key findings:

- **Overall agreement**: [X%] between human raters and LLM judges
- **Disagreement patterns**: LLM judges tended to [be more lenient / more strict] on [specific criteria]
- **Implications**: Automated evaluation is [reliable for / limited in] [specific use cases]

## Tracing Failures to Prompt Design

A key contribution of this evaluation is the ability to trace observed failures back to specific prompt design choices. The causal chain:

```
Observed failure in conversation
        ↓
Pattern identified across multiple conversations
        ↓
Prompt section analyzed for relevant guidance
        ↓
Root cause identified (missing example, competing instructions, etc.)
        ↓
Targeted fix proposed and tested
```

**Example trace for B-03 (Visible Decision-Making)**:

1. **Observation**: Mentor says "I avoided judgments like 'unprofessional'" but doesn't show considering and rejecting alternatives
2. **Pattern**: 19/60 failures, concentrated in challenging personas
3. **Prompt analysis**: Modeling section says "surface decision points" without example
4. **Competing instruction**: "Typical turn: 2-5 sentences" creates pressure to be brief
5. **Root cause**: Abstract guidance + brevity pressure = skipped deliberation
6. **Proposed fix**: Add explicit example: "Notice I'm saying 'spoke over me' instead of 'rude'—I had to choose between the label and the specific action."

## Implications for Prompt Engineering

Several lessons emerged for designing effective instructional agent prompts:

1. **Explicit examples outperform abstract guidance**. "Surface decision points" failed; "Say: 'I could use X but chose Y because...'" would succeed.

2. **Position matters**. Critical behaviors need prominence—buried guidance gets overridden by more salient instructions.

3. **Stress-test with challenging personas**. Behaviors that appear robust with cooperative users may fail under pressure.

4. **Watch for instruction interactions**. Individual instructions can be reasonable while their combination creates failure modes.

5. **Model default behavior works against you**. LLMs prefer polished, complete, consistent output—exactly the opposite of showing deliberation, using short turns, or breaking patterns.

## Limitations

Several limitations should be considered when interpreting these results:

1. **Synthetic personas may not capture real learner diversity**. Actual learners vary in ways the six personas cannot fully represent.

2. **LLM judges may share blind spots with the LLM mentor**. Both are built on similar architectures and training, potentially missing failure modes a human would catch.

3. **Criteria definitions shape measurement**. We can only evaluate what we operationalized—other important tutoring behaviors may go unmeasured.

4. **Binary pass/fail loses nuance**. A criterion marked PASS may have degrees of quality not captured by the verdict.

5. **Single task domain**. All evaluation was conducted on SBI feedback delivery. Transfer to other instructional domains is unknown.

## Future Directions

Based on evaluation findings, several directions warrant further investigation:

1. **Robustness interventions**: Can prompt modifications maintain quality with challenging learners without sacrificing responsiveness?

2. **Human-in-the-loop validation**: Expand spot-checking to refine criteria definitions and calibrate LLM judges.

3. **Multi-domain evaluation**: Test whether identified patterns (e.g., formulaic turn structure) appear across different learning tasks.

4. **Longitudinal effects**: Do learners actually internalize skills better when the mentor demonstrates self-checking? Outcome-based evaluation beyond process criteria.

5. **Adaptive prompting**: Could the mentor detect its own degradation with challenging learners and explicitly compensate?
