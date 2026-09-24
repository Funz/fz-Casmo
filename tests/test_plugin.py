"""Tests for the fz-Casmo wrapper.

They run the fz CLI (fzi/fzc/fzo/fzr) as a user would, without CASMO5:
- tests/mock/cas5 stands in for the CASMO5 launcher (runner wiring, exit codes);
- tests/fixtures/<case>/ holds output files plus an expected.json, checked with fzo
  (output parsers). Add real CASMO5 output excerpts there to validate the parsers.

Run from the repository root:  pytest tests/
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MODEL = REPO / ".fz" / "models" / "CASMO.json"
ALIAS = REPO / ".fz" / "calculators" / "localhost_CASMO.json"
RUNNER = REPO / ".fz" / "calculators" / "CASMO.sh"
EXAMPLE = REPO / "examples" / "CASMO" / "input.inp"
MOCK_CAS5 = REPO / "tests" / "mock" / "cas5"
FIXTURES = REPO / "tests" / "fixtures"

EXAMPLE_VARIABLES = {
    "boron": 600, "burnup_max": 60, "enrichment": 4.0, "fuel_temp": 900,
    "moderator_temp": 580, "power_density": 104.5, "theoretical_density": 0.95,
}


def fz_cli(tool, *args, env=None, check=True):
    """Run an fz CLI tool and return its decoded JSON output (None for fzc)."""
    fmt = [] if tool == "fzc" else ["--format", "json"]
    proc = subprocess.run([tool, *args, *fmt], capture_output=True, text=True, env=env)
    if check:
        assert proc.returncode == 0, f"{tool} failed:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(proc.stdout) if fmt else None


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A scratch project with the wrapper's .fz/ installed, as `fz install` would."""
    shutil.copytree(REPO / ".fz", tmp_path / ".fz")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def mock_env(**extra):
    env = dict(os.environ, CASMO_CMD=str(MOCK_CAS5), FZ_MAX_RETRIES="1")
    env.pop("CASMO_PATH", None)
    env.update(extra)
    return env


# --- static checks -------------------------------------------------------------

def test_model_json():
    model = json.loads(MODEL.read_text())
    assert model["id"] == MODEL.stem
    for key in ("varprefix", "formulaprefix", "delim", "commentline", "output"):
        assert key in model
    assert model["commentline"] == "*"
    assert model["output"]


def test_alias_binds_model_to_runner():
    alias = json.loads(ALIAS.read_text())
    assert alias["uri"] == "sh://"
    assert alias["models"] == {"CASMO": "bash .fz/calculators/CASMO.sh"}
    assert os.access(RUNNER, os.X_OK)
    assert subprocess.run(["bash", "-n", str(RUNNER)]).returncode == 0


# --- input side ----------------------------------------------------------------

def test_fzi_finds_example_variables(project):
    found = fz_cli("fzi", "--input_path", str(EXAMPLE), "--model", "CASMO")
    for name, default in EXAMPLE_VARIABLES.items():
        assert found.get(name) == default, name


def test_fzc_compiles_example(project):
    fz_cli("fzc", "--input_path", str(EXAMPLE), "--model", "CASMO",
           "--input_variables", json.dumps({"enrichment": 3.5, "theoretical_density": 0.9}),
           "--output_dir", "compiled")
    compiled = next(Path("compiled").rglob("input.inp")).read_text()
    assert "${" not in compiled and "@{" not in compiled
    assert "FUE 1 9.864/3.5" in compiled          # formula 10.96 * 0.9, rounded
    assert "TFU=900 TMO=580 BOR=600" in compiled  # defaults applied
    assert "DEP -60" in compiled


# --- output side: fixtures -----------------------------------------------------

FIXTURE_CASES = sorted(p.parent.name for p in FIXTURES.glob("*/expected.json"))


@pytest.mark.parametrize("case", FIXTURE_CASES)
def test_output_parsers_on_fixture(project, case):
    shutil.copytree(FIXTURES / case, "case")
    Path("case/expected.json").unlink()
    expected = json.loads((FIXTURES / case / "expected.json").read_text())
    parsed = fz_cli("fzo", "--output_path", "case", "--model", "CASMO")[0]
    for name, value in expected.items():
        assert parsed.get(name) == pytest.approx(value), name


# --- end to end with the mock launcher ----------------------------------------

def test_fzr_discovers_alias_and_runs(project):
    """No --calculators: the installed localhost_CASMO alias must be found."""
    rows = fz_cli("fzr", "--input_path", str(EXAMPLE), "--model", "CASMO",
                  "--input_variables", json.dumps({"enrichment": [3.0, 4.0, 5.0]}),
                  "--results_dir", "results", env=mock_env())
    assert [r["status"] for r in rows] == ["done"] * 3
    by_enr = {r["enrichment"]: r for r in rows}
    assert by_enr[3.0]["k_inf"] == pytest.approx(1.2)
    assert by_enr[5.0]["k_inf"] == pytest.approx(1.4)
    assert by_enr[4.0]["cax_files"] == ["input.cax"]


def test_fzr_reports_code_failure(project):
    rows = fz_cli("fzr", "--input_path", str(EXAMPLE), "--model", "CASMO",
                  "--input_variables", json.dumps({"enrichment": 4.0}),
                  "--results_dir", "results", env=mock_env(MOCK_CASMO_FAIL="1"),
                  check=False)
    assert rows[0]["status"] != "done"


def test_runner_without_launcher_fails_clearly(project, tmp_path):
    shutil.copy(EXAMPLE, "input.inp")
    env = dict(os.environ, PATH="/usr/bin:/bin")
    for var in ("CASMO_CMD", "CASMO_PATH"):
        env.pop(var, None)
    proc = subprocess.run(["bash", str(RUNNER), "input.inp"],
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 2
    assert "CASMO5 launcher not found" in proc.stderr
