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

Human raters (Janine and Nthato) spot-checked 12 conversations to validate automated evaluation accuracy. Key findings:

- **Overall agreement**: 89.7% between human raters and LLM judges (252 of 281 criteria compared)
- **Disagreement patterns**: Most disagreements occurred on E-01 (checks before advancing), E-02 (fades support), B-03 (visible decision-making), and F-01 (varied turn structure). LLM judges tended to be stricter on modeling quality criteria (B-03, B-04) while humans were stricter on adaptive pacing criteria (E-01, E-02).
- **Implications**: Automated evaluation is reliable for detecting clear pass/fail cases. Edge cases on "soft" criteria (turn variety, support fading) benefit from human review.

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

Limitations describe constraints on interpreting the current findings—what we couldn't measure, what biases may affect results, and why readers should be cautious about generalizing. These are inherent to the study as conducted.

### Synthetic Learner Validity

The six personas are LLM-generated approximations of learner archetypes, not recordings of real learners. This creates several issues:

- **Persona consistency**: Each persona follows its script reliably, but real learners shift between states (cooperative one moment, frustrated the next). The mentor never faces genuinely unpredictable behavior.

- **Missing learner types**: The personas cover impatience, disengagement, and cooperation—but not confusion stemming from genuine misconceptions, cultural differences in feedback norms, or domain expertise that exceeds the mentor's.

- **Authentic mistakes**: Despite prompt engineering to make personas produce realistic errors, LLMs resist generating "wrong" answers. The mistakes may be too clean or too easily correctable.

### LLM-as-Judge Limitations

Using LLMs to evaluate LLM tutoring creates structural blind spots:

- **Shared training biases**: If the mentor and judge share assumptions about what "good tutoring" looks like, failures invisible to both go undetected.

- **Surface feature sensitivity**: LLM judges may over-weight linguistic markers ("Let me test...") rather than pedagogical substance. A mentor could game criteria with performative phrases.

- **Criterion interpretation drift**: Different runs of the same judge may interpret edge cases differently, introducing noise.

- **No access to learning outcomes**: The judge evaluates process (did the mentor do X?) not outcomes (did the learner actually learn?). A "passing" conversation may still fail pedagogically.

### Measurement Constraints

- **Binary pass/fail**: A criterion marked PASS encompasses everything from "barely passed" to "exemplary." We lose the ability to track improvement within passing range.

- **Criteria define the ceiling**: We can only measure what we operationalized. Important tutoring behaviors not in our criteria go unevaluated (e.g., appropriate wait time, metacognitive prompting quality).

- **N/A handling**: Some criteria are marked N/A when conditions aren't triggered (e.g., F-03 requires learner frustration). This reduces sample size for certain criteria and may hide problems.

### Generalizability Constraints

- **Single task domain**: All evaluation used SBI feedback delivery. The mentor's performance on other cognitive apprenticeship tasks (debugging code, analyzing arguments, clinical reasoning) is unknown.

- **Single model**: Evaluation was conducted on one model. Other models may exhibit different failure patterns or strengths.

- **Prompt-specific findings**: Root causes traced to this prompt design may not apply to other instructional agent prompts. The specific failure modes (formulaic turns, missing self-check) reflect this prompt's architecture.

### Sample Size and Statistical Power

- **~60 conversations**: Sufficient to identify strong patterns but limited for detecting smaller effects or rare failure modes.

- **Balanced but small cells**: 10 conversations per persona provides balanced comparison but limits power for detecting moderate effects.

- **No statistical significance testing**: Reported differences (e.g., 60% vs 20% fail rates) are descriptive, not inferentially tested.

### Evaluation Process Limitations

- **Same team designed mentor and evaluation**: Criteria may reflect the designers' theory of good tutoring rather than empirically validated pedagogical principles. Blind spots in the design appear as blind spots in evaluation.

- **No adversarial testing**: Personas were designed to be challenging but not adversarial. We didn't test edge cases like learners who deliberately try to break the system, provide nonsensical input, or test boundaries.

- **Snapshot evaluation**: Each conversation is evaluated independently. We don't assess consistency across conversations or improvement over iterative prompt refinements on the same criteria.

## Future Directions

Future directions describe what we *could* do next—opportunities to address the limitations above, extend the work to new contexts, or explore questions that emerged from current findings. Where limitations say "here's what we couldn't do," future directions say "here's what would be valuable to try."

### Addressing Synthetic Learner Limitations

- **Real learner pilots**: Deploy MentorAI with actual learners in controlled settings. Compare process metrics (do the same criteria pass/fail?) and add outcome metrics (did learning transfer?).

- **Diverse persona expansion**: Add personas representing genuine misconceptions, non-native speakers, experts who push back with valid challenges, and learners who change state mid-conversation.

- **Adversarial testing**: Systematically probe edge cases—off-topic requests, nonsensical input, attempts to extract the system prompt, deliberately triggering failure modes.

### Improving Evaluation Validity

- **Human-LLM judge calibration**: Expand spot-checking with multiple human raters. Identify criteria where humans and LLM judges systematically disagree and refine definitions accordingly.

- **Continuous scoring**: Replace binary pass/fail with rubric-based scoring (1-4 scale) to capture gradations of quality and track improvement within the passing range.

- **Outcome-based criteria**: Add evaluation of learning outcomes—can the learner apply SBI independently in a transfer task after the session? Process criteria predict but don't guarantee learning.

### Extending Generalizability

- **Multi-domain evaluation**: Apply the same cognitive apprenticeship framework to different learning tasks (code debugging, argument analysis, clinical reasoning). Test whether identified failure patterns (formulaic turns, missing self-check) are prompt-specific or domain-general.

- **Cross-model comparison**: Run the same evaluation on different foundation models. Identify which behaviors are model-specific vs. inherent to the prompt design.

- **Prompt architecture variations**: Test whether alternative prompt structures (different CA method orderings, explicit turn templates, persona-conditional instructions) produce different failure patterns.

### Robustness and Adaptation

- **Robustness interventions**: Implement the proposed fixes (explicit self-check examples, permission for short turns) and measure impact on pass rates, particularly with challenging personas.

- **Adaptive prompting**: Could the mentor detect its own degradation with challenging learners? Explore self-monitoring mechanisms that trigger explicit compensation ("I notice I'm being brief—let me slow down and demonstrate the self-check").

- **Graceful degradation**: If full pedagogical quality isn't achievable with a highly resistant learner, what's the minimum viable tutoring? Define acceptable fallback behaviors.

### Longitudinal and Ecological Studies

- **Session-over-session learning**: Track learners across multiple sessions. Do they internalize self-check procedures? Does transfer improve?

- **Real-world deployment**: Move beyond controlled evaluation to classroom or workplace settings. What new failure modes emerge? What contextual factors matter?

- **Instructor augmentation**: Rather than replacing human instructors, how might MentorAI augment them? Evaluate hybrid human-AI tutoring configurations.
