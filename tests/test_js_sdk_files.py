from pathlib import Path


def test_javascript_sdk_exposes_minimum_v02_methods() -> None:
    client = Path("sdk/javascript/src/client.ts").read_text(encoding="utf-8")
    guidance = Path("sdk/javascript/src/guidance.ts").read_text(encoding="utf-8")

    assert "guidance = new GuidanceResource" in client
    assert "experiences = new ExperiencesResource" in client
    assert "async get(" in guidance
    assert "async create(" in client
