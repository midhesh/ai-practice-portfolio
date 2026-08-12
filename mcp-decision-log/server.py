"""
Decision Log MCP Server
------------------------
Problem this addresses:
Organizational decisions go stale silently. Something gets decided, gets
half-remembered or half-superseded months later, and nobody notices the
contradiction until it causes real friction - two teams building on
opposite assumptions, or the same debate happening twice with different
outcomes. This has gotten measurably worse as AI chat tools have become
part of daily work: a growing share of real reasoning now happens inside
disposable, one-off AI conversations that leave no institutional trace
once the tab closes - the outcome persists, the *why* doesn't, and there
is no way for anyone (or any AI assistant) to check a new plan against
what was already decided.

What this does:
An MCP (Model Context Protocol) server exposing tools to any
MCP-compatible AI client (Claude Desktop, etc.):
  - log_decision:     capture a decision + its rationale + alternatives
                       considered. Before saving, it PROACTIVELY searches
                       existing active decisions for semantic overlap and
                       flags a possible contradiction/duplicate if found -
                       this is the agentic part: it doesn't wait to be
                       asked, it checks on every write.
  - query_decisions:  ask a natural-language question, get back the most
                       relevant past decisions, ranked by TF-IDF + cosine
                       similarity (hand-rolled vector search, no external
                       model or API required), with superseded decisions
                       clearly marked so nobody acts on a decision that
                       was later overturned.
  log_decision also accepts an optional supersedes_id to explicitly mark
  an old decision as replaced by a new one - both stay in the record with
  the relationship intact, nothing is ever silently overwritten or deleted.

Storage is a flat local JSON file (decisions.json) - deliberately no
database, no server infra - because the point is to prove the workflow
works, not to build production infrastructure in an afternoon.
"""

import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone

from mcp.server.mcpserver import MCPServer
from judge import judge_overlap

DB_PATH = os.path.join(os.path.dirname(__file__), "decisions.json")
CONTRADICTION_THRESHOLD = 0.30  # cosine similarity above which a new decision
                                 # is flagged as potentially overlapping an
                                 # existing active one

mcp = MCPServer("decision-log")


def _load() -> list[dict]:
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(decisions: list[dict]) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or",
    "in", "on", "for", "with", "this", "that", "it", "we", "our", "be",
    "as", "by", "at", "not", "no", "so", "if", "than", "because", "since",
}


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _entry_text(entry: dict) -> str:
    return " ".join(
        [entry["title"], entry["rationale"], entry.get("alternatives_rejected", ""), " ".join(entry.get("tags", []))]
    )


def _tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {term: count / total for term, count in counts.items()}


def _idf(corpus_tokens: list[list[str]]) -> dict[str, float]:
    n_docs = len(corpus_tokens) or 1
    df = Counter()
    for tokens in corpus_tokens:
        for term in set(tokens):
            df[term] += 1
    # smoothed idf: log((1 + N) / (1 + df)) + 1, standard TF-IDF smoothing so
    # unseen terms don't blow up and every term gets a nonzero weight
    return {term: math.log((1 + n_docs) / (1 + count)) + 1 for term, count in df.items()}


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = _tf(tokens)
    return {term: weight * idf.get(term, math.log(2)) for term, weight in tf.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    shared = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values())) or 1e-9
    norm_b = math.sqrt(sum(v * v for v in b.values())) or 1e-9
    return dot / (norm_a * norm_b)


def _rank_by_similarity(query: str, entries: list[dict]) -> list[tuple[dict, float]]:
    """TF-IDF + cosine similarity vector search — the same core mechanism behind
    production embedding-based retrieval (RAG), just with a hand-rolled sparse
    term-frequency vector space instead of a trained neural embedding model.
    Good enough to rank relevance meaningfully at small scale, with zero
    external dependencies or API calls."""
    if not entries:
        return []
    corpus_tokens = [_tokenize(_entry_text(e)) for e in entries]
    idf = _idf(corpus_tokens)
    doc_vectors = [_tfidf_vector(tokens, idf) for tokens in corpus_tokens]
    query_vector = _tfidf_vector(_tokenize(query), idf)
    scored = [(entry, _cosine(query_vector, vec)) for entry, vec in zip(entries, doc_vectors)]
    return sorted(scored, key=lambda pair: pair[1], reverse=True)


def _auto_tags(text: str, existing_tags: list[str], top_n: int = 4) -> list[str]:
    """Auto-extract salient keywords via TF weighted by inverse global frequency
    across this doc alone (a lightweight single-document keyword extraction) so
    every decision gets useful tags even if the caller doesn't provide any."""
    tokens = [t for t in _tokenize(text) if t not in _STOPWORDS and len(t) > 3]
    if not tokens:
        return existing_tags
    counts = Counter(tokens)
    ranked = [term for term, _ in counts.most_common(top_n)]
    merged = list(existing_tags)
    for term in ranked:
        if term not in merged:
            merged.append(term)
    return merged[: max(top_n, len(existing_tags))]


@mcp.tool()
def log_decision(
    title: str,
    rationale: str,
    alternatives_rejected: str = "",
    tags: list[str] | None = None,
    supersedes_id: int | None = None,
) -> str:
    """Log a decision with its rationale so it can be retrieved later.

    Proactively checks for semantic overlap with existing active decisions
    and flags a possible contradiction/duplicate before saving.

    Args:
        title: Short name for the decision (e.g. "Use hybrid search for internal KB").
        rationale: Why this decision was made - the actual reasoning, not just the outcome.
        alternatives_rejected: What else was considered, and why it was rejected.
        tags: Optional keywords for retrieval. Auto-extracted keywords are added regardless.
        supersedes_id: If this decision replaces an earlier one, its id - the old
            entry is marked superseded rather than deleted.
    """
    decisions = _load()
    candidate_text = " ".join([title, rationale, alternatives_rejected])

    active = [d for d in decisions if d.get("status", "active") == "active"]
    overlap_warning = ""
    if active:
        # Stage 1: cheap lexical prefilter (TF-IDF) - just proposes candidates worth a
        # second look, out of what could be thousands of logged decisions. It is
        # deliberately not trusted to make the actual call.
        ranked = _rank_by_similarity(candidate_text, active)
        best_entry, best_score = ranked[0]
        if best_score >= CONTRADICTION_THRESHOLD and best_entry["id"] != supersedes_id:
            # Stage 2: the real judgment - an LLM reasons about the actual relationship
            # between the two decisions, not just their word overlap. Uses substantive
            # content only (not auto-extracted tags, which are metadata, not reasoning).
            best_entry_text = " ".join(
                [best_entry["title"], best_entry["rationale"], best_entry.get("alternatives_rejected", "")]
            )
            verdict = judge_overlap(candidate_text, best_entry_text)
            if verdict["verdict"] == "FALSE_POSITIVE":
                overlap_warning = (
                    f"\n\n(Lexical prefilter found {best_score:.0%} word overlap with #{best_entry['id']}, "
                    f"but the judgment layer cleared it: {verdict['reason']} No action needed.)"
                )
            elif verdict["verdict"] in ("CONTRADICTION", "RELATED_NOT_CONFLICTING"):
                label = "LIKELY SUPERSEDES" if verdict["verdict"] == "CONTRADICTION" else "RELATED, NOT CONFLICTING"
                overlap_warning = (
                    f"\n\n[!] {label} — active decision #{best_entry['id']} ('{best_entry['title']}'). "
                    f"{verdict['reason']} "
                    + (f"Consider re-logging with supersedes_id={best_entry['id']}."
                       if verdict["verdict"] == "CONTRADICTION" else "")
                )
            else:
                overlap_warning = (
                    f"\n\n[!] {best_score:.0%} lexical overlap with #{best_entry['id']} "
                    f"('{best_entry['title']}') - no live judgment available in this offline demo, review manually."
                )

    entry = {
        "id": len(decisions) + 1,
        "title": title,
        "rationale": rationale,
        "alternatives_rejected": alternatives_rejected,
        "tags": _auto_tags(candidate_text, tags or []),
        "status": "active",
        "supersedes": supersedes_id,
        "superseded_by": None,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    decisions.append(entry)

    if supersedes_id is not None:
        for d in decisions:
            if d["id"] == supersedes_id:
                d["status"] = "superseded"
                d["superseded_by"] = entry["id"]

    _save(decisions)
    supersede_note = f" (supersedes #{supersedes_id})" if supersedes_id else ""
    return f"Logged decision #{entry['id']}: {title}{supersede_note}{overlap_warning}"


@mcp.tool()
def query_decisions(query: str, top_k: int = 3) -> str:
    """Find past decisions relevant to a natural-language question.
    Superseded decisions are still returned but clearly marked, so nobody
    acts on a decision that was later overturned.

    Args:
        query: What you want to know, e.g. "why did we choose X over Y".
        top_k: Max number of matching decisions to return.
    """
    decisions = _load()
    if not decisions:
        return "No decisions logged yet."

    ranked = _rank_by_similarity(query, decisions)
    top = [(e, score) for e, score in ranked[:top_k] if score > 0.05]

    if not top:
        return f"No logged decision closely matches: '{query}'"

    lines = []
    for e, score in top:
        status_line = ""
        if e.get("status") == "superseded":
            status_line = f"\n  [!] SUPERSEDED by #{e['superseded_by']} - do not treat as current"
        elif e.get("supersedes"):
            status_line = f"\n  (this superseded #{e['supersedes']})"
        lines.append(
            f"#{e['id']} — {e['title']}  (relevance: {score:.2f}){status_line}\n"
            f"  Rationale: {e['rationale']}\n"
            f"  Rejected alternatives: {e['alternatives_rejected'] or 'n/a'}\n"
            f"  Tags: {', '.join(e['tags']) or 'none'}\n"
            f"  Logged: {e['logged_at']}"
        )
    return "\n\n".join(lines)


if __name__ == "__main__":
    mcp.run()
