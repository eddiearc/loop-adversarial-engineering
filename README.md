# Loop Adversarial Engineering

A small Codex Skill for running complex Agent work as an adversarial feedback loop.

The idea is simple:

```text
goal -> implement -> adversarial review/test -> fix -> evidence -> done
```

One subagent does the work. Another subagent reviews, tests, or attacks the result. The main agent owns the goal, reconciles findings, fixes confirmed issues, and stops only when there is evidence.

## Why

This is inspired by cybernetics: closed-loop control, feedback, error correction, and adjustment toward a goal.

It is not a formal control theory implementation. It is a practical Agent workflow pattern for making AI work less dependent on one-shot confidence.

## Principles

- Default to goal mode when the current agent supports goals.
- Keep each subagent single-purpose: one responsibility, one output, one validation surface.
- Prefer real checks over verbal confidence.
- Separate implementation from adversarial review or integration testing.
- Stop with evidence, not vibes.

## Install

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R loop-adversarial-engineering ~/.codex/skills/
```

Then invoke it with:

```text
Use $loop-adversarial-engineering to run this task as an adversarial loop.
```

Natural-language triggers also work when the skill is discoverable:

```text
开一个对抗 loop，把这个任务跑完
```

```text
把这个设置成 goal：一个 subagent 实现，另一个 review + 集成测试
```

## Shell Driver

Generate a reusable loop spec:

```bash
~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "完成接口改造并验证"
```

Set a different default round count:

```bash
ROUNDS=1 ~/.codex/skills/loop-adversarial-engineering/scripts/loop_spec.sh "修复 bug 并验证"
```

## Files

```text
SKILL.md                  # Codex skill instructions
agents/openai.yaml        # UI metadata
scripts/loop_spec.sh      # Shell generator for loop specs
```
