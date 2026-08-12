"""
Real, runnable demo of the decision-log tools (calls the same functions the
MCP server exposes, without needing a full MCP client session running).
Produces genuine output, captured verbatim into README.md.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

DB_PATH = os.path.join(os.path.dirname(__file__), "decisions.json")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

from server import log_decision, query_decisions  # noqa: E402
from judge import register_recorded_judgment  # noqa: E402


def candidate_text(title, rationale, alternatives):
    """Mirrors server.py's log_decision candidate_text construction exactly."""
    return " ".join([title, rationale, alternatives])


def entry_text(title, rationale, alternatives, tags):
    """Mirrors server.py's _entry_text() exactly, including auto-tags. Auto-tags
    are predictable (top TF terms) but to keep this demo simple and robust we
    register the judgment under the pre-tag text only, matched against
    candidate_text() on the querying side - see judge.py's lookup, which keys
    on (new candidate_text, existing candidate_text), not the tagged entry text."""
    return " ".join([title, rationale, alternatives])


# --- Decision #1 ---
d1 = dict(
    title="Use RAG over full fine-tuning for the internal knowledge assistant",
    rationale=(
        "Our project documentation changes weekly across offices, and fine-tuning "
        "would require expensive retraining every time content changes. RAG lets us "
        "update the source documents directly and the assistant reflects changes "
        "immediately with no retraining cost."
    ),
    alternatives_rejected="Fine-tuning a model on our project archive - rejected, slow and expensive to keep current.",
    tags=["knowledge-management", "architecture"],
)
print("--- Decision #1: initial architecture choice ---")
print(log_decision(**d1))

# --- Decision #2: a genuine near-duplicate ---
d2 = dict(
    title="Adopt retrieval-based Q&A instead of training a custom model on our docs",
    rationale=(
        "Training a custom model on our knowledge base is expensive to keep updated "
        "as documents change. A retrieval approach that pulls from live documents "
        "avoids retraining entirely."
    ),
    alternatives_rejected="Training/fine-tuning a dedicated model - too costly to refresh.",
    tags=["knowledge-base"],
)
register_recorded_judgment(
    candidate_text(d2["title"], d2["rationale"], d2["alternatives_rejected"]),
    candidate_text(d1["title"], d1["rationale"], d1["alternatives_rejected"]),
    verdict="CONTRADICTION",
    reason=(
        "Both decisions answer the exact same question (RAG vs. fine-tuning for the same "
        "knowledge assistant) with the same conclusion, phrased differently - this is a "
        "duplicate decision made independently, not two different topics."
    ),
)
print("\n--- Decision #2: a colleague in another office logs a near-duplicate decision, unaware #1 exists ---")
print(log_decision(**d2))

# --- Decision #3: explicitly supersedes #1 ---
d3 = dict(
    title="Add a reranking step on top of the RAG pipeline",
    rationale=(
        "Pure vector search was returning plausible-but-wrong chunks often enough "
        "to erode trust. Adding a reranking pass on the top candidates before "
        "generation fixed most of the visibly wrong retrievals."
    ),
    alternatives_rejected="Bigger context window instead of reranking - rejected, cost scales badly.",
    tags=["architecture"],
    supersedes_id=1,
)
print("\n--- Months later: the team decides to add a reranking step, explicitly superseding decision #1 ---")
print(log_decision(**d3))

# --- Decision #4: sales travel budget ---
d4 = dict(
    title="Approve an increase to the sales team's annual conference travel budget",
    rationale=(
        "Sales is attending two additional industry conferences this year to support new "
        "market entry, so the annual travel budget needs to increase to cover the extra trips."
    ),
    alternatives_rejected="Keeping the travel budget flat and cutting other conferences instead - rejected, would mean skipping the new markets entirely.",
    tags=["sales"],
)
print("\n--- Decision #4: an unrelated prior decision that happens to share budget vocabulary ---")
print(log_decision(**d4))

# --- Decision #5: marketing sponsorship budget - a genuine lexical false positive against #4 ---
d5 = dict(
    title="Increase the marketing team's annual event sponsorship budget",
    rationale=(
        "Marketing wants to sponsor two additional industry events this year to raise brand "
        "visibility, so the annual sponsorship budget needs to increase to cover it."
    ),
    alternatives_rejected="Keeping the sponsorship budget flat and reducing paid ads instead - rejected, weaker return on visibility.",
    tags=["marketing"],
)
register_recorded_judgment(
    candidate_text(d5["title"], d5["rationale"], d5["alternatives_rejected"]),
    candidate_text(d4["title"], d4["rationale"], d4["alternatives_rejected"]),
    verdict="FALSE_POSITIVE",
    reason=(
        "Both mention an annual budget increase tied to attending or sponsoring more industry "
        "events, but one is sales travel spend and the other is marketing sponsorship spend - "
        "different budget lines with no actual dependency or conflict between them."
    ),
)
print("\n--- Decision #5: an unrelated budget decision that happens to share vocabulary with #4 ---")
print(log_decision(**d5))

print("\n--- A new team member asks: why are we using RAG instead of fine-tuning? ---\n")
print(query_decisions("why are we using RAG instead of fine-tuning"))
