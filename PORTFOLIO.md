# AI Practice Portfolio — Midhesh Mahadevan Shankar

Three small, working prototypes built while preparing for this role — each tackles a real, current problem created or exposed by how AI is actually being adopted in organizations right now. All code, real captured outputs, and full writeups are in the accompanying repository: **github.com/midhesh/ai-practice-portfolio**

---

## 1. Decision Log — an MCP server that proactively catches contradictions

**Problem:** organizational decisions go stale silently, and this has gotten measurably worse as AI chat tools became part of daily work — a growing share of real reasoning now happens inside disposable, one-off AI conversations that leave no institutional trace once the tab closes. The outcome persists; the *why* doesn't, and there's no way for anyone (or any AI assistant) to check a new plan against what was already decided.

**What I built:** an MCP (Model Context Protocol — the current open standard for connecting AI assistants to tools and data) server with a genuinely **agentic** behavior at its core: `log_decision` doesn't just store what it's told — before saving, it proactively searches all existing active decisions for semantic overlap using real TF-IDF + cosine-similarity vector search (hand-built from scratch, zero external dependencies), and flags a possible contradiction without being asked. Decisions can also explicitly supersede earlier ones, so history stays auditable instead of silently overwritten.

**Real, verified result:** a colleague logs a near-duplicate decision unaware the first exists → correctly flagged at 34% similarity. A later decision explicitly supersedes the original → a new query for "why RAG instead of fine-tuning" correctly surfaces the original decision **marked SUPERSEDED**, pointing to the current one, instead of resurfacing dead reasoning as if it were live.

---

## 2. PromptGrade — a self-patching eval harness

**Problem:** AI tool adoption is accelerating faster than any team's ability to verify it's actually reliable. Prompts get trusted because they "seemed fine" on a couple of manual tries; failures on edge cases surface only after rollout.

**What I built:** a harness that grades AI responses against defined rubrics across realistic test cases — and closes the loop agentically with `synthesize_patch()`, which derives a targeted prompt fix directly and generically from a failing case's own rubric, no human-authored patch required. The loop is genuinely *observe → diagnose → patch → re-verify*.

**Real, verified result (not cherry-picked):** on the original 5-case triage suite, prompt v1 scored 4/5, missing a real, costly failure mode (a 3rd-occurrence HVAC complaint misread as one-off). One added instruction brought it to 5/5. To prove the auto-patch loop generalizes rather than being tuned to known cases, I ran it live against a **held-out case it had never seen**: an email with "URGENT!!!" in the subject about a trivial repainted parking spot — a classic keyword-triggered false positive. The current-best prompt failed it (misread as urgent); `synthesize_patch()` auto-derived a fix directly from the rubric; the patched prompt passed on the first re-try.

---

## 3. AI Pilot Scorecard — with a responsible-use risk gate

**Problem:** MIT's 2025 "State of AI in Business" study found ~95% of generative AI pilots fail to reach production or deliver measurable ROI — the report's own conclusion is that most pilots never had a defined success bar, so results get judged by feeling after the fact. ([source](https://www.forbes.com/sites/andreahill/2025/08/21/why-95-of-ai-pilots-fail-and-what-business-leaders-should-do-instead/))

**What I built:** an interactive tool that forces success criteria to be defined *before* a pilot runs, then grades the real post-trial result against that pre-committed bar. It goes one step further than a metrics-only scorecard: a **responsible-use risk gate** checks whether the pilot touches irreversible actions, PII, client-facing exposure, or has no human review step — and if the risk profile is high enough, the verdict is capped at *Iterate* **regardless of how good the metric looks**, with a specific, situation-aware suggested next step (not a generic warning).

**Real, verified result:** an 80%-actual-vs-70%-target pilot that would otherwise score *Scale* is correctly capped to *Iterate* the moment "irreversible action" and "no human review" are both flagged — the tool catches a good number hiding a bad decision, which a metrics-only scorecard would miss entirely.

---

## Why these three, together

Each addresses a different failure mode in how AI actually gets adopted inside organizations: **losing the reasoning behind decisions and letting stale ones linger** (Decision Log), **trusting AI workflows without verifying or fixing them** (PromptGrade), and **scaling a pilot on a good number while missing the risk underneath it** (Pilot Scorecard). None of these are about AI being more powerful — they're about AI adoption being more disciplined, which is the actual work this role is describing.
