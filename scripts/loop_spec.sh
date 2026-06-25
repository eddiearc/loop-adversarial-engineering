#!/usr/bin/env bash
set -euo pipefail

goal="${1:-}"
rounds="${ROUNDS:-1}"

if [[ -z "$goal" ]]; then
  echo "Usage: $0 \"task goal\"" >&2
  echo "Optional: ROUNDS=1 $0 \"task goal\"" >&2
  exit 1
fi

if ! [[ "$rounds" =~ ^[1-9][0-9]*$ ]]; then
  echo "ROUNDS must be a positive integer" >&2
  exit 1
fi

cat <<EOF
# Loop Adversarial Engineering Spec

## Objective
$goal

## Acceptance Checks
- The requested outcome exists and matches the user's constraints.
- Goal mode was used before generation.
- When subagent tools were available, generation and evaluation were performed by separate independent subagents.
- The result has been independently evaluated, reviewed, or tested.
- Any remaining risk is explicit and justified.

## Goal Tool Policy
Goal mode is mandatory for this loop.
Inspect the current goal; create one if none exists; update or reuse it if aligned.
A todo list, local checklist, or written plan is not a substitute for goal mode.
If goal tooling is unavailable or runtime policy blocks goal creation/update, stop and ask whether to continue without this skill.

## Role Independence Policy
- Main owns orchestration only: goal setup, scope, handoff prompts, routing issues to generator, applying or merging generator output, running mechanical checks, final evidence, and stop/continue decisions.
- Generator owns production only: implement, draft, or produce the requested artifact.
- Evaluator owns pressure-testing only: inspect the result against the goal and run real checks where possible.
- Main must not produce artifacts and must not make evaluator judgments. Main may only summarize evaluator findings and mechanical check results.
- If subagent tools are available, main must spawn independent generator and evaluator subagents. Main-thread generation plus self-review does not count as this loop.

## Loop
1. If subagent tools are available, an independent generator subagent produces the smallest complete solution or artifact.
2. If subagent tools are available, an independent evaluator subagent attacks the result with real checks where possible. Main-thread generation plus self-review does not count as adversarial validation.
3. Main agent routes confirmed issues back to an independent generator pass, applies or merges generator output, runs mechanical checks, and summarizes evidence. Main must not produce artifacts or make evaluator judgments.
4. Stop after $rounds full evaluator round(s), unless new blocking evidence appears and another round is likely to produce concrete improvement.

## Subagent Scope Rule
Give each subagent exactly one responsibility and one expected output.
Split broad work into separate subagents instead of mixing implementation, review, testing, and planning.
If subagent tools are unavailable, disclose the limitation before simulating generator/evaluator roles in the main thread, and state in final evidence that this was not a complete adversarial loop.

## Generator Prompt
You are the generator. Complete this objective:

$goal

Edit or produce artifacts directly when appropriate. Do not revert unrelated changes.
Return only: files/artifacts changed, commands run with results, uncertainties, and suggested verification entry points. Do not judge final completeness.

## Evaluator Prompt
You are the evaluator. Find problems; do not praise.

Original objective:
$goal

Re-read the result against the objective. Look for bugs, missing requirements, weak evidence,
integration failures, edge cases, and requirement drift. Run real checks when possible.
Return findings grouped as: blocking, important, missing evidence, residual risk, or no issue. Do not provide generic advice.

## Final Evidence Format
- Outcome:
- Changes:
- Validation:
- Generator/evaluator independence:
- Evaluator findings:
- Remaining risk:
EOF
