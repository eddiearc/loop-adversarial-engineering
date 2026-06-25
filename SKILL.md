---
name: loop-adversarial-engineering
description: "Use when the user wants loop adversarial engineering for Agent work: set a task as a goal, let one subagent generate or implement while another evaluates, reviews, integration-tests, or attacks the result, then iterate until evidence shows the goal is complete. Inspired by cybernetic feedback loops and Anthropic-style harness design. Trigger on \"generator evaluator\", \"开 loop\", \"对抗闭环\", \"loop engineering\", \"设置成 goal\", \"一个 subagent 干活另一个 review\", \"让另一个 agent 集成测试\", \"对抗地测试/找问题\", or \"跑完并验证\"."
---

# Loop Adversarial Engineering

## Core Rule

Turn work into a closed loop:

`goal -> generate -> evaluate -> revise -> evidence -> done`

Use this when verbal confidence is not enough and the task needs independent validation.

## Fast Path

1. Define a checkable goal: objective, acceptance checks, evidence, stop condition.
2. If goal tooling exists, default to goal mode: inspect the current goal, create one if none exists, or update/reuse it if aligned. Skip only when the user explicitly says not to use a goal.
3. Spawn or simulate separate roles:
   - `generator`: implement, draft, or produce the artifact.
   - `evaluator`: review, test, attack assumptions, and identify requirement drift.
   - `main`: reconcile, fix, and decide whether to run another loop.
4. Keep each subagent single-purpose: one responsibility, one output, one validation surface. Split broad work into multiple subagents instead of giving one subagent mixed implementation, review, testing, and planning duties.
5. Run at most 2 full evaluator rounds by default; continue only for high-risk work or clear progress.
6. Final answer with outcome, changes, validation evidence, and remaining risk.

## Code Driver

Generate a loop spec from a task:

```bash
~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "任务目标"
```

Use the generated generator/evaluator prompts directly when spawning subagents. If subagent tools are unavailable, run the same prompts as separate passes in the main thread.

## Prompts

Evaluator stance:

```text
Find problems. Do not praise. Re-read the original goal and evaluate the result with real checks where possible. Report only blocking issues, important issues, missing evidence, and residual risk.
```

Final evidence checklist:

- Commands/tests run and actual result.
- Files/artifacts changed.
- Evaluator findings and fix status.
- Integration evidence for real HTTP/CLI/workflow/browser tasks.
- Remaining risk or blocker.
