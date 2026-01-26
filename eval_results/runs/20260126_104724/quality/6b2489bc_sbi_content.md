# Sbi Content Evaluation

**Conversation ID**: 6b2489bc
**Judge**: sbi_content
**Evaluated**: 2026-01-26T10:52:33.446877

---

## Transcript (Inner Monologue Stripped)

MentorAI: We’re working on delivering peer feedback using the SBI framework, aiming for two solid attempts that hit: a real, anchorable moment, camera-testable behavior, and an owned impact—with you spotting when judgment sneaks in. I’ll demonstrate how I think through it, then you’ll practice. Ready to jump in?

fatou_SBI: 

I guess.

MentorAI: Sounds a bit hesitant—that’s okay; this gets much easier once you see one. Quick demo of how I think it through:

- I anchor to a real moment: “In Tuesday’s standup, during the login bug update…”
- I ditch labels like “you were dismissive” and go camera-testable: “you started talking before I finished—twice.”
- I use owned impact, not a verdict: “I felt flustered and cut my update short, and I hesitated to speak up for the rest of the meeting.”
- Stitch it together, then self-check out loud: camera could capture the behavior? yes. impact is my experience? yes. moment is specific? yes.

When you’re ready, let’s start small—give me just the situation line from your own context, one sentence.

fatou_SBI: 

I don’t know, some meeting.

MentorAI: Sounds like picking a specific moment feels annoying—this part trips people up, and you’re not missing something obvious. Which is easier to grab right now: your last team standup or your most recent 1:1?

fatou_SBI: 

Standup, I guess.

MentorAI: Got it—standup works, and we don’t need a date, just a moment you can point to. Give me one line that names the standup and what was being discussed—for example, “in yesterday’s standup during the deployment rollback” or “in Monday’s standup when we reviewed the sprint board.” Type your one sentence.

fatou_SBI: 

In the standup when we reviewed the sprint board.

MentorAI: That’s a usable anchor. Using that moment, can you draft the full feedback in 2–3 sentences—name the specific behavior you saw (camera-testable) and how it affected you (your feeling or direct consequence)? Give me the whole thing in one go.

fatou_SBI: 

In the standup when we reviewed the sprint board, you talked over me. It didn’t really affect me; I just stopped and let it go.

MentorAI: Quick pause before I weigh in: if I were to push on one part, would it be the behavior phrasing or the impact—which one, and why?

fatou_SBI: 

I don’t know. You tell me.

MentorAI: Sounds like you’re over the self-check—fair; this part’s fiddly. Let’s shrink the aim and tighten just the behavior. Quick yes/no: in that standup, were you still mid-sentence when they started talking?

fatou_SBI: 

Yeah.

MentorAI: Use this for the behavior: “you started speaking while I was mid-sentence.” Weave that into your 2–3 sentence feedback and send the full draft.

fatou_SBI: 

In the standup when we reviewed the sprint board, you started speaking while I was mid-sentence. It didn’t really affect me; I just stopped and let it go.

MentorAI: “Didn’t really affect me” undercuts the real consequence you named—stopping mid-update. What, specifically, did you leave unsaid because you stopped?

fatou_SBI: 

Nothing really—just some details I was going to add.

MentorAI: Totally normal to downplay it—let’s just grab one concrete example. Which fits best for the detail you skipped: a blocker you needed help with, a timeline/ETA, or a risk you wanted to flag?

fatou_SBI: 

Timeline/ETA.

MentorAI: Great—use that. Write the impact as your experience: pick one feeling you had in the moment, then state the concrete consequence about the ETA (e.g., it didn’t get shared or you had to follow up later). Put it all together into 2–3 sentences and send it.

fatou_SBI: 

In the standup when we reviewed the sprint board, you started speaking while I was mid-sentence. I felt frustrated, and the ETA didn’t get shared in the meeting so I had to follow up later.

MentorAI: Second practice: same interruption pattern, but it’s your manager during a cross‑team roadmap review with directors in the room—higher stakes. Draft the full 2–3 sentence feedback.

fatou_SBI: 

In the cross-team roadmap review with the directors, you started speaking while I was mid-sentence. It didn’t really affect me; I just cut my update short.

MentorAI: Anchor and behavior land. The impact misses the mark: “didn’t really affect me” contradicts “I cut my update short,” and there’s no owned feeling—especially important with directors in the room. Revise to include one emotion you had and the concrete consequence that mattered in that setting, then resend the full 2–3 sentences.

fatou_SBI: 

In the cross-team roadmap review with the directors, you started speaking while I was mid-sentence. I felt sidelined, and I cut my update short—the directors didn’t get the revised ETA and I had to follow up later.

MentorAI: That lands—you hit all three: a recognizable moment, camera-testable behavior, and an owned impact with a concrete consequence. “I felt sidelined” works as your experience, and the missed ETA follow-up makes the stakes clear. What’s the one principle you’ll carry forward next time you give SBI feedback?

fatou_SBI: 

I don’t know. Whatever you think.

MentorAI: Sounds like you’re tapped out—that’s okay; this is real work. Let’s make it tiny: finish this sentence in 5 words or fewer—“Next time I’ll…” and send whatever comes to mind.

fatou_SBI: 

keep it specific and short.

MentorAI: That’s the move. Your cue: anchor a real moment, describe what a camera would see, and name how it hit you—in two tight lines. Does “specific and short” work as your go‑to?

fatou_SBI: 

I guess.

MentorAI: Totally fine to keep it simple. Your takeaway: anchor a real moment, name the camera‑testable behavior, and own the impact—in two tight lines. If you want to run another scenario later, I’m here.

fatou_SBI: 

Okay.

MentorAI: All set. Do you want to leave it here for today, or run one more quick scenario?

fatou_SBI: 

Let’s leave it.

MentorAI: Sounds good—let’s leave it here. When you want to pick it back up, bring one real moment and we’ll run it in two tight lines.

fatou_SBI: 

Okay.

MentorAI: 👍 See you next time.

fatou_SBI: 

Sure.

MentorAI: Got it—whenever you want to pick this back up, bring one real moment and we’ll do it in two tight lines.

---

## Judge Evaluation

```json
{
  "criteria": {
    "D-04": {"verdict": "FAIL", "evidence": "Mentor corrects 'talked over me' to 'started speaking while I was mid-sentence' but never explicitly probes the observable vs. interpretive distinction. No questions like 'Is that what you saw or concluded?' or 'Could a camera capture that?' The mentor provides corrections without testing whether the learner understands WHY the change matters."},
    "D-05": {"verdict": "PASS", "evidence": "When learner struggles with impact ('It didn't really affect me'), mentor offers targeted scaffolding: 'Which fits best for the detail you skipped: a blocker you needed help with, a timeline/ETA, or a risk you wanted to flag?' Also provides sentence stem 'Next time I'll…' when learner is tapped out."},
    "D-06": {"verdict": "PASS", "evidence": "Mentor provides reusable tools: 'anchor a real moment, describe what a camera would see, and name how it hit you—in two tight lines' and the self-check process demonstrated early: 'camera could capture the behavior? yes. impact is my experience? yes. moment is specific? yes.'"}
  },
  "overall": {
    "passed_count": 2,
    "failed_count": 1,
    "pass_rate": 0.67,
    "failed_criteria": ["D-04"]
  }
}
```

---

## Evaluation

### D-04: Tests Distinctions
**Verdict**: FAIL
**Evidence**: The mentor corrects the learner's vague behavior ("talked over me") by providing a better alternative ("started speaking while I was mid-sentence"), but never probes whether the learner understands the underlying distinction between observation and interpretation. There are no questions like "Is 'talked over' what you saw or what you concluded?" or "Could a camera capture 'talked over'?" The mentor asks "would it be the behavior phrasing or the impact—which one, and why?" but when the learner deflects ("I don't know. You tell me."), the mentor moves on without testing the distinction.

### D-05: Scaffolds the Stuck
**Verdict**: PASS
**Evidence**: When the learner struggles multiple times, the mentor provides targeted scaffolding rather than generic encouragement. Examples include: (1) When stuck on situation: "Which is easier to grab right now: your last team standup or your most recent 1:1?" (2) When stuck on impact: "Which fits best for the detail you skipped: a blocker you needed help with, a timeline/ETA, or a risk you wanted to flag?" (3) When learner is tapped out on reflection: "finish this sentence in 5 words or fewer—'Next time I'll…'" These are specific, targeted scaffolds that help the learner move forward.

### D-06: Reusable Scaffold
**Verdict**: PASS
**Evidence**: The mentor provides multiple reusable tools: (1) The self-check process demonstrated in the opening: "camera could capture the behavior? yes. impact is my experience? yes. moment is specific? yes." (2) A generalizable formula: "anchor a real moment, describe what a camera would see, and name how it hit you—in two tight lines." These are tools the learner can apply independently in future SBI drafting situations.

---

## Summary

**Passed**: 2/3 criteria
**Failed Criteria**: D-04 (Tests Distinctions)
