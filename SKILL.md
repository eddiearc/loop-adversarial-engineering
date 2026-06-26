---
name: loop-adversarial-engineering
description: "Use when the user asks for mandatory-goal adversarial validation, independent generator/evaluator subagents, integration testing, or repeated problem-finding for complex Agent work."
---

# Loop Adversarial Engineering

## Overview

Turn work into a closed loop:

`goal -> independent generation -> independent evaluation -> integration -> evidence -> done`

Use this when verbal confidence is not enough and the task needs independent validation.

## When to Use

Use for work where independent pressure materially improves the outcome:

- The user asks for a generator/evaluator loop, adversarial review, repeated problem-finding, or "跑完并验证".
- The task has real blast radius: code changes, public writing, migration, workflow automation, or integration behavior.
- The result needs evidence from tests, commands, browser checks, API calls, or source-grounded review.
- A single pass is likely to miss requirement drift, hidden edge cases, or weak assumptions.

Do not auto-trigger for simple answers, low-risk formatting edits, pure brainstorming, or tasks where the user explicitly asks for a quick one-pass response. Explicit user invocation still takes priority.

## Loop Contract

1. Define a checkable goal: requested outcome, constraints, acceptance checks, evidence, and stop condition.
2. Use goal tooling before generation. Inspect the current goal; create one if none exists; update or reuse it if aligned. A todo list, local checklist, or written plan is not a substitute for goal mode. If goal tooling is unavailable or runtime policy blocks goal creation/update, stop and ask whether to continue without this skill.
3. Separate roles:
   - `generator`: implement, draft, or produce the artifact.
   - `evaluator`: find blocking issues, important issues, missing evidence, and residual risk.
   - `main`: orchestrate the loop, integrate accepted generator output, run mechanical checks, record evidence, and make the final completion call.
4. If subagent tools are available, both generator and evaluator must be independent subagents. The main agent must not act as the generator, must not act as the evaluator, and must not label main-thread generation plus self-review as a loop.
5. Keep each role single-purpose: one responsibility, one output, one validation surface. Split broad work instead of mixing implementation, review, testing, and planning.
6. Run 1 evaluator round by default. Run a second round when the first round finds important issues or the task is high risk. Continue past 2 rounds only when new blocking evidence appears and each round is still producing concrete improvements.
7. Stop when acceptance checks pass, evaluator findings are resolved or explicitly accepted, and remaining risk is specific.

## Role Independence Contract

- `main` is the orchestrator + integrator: goal setup, scope, handoff prompts, reconciliation, applying or merging accepted generator output, mechanical checks, final evidence, and stop/continue decisions.
- `main` may perform integration mechanics such as applying patches, resolving merge conflicts, running formatters/tests, copying generated artifacts, or wiring generated output into the workspace.
- `main` must not originate the substantive artifact, produce generator output, make evaluator judgments, or call its own main-thread work adversarial validation.
- `generator` owns production only: make the smallest sufficient change or artifact, report changed files and checks, and avoid judging final completeness.
- `evaluator` owns pressure-testing only: re-read the goal, inspect the result, run real checks where possible, and report issues or "no issue" with evidence.
- When subagent tools exist, a loop is invalid unless generation and evaluation are performed by separate subagents. If the current agent is assigned the `generator` role, it must not perform evaluator duties in the same pass.

## Quick Reference

| Situation | Action |
|---|---|
| Subagent tools are available | Spawn an independent generator subagent, then an independent evaluator subagent. |
| User explicitly asks for parallel work | Spawn narrow, non-overlapping subagents and keep evaluator independent from implementation. |
| Subagent tools are unavailable | Simulate roles as separate passes only after disclosing the limitation; final evidence must state this was not a complete adversarial loop. |
| Goal tooling is available | Inspect the current goal; create or update an aligned goal before generation. |
| Goal tooling is unavailable or blocked by runtime policy | Stop, report that mandatory goal mode is unavailable, and ask whether to continue without this skill. |
| Evaluator reports only residual risk | Stop after documenting risk and evidence. |
| Evaluator finds blocking or important issues | Main routes issues to an independent generator for fixes, integrates accepted generator output, runs mechanical checks only, then routes one targeted re-evaluation. |

## Code Driver

Generate a loop spec from a task:

```bash
~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "任务目标"
```

Use the generated generator/evaluator prompts directly when spawning subagents. If subagent tools are available, both prompts must be run by independent subagents. If subagent tools are unavailable, run the same prompts as separate passes in the main thread only after disclosing the limitation and final evidence must state this was not a complete adversarial loop.

## Evidence Validator

Use `loop-evidence` to create and validate v1 loop evidence packets:

```bash
loop-evidence init "Improve loop-adversarial-engineering skill" > evidence.json
loop-evidence validate evidence.json
loop-evidence init "Improve loop-adversarial-engineering skill" | loop-evidence validate -
```

The evidence packet must use a full `goal` object with `objective`, `status`, and `codex_goal_used`. It must not require a synthetic local `goal.id`. Generator and evaluator outputs are structured JSON objects, while main/orchestrator only records evidence and selects one route: `continue`, `complete`, or `blocked`. The `recorder` object must identify `main` and must not claim to produce generator or evaluator output.

`route=complete` is a completion claim. It may only appear on the final round, must be paired with `goal.status=complete`, and triggers the same final evidence checks as a complete goal status.

Validation rejects completion when:

- `goal.status` is not `active`, `complete`, or `blocked`.
- A round lacks generator output or evaluator findings.
- `recorder` is missing, is not `main`, or claims to produce generator/evaluator output.
- `route=complete` appears before the final round.
- `route=complete` appears while `goal.status` is not `complete`.
- `goal.status` is `complete` but the final route is not `complete`.
- Completion is claimed by either `goal.status=complete` or final `route=complete`, but final generator/evaluator evidence is incomplete.
- Completion is claimed and final evaluator findings contain blocking or important items.
- Generator/evaluator checks or finding items are bare strings instead of structured objects.
- Roles were simulated, but the evidence claims a complete adversarial loop or does not explicitly state the run was not a complete adversarial loop.

## Prompts

Generator prompt contract:

```text
Complete the objective with the smallest sufficient change. Return only: files/artifacts changed, commands run with results, validation entry points, and uncertainties. Do not judge final completeness.
```

Evaluator prompt contract:

```text
Find problems. Do not praise. Re-read the original objective and evaluate the result with real checks where possible. Report only blocking issues, important issues, missing evidence, and residual risk. If there is no issue, say "no issue" and name the evidence checked.
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating the description as the full workflow | Read the skill body and follow the loop contract. |
| Skipping goal setup because the task feels small | Goal mode is mandatory when this skill is active; set the goal first. |
| Replacing goal mode with a todo list or plan | Use the runtime goal tool before generation; local plans are only supporting notes. |
| Silently falling back when goal tooling is missing | Stop and get user consent before continuing outside this skill. |
| Calling main-thread work "adversarial" | Use independent generator and evaluator subagents whenever subagent tools are available. |
| Letting main implement and then asking only evaluator to review | Spawn an independent generator first; main coordinates and integrates. |
| Giving one agent implementation, review, and planning duties | Split roles or run separate passes. |
| Letting evaluator provide generic advice | Require blocking/important/missing-evidence/residual-risk categories. |
| Continuing loops because more review is possible | Continue only when there is new concrete evidence or unresolved important issues. |
| Finishing with "looks good" | Finish with commands, files, evaluator findings, and remaining risk. |

## Final Evidence Checklist

- Commands/tests run and actual result.
- Files/artifacts changed.
- Whether generation and evaluation were performed by independent subagents; if not, why not and that this was not a complete adversarial loop.
- Evaluator findings and fix status.
- Integration evidence for real HTTP/CLI/workflow/browser tasks.
- Remaining risk or blocker.
