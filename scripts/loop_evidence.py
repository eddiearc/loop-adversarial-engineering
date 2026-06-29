#!/usr/bin/env python3
import argparse
import json
import sys


VALID_GOAL_STATUSES = {"active", "complete", "blocked"}
VALID_ROUTES = {"continue", "complete", "blocked"}
FINDING_KEYS = ("blocking", "important", "missing_evidence", "residual_risk")


def evidence_template(objective):
    return {
        "goal": {
            "objective": objective,
            "status": "active",
            "codex_goal_used": True,
        },
        "independence": {
            "subagent_tools_available": False,
            "roles_simulated": False,
            "complete_adversarial_loop": False,
            "statement": "",
        },
        "recorder": {
            "role": "main",
            "produced_generator_output": False,
            "produced_evaluator_output": False,
        },
        "rounds": [
            {
                "generator": {
                    "summary": "",
                    "artifacts": [],
                    "checks": [],
                    "uncertainties": [],
                },
                "evaluator": {
                    "findings": {
                        "blocking": [],
                        "important": [],
                        "missing_evidence": [],
                        "residual_risk": [],
                    },
                    "checks": [],
                },
                "route": "continue",
            }
        ],
        "acceptance": [],
    }


def is_nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def has_evidence_content(value):
    if isinstance(value, str):
        return is_nonempty_string(value)
    if isinstance(value, dict):
        return bool(value) and any(has_evidence_content(item) for item in value.values())
    if isinstance(value, list):
        return bool(value) and any(has_evidence_content(item) for item in value)
    return False


def require_object(errors, value, path):
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return False
    return True


def require_list(errors, value, path):
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return False
    return True


def require_nonempty_list(errors, value, path):
    if require_list(errors, value, path) and not value:
        errors.append(f"{path} must contain complete evidence")


def require_nonempty_evidence_list(errors, value, path):
    if not require_list(errors, value, path):
        return
    if not value:
        errors.append(f"{path} must contain complete evidence")
        return
    for index, item in enumerate(value):
        if not has_evidence_content(item):
            errors.append(f"{path}[{index}] must contain complete evidence")


def require_structured_entries(errors, value, path, required_fields):
    if not require_list(errors, value, path):
        return
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not require_object(errors, item, item_path):
            continue
        for field in required_fields:
            if not is_nonempty_string(item.get(field)):
                errors.append(f"{item_path}.{field} is required")


def validate_generator(errors, value, path):
    if not require_object(errors, value, path):
        return
    if not isinstance(value.get("summary"), str):
        errors.append(f"{path}.summary must be a string")
    require_list(errors, value.get("artifacts"), f"{path}.artifacts")
    require_structured_entries(errors, value.get("checks"), f"{path}.checks", ("name", "result"))
    for key in ("uncertainties",):
        require_list(errors, value.get(key), f"{path}.{key}")


def validate_findings(errors, value, path):
    if not require_object(errors, value, path):
        return
    for key in FINDING_KEYS:
        require_structured_entries(errors, value.get(key), f"{path}.{key}", ("summary",))


def validate_evaluator(errors, value, path):
    if not require_object(errors, value, path):
        return
    validate_findings(errors, value.get("findings"), f"{path}.findings")
    require_structured_entries(errors, value.get("checks"), f"{path}.checks", ("name", "result"))


def finding_count(findings, key):
    value = findings.get(key) if isinstance(findings, dict) else None
    return len(value) if isinstance(value, list) else 0


def validate_evidence(payload):
    errors = []

    if not require_object(errors, payload, "evidence"):
        return errors

    goal = payload.get("goal")
    if require_object(errors, goal, "goal"):
        if not is_nonempty_string(goal.get("objective")):
            errors.append("goal.objective is required")
        if goal.get("status") not in VALID_GOAL_STATUSES:
            errors.append("goal.status must be active, complete, or blocked")
        if goal.get("codex_goal_used") is not True:
            errors.append("goal.codex_goal_used must be true")

    independence = payload.get("independence")
    if require_object(errors, independence, "independence"):
        if not isinstance(independence.get("subagent_tools_available"), bool):
            errors.append("independence.subagent_tools_available must be a boolean")
        if not isinstance(independence.get("roles_simulated"), bool):
            errors.append("independence.roles_simulated must be a boolean")
        if not isinstance(independence.get("complete_adversarial_loop"), bool):
            errors.append("independence.complete_adversarial_loop must be a boolean")
        if (
            independence.get("subagent_tools_available") is False
            and independence.get("complete_adversarial_loop") is not False
        ):
            errors.append(
                "independence.complete_adversarial_loop must be false when "
                "subagent_tools_available is false"
            )
        if independence.get("roles_simulated") is True:
            statement = independence.get("statement", "")
            if independence.get("complete_adversarial_loop") is not False or (
                "not a complete adversarial loop" not in statement.lower()
            ):
                errors.append(
                    "simulated roles must state "
                    "this was not a complete adversarial loop"
                )

    recorder = payload.get("recorder")
    if require_object(errors, recorder, "recorder"):
        if recorder.get("role") != "main":
            errors.append("recorder.role must be main")
        if recorder.get("produced_generator_output") is not False:
            errors.append("recorder must not produce generator output")
        if recorder.get("produced_evaluator_output") is not False:
            errors.append("recorder must not produce evaluator output")

    rounds = payload.get("rounds")
    complete_route_indexes = []
    if require_list(errors, rounds, "rounds"):
        if not rounds:
            errors.append("rounds must contain at least one round")
        for index, round_payload in enumerate(rounds):
            round_path = f"rounds[{index}]"
            if not require_object(errors, round_payload, round_path):
                continue

            if "generator" not in round_payload:
                errors.append(f"{round_path}.generator is required")
            else:
                validate_generator(errors, round_payload.get("generator"), f"{round_path}.generator")

            if "evaluator" not in round_payload:
                errors.append(f"{round_path}.evaluator is required")
                findings = None
            else:
                evaluator = round_payload.get("evaluator")
                validate_evaluator(errors, evaluator, f"{round_path}.evaluator")
                findings = evaluator.get("findings") if isinstance(evaluator, dict) else None

            route = round_payload.get("route")
            if route not in VALID_ROUTES:
                errors.append(f"{round_path}.route must be continue, complete, or blocked")
            elif route == "complete":
                complete_route_indexes.append(index)
            if finding_count(findings, "blocking") or finding_count(findings, "important"):
                if route not in {"continue", "blocked"}:
                    errors.append(
                        f"{round_path}.route must be continue or blocked when "
                        "blocking or important findings remain"
                    )

    acceptance = payload.get("acceptance")
    require_list(errors, acceptance, "acceptance")

    goal_status = goal.get("status") if isinstance(goal, dict) else None
    if isinstance(rounds, list) and rounds:
        final_round = rounds[-1] if isinstance(rounds[-1], dict) else {}
        final_route = final_round.get("route")
        for index in complete_route_indexes:
            if index != len(rounds) - 1:
                errors.append(
                    f"rounds[{index}].route=complete must only appear on the final round"
                )
        if complete_route_indexes and goal_status != "complete":
            errors.append("route=complete requires goal.status=complete")
        if goal_status == "complete" and final_route != "complete":
            errors.append("goal.status=complete requires final route to be complete")
        completion_claimed = goal_status == "complete" or final_route == "complete"
    else:
        completion_claimed = goal_status == "complete"

    if completion_claimed and isinstance(rounds, list) and rounds:
        final_round = rounds[-1] if isinstance(rounds[-1], dict) else {}
        final_evaluator = final_round.get("evaluator")
        final_findings = (
            final_evaluator.get("findings") if isinstance(final_evaluator, dict) else None
        )
        final_generator = final_round.get("generator")
        if isinstance(final_generator, dict):
            if not is_nonempty_string(final_generator.get("summary")):
                errors.append("goal.status=complete requires complete evidence in final generator summary")
            require_nonempty_evidence_list(
                errors,
                final_generator.get("artifacts"),
                "rounds[-1].generator.artifacts",
            )
            require_nonempty_evidence_list(
                errors,
                final_generator.get("checks"),
                "rounds[-1].generator.checks",
            )
        if isinstance(final_evaluator, dict):
            require_nonempty_evidence_list(
                errors,
                final_evaluator.get("checks"),
                "rounds[-1].evaluator.checks",
            )
        if finding_count(final_findings, "blocking") or finding_count(final_findings, "important"):
            errors.append(
                "goal.status=complete requires no final blocking or important findings"
            )
        if finding_count(final_findings, "missing_evidence"):
            errors.append(
                "goal.status=complete requires no final missing evidence findings"
            )
        if isinstance(independence, dict) and independence.get("complete_adversarial_loop") is not True:
            errors.append(
                "goal.status=complete requires independence.complete_adversarial_loop=true"
            )
        require_nonempty_evidence_list(errors, acceptance, "acceptance")

    return errors


def load_json(path):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def cmd_init(args):
    json.dump(evidence_template(args.objective), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_validate(args):
    try:
        payload = load_json(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid JSON evidence: {exc}", file=sys.stderr)
        return 1

    errors = validate_evidence(payload)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print("valid")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="loop-evidence")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="write a v1 evidence template")
    init_parser.add_argument("objective")
    init_parser.set_defaults(func=cmd_init)

    validate_parser = subparsers.add_parser("validate", help="validate a v1 evidence file")
    validate_parser.add_argument("path", help="path to evidence JSON, or '-' to read stdin")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
