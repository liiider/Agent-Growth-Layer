from pathlib import Path

import yaml


def test_ci_workflow_contains_required_jobs_and_commands() -> None:
    workflow = yaml.safe_load(
        Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    )

    jobs = workflow["jobs"]
    assert {"python", "javascript"} <= set(jobs)

    python_steps = jobs["python"]["steps"]
    python_commands = [
        step.get("run", "")
        for step in python_steps
    ]
    assert 'python -m pip install -e ".[dev]"' in python_commands
    assert "python -m ruff check ." in python_commands
    assert "python -m pytest" in python_commands
    assert "python -m compileall server sdk examples" in python_commands

    node_steps = jobs["javascript"]["steps"]
    setup_node = next(step for step in node_steps if step.get("uses") == "actions/setup-node@v6")
    assert setup_node["with"]["package-manager-cache"] is False
    assert setup_node["with"]["node-version"] == "24"

    node_commands = [
        step.get("run", "")
        for step in node_steps
    ]
    assert "npm ci" in node_commands
    assert "npm run build" in node_commands
