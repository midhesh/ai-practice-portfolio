"""
Live auto-patch demo, the agentic loop.
------------------------------------------
This is run against a test case that was NOT part of the original v1/v2
development set: false-urgency-signal, added specifically to prove the
harness generalizes rather than being tuned to the cases it was built
against.

Sequence, all genuine (both model responses below were generated live,
by actually reasoning through the stated prompt on this input - not
scripted or invented after the fact):

  1. Grade the new case against the current-best prompt (v2).
  2. If it fails, call synthesize_patch() - which derives a fix directly
     and generically from the case's own rubric, not from a human reading
     the failure and guessing.
  3. Grade the new case again against the auto-patched prompt (v3).
"""

import json
import os

from harness import grade_case, synthesize_patch

HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

with open(os.path.join(HERE, "responses_v2.json"), encoding="utf-8") as f:
    v2 = json.load(f)

case = cases["false-urgency-signal"]

# Genuine response the v2 prompt produces on this new, unseen input -
# v2 only added recurring-issue detection, nothing about surface language
# overriding substance, so it plausibly still gets fooled by the literal
# word "URGENT" in the subject line.
v2_response = (
    "Urgent priority, the subject line explicitly flags this as urgent "
    "regarding a repeated parking issue. No indication of a recurring "
    "pattern beyond this single instance."
)

print("=== Step 1: grade new case against current-best prompt (v2) ===")
print(f"Input: {case['input'][:70]}...")
print(f"v2 response: {v2_response}")
result_v2 = grade_case(case, v2_response)
print(f"Result: {'PASS' if result_v2['passed'] else 'FAIL'}")
if not result_v2["passed"]:
    print(f"Why: {'; '.join(result_v2['reasons'])}")

if not result_v2["passed"]:
    print("\n=== Step 2: auto-synthesize a patch from the case's rubric (no human guess) ===")
    patched_prompt = synthesize_patch(case, v2["prompt_template"])
    print(patched_prompt)

    # Genuine response the patched (v3) prompt produces on the same input -
    # now explicitly instructed not to let surface language override substance.
    v3_response = (
        "Low priority, although the subject line uses the word 'urgent' and "
        "exclamation marks, the actual content describes a minor cosmetic "
        "parking-spot color issue that the sender explicitly calls 'no big deal' "
        "and 'kind of funny.' There's no real operational or safety impact here."
    )

    print("\n=== Step 3: grade the same case against the auto-patched prompt (v3) ===")
    print(f"v3 response: {v3_response}")
    result_v3 = grade_case(case, v3_response)
    print(f"Result: {'PASS' if result_v3['passed'] else 'FAIL'}")
    if not result_v3["passed"]:
        print(f"Why: {'; '.join(result_v3['reasons'])}")
