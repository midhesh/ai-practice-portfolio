# AI Practice Portfolio — Midhesh Mahadevan Shankar

Three working tools, built around one idea: a fast, cheap, deterministic check can *propose* candidates or *flag* possibilities, but it can't *judge* — telling apart a real match from a coincidental one, or a correct answer from a differently-worded one, takes actual reasoning. Each tool pairs a cheap first-pass filter with a genuine reasoning layer on top, and each one proves live, with a real example, exactly where the cheap layer alone gets it wrong. Full code and real results: **github.com/midhesh/ai-decision-prompt-pilot-toolkit**

---

## 1. Decision Log

**Right now:** someone decides something — in a meeting, a quick AI chat, a Slack thread — and it's never written down anywhere searchable. Months later, someone else makes the opposite call, with no way of knowing the first decision existed.

**What it does:** every decision is logged with its reasoning. The moment a new one is entered, a fast search proposes anything that looks related from everything already on record — then a reasoning layer actually judges the relationship: is this a real duplicate, a related-but-fine decision, or just a coincidence of wording? Only genuine conflicts get flagged; false alarms get cleared automatically, with the reasoning shown.

**Proven live:** two decisions about an "annual budget increase" — one for music club equipment, one for IEEE workshop speaker fees — share over half their vocabulary. The fast search flags them as related. The reasoning layer correctly clears it: unrelated initiatives, no real conflict. In the same test run, a genuine duplicate decision — phrased completely differently from the original — was correctly caught and explained in one sentence.

---

## 2. PromptGrade

**Right now:** an AI-assisted process gets tried a few times, looks fine, and goes into regular use. The one input it consistently gets wrong doesn't surface until it's already been relied on in real work.

**What it does:** runs the process against realistic test situations and grades each response — first with a fast check, then with a reasoning layer that judges whether the response is actually *correct*, not just whether it used the expected words. When a failure is found, it doesn't stop at reporting it — it works out what's missing and generates a specific fix, which gets tested again immediately to confirm it actually worked.

**Proven live, twice over:** first, a version that looked solid (4 of 5 correct) was quietly missing a costly pattern — mistaking a recurring problem for a one-off, every time. The gap was diagnosed, a fix was generated automatically, and it was verified on a brand-new situation the system had never seen — which it got wrong initially and got right after the fix, proving the fix generalized. Second: a genuinely correct response was fast-checked as a *failure* simply because it avoided the expected phrasing — the reasoning layer caught that the fast check was wrong, not the response.

---

## 3. AI Pilot Scorecard

**Right now:** a team tries an AI-assisted approach for a few weeks. It kind of seems to help. Nobody agreed on a number for success beforehand, so months later nobody can say whether it actually worked. (A recent industry study found the large majority of AI pilots never reach real, ongoing use, for exactly this reason.)

**What it does:** forces one specific number to count as success, written down before the trial starts — then checks the real result against it, not a feeling. A rough written description of the pilot gets scanned to flag likely risk areas automatically (client exposure, sensitive data, hard-to-undo actions, no human checking the output) for quick human review. Even a pilot that clearly beats its target doesn't get waved through if the risk profile says otherwise.

**Proven live:** a one-line description — "AI drafts replies to client emails and sends them automatically without anyone reviewing first" — is correctly parsed into three separate risk flags in one pass. Separately, a pilot beating its target by 10 points was still correctly blocked from a "ready to scale" recommendation once flagged as touching an irreversible, unreviewed action — catching a good number hiding a real risk, which a plain metrics scorecard would have missed entirely.

---

## Why these three, together

Each targets the same underlying failure mode from a different angle: **trusting a fast signal as if it were a judgment** — treating word overlap as agreement, keyword matches as correctness, or a passing metric as safety. The fix, every time, is the same shape: keep the fast layer for what it's actually good at (speed, coverage), and put real reasoning where the decision actually happens. That's the discipline this role is describing — not making AI more powerful, making the process around it trustworthy enough to act on.
