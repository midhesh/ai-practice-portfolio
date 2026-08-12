# AI Pilot Scorecard

## The problem

MIT's 2025 "State of AI in Business" study (widely reported, e.g. [Forbes](https://www.forbes.com/sites/andreahill/2025/08/21/why-95-of-ai-pilots-fail-and-what-business-leaders-should-do-instead/)) found that roughly 95% of generative AI pilots fail to reach production or deliver measurable ROI. The report's own conclusion isn't "the technology doesn't work" — it's that most pilots never had a defined bar for success in the first place, so results get judged by feeling after the fact. A mediocre result gets rationalized as fine; a genuinely good one gets dismissed because nobody agreed in advance what "good" meant.

## What it does

A single self-contained interactive page (`index.html`, no dependencies, works offline) that forces the definition-before-execution discipline, in four steps:

1. **Scope the pilot** — what the professional provides, what the AI actually does, what the human still decides. If any of these can't be filled in separately, the pilot isn't scoped yet.
2. **Lock in success criteria before the trial** — a specific metric, a baseline, and a numeric threshold for "this worked."
3. **Responsible-use risk check** — four flags (client-facing exposure, PII, irreversible actions, no human review) that don't block the pilot but raise the bar for what counts as scale-ready.
4. **Grade the real result** against the pre-committed bar, combined with two human-factor signals (trust, time saved), into a transparent **Scale / Iterate / Kill** verdict — plus an auto-generated, situation-specific suggested next step.

## The risk gate — the part that stops a good number from hiding a bad decision

A pilot can hit its numeric target and still not be ready to scale. If a pilot **touches an irreversible action with no human review step** (or trips 3+ of the 4 risk flags), the verdict is capped at *Iterate* regardless of how good the metric looks — verified live: an 80%-actual-vs-70%-target pilot that would otherwise score *Scale* gets correctly capped to *Iterate* the moment "irreversible action" and "no human review" are both checked, with the reasoning stating exactly why and the specific fix needed (add a human-approval step) rather than a vague warning.

## Why the verdict logic is deliberately simple and fully visible

The scoring is a transparent, inspectable rule set (visible directly in the `<script>` block), not a model or a black box — because the entire point of this tool is to make a judgment call *legible and defensible*, which a hidden scoring algorithm would undermine. This mirrors the actual judgment this role requires: the value isn't in a clever algorithm, it's in forcing the right questions to be answered honestly, in the right order, including the responsible-use question most metric-only pilots skip entirely.

## Run it

Open `index.html` directly in any browser — no server, no build step, no install.
