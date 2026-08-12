# Decision Log — an MCP server that proactively catches contradictions

## The problem

Organizational decisions go stale silently. Something gets decided, gets half-remembered or half-superseded months later, and nobody notices the contradiction until it causes real friction — two people building on opposite assumptions, or the same debate happening twice with different outcomes. This has gotten measurably worse as AI chat tools became part of daily work: a growing share of real reasoning now happens inside disposable, one-off AI conversations that leave no institutional trace once the tab closes. The outcome persists; the *why* doesn't — and there's no way for anyone, or any AI assistant, to check a new plan against what was already decided.

## What it does

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server — the current open standard for connecting AI assistants to tools and data — exposing tools to any MCP-compatible client (Claude Desktop, etc.):

- **`log_decision`** — capture a decision, its rationale, and what was rejected. This is where the agentic behavior lives: *before* saving, it proactively searches all existing active decisions for semantic overlap and flags a possible contradiction — it doesn't wait to be asked, it checks on every write.
- **`query_decisions`** — ask a natural-language question, get back the most relevant past decisions, ranked by real vector search, with superseded decisions clearly marked so nobody acts on something that was later overturned.
- **Supersede tracking** — decisions are never silently deleted or overwritten. Marking a new decision as superseding an old one keeps both in the record with the relationship intact, so the history stays auditable.
- **Auto-tagging** — every decision is automatically tagged with its most salient keywords (lightweight single-document keyword extraction), so retrieval quality doesn't depend on someone remembering to tag things well.

## The retrieval and detection mechanism — real vector search, built from scratch

Both the query tool and the proactive-overlap check use the same engine: **TF-IDF + cosine similarity**, a genuine vector-space retrieval technique implemented with zero external dependencies. Every decision becomes a sparse weighted term vector (term frequency × inverse document frequency, so common words are downweighted and distinctive words carry the signal); new text is compared against the existing corpus the same way. This is the same core idea behind production embedding-based RAG — query and document as vectors, ranked by distance — just inspectable rather than a black box, and reused for two different jobs: retrieval on query, and contradiction-detection on write.

## Real output from a live run

Three decisions logged in sequence, exactly as they'd occur in practice:

```
Decision #1: "Use RAG over full fine-tuning for the internal knowledge assistant"

Decision #2 (a colleague elsewhere logs a near-duplicate, unaware #1 exists):
  "Adopt retrieval-based Q&A instead of training a custom model on our docs"
  → [!] POSSIBLE OVERLAP DETECTED: 34% similar to active decision #1.
     If this changes that decision, re-log with supersedes_id=1.

Decision #3 (months later, explicitly supersedes #1):
  "Add a reranking step on top of the RAG pipeline"
  → Logged decision #3 (supersedes #1)

Query: "why are we using RAG instead of fine-tuning"
→ #1 (relevance 0.32) — [!] SUPERSEDED by #3 - do not treat as current
  #3 (relevance 0.17) — this superseded #1
  #2 (relevance 0.13)
```

Two things caught automatically, with no human remembering to check: the near-duplicate decision logged by someone unaware the first one existed, and the fact that decision #1 is no longer current — a new team member asking "why RAG" gets pointed to the live decision, not a dead one.

## Run it yourself

```bash
python -m pip install mcp
python demo.py          # runs the real scenario above end-to-end
python server.py        # runs as an actual MCP server over stdio, connectable from Claude Desktop or any MCP client
```
