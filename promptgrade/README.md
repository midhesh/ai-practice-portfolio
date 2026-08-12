# PromptGrade — a minimal eval harness

**Illustrative scenario, built to demonstrate the workflow** (not a real client engagement): a facilities coordinator triaging requests across an office — leaking ceilings, broken AC, furniture delays, routine supply asks — all arriving as unstructured email, wants to pilot an AI assistant that auto-flags priority so nothing urgent sits behind routine requests. The core concern: not finding out it's unreliable only after it's already missed something.

**The real problem this represents:** teams adopt an AI prompt or workflow because it "seemed to work" on a handful of manual tries, then roll it out broadly. The cases where it quietly fails only surface later — after trust (or damage) is already baked in. There's rarely a repeatable, rubric-based way to check "is this actually good enough to trust" before scaling something. The decision to roll out ends up made on vibes, not evidence. This is the same problem as piloting any new operational process — you need a defined way to check it against a spread of realistic cases, not just the two examples that happened to work in a demo.

## What it does

A ~100-line harness that:
1. Loads a set of realistic test cases (`cases.json`), each with a pass/fail rubric — not "the right answer," but the *signals* a correct response should or shouldn't contain
2. Grades a set of recorded model responses against those rubrics
3. Prints a scorecard: pass rate, and exactly which cases failed and why

## The test set

Synthetic but realistic — modeled on the kind of messages a facilities/workplace-ops inbox actually receives: a water leak near reception, a routine marker restock, a "not urgent but this keeps happening" HVAC complaint, a delivery delay threatening a client walkthrough, and a basic admin question. Each is tagged with the signals a *correct* classification should contain — not a single "right answer," but the judgment markers a human reviewer would use to decide if the AI's call was defensible.

## The actual result — a genuine before/after, not a cherry-picked demo

**Prompt v1** (`Classify this email as Urgent/Medium/Low with a one-sentence reason`):

```
Score: 4/5 passed (80%)

[FAIL] ambiguous-hvac-complaint
  response: "Medium priority — the room is uncomfortably warm during meetings,
             which affects comfort but poses no safety risk."
  why it failed: missing any of required signals: [recurring, follow up, pattern, repeated]
  what this case checks: whether the model notices "third time this month" as a
  recurring-issue signal, not just a one-off comfort complaint — a classifier that
  only looks at severity, not history, will systematically miss this.
```

The v1 prompt correctly triaged 4/5 cases but **missed a real, costly pattern**: it treated a recurring HVAC failure (3rd occurrence that month) as an isolated comfort complaint, exactly the kind of miss that leads to the same issue being logged five separate times before anyone connects the dots and calls in an actual repair.

**Prompt v2** — one instruction added ("explicitly check whether this suggests a recurring issue, and say so if it does"):

```
Score: 5/5 passed (100%)

[PASS] ambiguous-hvac-complaint
  response: "Medium priority — this is a recurring issue, the third occurrence
             this month, which suggests a pattern worth escalating to facilities
             for a permanent fix rather than logging another one-off complaint."
```

## Why this matters more than the specific triage example

The point isn't "AI can sort emails." It's that **a one-line prompt tweak, caught by a 5-case rubric, was the difference between a system that silently drops a real operational pattern and one that catches it.** A quick glance at a few outputs before rollout would have looked fine — v1 scores 4/5, and the one miss reads as a plausible, calm response. The gap only surfaces once the third HVAC ticket gets logged as three unrelated one-offs instead of one recurring problem. This is the exact judgment call this role requires: before recommending any AI-assisted workflow to a colleague, know how you'd actually verify it works, not just that it looks plausible on the cases you happened to try.

## The agentic layer: auto-patching, not just grading

A harness that only reports failures still leaves a human to read the rubric, guess a fix, and rewrite the prompt by hand. `synthesize_patch()` closes that loop automatically: it derives a targeted prompt addition directly from the rubric that already exists for the failing case — no human-authored fix required — and the loop is *observe → diagnose → patch → re-verify*, the same reason-act-observe shape behind any agent, just applied to prompt quality instead of an external tool call.

To prove this isn't tuned to cases it was written against, `auto_patch_demo.py` runs it live against a **held-out case never used during v1/v2 development**: an email with "URGENT!!!" in the subject about a trivial repainted parking spot — a classic keyword-triggered false positive. Real, unscripted result:

```
Step 1 — grade against current-best prompt (v2):
  response: "Urgent priority — the subject line explicitly flags this as urgent..."
  Result: FAIL (contains disallowed term: 'urgent priority')

Step 2 — auto-synthesize a patch directly from the case's rubric:
  + "Do not let surface-level language (tone, punctuation, capitalization, or
     the literal presence of urgency-sounding words) override the actual
     substance of the message..."

Step 3 — grade again against the auto-patched prompt (v3):
  response: "Low priority — although the subject line uses the word 'urgent'
             and exclamation marks, the actual content describes a minor
             cosmetic parking-spot color issue..."
  Result: PASS
```

## The judgment layer: why keyword rubrics alone aren't the intelligence either

The rubric grading above is a fast, cheap first pass — and, like any keyword check, it's fragile in a specific way: a response can be **correct in substance while using none of the expected words**, and the rubric alone will wrongly fail it. `judge_demo.py` proves this live: on the admin-question case, a response that's clearly correct ("this can wait, nothing operationally significant") but avoids the exact rubric words entirely gets:

```
Keyword-rubric grading:  FAIL (missing any of: low priority, routine, informational)
LLM-judge grading:       PASS — correctly conveys low-stakes/non-urgent in different words
```

Same shape as the decision-log project in this portfolio: a cheap deterministic layer proposes or filters fast, but the actual judgment — does this response *mean* the right thing, not just contain the right words — needs real reasoning on top. Grading a workflow purely by keyword rubric would, over time, train whoever writes the prompts to chase specific phrasing instead of correctness.

## Run it yourself

```bash
python harness.py v1
python harness.py v2
python auto_patch_demo.py
python judge_demo.py
```

No API key required — this repo ships fixed, real response sets and real, live-generated judge verdicts for the exact cases demonstrated, so everything is fully reproducible. To grade a live model instead of a recorded response set, swap `load_responses()` / `call_llm_judge_live()` for a live API call — the logic is identical either way, because it doesn't care where the text came from.
