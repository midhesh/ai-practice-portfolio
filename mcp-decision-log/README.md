# Decision Log

## The problem

A decision gets made somewhere, in a meeting, in a quick AI chat, in a Slack thread, and then it's never written down anywhere anyone would think to search. Weeks later someone else, working on something adjacent, makes the opposite call with no way of knowing the first decision existed. Nobody finds out until the two approaches collide.

This has gotten worse since AI chat tools became part of daily work. A lot of real reasoning now happens inside a quick back and forth with an assistant that gets closed the moment the answer is good enough, and none of that ever ends up anywhere searchable. The outcome sticks around. The reasoning behind it doesn't.

## What it does

This is an MCP (Model Context Protocol) server, the current open standard for connecting an AI assistant to tools and data, exposing `log_decision` and `query_decisions` to any MCP-compatible client like Claude Desktop. The main thing worth noticing is that it checks itself. Every time someone logs a new decision, it's automatically compared against everything already on record before it gets saved, not just whenever someone remembers to go searching.

## Two passes, not one

The first pass is a fast keyword search. It's cheap and it's fine at proposing candidates worth a second look, but word overlap alone can't actually tell you much. Two decisions can use almost identical language and be about completely unrelated things, and two decisions can genuinely conflict while sharing almost no words at all. So every candidate the first pass surfaces gets a second look: an actual judgment about whether the two decisions are really connected, phrased as a plain answer along with one sentence of reasoning a person could act on immediately.

## What this looked like in a real run

A genuine duplicate, caught and explained without anyone asking for it:

```
[!] LIKELY SUPERSEDES , active decision #1 ('Use RAG over full fine-tuning...').
Both decisions answer the exact same question (RAG vs. fine-tuning for the same
knowledge assistant) with the same conclusion, phrased differently. This is a
duplicate decision made independently, not two different topics.
Consider re-logging with supersedes_id=1.
```

Two completely unrelated decisions that happened to share language: one approving more sales travel budget, the other approving more marketing sponsorship budget. Both talk about increasing an annual budget to cover more industry events, and the two ended up sharing close to seventy percent of their wording. A search that stopped at word overlap would have flagged this as a conflict. The second pass got it right:

```
(Lexical prefilter found 69% word overlap with #4, but the judgment layer cleared it:
Both mention an annual budget increase tied to attending or sponsoring more industry
events, but one is sales travel spend and the other is marketing sponsorship spend,
different budget lines with no actual dependency or conflict between them.)
```

That second case is really the point of this whole thing. Any search tool, whether it's a vector database or plain keyword matching, would have flagged that overlap and left a person to sort it out manually. Putting real judgment on top of the search is what makes it trustworthy enough to act on without a human checking every single flag.

## Run it yourself

```bash
python -m pip install mcp
python demo.py          # runs the scenario above end to end
python server.py        # runs as an actual MCP server over stdio
```

`judge.py` ships with real judgments generated for the exact scenarios in `demo.py`, so the demo runs without needing an API key. Wiring in a live model call for arbitrary new decisions is a one-function change (`call_llm_judge_live`).
