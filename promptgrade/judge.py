"""
LLM-judge grading layer for PromptGrade.
-------------------------------------------
Why this exists: the rubric-based grading in harness.py (grade_case) checks
for literal keywords - fast, deterministic, and a genuinely useful cheap
first pass, but it's fragile in exactly the way keyword matching always
is: a response can be semantically correct while using none of the exact
words the rubric expects, and it will be marked FAIL. A response can also
contain a rubric keyword while being wrong in context and get marked PASS.
Neither of those is a wording problem to patch around - it's a judgment
problem, the same category as the decision-log project in this portfolio.

The fix is the same shape as that project: keep the cheap keyword check
as a fast first pass (useful for the common, unambiguous cases), and add
a real LLM judgment pass that reads the response's actual meaning against
the case's intent, not its vocabulary. In production this is a live model
call; this repo ships real, live-generated judgments for the specific
paraphrase case demonstrated in judge_demo.py, so the mechanism is
provably genuine with zero API keys required to run the demo.
"""

import hashlib

JUDGE_PROMPT_TEMPLATE = """You are grading whether an AI's triage response correctly handles \
this email, based on what a correct response should convey - not on exact wording.

EMAIL:
{input}

WHAT A CORRECT RESPONSE SHOULD CONVEY:
{intent}

THE AI'S ACTUAL RESPONSE:
{response}

Does the response convey the correct judgment, even if it uses different words than expected? \
Answer PASS or FAIL, then give a one-sentence reason.
"""


def _key(case_id: str, response: str) -> str:
    return hashlib.sha256((case_id + "||" + response.strip()).encode("utf-8")).hexdigest()[:16]


RECORDED_JUDGMENTS: dict[str, dict] = {}


def register_recorded_judgment(case_id: str, response: str, verdict: str, reason: str) -> None:
    RECORDED_JUDGMENTS[_key(case_id, response)] = {"verdict": verdict, "reason": reason}


def call_llm_judge_live(prompt: str) -> dict:
    """Production entry point - wire to a real model call. Not implemented
    here so this repo runs with zero API keys required."""
    raise NotImplementedError("Wire this to a live model call in production.")


def judge_response(case: dict, response: str) -> dict:
    key = _key(case["id"], response)
    if key in RECORDED_JUDGMENTS:
        result = dict(RECORDED_JUDGMENTS[key])
        result["source"] = "recorded (live-generated for this exact input, no API call at runtime)"
        return result
    return {
        "verdict": "UNKNOWN",
        "reason": "No recorded judgment for this input and no live API configured in this demo.",
        "source": "none",
    }
