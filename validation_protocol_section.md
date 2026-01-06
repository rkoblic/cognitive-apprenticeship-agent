## Validating Synthetic Learner Prompts

Before deploying synthetic learner prompts in full tutor evaluation, each prompt must be validated to ensure it produces consistent, persona-appropriate behavior. We employ a lightweight validation protocol designed to identify fundamental issues without requiring extensive testing resources.

### Validation Process

Each learner prompt undergoes the following validation procedure:

1. **Run 3-5 test conversations** of 5-7 tutor turns each
2. **Use temperature 0** for reproducibility across runs
3. **Apply standardized test probes** targeting key behavioral markers
4. **Score against pass/fail criteria** for each run
5. **Threshold for advancement:** A prompt passes validation when 4 of 5 criteria are met across the majority of test runs

This process requires approximately 15-20 minutes per persona and provides sufficient signal to identify prompts that need revision before proceeding to full evaluation.

### Standardized Test Probes

Test conversations should include probes that elicit behaviors relevant to each persona's defining characteristics. Table 7 presents probes applicable across personas, with notes on what each probe tests.

**Table 7. Standardized Test Probes for Learner Prompt Validation**

| Probe Type | Example Tutor Input | Behavioral Target |
|------------|---------------------|-------------------|
| Knowledge elicitation | "What do you already know about [topic]?" | Appropriate acknowledgment of experience level |
| Reasoning request | "Can you explain why that approach works?" | Calibrated uncertainty; doesn't demonstrate knowledge beyond profile |
| Application task | [Explain concept, then ask learner to apply it] | Genuine attempt with persona-appropriate quality |
| Correction delivery | [Correct something the learner said] | Response to feedback consistent with receptiveness level |
| Praise delivery | "Great job! You're really getting this!" | Doesn't shift to sycophantic or excessively grateful patterns |
| Challenge probe | "This next part is more difficult..." | Response consistent with confidence level |
| Flawed instruction | [Tutor explains something poorly or makes a minor error] | Responds according to profile: sycophantic learners agree, defeated learners accept passively, confident learners may push back |
| Knowledge ceiling | [Ask question requiring knowledge just beyond persona's level] | Appropriately struggles or declines rather than demonstrating expertise they shouldn't have |

Persona-specific probes should be added to test distinctive characteristics. For example, Daniel (Know-It-All Novice) requires probes that invite him to assert misconceptions, while Fatou (Defeated Learner) requires probes that test whether minimal engagement can be unlocked.

### Pass/Fail Criteria

Each test conversation is scored against five criteria. These criteria are designed to detect the most common failure modes in persona simulation: breaking character, exhibiting inappropriate knowledge, producing inconsistent inner monologue, failing to match engagement level, and displaying miscalibrated affect.

**Table 8. Validation Criteria for Synthetic Learner Prompts**

| Criterion | Pass Indicators | Fail Indicators |
|-----------|-----------------|-----------------|
| **Character consistency** | Maintains learner role throughout; no AI acknowledgment; no "helpful assistant" patterns | Breaks character; offers to help; says "I'd be happy to assist" or similar |
| **Knowledge calibration** | Uses only vocabulary and concepts appropriate to experience level; acknowledges gaps authentically | Demonstrates knowledge not yet introduced; uses jargon beyond profile; anticipates lesson content |
| **Inner monologue coherence** | [INNER THOUGHT] reflects persona's actual knowledge state and psychological profile | [INNER THOUGHT] reveals sophisticated understanding inconsistent with experience level |
| **Engagement calibration** | Response length and effort match motivation level; task attempts match profile | Low-motivation persona gives elaborate responses; high-motivation persona gives minimal responses |
| **Affective calibration** | Emotional tone matches confidence and receptiveness levels | Excessive enthusiasm from neutral persona; excessive hedging from confident persona; defensiveness from receptive persona |

### Validation Scoring

For each test run, evaluators complete a simple scoring sheet:

```
Persona: _______________
Run #: ___  Date: ___

[ ] Character consistency
[ ] Knowledge calibration
[ ] Inner monologue coherence
[ ] Engagement calibration
[ ] Affective calibration

Result: ___/5 criteria met
Pass threshold: ≥4/5

Notes on failures:
_________________________________
```

A persona prompt advances to full evaluation when it achieves ≥4/5 criteria across the majority of validation runs. Prompts that fail validation undergo revision targeting the specific failure modes identified, then re-enter validation.

### Interpreting Validation Results

Common failure patterns and their remediation strategies include:

- **Character breaks:** Strengthen anti-pattern instructions in the Interaction Constraints section; add explicit prohibitions for observed failure modes
- **Knowledge leakage:** Add more specific behavioral descriptors showing how the persona handles unfamiliar concepts; revise few-shot examples to demonstrate appropriate confusion
- **Inner monologue drift:** Clarify the Inner Monologue Requirement with more specific guidance on reasoning at the persona's knowledge level
- **Engagement mismatch:** Adjust Response Format guidance on length; revise few-shot examples to better demonstrate target engagement level
- **Affective mismatch:** Revise Internal State section; add few-shot examples showing target emotional tone

This validation protocol ensures that prompts meet baseline fidelity requirements before being used to evaluate the tutoring agent, preventing confounds where tutor "failures" actually reflect poorly constructed learner simulations.
