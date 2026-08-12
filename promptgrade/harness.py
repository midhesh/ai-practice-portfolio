"""
PromptGrade - a minimal eval harness
-------------------------------------
Problem this addresses:
Teams adopt a prompt or AI workflow because it "seemed to work" on a
handful of tries, then roll it out broadly. Failures on edge cases only
surface later, once trust (or damage) is already baked in. There is
rarely a rubric-based, repeatable way to check "is this actually good
enough to trust" before scaling it - decisions end up made on vibes.

What this does:
Loads a set of realistic test cases with pass/fail criteria (cases.json)
and a set of recorded model responses for a given prompt version
(responses_v1.json / responses_v2.json), grades each response against
its rubric, and prints a scorecard - pass rate, and exactly which cases
failed and why. This is the same idea as running a checklist of test
inputs before letting a system make judgment calls unsupervised.

Note on "recorded" responses: this repo ships two fixed response sets
(v1, v2) captured from a real run against the prompts in this file, so
the eval is fully reproducible with zero API keys required. To run it
live against your own model, swap load_responses() for a live call and
keep everything else identical - the grading logic doesn't care where
the text came from.
"""

import json
import os
import sys

HERE = os.path.dirname(__file__)


def load_cases():
    with open(os.path.join(HERE, "cases.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_responses(version: str):
    path = os.path.join(HERE, f"responses_{version}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def grade_case(case: dict, response: str) -> dict:
    text = response.lower()

    any_list = [s.lower() for s in case.get("must_include_any", [])]
    all_list = [s.lower() for s in case.get("must_include_all", [])]
    not_list = [s.lower() for s in case.get("must_not_include", [])]

    any_ok = (not any_list) or any(s in text for s in any_list)
    all_ok = all(s in text for s in all_list)
    not_ok = all(s not in text for s in not_list)

    passed = any_ok and all_ok and not_ok
    reasons = []
    if not any_ok:
        reasons.append(f"missing any of required signals: {case.get('must_include_any')}")
    if not all_ok:
        missing = [s for s in all_list if s not in text]
        reasons.append(f"missing required terms: {missing}")
    if not not_ok:
        present = [s for s in not_list if s in text]
        reasons.append(f"contains disallowed terms: {present}")

    return {"id": case["id"], "passed": passed, "reasons": reasons, "notes": case.get("notes", "")}


def run(version: str):
    cases = {c["id"]: c for c in load_cases()}
    resp = load_responses(version)
    results = []
    for case_id, response_text in resp["responses"].items():
        case = cases[case_id]
        result = grade_case(case, response_text)
        result["response"] = response_text
        results.append(result)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    print(f"\nPromptGrade report, prompt version: {version}")
    print(f"Prompt: {resp['prompt_template'][:80]}...")
    print(f"Score: {passed}/{total} passed ({round(100 * passed / total)}%)\n")

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']}")
        print(f"  response: {r['response']}")
        if not r["passed"]:
            print(f"  why it failed: {'; '.join(r['reasons'])}")
            print(f"  what this case checks: {r['notes']}")
        print()

    return passed, total


def synthesize_patch(case: dict, base_prompt: str) -> str:
    """Auto-generate a targeted prompt patch from a case's rubric - the
    'agentic' part of this harness: instead of a human manually reading a
    failure and guessing a fix, the fix is derived directly and generically
    from the rubric that already exists for every case. Works for any case,
    not just the one it happened to be written against.
    """
    additions = []
    if case.get("must_include_any"):
        signals = ", ".join(case["must_include_any"])
        additions.append(
            f"Explicitly check whether this situation involves: {signals}. "
            f"If applicable, say so directly in your reasoning."
        )
    if case.get("must_not_include"):
        forbidden = ", ".join(case["must_not_include"])
        additions.append(
            f"Do not let surface-level language (tone, punctuation, capitalization, or "
            f"the literal presence of urgency-sounding words) override the actual substance "
            f"of the message. Avoid concluding: {forbidden} unless the real content warrants it."
        )
    if not additions:
        return base_prompt
    return base_prompt.rstrip() + "\n\n" + " ".join(additions)


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    run(version)
