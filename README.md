# Loop Adversarial Engineering

A small Agent Skill for running complex work through adversarial validation.

The idea is simple:

```text
goal -> independent generation -> independent evaluation -> integration -> evidence -> done
```

One independent subagent generates or implements. Another independent subagent evaluates, reviews, tests, or attacks the result. The main agent owns orchestration: goal setup, handoff prompts, routing issues to the generator, applying or merging generator output, mechanical checks, evidence summary, and the final completion call. Main-thread implementation plus self-review is not this pattern when subagent tools are available.

## Why

This pattern has two roots.

First, it is inspired by cybernetics: closed-loop control, feedback, error correction, and adjustment toward a goal. It is not a formal control theory implementation; it is a practical Agent workflow pattern for making AI work less dependent on one-shot confidence.

Second, it is aligned with Anthropic's harness work for long-running app development. In [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), Anthropic describes a multi-agent structure with planner, generator, and evaluator roles. The key engineering move is to separate the agent doing the work from the agent judging it, then feed concrete evaluator feedback back into the generator.

## Principles

- Use goal mode as the mandatory entry point. A todo list, local checklist, or written plan is not a substitute.
- Keep each subagent single-purpose: one responsibility, one output, one validation surface.
- Use independent generator and evaluator subagents whenever subagent tools are available; main-thread generation plus self-review is not adversarial validation.
- Keep main out of production and evaluation when subagent tools are available; main routes work, applies or merges generator output, runs mechanical checks, and summarizes evidence.
- Prefer real checks over verbal confidence.
- Separate generation/implementation from evaluation, review, or integration testing.
- Make the evaluator skeptical, concrete, and evidence-driven.
- Stop with evidence, not vibes.

## Install

Copy this folder into a skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R loop-adversarial-engineering ~/.codex/skills/
```

For cross-runtime installs, `~/.agents/skills/` is also supported by many Agent runtimes:

```bash
mkdir -p ~/.agents/skills
cp -R loop-adversarial-engineering ~/.agents/skills/
```

Then invoke it with:

```text
Use $loop-adversarial-engineering to run this task as an adversarial generator/evaluator loop.
```

Natural-language triggers also work when the skill is discoverable:

```text
开一个对抗 loop，把这个任务跑完
```

```text
把这个设置成 goal：一个 subagent 生成/实现，另一个 evaluator review + 集成测试
```

## When Not To Use

Do not auto-trigger this skill for simple answers, low-risk formatting edits, pure brainstorming, or tasks where the user asks for a quick one-pass response. Explicit user invocation still takes priority.

If goal tooling is unavailable or runtime policy blocks goal creation/update, stop and ask whether to continue without this skill.

If subagent tools are available, both the generator and evaluator must be independent subagents. If subagent tools are unavailable, disclose the limitation before simulating roles as separate main-thread passes and state in final evidence that this was not a complete adversarial loop.

## Shell Driver

Generate a reusable loop spec:

```bash
~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "完成接口改造并验证"
```

Set a different default round count:

```bash
ROUNDS=2 ~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "修复 bug 并验证"
```

## Evidence Validator

v1 includes a small evidence template and validator. It does not create Codex goals,
spawn subagents, wait for agents, or run a DAG workflow. The main/orchestrator records
evidence produced by the generator and evaluator.

Create a template:

```bash
loop-evidence init "Improve loop-adversarial-engineering skill" > evidence.json
```

Validate evidence:

```bash
loop-evidence validate evidence.json
```

The evidence file uses a full `goal` object and does not require `goal.id`:

```json
{
  "goal": {
    "objective": "Improve loop-adversarial-engineering skill",
    "status": "active",
    "codex_goal_used": true
  },
  "independence": {
    "subagent_tools_available": true,
    "roles_simulated": false,
    "complete_adversarial_loop": true,
    "statement": ""
  },
  "recorder": {
    "role": "main",
    "produced_generator_output": false,
    "produced_evaluator_output": false
  },
  "rounds": [
    {
      "generator": {
        "summary": "",
        "artifacts": [],
        "checks": [],
        "uncertainties": []
      },
      "evaluator": {
        "findings": {
          "blocking": [],
          "important": [],
          "missing_evidence": [],
          "residual_risk": []
        },
        "checks": []
      },
      "route": "continue"
    }
  ],
  "acceptance": []
}
```

Routes are limited to `continue`, `complete`, and `blocked`. A `complete` goal must
end with a final `complete` route, complete acceptance evidence, non-empty final
generator/evaluator checks, generator artifacts, a generator summary, and no final
blocking or important evaluator findings. Generator/evaluator checks and all
finding items must be structured objects, not bare strings. The `recorder` must be
`main` and must not claim to produce generator or evaluator output. If roles were
simulated, set `complete_adversarial_loop` to `false` and include a statement
saying the run was not a complete adversarial loop.

## Files

```text
SKILL.md                  # Codex skill instructions
agents/openai.yaml        # UI metadata
scripts/loop_spec.sh      # Shell generator for loop specs
scripts/loop-evidence     # v1 evidence template and validator CLI
loop-evidence             # Repo-root wrapper for the validator CLI
```
