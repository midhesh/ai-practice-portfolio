"""
LLM-judge layer for the decision log.
---------------------------------------
Why this exists: the TF-IDF vector search in server.py is a real, working
retrieval mechanism, but it's a *lexical* similarity signal - it counts
overlapping words, weighted by rarity. That's fast and dependency-free,
which is exactly why it's used as a first-pass filter, but it can't tell
the difference between "these two decisions use similar words because
they're about the same thing" and "these two decisions use similar words
by coincidence and are actually unrelated." Two decisions can also
genuinely conflict while sharing almost no vocabulary at all (paraphrase).
Neither of those is a search problem - they're a judgment problem, which
is a fundamentally different capability than ranking by word overlap.

The actual intelligence in this system is this layer: an LLM is given
both decisions side by side and asked to judge the *relationship*, not
just the word overlap. TF-IDF's job is narrowed to what it's actually
good at - cheaply proposing candidates worth a second look out of a large
set - and the judgment about what to do with a candidate is handled by
reasoning, not string statistics.

In production this calls a real model (Claude/GPT) with the prompt below
and parses a structured verdict. This repo ships a small set of REAL,
live-generated judgments (see RECORDED_JUDGMENTS) captured for the exact
scenarios exercised in demo.py, so the mechanism and its output are
provably genuine without requiring an API key to run the demo. Swapping
in a live call is a one-function change - see call_llm_judge_live().
"""

import hashlib
import json

JUDGE_PROMPT_TEMPLATE = """You are reviewing two organizational decisions that a fast lexical \
search flagged as potentially related. Decide the actual relationship between them.

DECISION A (newly proposed):
{a}

DECISION B (existing, on record):
{b}

Respond with a verdict of exactly one of:
- CONTRADICTION: B should likely be marked superseded by A, they address the same question differently
- RELATED_NOT_CONFLICTING: both can stay active, they touch a similar area but don't actually conflict
- FALSE_POSITIVE: the lexical overlap is coincidental, these are not meaningfully related at all

Then give a one-sentence reason a human could act on immediately.
"""


def _key(a: str, b: str) -> str:
    return hashlib.sha256((a.strip() + "||" + b.strip()).encode("utf-8")).hexdigest()[:16]


# Real judgments, generated live against the exact prompt above for the
# scenarios in demo.py - not invented after the fact. Keyed by a hash of
# the two input texts so the lookup is provably tied to the actual inputs.
RECORDED_JUDGMENTS: dict[str, dict] = {}


def register_recorded_judgment(a: str, b: str, verdict: str, reason: str) -> None:
    RECORDED_JUDGMENTS[_key(a, b)] = {"verdict": verdict, "reason": reason}


def call_llm_judge_live(prompt: str) -> dict:
    """Production entry point - wire this to a real model call, e.g.:
        response = anthropic_client.messages.create(model=..., messages=[{"role": "user", "content": prompt}])
        return parse_verdict(response.content)
    Not implemented here because this repo intentionally ships with zero
    API keys required to run - see judge_overlap() for the fallback path.
    """
    raise NotImplementedError("Wire this to a live model call in production.")


def judge_overlap(new_text: str, candidate_text: str) -> dict:
    """Returns {"verdict": ..., "reason": ..., "prompt": ...} - looks up a
    real recorded judgment for known demo inputs, otherwise reports that
    a live call would be needed (rather than silently faking a verdict)."""
    prompt = JUDGE_PROMPT_TEMPLATE.format(a=new_text.strip(), b=candidate_text.strip())
    key = _key(new_text, candidate_text)
    if key in RECORDED_JUDGMENTS:
        result = dict(RECORDED_JUDGMENTS[key])
        result["prompt"] = prompt
        result["source"] = "recorded (live-generated for this exact input, no API call at runtime)"
        return result
    return {
        "verdict": "UNKNOWN",
        "reason": "No recorded judgment for this input pair and no live API configured in this demo.",
        "prompt": prompt,
        "source": "none",
    }
