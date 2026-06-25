# Generator Evaluator Loop

A small Codex Skill for running complex Agent work as a generator/evaluator feedback loop.

The idea is simple:

```text
goal -> generate -> evaluate -> revise -> evidence -> done
```

One subagent generates or implements. Another subagent evaluates, reviews, tests, or attacks the result. The main agent owns the goal, reconciles findings, fixes confirmed issues, and stops only when there is evidence.

## Why

This pattern has two roots.

First, it is inspired by cybernetics: closed-loop control, feedback, error correction, and adjustment toward a goal. It is not a formal control theory implementation; it is a practical Agent workflow pattern for making AI work less dependent on one-shot confidence.

Second, it is aligned with Anthropic's harness work for long-running app development. In [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), Anthropic describes a multi-agent structure with planner, generator, and evaluator roles. The key engineering move is to separate the agent doing the work from the agent judging it, then feed concrete evaluator feedback back into the generator.

## Principles

- Default to goal mode when the current agent supports goals.
- Keep each subagent single-purpose: one responsibility, one output, one validation surface.
- Prefer real checks over verbal confidence.
- Separate generation/implementation from evaluation, review, or integration testing.
- Make the evaluator skeptical, concrete, and evidence-driven.
- Stop with evidence, not vibes.

## Install

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R generator-evaluator-loop ~/.codex/skills/
```

Then invoke it with:

```text
Use $generator-evaluator-loop to run this task as a generator/evaluator loop.
```

Natural-language triggers also work when the skill is discoverable:

```text
开一个 generator/evaluator loop，把这个任务跑完
```

```text
把这个设置成 goal：一个 subagent 生成/实现，另一个 evaluator review + 集成测试
```

## Shell Driver

Generate a reusable loop spec:

```bash
~/.codex/skills/generator-evaluator-loop/scripts/loop_spec.sh "完成接口改造并验证"
```

Set a different default round count:

```bash
ROUNDS=1 ~/.codex/skills/generator-evaluator-loop/scripts/loop_spec.sh "修复 bug 并验证"
```

## Files

```text
SKILL.md                  # Codex skill instructions
agents/openai.yaml        # UI metadata
scripts/loop_spec.sh      # Shell generator for loop specs
```
