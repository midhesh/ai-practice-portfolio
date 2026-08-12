# AI Practice Portfolio — Midhesh Mahadevan Shankar

Three working tools, each solving a specific, common problem that shows up whenever a team starts relying more on AI in day-to-day work. Full code and real results: **github.com/midhesh/ai-practice-portfolio**

---

## 1. Decision Log

**The problem:** teams lose track of *why* something was decided. The outcome sticks around; the reasoning behind it doesn't — especially now that a lot of that reasoning happens in quick AI chats that vanish once the conversation ends. Months later, the same question gets debated twice, or two people end up working from opposite assumptions without realizing it.

**What it does:** a searchable record of decisions — not just what was decided, but why, and what was ruled out. The useful part: it checks itself. Every time a new decision is added, it automatically compares it against everything already on record and flags anything that looks like it overlaps or contradicts a past decision — before that conflict turns into wasted work. If a decision is later replaced, the old one stays on record but is clearly marked as outdated, so nobody acts on it by mistake.

**Proven in practice:** a duplicate decision made by someone unaware an earlier one existed was caught automatically. When an old decision was later replaced, anyone looking it up afterward was correctly pointed to the current answer instead of the outdated one.

---

## 2. PromptGrade

**The problem:** teams adopt an AI-assisted process because it looked fine the first few times they tried it, then find out much later — after it's already been relied on — that it fails in ways nobody caught. There's rarely a real check in place before something gets trusted.

**What it does:** tests an AI-assisted process against a set of realistic situations, including tricky edge cases, and gives a clear pass/fail readout instead of a gut feeling. When something fails, it doesn't just report the failure — it works out what's missing and proposes a specific fix, which can then be tested again immediately. It's a way of answering "is this actually reliable enough to trust" with evidence, and of closing the gap the moment a weakness is found rather than leaving it for someone to notice later.

**Proven in practice:** an initial version handled 4 out of 5 realistic cases correctly, missing one where a small recurring issue was mistaken for a one-off. A targeted fix brought it to 5 out of 5. Tested again on a brand-new situation it had never seen — one designed to trip it up with misleading wording — it failed on the first attempt, and the automatically proposed fix corrected it on the very next try.

---

## 3. AI Pilot Scorecard

**The problem:** most AI pilots inside companies don't clearly succeed or fail — they just quietly stall, because nobody agreed in advance what "success" would actually look like. A recent industry study found the large majority of AI pilots never reach real, ongoing use for exactly this reason.

**What it does:** a simple tool that makes a team agree on what success means *before* a trial starts — a specific target, not a feeling — and then judges the real result against that target afterward. It goes a step further than a plain scorecard: even if the numbers look good, it won't recommend rolling something out further if it involves sensitive information, hard-to-reverse actions, or no human checking the output — those situations get flagged as needing more caution regardless of how good the metric looks, with a specific explanation of what to fix next.

**Proven in practice:** a pilot that comfortably beat its target number was still correctly held back from a "ready to scale" recommendation once it was flagged as touching an irreversible action with nobody reviewing the output — catching a case where a good number was hiding a real risk.

---

## Why these three, together

Each one addresses a different, common way AI adoption quietly goes wrong: **losing track of decisions and reasoning** (Decision Log), **trusting a process without ever really testing it** (PromptGrade), and **scaling something based on a good number while missing the risk underneath it** (Pilot Scorecard). None of this is about AI being more powerful — it's about using it more carefully, which is the actual work behind good AI adoption.
