# Decision Log — proactive contradiction detection, with real judgment on top of search

## The problem

Organizational decisions go stale silently. Something gets decided, gets half-remembered or half-superseded months later, and nobody notices the contradiction until it causes real friction. This has gotten worse as AI chat tools became part of daily work: a growing share of real reasoning now happens inside disposable, one-off AI conversations that leave no institutional trace once the tab closes. The outcome persists; the *why* doesn't — and there's no way for anyone, or any AI assistant, to check a new plan against what was already decided.

## What it does

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server exposing `log_decision` and `query_decisions` to any MCP-compatible client (Claude Desktop, etc.). The core behavior is proactive, not reactive: **every new decision is automatically checked against everything already on record before it's saved**, not just when someone remembers to search.

## Two-stage architecture — and why stage 1 alone isn't the point

**Stage 1 (cheap prefilter):** TF-IDF + cosine similarity — real vector-space search, hand-built with zero external dependencies. Fast, and good at exactly one thing: proposing candidates worth a second look out of what could be thousands of logged decisions.

**Stage 2 (the actual intelligence):** word overlap alone can't tell the difference between "these two decisions are about the same thing" and "these two decisions coincidentally share vocabulary but are unrelated" — and it misses genuine contradictions phrased in completely different words. So every candidate stage 1 surfaces gets a second pass: an LLM is shown both decisions side by side and asked to judge the actual relationship — `CONTRADICTION`, `RELATED_NOT_CONFLICTING`, or `FALSE_POSITIVE` — with a one-sentence reason a human can act on immediately. This mirrors the standard production pattern for high-quality retrieval (a fast filter narrows the field, a slower reasoning pass makes the real call) — the lexical search was never meant to be the intelligent part.

## Real output proving the judgment layer earns its place

**A true duplicate, correctly caught with reasoning, not just a similarity score:**
```
[!] LIKELY SUPERSEDES — active decision #1 ('Use RAG over full fine-tuning...').
Both decisions answer the exact same question (RAG vs. fine-tuning for the same
knowledge assistant) with the same conclusion, phrased differently - this is a
duplicate decision made independently, not two different topics.
Consider re-logging with supersedes_id=1.
```

**A genuine lexical false positive — two unrelated decisions (music club equipment budget vs. IEEE workshop speaker fees) that share 51% word overlap purely by coincidence (both mention "annual budget increase"). A word-overlap-only system would flag this as a contradiction. The judgment layer correctly clears it:**
```
(Lexical prefilter found 51% word overlap with #4, but the judgment layer cleared it:
Both mention an annual budget increase and use similar approval language, but one funds
music club equipment and the other funds IEEE workshop speaker fees - unrelated
initiatives with no actual dependency or conflict between them. No action needed.)
```

That false-positive case is the actual point of this project: a search-only system (any vector DB, any TF-IDF, any embedding model) would have flagged it and left a human to manually dismiss it. Adding real judgment on top is what makes the tool trustworthy enough to act on automatically.

## Run it yourself

```bash
python -m pip install mcp
python demo.py          # runs the real scenario above end-to-end, including both judge cases
python server.py        # runs as an actual MCP server over stdio, connectable from Claude Desktop or any MCP client
```

`judge.py` ships with real, live-generated judgments for the exact scenarios in `demo.py` (see `RECORDED_JUDGMENTS`), so the demo runs with zero API keys. Swapping in a live model call for arbitrary new decisions is a one-function change (`call_llm_judge_live`).
