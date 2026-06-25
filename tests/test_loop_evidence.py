import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "loop-evidence"
SCRIPT_SPEC = ROOT / "scripts" / "loop_spec.sh"
PY_IMPL = ROOT / "scripts" / "loop_evidence.py"


def run_cli(*args):
    return subprocess.run(
        [str(CLI), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_bare_cli(*args):
    env = os.environ.copy()
    env["PATH"] = f"{ROOT}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        ["loop-evidence", *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_evidence(payload):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    with tmp:
        json.dump(payload, tmp)
    return tmp.name


def complete_evidence():
    return {
        "goal": {
            "objective": "Improve loop-adversarial-engineering skill",
            "status": "complete",
            "codex_goal_used": True,
        },
        "independence": {
            "subagent_tools_available": True,
            "roles_simulated": False,
            "complete_adversarial_loop": True,
        },
        "recorder": {
            "role": "main",
            "produced_generator_output": False,
            "produced_evaluator_output": False,
        },
        "rounds": [
            {
                "generator": {
                    "summary": "Implemented evidence validator.",
                    "artifacts": ["scripts/loop-evidence"],
                    "checks": [{"name": "python -m unittest", "result": "pass"}],
                    "uncertainties": [],
                },
                "evaluator": {
                    "findings": {
                        "blocking": [],
                        "important": [],
                        "missing_evidence": [],
                        "residual_risk": [],
                    },
                    "checks": [{"name": "loop-evidence validate", "result": "pass"}],
                },
                "route": "complete",
            }
        ],
        "acceptance": ["validator passes complete evidence"],
    }


class LoopEvidenceCliTests(unittest.TestCase):
    def test_init_outputs_valid_json_template_without_goal_id(self):
        result = run_cli("init", "Improve loop-adversarial-engineering skill")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["goal"]["objective"], "Improve loop-adversarial-engineering skill")
        self.assertEqual(payload["goal"]["status"], "active")
        self.assertNotIn("id", payload["goal"])
        self.assertEqual(payload["recorder"]["role"], "main")
        self.assertFalse(payload["recorder"]["produced_generator_output"])
        self.assertFalse(payload["recorder"]["produced_evaluator_output"])
        self.assertIsInstance(payload["rounds"][0]["generator"], dict)
        self.assertIsInstance(payload["rounds"][0]["evaluator"], dict)

    def test_validate_passes_complete_evidence_without_goal_id(self):
        path = write_evidence(complete_evidence())

        result = run_cli("validate", path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid", result.stdout)

    def test_validate_fails_when_goal_objective_missing(self):
        payload = complete_evidence()
        del payload["goal"]["objective"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("goal.objective", result.stderr)

    def test_validate_fails_when_goal_status_is_unknown(self):
        payload = complete_evidence()
        payload["goal"]["status"] = "done"

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("goal.status", result.stderr)

    def test_validate_fails_when_round_missing_generator(self):
        payload = complete_evidence()
        del payload["rounds"][0]["generator"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rounds[0].generator", result.stderr)

    def test_validate_fails_when_round_missing_evaluator_findings(self):
        payload = complete_evidence()
        del payload["rounds"][0]["evaluator"]["findings"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rounds[0].evaluator.findings", result.stderr)

    def test_validate_fails_when_complete_goal_final_route_is_not_complete(self):
        payload = complete_evidence()
        payload["rounds"][0]["route"] = "continue"

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("final route", result.stderr)

    def test_validate_fails_when_complete_goal_has_blocking_or_important_findings(self):
        payload = complete_evidence()
        payload["rounds"][0]["evaluator"]["findings"]["important"] = [
            {"summary": "README does not document the command"}
        ]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocking or important", result.stderr)

    def test_validate_fails_when_complete_goal_has_empty_final_evidence_template(self):
        payload = complete_evidence()
        payload["rounds"][0]["generator"] = {
            "summary": "",
            "artifacts": [],
            "checks": [],
            "uncertainties": [],
        }
        payload["rounds"][0]["evaluator"] = {
            "findings": {
                "blocking": [],
                "important": [],
                "missing_evidence": [],
                "residual_risk": [],
            },
            "checks": [],
        }
        payload["acceptance"] = ["x"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete evidence", result.stderr)

    def test_validate_fails_when_simulated_roles_do_not_disclose_incomplete_loop(self):
        payload = complete_evidence()
        payload["independence"] = {
            "subagent_tools_available": False,
            "roles_simulated": True,
            "complete_adversarial_loop": True,
        }

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a complete adversarial loop", result.stderr)

    def test_validate_fails_when_simulated_roles_claim_complete_loop_even_with_tools(self):
        payload = complete_evidence()
        payload["independence"] = {
            "subagent_tools_available": True,
            "roles_simulated": True,
            "complete_adversarial_loop": True,
            "statement": "",
        }

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a complete adversarial loop", result.stderr)

    def test_validate_fails_when_generator_checks_are_bare_strings(self):
        payload = complete_evidence()
        payload["rounds"][0]["generator"]["checks"] = ["python -m unittest"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generator.checks[0]", result.stderr)

    def test_validate_fails_when_evaluator_checks_are_bare_strings(self):
        payload = complete_evidence()
        payload["rounds"][0]["evaluator"]["checks"] = ["loop-evidence validate"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evaluator.checks[0]", result.stderr)

    def test_validate_fails_when_findings_are_bare_strings(self):
        payload = complete_evidence()
        payload["goal"]["status"] = "active"
        payload["rounds"][0]["route"] = "continue"
        payload["rounds"][0]["evaluator"]["findings"]["residual_risk"] = ["untested"]

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("findings.residual_risk[0]", result.stderr)

    def test_bare_loop_evidence_command_runs_from_repo_path(self):
        result = run_bare_cli("init", "Improve loop-adversarial-engineering skill")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["goal"]["objective"], "Improve loop-adversarial-engineering skill")

    def test_shell_scripts_pass_bash_syntax_check(self):
        result = subprocess.run(
            ["bash", "-n", str(CLI), str(SCRIPT_SPEC)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_python_implementation_passes_py_compile(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(PY_IMPL)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_fails_when_main_claims_to_produce_or_evaluate(self):
        payload = complete_evidence()
        payload["recorder"]["produced_evaluator_output"] = True

        result = run_cli("validate", write_evidence(payload))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("recorder", result.stderr)


if __name__ == "__main__":
    unittest.main()
