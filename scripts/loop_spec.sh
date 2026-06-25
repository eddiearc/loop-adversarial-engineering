#!/usr/bin/env bash
set -euo pipefail

goal="${1:-}"
rounds="${ROUNDS:-2}"

if [[ -z "$goal" ]]; then
  echo "Usage: $0 \"task goal\"" >&2
  echo "Optional: ROUNDS=1 $0 \"task goal\"" >&2
  exit 1
fi

cat <<EOF
# Generator Evaluator Loop Spec

## Goal
$goal

## Acceptance Checks
- The requested outcome exists and matches the user's constraints.
- The result has been independently evaluated, reviewed, or tested.
- Any remaining risk is explicit and justified.

## Goal Tool
If a goal tool is available, create or update a goal for this task before starting.
Mark it complete only after validation evidence is collected.

## Loop
1. Generator produces the smallest complete solution or artifact.
2. Evaluator attacks the result with real checks where possible.
3. Main agent fixes confirmed issues and reruns relevant checks.
4. Stop after $rounds full evaluator round(s), unless new blocking evidence appears.

## Subagent Scope Rule
Give each subagent exactly one responsibility and one expected output.
Split broad work into separate subagents instead of mixing implementation, review, testing, and planning.

## Generator Prompt
You are the generator. Complete this goal:

$goal

Edit or produce artifacts directly when appropriate. Do not revert unrelated changes.
Return: files/artifacts changed, commands run, results, uncertainties, and suggested verification entry points.

## Evaluator Prompt
You are the evaluator. Find problems; do not praise.

Original goal:
$goal

Re-read the result against the goal. Look for bugs, missing requirements, weak evidence,
integration failures, edge cases, and requirement drift. Run real checks when possible.
Return findings grouped as: blocking, important, missing evidence, residual risk, or no issue.

## Final Evidence Format
- Outcome:
- Changes:
- Validation:
- Evaluator findings:
- Remaining risk:
EOF
