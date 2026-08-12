# Meeting Bridge, turning meeting notes into a working Decision Log

## The problem

The Decision Log tool in this portfolio only helps if decisions actually get logged into it, and nobody reliably stops mid-meeting to fill out a form. Most real decisions get made inside ordinary meeting notes, sitting next to reminders, small talk, and unrelated updates, and never make it into anything searchable.

## What it does

1. **Cheap filter:** splits raw meeting notes into paragraphs and heuristically flags ones that sound like they contain a decision (regex over phrases like "we decided," "agreed to," "going with"). Fast, free, and deliberately not trusted alone.
2. **Real judgment:** each flagged paragraph gets turned into a clean, structured decision, title, rationale, what was rejected, by actually reading and reasoning about the paragraph, not just extracting keywords.
3. **Real integration, not a reimplementation:** each structured decision is logged through the **actual** `log_decision()` function from the Decision Log project next door, meaning its existing proactive overlap-detection runs on machine-extracted decisions exactly the same way it runs on hand-typed ones.

## Why this project exists in this portfolio

The other two projects are strong on their own; this one proves they're not three disconnected demos, they compose into an actual pipeline, which is the more realistic and more valuable shape for something like this to take in practice.

## Real output from a live run

From 8 paragraphs of realistic, noisy meeting notes (coffee machine complaints, an onboarding reminder, an expense report deadline, a compliment about office renders, all correctly ignored):

```
Stage 1: heuristic filter flagged 2 of 8 paragraphs as possible decisions
  - "Priya raised that the Singapore team has been experimenting with search..."
  - "Separately, delivery raised a recurring problem: subcontractor invoices..."

Stage 3: structuring + logging through the real Decision Log tool
  Logged decision #2: Use retrieval-based search over the project archive
  instead of training a custom model

  [!] LIKELY SUPERSEDES, active decision #1 ('Use RAG over full fine-tuning...').
  Both decisions choose retrieval over fine-tuning for the same underlying reason
  - this is very likely the same decision being made independently in a
  different meeting, not a new topic.

  Logged decision #3: Standardize subcontractor invoices on a single template
```

The second meeting's decision was correctly recognized as very likely the same decision already made in an earlier, unrelated meeting, caught automatically, from raw notes, with zero manual tagging.

## Run it yourself

```bash
python extract.py
```

Reuses `mcp-decision-log`'s real code directly (no API key required, same recorded-judgment approach as the rest of this portfolio, documented in `../mcp-decision-log/judge.py`).
