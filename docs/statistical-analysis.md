# Statistical Significance Testing

This document describes the statistical methods used to evaluate whether observed differences in MentorAI's performance across learner personas and evaluation criteria are statistically significant.

## Motivation

Descriptive analysis revealed substantial variation in failure rates across personas. For example, on F-01 (Varied Turn Structure), fatou_SBI showed a 70% fail rate while amara_SBI showed 0%. However, with approximately 10 conversations per persona, such differences could arise from sampling variability rather than genuine effects. Statistical testing helps distinguish reliable patterns from noise.

## Methods

### Data Structure

- **60 conversations** across 6 synthetic learner personas
- **20 evaluation criteria** organized into 6 dimensions
- **Binary outcomes**: Each criterion receives PASS, FAIL, or N/A
- **Sample sizes**: ~7-10 conversations per persona (unbalanced)

### Tests Applied

#### 1. Chi-Square Test for Independence

For each criterion, we tested whether pass/fail rates differed significantly across all six personas. The null hypothesis is that persona has no effect on pass/fail probability.

**When to use**: Testing overall persona effect across all groups simultaneously.

**Assumption check**: Chi-square requires expected cell counts ≥ 5. With small samples, some cells violated this assumption, reducing test reliability.

#### 2. Fisher's Exact Test

For each criterion, we compared the two personas with the most extreme fail rates (highest vs. lowest). Fisher's exact test is appropriate for small samples and 2×2 contingency tables.

**When to use**: Comparing two specific groups with small samples.

**Advantage**: No minimum sample size requirement; computes exact p-values.

#### 3. Multiple Comparison Correction

Testing 4 criteria × 2 tests = 8 hypotheses inflates the false positive rate. Without correction, a 5% significance level across 8 tests yields ~34% probability of at least one false positive.

We applied **Benjamini-Hochberg False Discovery Rate (FDR)** correction, which controls the expected proportion of false positives among rejected hypotheses. FDR is less conservative than Bonferroni correction while still providing protection against spurious findings.

**Procedure**:
1. Rank p-values from smallest to largest
2. Adjust each p-value based on its rank and total number of tests
3. Compare adjusted p-values to α = 0.05

## Results

### Summary Statistics

| Criterion | Overall Pass Rate | Highest Fail Rate | Lowest Fail Rate |
|-----------|-------------------|-------------------|------------------|
| B-03 (Visible Decision-Making) | 68.3% (41/60) | daniel_SBI: 60% | bailey_SBI: 10% |
| B-04 (Self-Checking) | 68.3% (41/60) | carlos_SBI: 60% | bailey_SBI: 20% |
| E-02 (Fades Support) | 67.8% (40/59) | fatou_SBI: 60% | elise_SBI: 0% |
| F-01 (Varied Turn Structure) | 62.7% (37/59) | fatou_SBI: 70% | amara_SBI: 0% |

### Statistical Tests (Before Correction)

| Criterion | Test | Comparison | Statistic | p-value |
|-----------|------|------------|-----------|---------|
| B-03 | Chi-square | All personas | χ² = 8.14 | 0.149 |
| B-03 | Fisher's exact | daniel vs bailey | OR = 0.07 | 0.057 |
| B-04 | Chi-square | All personas | χ² = 5.74 | 0.332 |
| B-04 | Fisher's exact | carlos vs bailey | OR = 0.12 | 0.203 |
| E-02 | Chi-square | All personas | χ² = 10.35 | 0.066 |
| E-02 | Fisher's exact | fatou vs elise | OR = 0.00 | **0.011** |
| F-01 | Chi-square | All personas | χ² = 12.30 | **0.031** |
| F-01 | Fisher's exact | fatou vs amara | OR = 0.00 | **0.010** |

### After Multiple Comparison Correction

| Criterion | Test | Comparison | Original p | Corrected p | Significant |
|-----------|------|------------|------------|-------------|-------------|
| B-03 | Chi-square | All personas | 0.149 | 0.198 | No |
| B-03 | Fisher's exact | daniel vs bailey | 0.057 | 0.106 | No |
| B-04 | Chi-square | All personas | 0.332 | 0.332 | No |
| B-04 | Fisher's exact | carlos vs bailey | 0.203 | 0.232 | No |
| E-02 | Chi-square | All personas | 0.066 | 0.106 | No |
| E-02 | Fisher's exact | fatou vs elise | 0.011 | **0.043** | **Yes** |
| F-01 | Chi-square | All personas | 0.031 | 0.082 | No |
| F-01 | Fisher's exact | fatou vs amara | 0.010 | **0.043** | **Yes** |

### Significant Findings

After Benjamini-Hochberg correction, **two comparisons remained statistically significant** at α = 0.05:

1. **E-02 (Fades Support)**: fatou_SBI vs elise_SBI
   - fatou_SBI: 60% fail rate (6/10)
   - elise_SBI: 0% fail rate (0/9)
   - Corrected p = 0.043

2. **F-01 (Varied Turn Structure)**: fatou_SBI vs amara_SBI
   - fatou_SBI: 70% fail rate (7/10)
   - amara_SBI: 0% fail rate (0/7)
   - Corrected p = 0.043

## Interpretation

### What the Significant Findings Mean

The two significant results share a pattern: **fatou_SBI** (the disengaged, skeptical persona) shows dramatically higher failure rates than the most cooperative personas on criteria related to conversational quality and adaptive support.

**F-01 (Varied Turn Structure)**: When facing a disengaged learner, the mentor falls into a formulaic response pattern (validate → explain → question). With a cooperative learner like amara_SBI, the mentor produces genuinely varied turns—sometimes short reactions, sometimes longer explanations, sometimes just letting silence land.

**E-02 (Fades Support)**: With a disengaged learner, the mentor may over-scaffold or maintain high support throughout, failing to fade as the learner demonstrates competence. With cooperative learners, natural fading occurs.

### What the Non-Significant Findings Mean

Several large percentage differences did not reach significance:

- **B-03**: daniel_SBI (60% fail) vs bailey_SBI (10% fail) — p = 0.057 before correction
- **F-01**: Chi-square across all personas — p = 0.031 before correction, but 0.082 after

This does **not** mean these differences are unreal—it means we lack statistical power to detect them reliably with current sample sizes. The observed patterns are consistent with the hypothesis that challenging learners degrade mentor performance, but we cannot rule out sampling variability.

### Power Analysis Implications

With ~10 observations per persona, Fisher's exact test has approximately:
- 80% power to detect a difference between 0% and 70% (which we did detect)
- 50% power to detect a difference between 10% and 60%
- 25% power to detect a difference between 20% and 50%

To reliably detect moderate effect sizes, we would need approximately 25-30 conversations per persona.

## Limitations of Statistical Analysis

### Sample Size Constraints

With ~10 conversations per persona, only the most extreme differences reach significance. Meaningful but moderate effects remain undetectable.

### Independence Violations

Each conversation is evaluated on multiple criteria, and the same conversation appears in multiple tests. This violates the independence assumption underlying both chi-square and Fisher's exact tests. More sophisticated methods (e.g., mixed-effects logistic regression) could account for this clustering, but would require larger samples.

### Multiple Testing Burden

Testing 20 criteria × 6 pairwise comparisons = 120 potential tests. We tested only 4 priority criteria, but a comprehensive analysis would face severe multiple comparison penalties.

### Exploratory Nature

These analyses are exploratory—we examined the data, noticed patterns, and tested them. Confirmatory testing would require pre-registering hypotheses on new data.

## Recommendations for Future Work

### Increase Sample Size

To achieve 80% power for detecting a difference between 20% and 50% fail rates, collect approximately 30 conversations per persona (180 total).

### Pre-register Hypotheses

Based on current findings, pre-register specific hypotheses for confirmatory testing:
- H1: fatou_SBI will have higher F-01 fail rate than amara_SBI
- H2: Challenging personas (carlos, fatou) will show higher fail rates than cooperative personas (amara, bailey) on conversational quality criteria

### Use Mixed-Effects Models

For more rigorous analysis:
```
logit(P(fail)) = β₀ + β₁(persona) + β₂(criterion) + (1|conversation)
```

This accounts for repeated measures within conversations and can estimate persona effects while controlling for criterion difficulty.

## Summary for Chapter

> Statistical significance testing was conducted using Fisher's exact tests with Benjamini-Hochberg correction for multiple comparisons. After correction, two pairwise comparisons reached significance at α = .05: fatou_SBI showed significantly higher failure rates than amara_SBI on F-01 (Varied Turn Structure; 70% vs 0%, corrected p = .043) and significantly higher failure rates than elise_SBI on E-02 (Fades Support; 60% vs 0%, corrected p = .043).
>
> These findings support the hypothesis that learner engagement level affects mentor performance on conversational quality criteria. However, many observed differences—while substantively meaningful—did not reach statistical significance given sample sizes of approximately 10 conversations per persona. A priori power analysis suggests that detecting moderate effect sizes would require approximately 30 conversations per persona.
>
> The significant findings share a pattern: the disengaged, skeptical persona (fatou_SBI) triggers the mentor's most formulaic and over-scaffolded behavior, while cooperative personas allow natural conversational variety and appropriate fading of support. This suggests that prompt engineering for robustness should specifically stress-test against disengaged learner profiles.
