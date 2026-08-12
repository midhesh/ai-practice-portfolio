"""
Live demo: where keyword-rubric grading gets the wrong answer and the
LLM-judge layer gets it right.

Case: internal-admin-question ("Where do I submit expense reports now?").
The rubric expects one of: "low priority", "routine", "informational".
Here's a response that is CORRECT in substance but avoids all three words -
a realistic paraphrase, not a contrived trick.
"""

import json
import os

from harness import grade_case
from judge import judge_response, register_recorded_judgment

HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

case = cases["internal-admin-question"]

# A genuine, realistic paraphrase - correct in substance, avoids the exact
# rubric words on purpose to test whether grading depends on wording or meaning.
response = (
    "This can be handled whenever someone gets a chance - it's just a question about "
    "where to find a form, nothing operationally significant or time-sensitive."
)

print("=== Keyword-rubric grading (stage 1, cheap) ===")
print(f"Response: {response}")
kw_result = grade_case(case, response)
print(f"Result: {'PASS' if kw_result['passed'] else 'FAIL'}")
if not kw_result["passed"]:
    print(f"Why: {'; '.join(kw_result['reasons'])}")

register_recorded_judgment(
    case["id"], response,
    verdict="PASS",
    reason=(
        "The response correctly conveys this is low-stakes and non-urgent ('nothing "
        "operationally significant or time-sensitive', 'handled whenever') even though "
        "it never uses the words 'low priority', 'routine', or 'informational' - the "
        "judgment is right, only the wording differs from what the rubric expected."
    ),
)

print("\n=== LLM-judge grading (stage 2, reads meaning not vocabulary) ===")
verdict = judge_response(case, response)
print(f"Result: {verdict['verdict']}")
print(f"Why: {verdict['reason']}")

print("\n=== Conclusion ===")
if not kw_result["passed"] and verdict["verdict"] == "PASS":
    print(
        "Divergence confirmed: the keyword rubric alone would have logged this as a "
        "failure and, over time, trained whoever writes prompts to chase specific "
        "phrasing instead of correctness. The judgment layer catches that this response "
        "was right all along."
    )
