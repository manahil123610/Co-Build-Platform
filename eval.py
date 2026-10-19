"""Run the hand-labeled extraction and match evaluation set."""

import json
from pathlib import Path

from extract import extract_profile
from match import load_profiles, top_matches


def main() -> None:
    cases = json.loads(Path("data/eval_pairs.json").read_text(encoding="utf-8"))
    profiles = load_profiles()
    top1 = top3 = 0
    report = ["# Evaluation Results", "", f"Gemma 4 extraction and matching on {len(cases)} hand-labeled posts.", ""]
    for index, case in enumerate(cases, start=1):
        profile = extract_profile(case["post"])
        matches = top_matches(profile, profiles)
        ids = [item["profile"]["id"] for item in matches]
        first_match = bool(ids and ids[0] == case["expected_id"])
        any_match = case["expected_id"] in ids
        top1 += first_match
        top3 += any_match
        report.append(f"- Case {index:02d}: expected `{case['expected_id']}`; ranked `{', '.join(ids)}`; top-1 {first_match}; top-3 {any_match}.")
        print(f"Case {index:02d}: expected={case['expected_id']} top3={','.join(ids)}")
    report.extend([
        "",
        f"- Top-1 agreement: {top1}/{len(cases)} ({top1 / len(cases):.1%})",
        f"- Top-3 agreement: {top3}/{len(cases)} ({top3 / len(cases):.1%})",
        "",
        "This small hand-labeled set is a smoke test, not a measure of real-world matching quality.",
    ])
    Path("RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(report[-4])
    print(report[-3])
    print("Saved detailed results to RESULTS.md")


if __name__ == "__main__":
    main()
