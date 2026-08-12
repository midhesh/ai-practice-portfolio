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

print("--- Decision #1: initial architecture choice ---")
print(log_decision(
    title="Use RAG over full fine-tuning for the internal knowledge assistant",
    rationale=(
        "Our project documentation changes weekly across offices, and fine-tuning "
        "would require expensive retraining every time content changes. RAG lets us "
        "update the source documents directly and the assistant reflects changes "
        "immediately with no retraining cost."
    ),
    alternatives_rejected="Fine-tuning a model on our project archive - rejected, slow and expensive to keep current.",
    tags=["knowledge-management", "architecture"],
))

print("\n--- Decision #2: a colleague in another office logs a near-duplicate decision, unaware #1 exists ---")
print(log_decision(
    title="Adopt retrieval-based Q&A instead of training a custom model on our docs",
    rationale=(
        "Training a custom model on our knowledge base is expensive to keep updated "
        "as documents change. A retrieval approach that pulls from live documents "
        "avoids retraining entirely."
    ),
    alternatives_rejected="Training/fine-tuning a dedicated model - too costly to refresh.",
    tags=["knowledge-base"],
))

print("\n--- Months later: the team decides to add a reranking step, explicitly superseding decision #1 ---")
print(log_decision(
    title="Add a reranking step on top of the RAG pipeline",
    rationale=(
        "Pure vector search was returning plausible-but-wrong chunks often enough "
        "to erode trust. Adding a reranking pass on the top candidates before "
        "generation fixed most of the visibly wrong retrievals."
    ),
    alternatives_rejected="Bigger context window instead of reranking - rejected, cost scales badly.",
    tags=["architecture"],
    supersedes_id=1,
))

print("\n--- A new team member asks: why are we using RAG instead of fine-tuning? ---\n")
print(query_decisions("why are we using RAG instead of fine-tuning"))
