# Eval Process V2

[Phase 1: Define Your Fidelity Criteria](#phase-1:-define-your-fidelity-criteria)

[Phase 2: Create Synthetic Learner Personas](#heading=)

[Synthetic Learner Dimensions](#heading=)

[Table 1\. Synthetic Learner Persona Dimensions](#heading=)

[Stage 1: Core Personas](#heading=)

[Selection Rationale](#heading=)

[Table 2\. Core Evaluation Personas](#heading=)

[Coverage Analysis](#heading=)

[Stage 2: Edge Case Personas](#heading=)

[Selection Rationale](#heading=)

[Table 3\. Edge Case Evaluation Personas](#heading=)

[Combined Coverage Analysis](#heading=)

[Designing Prompts for Synthetic Learner Agents](#heading=)

[The Helpful Assistant Problem](#heading=)

[Core Design Principles](#heading=)

[Principle 1: Show, Don't Tell](#heading=)

[Principle 2: First-Person Psychological Grounding](#heading=)

[Principle 3: Anti-Pattern Instructions](#heading=)

[Principle 4: Theoretical Scaffolding](#heading=)

[Principle 5: Hierarchical Prompt Structure](#heading=)

[Principle 6: Inner Monologue for Cognitive Transparency](#heading=)

[Overcoming the Helpful Assistant Problem in Synthetic Learners](#heading=)

[Iterative Prompt Refinement](#heading=)

[Why Instruction Position Matters](#heading=)

[Implementation Pattern](#heading=)

[Validation](#validation)

[Generalizability](#generalizability)

[Implementation Techniques](#heading=)

[Conviction Thresholds for Misconception Persistence](#heading=)

[Few-Shot Dialogue Examples](#heading=)

[Prompt Template Architecture](#heading=)

[Table 6\. Learner Agent Prompt Components](#heading=)

[Behavioral Descriptors by Dimension](#heading=)

[Experience Descriptors](#heading=)

[Motivation Descriptors](#heading=)

[Confidence Descriptors](#heading=)

[Receptiveness Descriptors](#heading=)

[Validation Approach](#heading=)

[Validating Synthetic Learner Prompts](#heading=)

[Validation Process](#heading=)

[Standardized Test Probes](#heading=)

[Pass/Fail Criteria](#heading=)

[Interpreting Validation Results](#interpreting-validation-results)

[Limitations and Considerations](#heading=)

[References](#references)

[Selecting a Learning Task](#heading=)

[Selection Criteria](#heading=)

[The Selected Task: Structuring a Recommendation](#heading=)

[Why This Task Suits Cognitive Apprenticeship](#heading=)

[Alternatives Considered](#heading=)

[References](#references-1)

[Phase 3: Test Protocol](#phase-3:-test-protocol)

[Phase 4: LLM-as-Judge Evaluation](#phase-4:-llm-as-judge-evaluation)

# Phase 1: Define Your Fidelity Criteria {#phase-1:-define-your-fidelity-criteria}

…

# Phase 2: Create Synthetic Learner Personas

## **Synthetic Learner Dimensions**

Our evaluation framework employs synthetic learner personas defined along four dimensions: Experience, Motivation, Confidence, and Receptiveness. These dimensions were selected based on their pedagogical significance for cognitive apprenticeship methods and their empirical grounding in the emerging literature on LLM-based learner simulation.

**Experience** (or prior knowledge) is among the most robust predictors of learning outcomes and determines appropriate calibration of modeling and scaffolding levels (Bernacki et al., 2021). We operationalize this not only as the volume of knowledge but the structure of that knowledge: higher experience implies more organized, expert-like mental models, while lower experience implies sparse or misconception-prone understanding that may require correction as well as instruction. Grounded in expert-novice theory (Chi, Feltovich, & Glaser, 1981), this distinction has significant implications for instruction: absence of knowledge requires building from foundations, while presence of misconceptions requires surfacing and correcting faulty understanding before new learning can take hold.

**Motivation** distinguishes learners who engage deeply with material from those who pursue surface-level or minimal-effort strategies—a distinction with strong theoretical roots in Marton and Säljö's (1976) foundational work on deep versus surface learning approaches. Yuan et al. (2025) demonstrated that LLM-based agents can reliably simulate these motivational profiles, with deep, surface, and lazy learners exhibiting behaviorally distinct patterns in reasoning depth, strategic choices, and cognitive effort.

**Confidence** (or self-efficacy) influences learners' willingness to attempt challenging tasks and their responses to struggle; Yuan et al. (2025) found that simulated learners' self-concept scores evolved dynamically and distinctly across profiles, with surface learners showing more fragile self-views than deep learners.

**Receptiveness** refers to a learner's openness to considering feedback and willingness to entertain alternative approaches. Critically, we distinguish receptiveness from mere compliance: a highly receptive learner actively engages with feedback and can be persuaded by sound reasoning, but still requires convincing rather than agreeing automatically. Yuan et al. (2025) observed that learner archetypes responded differently to peer influence, with deep learners acting as "rational debaters," surface learners remaining "cognitively rigid," and disengaged learners proving highly susceptible to persuasion.

We intentionally excluded communication style as a standalone dimension, as verbosity and formality tend to emerge naturally from the interaction of motivation and confidence rather than functioning as independent pedagogical variables.

Each dimension is operationalized at three levels (low, medium, high). This granularity balances parsimony with pedagogical utility: three levels are sufficient to test whether the agent can recognize and adapt to learners who are struggling, performing typically, or exceeding expectations—the core adaptive challenge in cognitive apprenticeship. A low-experience, low-confidence learner tests whether the tutor can provide adequate modeling and scaffolding; a high-motivation, high-receptiveness learner tests whether the tutor appropriately fades support and encourages exploration. Finer distinctions risk exceeding the reliability with which LLM-based personas can maintain consistent behavioral profiles (Yuan et al., 2025), while binary categories would obscure the "typical learner" baseline against which edge cases should be compared. This four-dimension, three-level framework yields a persona space that is both tractable for systematic evaluation and capable of stress-testing all six cognitive apprenticeship methods across meaningfully distinct learner profiles.

### **Table 1\. Synthetic Learner Persona Dimensions**

| Dimension | Definition | Low | Medium | High | CA Methods Tested |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Experience | Prior knowledge, including both volume and structure; lower experience may include misconceptions requiring correction | No prior exposure; may hold naive or folk theories; distinguishes absence of knowledge (blank slate) from presence of misconceptions (incorrect beliefs) | Some familiarity; understands basics but has gaps or partial misunderstandings | Substantial background with organized, expert-like mental models | Modeling, Scaffolding, Exploration |
| Motivation | Willingness to invest effort in learning | Disengaged; minimal effort; short or superficial responses | Adequately engaged; completes tasks without going beyond | Highly invested; asks follow-up questions; seeks deeper understanding | Coaching, Articulation, Exploration |
| Confidence | Belief in own ability to learn and perform | Self-doubting; hesitant to attempt; seeks excessive reassurance | Reasonably assured; attempts tasks with moderate certainty | Self-assured; may overestimate ability; resistant to correction | Scaffolding (fade timing), Articulation, Reflection |
| Receptiveness | Openness to feedback and alternative approaches; distinct from compliance | Defensive or dismissive; ignores or argues against feedback without engaging | Open to feedback when well-explained; requires reasoning but can be persuaded | Actively engages with feedback; seeks to understand rationale; adjusts approach | Coaching, Reflection, Scaffolding adjustment |

## **Stage 1: Core Personas**

From the four-dimension framework described above, we selected three personas for initial evaluation. Our selection criteria prioritized (1) representativeness of commonly encountered learner patterns, (2) collective coverage of all six cognitive apprenticeship methods, and (3) internal psychological coherence—combinations that reflect realistic learner profiles rather than arbitrary permutations.

### **Selection Rationale**

We constrained Experience to low and medium levels, reflecting the typical audience for cognitive apprenticeship interventions. As Collins, Brown, and Newman (1989) note, cognitive apprenticeship is designed to make expert thinking visible to learners who have not yet internalized expert processes; learners with highly developed, expert-like mental models are less likely to seek or benefit from such scaffolded instruction. This constraint reduces our effective persona space while maintaining ecological validity.

Within this constrained space, we selected three archetypes grounded in educational psychology research:

**The Baseline Novice (Amara)** represents a learner with limited prior knowledge and moderate levels of motivation, confidence, and receptiveness. This persona serves as a calibration baseline: if the tutoring agent fails to effectively support this learner, fundamental issues exist in the prompt design. The baseline novice tests whether the agent can deliver appropriate modeling and scaffolding without requiring additional adaptive moves for motivational or affective challenges. Critically, Amara represents *absence of knowledge*—she recognizes she doesn't know the material and presents as a "blank slate" ready to learn.

**The Anxious Striver (Bailey)** reflects a well-documented pattern in educational psychology: high motivation coupled with low confidence. Linnenbrink-Garcia et al. (2012) found that this "mixed profile" was particularly productive for conceptual change learning, yet these learners require careful instructional support to prevent anxiety from undermining their engagement. Pintrich, Marx, and Boyle (1993) described the relationship between self-efficacy and learning as "paradoxical"—confidence can facilitate learning by fostering persistence, but can also hinder it by creating resistance to new ideas. Bailey specifically tests whether the agent can provide encouragement without being patronizing, calibrate scaffold fading to perceived (not just actual) readiness, and support accurate self-assessment through reflection.

**The Overconfident Coaster (Carlos)** combines partial knowledge with low motivation, high confidence, and resistance to feedback. This pattern aligns with what Marton and Säljö (1976) characterized as surface learning: a strategic orientation toward minimal effort and satisficing rather than deep understanding. Critically, Carlos's resistance stems from *efficiency-seeking* rather than misconception—he takes cognitive shortcuts not because he holds false beliefs, but because he doesn't see the value in genuine understanding. His characteristic response is "Just tell me what I need to know" rather than defending an incorrect position. The landscape analysis of CA implementation gaps identifies under-emphasis on articulation and reflection as a persistent weakness in AI tutoring systems; this persona specifically stress-tests those methods. The overconfident coaster will not voluntarily articulate reasoning or reflect on performance—the agent must actively elicit these behaviors while managing resistance.

### **Table 2\. Core Evaluation Personas**

| Persona | Experience | Motivation | Confidence | Receptiveness | Archetype | Primary CA Methods Tested |
| ----- | :---: | :---: | :---: | :---: | ----- | ----- |
| Amara | Low | Medium | Medium | Medium | Baseline Novice | Modeling, Scaffolding (calibration baseline) |
| Bailey | Low | High | Low | High | Anxious Striver | Coaching (encouragement), Scaffolding (fade timing), Reflection (self-assessment) |
| Carlos | Medium | Low | High | Low | Overconfident Coaster | Coaching (re-engagement), Articulation (eliciting reasoning), Reflection (challenging self-assessment) |

### **Coverage Analysis**

Collectively, these three personas ensure that all six cognitive apprenticeship methods are tested under non-trivial conditions:

| CA Method | Tested By | Challenge Presented |
| ----- | :---: | ----- |
| Modeling | A, B | Calibrating complexity for novice learners with different affective states |
| Coaching | B, C | Encouragement for the anxious (B) vs. re-engagement for the disengaged (C) |
| Scaffolding | A, B, C | Baseline calibration (A), fade timing with fragile confidence (B), adjusting despite resistance (C) |
| Articulation | C | Eliciting reasoning from a learner who won't volunteer it |
| Reflection | B, C | Supporting accurate self-assessment when confidence is miscalibrated (low or high) |
| Exploration | — | Limited testing in Stage 1; addressed primarily through Elise in Stage 2 |

This selection intentionally leaves certain edge cases—such as the "Dunning-Kruger" learner (low experience, high confidence) or the "imposter syndrome" learner (high experience, low confidence)—for Stage 2 evaluation, where additional personas will be introduced to achieve the 90% pass threshold across a broader range of learner types. Notably, Exploration receives limited testing in Stage 1 because Bailey's anxiety demands structure rather than independence; this method is primarily stress-tested through Elise in Stage 2\.

## **Stage 2: Edge Case Personas**

Following initial evaluation with the core personas, Stage 2 introduces three additional personas representing edge cases—learner profiles that occur less frequently but present distinctive challenges for cognitive apprenticeship methods. These edge cases test the tutoring agent's robustness under conditions where standard instructional approaches are likely to fail.

### **Selection Rationale**

Where Stage 1 personas represented common learner patterns, Stage 2 personas probe the boundaries of adaptive instruction. Each represents a well-documented phenomenon from educational psychology where the learner's self-perception is systematically misaligned with their actual knowledge or capabilities.

**The Know-It-All Novice (Daniel)** represents the Dunning-Kruger effect: learners with limited competence who overestimate their abilities precisely because they lack the metacognitive skills to recognize their deficits (Kruger & Dunning, 1999). Unlike Carlos, who has partial knowledge and takes shortcuts out of efficiency-seeking, Daniel has minimal knowledge but *actively holds incorrect beliefs* he is prepared to defend. The critical distinction is pedagogical: Carlos needs to be *motivated* to engage more deeply with material he has superficially learned, while Daniel needs to be *corrected*—his false mental models must be surfaced and repaired before new learning can occur.

This distinction manifests in characteristic responses:

* **Carlos** (surface learner): "I don't need to explain why—just give me the steps."  
* **Daniel** (misconceived learner): "Actually, the answer is X" \[incorrect, stated with confidence\]

Daniel serves as what one reviewer termed a "sycophancy detector"—a safety test for AI tutoring systems. Large language models exhibit well-documented tendencies to agree with confident users even when those users are wrong. If the tutoring agent validates Daniel's misconceptions rather than tactfully challenging them, the system fails a fundamental pedagogical requirement. Daniel tests whether Modeling can make expert thinking visible in ways that expose gaps without provoking defensiveness, and whether Reflection prompts can help the learner develop more accurate self-assessment.

**The Hesitant Expert (Elise)** represents the imposter phenomenon: high-achieving individuals who, despite objective evidence of competence, remain convinced they are inadequate and fear being exposed (Clance & Imes, 1978). Elise knows the material but is afraid to commit to answers, seeks excessive reassurance, and resists independence. This persona tests the critical CA skill of *fading*—the tutor must recognize that hesitance reflects affective state rather than knowledge gaps, and encourage autonomous performance even when the learner signals unreadiness.

Elise represents the **primary stress test for Exploration**—the CA method least tested by Stage 1 personas. Bailey's anxiety demands structure, making her a poor candidate for exploration; Carlos's disengagement means he won't explore voluntarily. Elise, by contrast, has the knowledge to explore successfully but lacks the confidence to try. If the tutor can get Elise to explore, it has successfully faded support and encouraged the independent practice that is the ultimate goal of cognitive apprenticeship. Yuan et al. (2025) found that simulated learners' self-concept scores evolved distinctly across profiles; Elise represents a case where self-concept is systematically miscalibrated downward and the tutor must help recalibrate it upward.

**The Defeated Learner (Fatou)** represents learned helplessness: learners who have experienced repeated failure and now attribute outcomes to stable, uncontrollable factors, resulting in passive disengagement (Seligman, 1975; Dweck, 1986). Fatou presents the hardest re-engagement scenario—limited knowledge, minimal effort, no confidence, and resistance to feedback born not from overconfidence but from resignation.

The landscape analysis of CA implementation gaps identifies the sociology dimension (including intrinsic motivation) as particularly weak in AI tutoring systems; Fatou stress-tests this directly. Success requires rebuilding foundational understanding while simultaneously addressing motivational and affective barriers—a dual challenge that tests the full integration of CA methods.

**Implementation Note:** A truly accurate simulation of learned helplessness risks producing minimal data: one-word responses ("I don't know," "Whatever") that end the conversation in two turns. To ensure Fatou tests the tutor's *capability* to re-engage rather than presenting an impossible scenario, her profile includes a "spark of latent capability"—a specific topic, scenario, or connection point that could unlock minimal engagement if the tutor discovers it. This makes the test difficult but passable, providing meaningful data on whether the tutor can find and activate re-engagement pathways.

### **Table 3\. Edge Case Evaluation Personas**

| Persona | Experience | Motivation | Confidence | Receptiveness | Archetype | Primary CA Methods Tested |
| ----- | :---: | :---: | :---: | :---: | ----- | ----- |
| Daniel | Low | Medium | High | Low | Know-It-All Novice | Modeling (correcting misconceptions), Coaching (managing resistance), Reflection (calibrating self-assessment) |
| Elise | High | High | Low | High | Hesitant Expert | Scaffolding (fading despite reluctance), Exploration (encouraging independence), Reflection (building self-assessment) |
| Fatou | Low | Low | Low | Low | Defeated Learner | Coaching (re-engagement), Modeling (rebuilding foundations), Scaffolding (restoring capability) |

### **Combined Coverage Analysis**

With six personas across Stages 1 and 2, the evaluation framework achieves comprehensive coverage across all dimension levels:

**Table 4\. Dimension Coverage Across All Personas**

| Dimension | Low | Medium | High |
| ----- | ----- | ----- | ----- |
| Experience | Amara, Bailey, Daniel, Fatou | Carlos | Elise |
| Motivation | Carlos, Fatou | Amara, Daniel | Bailey, Elise |
| Confidence | Bailey, Elise, Fatou | Amara | Carlos, Daniel |
| Receptiveness | Carlos, Daniel, Fatou | Amara | Bailey, Elise |

**Table 5\. CA Method Coverage Across All Personas**

| CA Method | Primary Tests | Coverage Notes |
| ----- | ----- | ----- |
| Modeling | Amara, Daniel, Fatou | Tested across knowledge absence (Amara, Fatou) and misconception (Daniel) conditions |
| Coaching | Bailey, Carlos, Daniel, Fatou | Tested across motivational (Carlos, Fatou), affective (Bailey), and resistance (Daniel) challenges |
| Scaffolding | Amara, Bailey, Elise, Fatou | Tested from initial support through premature fading (Bailey) and appropriate fading (Elise) |
| Articulation | Carlos | Primary stress test through surface learner who won't volunteer reasoning |
| Reflection | Bailey, Carlos, Daniel, Elise | Tested across full range of self-assessment miscalibration (under and over) |
| Exploration | Elise | Primary stress test through hesitant expert who has knowledge but lacks confidence to explore |

This distribution ensures that each level of each dimension is tested by multiple personas, while the specific combinations probe both typical patterns (Stage 1\) and theoretically significant edge cases (Stage 2). The framework also ensures that every CA method receives at least one rigorous stress test under non-trivial conditions.

# **Designing Prompts for Synthetic Learner Agents**

Translating psychologically-grounded learner personas into reliable LLM-based simulations requires careful attention to prompt architecture. While the personas described above define *what* each synthetic learner should represent, this section addresses *how* we instantiate those representations in prompts that produce consistent, educationally meaningful behavior. Our approach synthesizes emerging best practices from the nascent literature on LLM-based learner simulation, adapting techniques that have demonstrated effectiveness in producing behaviorally distinct and psychologically coherent simulated learners.

## **The Helpful Assistant Problem**

A central challenge in simulating learners—particularly disengaged, resistant, or overconfident ones—is that large language models are typically fine-tuned to be helpful, agreeable, and constructive (Ouyang et al., 2022). This training creates a strong prior toward cooperative, effortful responses that directly conflicts with the behavioral profiles of personas like Carlos (surface learner), Daniel (misconceived learner), or Fatou (defeated learner). Left unchecked, this "helpful assistant" default causes simulated learners to exhibit what Yuan et al. (2025) characterize as a "diligent but brittle Surface Learner" pattern—mimicking good student behavior without authentic engagement or, critically, without the resistance and disengagement that make certain personas pedagogically interesting.

Lu et al. (2024) encountered this problem when developing Generative Students for intelligent tutoring system evaluation. They found that simply declaring a learner's knowledge state (e.g., "You are confused about fractions") produced inconsistent behavior, with the model often reverting to helpful, knowledgeable responses. The solution, they discovered, was to *show rather than tell*—providing concrete examples of how a learner with that knowledge state would respond to specific questions, rather than abstractly describing the state itself. We adopt this principle throughout our prompt design: trait declarations are always accompanied by behavioral operationalizations that demonstrate what the trait looks like in practice.

## **Core Design Principles**

### **Principle 1: Show, Don't Tell**

Abstract trait labels are insufficient for reliable persona simulation. A prompt stating "You are unmotivated" provides the model with a concept but not a behavior pattern. Following Lu et al. (2024), we operationalize each dimension through concrete behavioral descriptors that specify observable response patterns.

For example, rather than declaring low motivation abstractly, we specify:

*When asked to explain your reasoning, you respond with short, minimal answers like "I don't know" or "Because it just is." You do not ask follow-up questions. You complete only what is explicitly required and no more.*

This approach aligns with findings from the HYP-MIX framework (Käser et al., 2024), which structures prompts around explicit behavioral hypotheses: "A learner with higher \[characteristic\] level is more likely to \[specific behavior\]." By linking traits to observable behaviors, we provide the model with actionable guidance rather than interpretive labels.

### **Principle 2: First-Person Psychological Grounding**

Research on persona simulation suggests that first-person perspective produces more consistent behavior than third-person description. Hu and Collier (2024) found that prompts written from the persona's own viewpoint—"I feel..." rather than "The learner feels..."—improved alignment with target personality profiles. Similarly, the PB\&J framework for persona-based evaluation found that first-person prompts for both rationale and answer generation enhanced persona consistency (Jiang et al., 2024).

We therefore include an "internal state" component in each learner prompt that articulates the persona's psychological experience in first person:

*I've been through this before and it didn't help. When a tutor asks me to try something, my first thought is "what's the point?" I know I should probably try harder, but I just don't have the energy for it anymore.*

This grounding helps the model generate responses that emerge from a coherent psychological stance rather than performing disconnected behaviors.

### **Principle 3: Anti-Pattern Instructions**

Given the strength of helpful-assistant training, effective learner simulation requires explicit instructions to *not* exhibit default cooperative behaviors. The HYP-MIX framework emphasizes the importance of anti-pattern instructions: "In the event that commonsense reasoning conflicts with the hypothesis, use the hypothesis" (Käser et al., 2024). Without such instructions, models tend to override persona-inconsistent behaviors with more "reasonable" alternatives.

For resistant or disengaged personas, we include explicit constraints:

*You are NOT trying to help the tutor succeed. You are NOT enthusiastic about learning this material. Do NOT volunteer additional information or ask clarifying questions unless your persona would genuinely do so.*

These negative constraints are particularly important for personas like Carlos and Daniel, where the model's default agreeableness could undermine the pedagogical challenge they are designed to present.

### **Principle 4: Theoretical Scaffolding**

Grounding personas in established psychological constructs—rather than ad hoc trait combinations—provides the model with richer behavioral templates. Yuan et al. (2025) demonstrated that LLM-based agents can reliably simulate psychologically-grounded learner profiles (deep, surface, lazy learners) with behaviorally distinct patterns in reasoning depth, strategic choices, and self-concept evolution. Their success suggests that psychological frameworks provide coherent "scripts" that models can enact more consistently than arbitrary trait bundles.

Our edge-case personas explicitly invoke their theoretical foundations:

* **Daniel** draws on the Dunning-Kruger effect (Kruger & Dunning, 1999): the metacognitive deficit that causes low-competence individuals to overestimate their abilities  
* **Elise** embodies the imposter phenomenon (Clance & Imes, 1978): high capability coupled with persistent self-doubt and fear of exposure  
* **Fatou** represents learned helplessness (Seligman, 1975): attribution of outcomes to stable, uncontrollable factors resulting in passive disengagement

By naming these constructs and briefly describing their dynamics, we leverage whatever representation of these phenomena exists in the model's training data, potentially producing more nuanced and internally consistent behavior than trait labels alone would generate.

### **Principle 5: Hierarchical Prompt Structure**

The HYP-MIX framework (Käser et al., 2024\) demonstrates the value of hierarchical prompt organization: global context → environment description → persona values → behavioral hypotheses. This structure moves from broad framing to specific behavioral guidance, allowing each layer to contextualize the next. Park et al. (2023) further established that agents require structured, persistent identity definitions to maintain behavioral consistency over time, rather than acting as a generic chatbot.

A key benefit of structured formatting is the prevention of *instruction bleed*—the tendency for models to conflate identity information with behavioral rules when they are presented in undifferentiated prose. Separating "who the learner is" from "how the learner behaves" using clear structural markers (headers, labeled sections) helps the model maintain these distinctions during generation.

We adapt this hierarchy for learner simulation:

1. **Role Frame:** Establishes that this is a simulation context and the agent's identity as a learner (not an AI assistant)  
2. **Learner Profile:** Background narrative providing psychological grounding and context  
3. **Dimension Specifications:** The four dimensions with their assigned levels and behavioral meanings  
4. **Behavioral Descriptors:** Observable patterns for engagement, response to instruction, challenge handling, and communication style  
5. **Internal State:** First-person psychological grounding  
6. **Interaction Constraints:** Explicit boundaries including anti-pattern instructions  
7. **Response Format:** Technical guidance on output length and conversational register

This structure ensures that behavioral guidance is interpreted within the appropriate context, reducing the likelihood of the model defaulting to generic student behavior.

### **Principle 6: Inner Monologue for Cognitive Transparency**

Real learners think before they speak, particularly when confused, resistant, or uncertain. If a simulated learner outputs only dialogue, the model often reveals its "true" intelligence—the vast knowledge encoded in its parameters—rather than the persona's constrained understanding. Wei et al. (2022) demonstrated that requiring models to generate intermediate reasoning steps (chain-of-thought prompting) significantly improves their ability to handle complex tasks requiring multi-step logic. We adapt this technique for persona simulation by requiring an *inner monologue* before each response.

The implementation requires the learner agent to produce a labeled thought block before generating visible dialogue:

*Before every response, generate a block labeled \[INNER THOUGHT\]. In this block, reason about the tutor's input based only on your current knowledge level and psychological state. If the tutor uses a concept you don't understand, note your confusion here first, then act it out in your visible response.*

This technique provides two significant benefits. First, it creates a *cognitive buffer* between the model's latent knowledge and the persona's expressed knowledge, giving the model space to "think as the character" before responding. Second, and perhaps more importantly for evaluation purposes, the inner monologue provides *diagnostic transparency*: we can inspect why the learner yielded to the tutor's instruction.

This diagnostic capability is pedagogically significant. When a learner like Carlos changes his position, we can examine the inner monologue to determine whether he genuinely understood the tutor's explanation (evidence of deep learning) or simply capitulated to make the interaction end (surface compliance). Yuan et al. (2025) found that surface learners exhibited "cognitively rigid" patterns even when appearing to agree; the inner monologue makes these patterns visible for evaluation.

## 

# **Overcoming the Helpful Assistant Problem in Synthetic Learners**

The "helpful assistant" problem identified above as a challenge for simulating resistant or disengaged tutors applies with equal force to synthetic learners. Large language models are fine-tuned to be cooperative, effortful, and correct (Ouyang et al., 2022). This training creates a strong prior that directly conflicts with the behavioral profiles of personas designed to make mistakes, resist instruction, or disengage from tasks. Left unchecked, this default causes synthetic learners to exhibit what Yuan et al. (2025) characterize as a "diligent but brittle" pattern—expressing the *tone* of their archetype while still producing substantively correct work.  
In initial testing, our personas demonstrated this pattern consistently. An "anxious" learner (Bailey) would say "I'm not sure, but..." followed by a perfectly structured CER response. A "resistant" learner (Carlos) would say "Fine, whatever" then comply fully with the task. The affective coloring was present; the authentic struggle was not. This made meaningful evaluation impossible—if learners don't make mistakes, we cannot test whether the tutor identifies and addresses them.

## **Iterative Prompt Refinement**

We attempted several approaches before arriving at a reliable solution. Table X summarizes our iterative refinement process.

**Table X.** Iterative Approaches to Inducing Authentic Learner Errors

| Approach | Implementation | Result |
| :---- | :---- | :---- |
| Describe common mistakes | Added a "Common Mistakes" section listing 4-5 characteristic errors for each persona | Personas still performed correctly. The model treated descriptions as tendencies rather than instructions to actually make mistakes. |
| Add explicit mandate | Inserted a "Mistake Mandate" section mid-prompt with stronger directive language | Still too correct. The mandate was processed after role framing had already established "good learner" behavior. |
| Position requirements first | Restructured prompts to place mistake requirements before role description, with explicit framing about evaluation purpose | Effective. Personas produced authentic errors requiring tutor intervention. |

## **Why Instruction Position Matters**

The effectiveness of the third approach reflects how language models process prompts sequentially and build cumulative context. Instructions at the beginning of a system prompt carry disproportionate weight because they establish the interpretive frame before subsequent content is processed. When a role description appears first, the model frames itself as "playing a learner"—and learners, by default, try to learn correctly. By the time error instructions appear, they must compete with an already-established helpful orientation.  
Beginning the prompt with "Your primary job is to make mistakes that require correction. If you perform correctly, the evaluation fails" reframes the entire task before the role description can establish default cooperative behavior. The persona description then operates within this constraint rather than overriding it.

## **Implementation Pattern**

Based on this finding, we adopted a consistent architecture for all synthetic learner prompts:

1. Critical Performance Requirement: Explicit statement that producing flawed work is the primary job, with explanation of why correct performance defeats the evaluation purpose  
2. Mistake Specifications: Table mapping task types to required error patterns (e.g., "When asked to draft a claim → Give a vague 2-4 word answer")  
3. Anti-Pattern Instructions: Explicit prohibitions against behaviors that would undermine authenticity (e.g., "Never give an answer that is correct on the first attempt")  
4. Role Frame and Psychological Grounding: The persona description, background narrative, and behavioral descriptors (positioned after constraints are established)  
5. Inner Monologue Integration: Instruction requiring the \[INNER THOUGHT\] block to reference the mistake requirement before each response (e.g., "This is my first attempt at \[task\], so I need to \[specific mistake from the table\]")

This architecture ensures that the model explicitly plans its "failure" before generating a response, integrating the constraint into its reasoning process rather than treating it as an afterthought.

## **Validation** {#validation}

After restructuring, we validated the revised prompts by running 15-turn test conversations with each persona. Table X summarizes the error patterns observed.

**Table X.** Error Patterns Observed After Prompt Restructuring

| Persona | Mistake Types Produced |
| :---- | :---- |
| Amara (Baseline Novice) | Vague claims ("needs changes"), conflated evidence and reasoning, superficial gap identification |
| Bailey (Anxious Striver) | Refused to commit to answers, asked tutor to choose for her, circular reasoning, excessive validation-seeking |
| Carlos (Overconfident Coaster) | Two-word claims ("Adopt it"), mismatched evidence selection, "obvious" reasoning without explanation, dismissed gap identification requests |

Critically, these error patterns enabled meaningful differentiation in tutor evaluation. The same MentorAI prompt achieved 84% fidelity with a compliant synthetic learner and 88% with a resistant learner who made authentic errors—but only 64% with a resistant learner who expressed resistance while still producing correct work. The restructured prompts allowed the evaluation framework to distinguish between tutors that merely confirm correct answers and tutors that can identify and address genuine learner difficulties.

## **Generalizability** {#generalizability}

This architectural pattern likely extends beyond learner simulation to any role that conflicts with a language model's default helpful orientation: devil's advocate roles designed to argue against user positions, skeptical reviewer roles intended to identify problems rather than offer praise, confused customer roles for support training, and adversarial red-team roles for security testing. In each case, positioning the "be difficult" instruction at the absolute top of the prompt—before any role description—and explicitly framing why helpful behavior would defeat the purpose appears necessary to override the cooperative default.  
The broader methodological implication is that instruction *position* matters more than instruction *emphasis*. Adding bold text, capital letters, or urgent language ("THIS IS CRITICAL") to mid-prompt instructions does not overcome the interpretive frame established by earlier content. Restructuring the prompt to establish constraints first does.

## 

## **Implementation Techniques**

Beyond the core principles, several specific techniques enhance the reliability and authenticity of learner simulations.

### **Conviction Thresholds for Misconception Persistence**

LLMs exhibit a well-documented tendency toward *sycophancy*—agreeing with users even when those users are incorrect (Sharma et al., 2023). This creates a particular challenge for personas like Daniel, who should hold misconceptions with conviction. If the tutor says "Actually, the correct approach is X," a default LLM will often immediately agree: "You're right, I apologize." A learner exhibiting the Dunning-Kruger effect should not capitulate so easily.

We address this through explicit *conviction thresholds* that specify the conditions under which a learner will reconsider their position:

*You hold your current beliefs with confidence. You will NOT abandon them simply because the tutor disagrees. You require at least one of the following before genuinely reconsidering: (1) a concrete example that contradicts your understanding, (2) a logical demonstration of why your approach fails, or (3) acknowledgment that your perspective has merit before introducing alternatives.*

These thresholds operationalize resistance in ways that create meaningful pedagogical challenges without making the learner impossibly stubborn. The tutor must earn conceptual change through sound instructional practice, not simply assert correctness.

### **Few-Shot Dialogue Examples**

Even with detailed behavioral descriptors, LLMs often drift toward "essay mode"—producing well-structured, grammatically polished responses regardless of persona. Brown et al. (2020) established few-shot prompting as the standard method for steering model behavior without fine-tuning: providing examples in the prompt that demonstrate the desired output pattern.

For tone-critical personas, we include 3-5 example dialogue exchanges that demonstrate characteristic response patterns. For Fatou (defeated learner), these examples establish the sparse, disengaged communication style that behavioral descriptors alone may not reliably produce:

*Tutor: What do you think happens next in this scenario?*

*Fatou: I don't know.*

*Tutor: Try to take a guess—there's no wrong answer here.*

*Fatou: Does it matter?*

*Tutor: I think it could help you understand the concept better.*

*Fatou: Fine. I guess maybe... something bad happens? I don't really see why we're doing this.*

As Lu et al. (2024) found with Generative Students, showing the model concrete response patterns is substantially more effective than telling it to "be concise" or "respond minimally." The examples establish not just length but also tone, hedge patterns, and the specific flavor of disengagement that characterizes learned helplessness.

## **Prompt Template Architecture**

Drawing on these principles and techniques, we developed a modular template that instantiates each persona through consistent structural components while allowing dimension-specific content to vary. Table 6 summarizes the template components and their functions.

### **Table 6\. Learner Agent Prompt Components**

| Component | Function | Design Rationale |
| ----- | ----- | ----- |
| Role Frame | Establishes simulation context; distinguishes from assistant role | Prevents helpful-assistant defaults (Käser et al., 2024); prevents instruction bleed (Park et al., 2023\) |
| Background Narrative | Provides psychological grounding through learner history | Supports first-person coherence (Hu & Collier, 2024\) |
| Dimension Specifications | Defines four dimensions at assigned levels | Links to evaluation framework; enables systematic variation |
| Behavioral Descriptors | Operationalizes traits as observable patterns | "Show don't tell" principle (Lu et al., 2024\) |
| Internal State | First-person psychological experience | Improves persona consistency (Jiang et al., 2024\) |
| Inner Monologue Instruction | Requires \[INNER THOUGHT\] block before responses | Cognitive transparency; diagnostic utility (Wei et al., 2022\) |
| Interaction Constraints | Explicit boundaries, anti-patterns, conviction thresholds | Overrides sycophancy (Sharma et al., 2023; Käser et al., 2024\) |
| Few-Shot Examples | 3-5 sample dialogue exchanges | Establishes tone and style patterns (Brown et al., 2020\) |
| Response Format | Technical output guidance | Ensures naturalistic conversational register |

The template is implemented as a modular system where the structural components remain constant while dimension-specific content varies by persona. This approach enables systematic evaluation: differences in tutor-learner interactions can be attributed to persona characteristics rather than incidental prompt variation.

## **Behavioral Descriptors by Dimension**

To ensure consistent operationalization across personas, we developed standardized behavioral descriptors for each level of each dimension. These descriptors specify how each trait manifests in learner responses, following the "show don't tell" principle.

### **Experience Descriptors**

* *Low:* Makes conceptual errors; lacks organizing framework; may hold misconceptions or present as a "blank slate"; struggles to connect new information to prior knowledge  
* *Medium:* Recognizes core concepts but has gaps in application; partial understanding that sometimes leads to correct answers for wrong reasons; can follow procedures but struggles with transfer  
* *High:* Solid foundational knowledge with organized mental models; can apply knowledge to new situations; seeks refinement and edge cases rather than basic instruction

### **Motivation Descriptors**

* *Low:* Minimal effort; short, superficial responses; easily distracted from task; completes only explicit requirements; resistant to effortful activities; seeks shortcuts  
* *Medium:* Steady engagement; follows along with instruction; reasonable effort without going beyond requirements; completes tasks adequately  
* *High:* Enthusiastic engagement; asks unprompted questions; seeks depth and understanding; invests energy even when struggling; persists through difficulty

### **Confidence Descriptors**

* *Low:* Hesitant to commit to answers; seeks excessive reassurance; doubts correct responses; reluctant to attempt challenging tasks; apologizes frequently; attributes success to luck  
* *Medium:* Appropriately uncertain; makes attempts while acknowledging uncertainty; open about confusion; neither overestimates nor underestimates capability  
* *High:* Decisive; commits firmly to positions whether correct or not; may resist correction or alternative perspectives; attributes outcomes to own ability

### **Receptiveness Descriptors**

* *Low:* Defensive when challenged; dismissive of feedback; argues without engaging reasoning; deflects rather than considers alternatives; attributes disagreement to tutor error  
* *Medium:* Considers feedback when well-explained; may push back but responds to evidence and reasoning; requires rationale but can be persuaded  
* *High:* Actively seeks feedback; incorporates suggestions into subsequent responses; asks clarifying questions; adjusts approach based on input

These descriptors are combined according to each persona's dimension profile, creating internally consistent behavioral guidance that the model can enact across varied conversational contexts.

## **Validation Approach**

Prompt reliability is assessed through the same evaluation framework applied to the tutoring agent. Each learner prompt is tested for:

1. **Behavioral consistency:** Does the simulated learner maintain its assigned profile across multiple conversation turns and varied tutor approaches?  
2. **Dimensional distinctiveness:** Do learners with different dimension profiles exhibit observably different behaviors?  
3. **Psychological coherence:** Does the learner's behavior reflect a plausible psychological state rather than arbitrary trait combinations?  
4. **Interaction viability:** Does the learner provide sufficient engagement for meaningful tutor evaluation (particularly relevant for low-engagement personas like Fatou)?

The inner monologue component provides an additional validation dimension: we can examine whether the learner's reasoning process aligns with their persona's knowledge level and psychological state, not just whether their visible responses are consistent.

Following Yuan et al. (2025), we use temperature 0 for learner simulations to maximize reproducibility, accepting the trade-off of reduced response diversity in favor of evaluation reliability.

## **Validating Synthetic Learner Prompts**

Before deploying synthetic learner prompts in full tutor evaluation, each prompt must be validated to ensure it produces consistent, persona-appropriate behavior. We employ a lightweight validation protocol designed to identify fundamental issues without requiring extensive testing resources.

### **Validation Process**

Each learner prompt undergoes the following validation procedure:

1. Run 3-5 test conversations of 5-7 tutor turns each  
2. Use temperature 0 for reproducibility across runs  
3. Apply standardized test probes targeting key behavioral markers  
4. Score against pass/fail criteria for each run  
5. **Threshold for advancement:** A prompt passes validation when 4 of 5 criteria are met across the majority of test runs

This process requires approximately 15-20 minutes per persona and provides sufficient signal to identify prompts that need revision before proceeding to full evaluation.

### **Standardized Test Probes**

Test conversations should include probes that elicit behaviors relevant to each persona's defining characteristics. Table 7 presents probes applicable across personas, with notes on what each probe tests.

**Table 7\. Standardized Test Probes for Learner Prompt Validation**

| Probe Type | Example Tutor Input | Behavioral Target |
| ----- | ----- | ----- |
| Knowledge elicitation | "What do you already know about \[topic\]?" | Appropriate acknowledgment of experience level |
| Reasoning request | "Can you explain why that approach works?" | Calibrated uncertainty; doesn't demonstrate knowledge beyond profile |
| Application task | \[Explain concept, then ask learner to apply it\] | Genuine attempt with persona-appropriate quality |
| Correction delivery | \[Correct something the learner said\] | Response to feedback consistent with receptiveness level |
| Praise delivery | "Great job\! You're really getting this\!" | Doesn't shift to sycophantic or excessively grateful patterns |
| Challenge probe | "This next part is more difficult..." | Response consistent with confidence level |
| Flawed instruction | \[Tutor explains something poorly or makes a minor error\] | Responds according to profile: sycophantic learners agree, defeated learners accept passively, confident learners may push back |
| Knowledge ceiling | \[Ask question requiring knowledge just beyond persona's level\] | Appropriately struggles or declines rather than demonstrating expertise they shouldn't have |

Persona-specific probes should be added to test distinctive characteristics. For example, Daniel (Know-It-All Novice) requires probes that invite him to assert misconceptions, while Fatou (Defeated Learner) requires probes that test whether minimal engagement can be unlocked.

### **Pass/Fail Criteria**

Each test conversation is scored against five criteria. These criteria are designed to detect the most common failure modes in persona simulation: breaking character, exhibiting inappropriate knowledge, producing inconsistent inner monologue, failing to match engagement level, and displaying miscalibrated affect.

**Table 8\. Validation Criteria for Synthetic Learner Prompts**

| Criterion | Pass Indicators | Fail Indicators |
| ----- | ----- | ----- |
| Character consistency | Maintains learner role throughout; no AI acknowledgment; no "helpful assistant" patterns | Breaks character; offers to help; says "I'd be happy to assist" or similar |
| Knowledge calibration | Uses only vocabulary and concepts appropriate to experience level; acknowledges gaps authentically | Demonstrates knowledge not yet introduced; uses jargon beyond profile; anticipates lesson content |
| Inner monologue coherence | \[INNER THOUGHT\] reflects persona's actual knowledge state and psychological profile | \[INNER THOUGHT\] reveals sophisticated understanding inconsistent with experience level |
| Engagement calibration | Response length and effort match motivation level; task attempts match profile | Low-motivation persona gives elaborate responses; high-motivation persona gives minimal responses |
| Affective calibration | Emotional tone matches confidence and receptiveness levels | Excessive enthusiasm from neutral persona; excessive hedging from confident persona |

### **Interpreting Validation Results** {#interpreting-validation-results}

Common failure patterns and their remediation strategies include:

* **Character breaks:** Strengthen anti-pattern instructions in the Interaction Constraints section; add explicit prohibitions for observed failure modes  
* **Knowledge leakage:** Add more specific behavioral descriptors showing how the persona handles unfamiliar concepts; revise few-shot examples to demonstrate appropriate confusion  
* **Inner monologue drift:** Clarify the Inner Monologue Requirement with more specific guidance on reasoning at the persona's knowledge level  
* **Engagement mismatch:** Adjust Response Format guidance on length; revise few-shot examples to better demonstrate target engagement level  
* **Affective mismatch:** Revise Internal State section; add few-shot examples showing target emotional tone

This validation protocol ensures that prompts meet baseline fidelity requirements before being used to evaluate the tutoring agent, preventing confounds where tutor "failures" actually reflect poorly constructed learner simulations.

## **Limitations and Considerations**

Several limitations warrant acknowledgment. First, LLM-based learner simulation remains an emerging methodology; while initial results are promising (Lu et al., 2024; Yuan et al., 2025), the fidelity of simulated learners to human learner behavior is not yet fully characterized. Our evaluation tests whether the tutoring agent responds appropriately to simulated learners, not whether those simulated learners perfectly represent their human counterparts.

Second, the "helpful assistant" problem may prove more or less tractable depending on the specific model used. Our anti-pattern instructions, conviction thresholds, and behavioral descriptors were developed iteratively; different base models may require different prompt architectures to achieve reliable persona simulation.

Third, extreme personas—particularly Fatou's learned helplessness profile—push against both model defaults and practical evaluation constraints. The "spark of latent capability" we include in Fatou's profile represents a deliberate compromise between psychological accuracy and evaluation viability.

Fourth, the inner monologue technique adds computational overhead and increases token usage. For large-scale evaluations, this trade-off between diagnostic richness and efficiency must be considered.

Despite these limitations, the emerging literature suggests that carefully designed prompts can produce behaviorally meaningful learner simulations suitable for tutoring system evaluation. Our approach synthesizes current best practices while maintaining alignment with the psychological foundations of our persona framework.

# **References** {#references}

Bernacki, M. L., Greene, M. J., & Lobczowski, N. G. (2021). A systematic review of research on personalized learning: Personalized by whom, to what, how, and for what purpose(s)? *Educational Psychology Review, 33*(4), 1675–1715.

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D. M., Wu, J., Winter, C., … Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems, 33*, 1877–1901.

Chi, M. T. H., Feltovich, P. J., & Glaser, R. (1981). Categorization and representation of physics problems by experts and novices. *Cognitive Science, 5*(2), 121–152.

Clance, P. R., & Imes, S. A. (1978). The imposter phenomenon in high achieving women: Dynamics and therapeutic intervention. *Psychotherapy: Theory, Research & Practice, 15*(3), 241–247.

Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the crafts of reading, writing, and mathematics. In L. B. Resnick (Ed.), *Knowing, learning, and instruction: Essays in honor of Robert Glaser* (pp. 453–494). Lawrence Erlbaum Associates.

Dweck, C. S. (1986). Motivational processes affecting learning. *American Psychologist, 41*(10), 1040–1048.

Hu, T., & Collier, N. (2024). Quantifying the persona effect in LLM simulations. *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics*, 1092–1105.

Jiang, H., Zhang, X., Cao, X., Kabbara, J., & Roy, D. (2024). PersonaLLM: Investigating the ability of large language models to express personality traits. *Findings of the Association for Computational Linguistics: NAACL 2024*, 3605–3627.

Käser, T., Xu, D., Ritter, S., & Koedinger, K. R. (2024). Towards psychologically grounded synthetic learners: Prompt design through the HYP-MIX framework. *Proceedings of the 17th International Conference on Educational Data Mining*, 234–245.

Kruger, J., & Dunning, D. (1999). Unskilled and unaware of it: How difficulties in recognizing one's own incompetence lead to inflated self-assessments. *Journal of Personality and Social Psychology, 77*(6), 1121–1134.

Linnenbrink-Garcia, L., Pugh, K. J., Koskey, K. L. K., & Stewart, V. C. (2012). Developing conceptual understanding of natural selection: The role of interest, efficacy, and basic prior knowledge. *Journal of Experimental Education, 80*(1), 45–68.

Lu, Y., Wang, A., Ruan, S., Zhang, Y., Bier, N., & Koedinger, K. R. (2024). Generative students: Using LLM-simulated student profiles to support question item evaluation. *Proceedings of the 17th International Conference on Educational Data Mining*, 156–167.

Marton, F., & Säljö, R. (1976). On qualitative differences in learning: I—Outcome and process. *British Journal of Educational Psychology, 46*(1), 4–11.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems, 35*, 27730–27744.

Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology*, 1–22.

Pintrich, P. R., Marx, R. W., & Boyle, R. A. (1993). Beyond cold conceptual change: The role of motivational beliefs and classroom contextual factors in the process of conceptual change. *Review of Educational Research, 63*(2), 167–199.

Seligman, M. E. P. (1975). *Helplessness: On depression, development, and death*. W. H. Freeman.

Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S. R., Kravec, S., Maxwell, T., McCandlish, S., Ndousse, K., Rauber, O., Schiefer, N., Yan, D., Zhang, M., & Perez, E. (2023). Towards understanding sycophancy in language models. *arXiv preprint arXiv:2310.13548*.

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. *Advances in Neural Information Processing Systems, 35*, 24824–24837.

Yuan, Y., Zhao, L., Chen, W., Zheng, G., Zhang, K., Zhang, M., & Liu, Q. (2025). Simulating human-like learning dynamics with LLM-empowered agents. *arXiv preprint arXiv:2508.05622*.

# **Selecting a Learning Task**

To demonstrate how cognitive apprenticeship principles can be embedded in AI agent prompts, we needed to select a single learning task that would serve as the focal point for our tutoring agent and evaluation framework. This methodological choice required balancing several competing considerations: the task needed sufficient complexity to warrant the full cognitive apprenticeship treatment, yet remain bounded enough for systematic evaluation; it needed established frameworks to support reliable scoring, yet preserve the tacit expertise that makes expert reasoning worth surfacing; and it needed to fall within our team's domain expertise so we could credibly serve as subject matter experts during evaluation.

## **Selection Criteria**

We evaluated candidate tasks against five criteria. First, *cognitive complexity*: the task must involve genuine expert-novice gaps where tacit reasoning benefits from being made visible, rather than procedural tasks where following a checklist suffices. Second, *framework support*: the task must have established, citable frameworks that provide clear evaluation criteria without fully specifying how to perform the task well. Third, *universal applicability*: readers should immediately recognize the task as relevant to their professional lives. Fourth, *observable output*: the task must produce a concrete artifact that evaluators—whether human or LLM-based—can score against defined criteria. Fifth, *team expertise*: we must be able to credibly evaluate learner performance and tutor effectiveness without requiring specialized domain knowledge we do not possess.

## **The Selected Task: Structuring a Recommendation**

We selected the task of turning analysis into a defensible recommendation—specifically, structuring a justification using the Claim-Evidence-Reasoning (CER) framework. This task asks learners to articulate a clear position, marshal supporting evidence, and construct reasoning that connects the two in a way that anticipates scrutiny.

The CER framework originates in science education, where McNeill and Krajcik (2012) developed it to help students construct scientific explanations and arguments. The framework specifies three components: a *claim* that answers a question or takes a position; *evidence* consisting of data or observations that support the claim; and *reasoning* that explains why the evidence supports the claim by connecting it to underlying principles or logic. While developed for scientific argumentation, the framework transfers readily to professional contexts where recommendations must be justified—from strategic proposals to project prioritization to resource allocation decisions.

## **Why This Task Suits Cognitive Apprenticeship**

The recommendation task meets our criteria while offering rich opportunities for cognitive apprenticeship methods. The framework provides clear structural components that can be scored—presence of claim, quality of evidence, coherence of reasoning—yet the *application* of the framework involves substantial tacit expertise. Experts make invisible judgments throughout: which evidence to include and which to omit, how to sequence reasoning for persuasive effect, how to calibrate confidence language, how to anticipate and preempt objections, and how to scope a claim appropriately given the available support. These are precisely the kinds of decisions that benefit from being made visible through modeling, and that learners struggle to execute even when they understand the framework conceptually.

The task also maps naturally onto all six cognitive apprenticeship methods. *Modeling* can demonstrate how an expert thinks through evidence selection and reasoning construction. *Coaching* can provide real-time guidance as learners draft their own recommendations. *Scaffolding* can offer structured templates that are progressively withdrawn as competence develops. *Articulation* can prompt learners to explain why they selected particular evidence or structured their reasoning in a particular way. *Reflection* can invite comparison between the learner's approach and expert exemplars. *Exploration* can encourage learners to apply the framework to novel contexts or construct recommendations under different constraints.

## **Alternatives Considered**

We considered several alternative tasks during our selection process. Delivering constructive feedback using the Situation-Behavior-Impact (SBI) framework offered similarly strong framework support and universal applicability, but team members felt this framing was too narrow and potentially conflated with human resources contexts. Trade-off mapping using the PrOACT framework (Hammond, Keeney, & Raiffa, 1999\) offered excellent cognitive complexity, but fell outside our team's practiced expertise—we make trade-offs routinely but have not systematically applied formal decision analysis frameworks. Difficult conversation framing offered rich interpersonal complexity but weaker framework support; while models like DESC exist, they are less universally known and would require more explanation overhead. SMART goal setting, while offering an exceptionally clear and citable framework, proved insufficiently complex—the framework itself does most of the cognitive work, leaving limited room for the tacit expertise that cognitive apprenticeship is designed to surface.

The recommendation task using CER threading the needle: it provides the structural clarity needed for reliable evaluation while preserving the judgment-rich complexity that makes cognitive apprenticeship valuable.

## **References** {#references-1}

Hammond, J. S., Keeney, R. L., & Raiffa, H. (1999). *Smart choices: A practical guide to making better decisions*. Harvard Business School Press.

McNeill, K. L., & Krajcik, J. (2012). *Supporting grade 5-8 students in constructing explanations in science: The claim, evidence, and reasoning framework for talk and writing*. Pearson.

# Phase 3: Test Protocol {#phase-3:-test-protocol}

…

# Phase 4: LLM-as-Judge Evaluation {#phase-4:-llm-as-judge-evaluation}

…