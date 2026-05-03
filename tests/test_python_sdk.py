from typing import Any

import httpx
from agent_growth import AgentGrowthClient, Guidance


def test_guidance_to_prompt_renders_cold_start_sections() -> None:
    guidance = Guidance(
        {
            "verified_skills": [],
            "candidate_skills": [],
            "seed_skills": [
                {
                    "name": "Uncertainty Handling",
                    "instructions": [
                        "State what information is missing.",
                        "Do not invent facts.",
                    ],
                    "constraints": ["Do not present assumptions as verified facts."],
                }
            ],
            "output_guidance": ["Start by identifying missing information."],
            "error_patterns": [],
        }
    )

    prompt = guidance.to_prompt()

    assert "Runtime Guidance" in prompt
    assert "Verified Skills:\nNone." in prompt
    assert "Candidate Skills:\nNone." in prompt
    assert "Seed Skills:" in prompt
    assert "Uncertainty Handling" in prompt
    assert "Start by identifying missing information." in prompt


def test_sdk_exports_client() -> None:
    client = AgentGrowthClient("http://example.test/")

    assert client.base_url == "http://example.test"
    assert client.experiences.base_url == "http://example.test"
    assert client.feedback.base_url == "http://example.test"
    assert client.cognitions.base_url == "http://example.test"
    assert client.skills.base_url == "http://example.test"
    assert client.audit.base_url == "http://example.test"


def test_guidance_to_prompt_marks_candidate_skills_as_unverified() -> None:
    guidance = Guidance(
        {
            "verified_skills": [],
            "candidate_skills": [
                {
                    "name": "Refund Policy Handling",
                    "weight": "low",
                    "confidence": 0.72,
                    "applies_when": [
                        "The user asks about refund eligibility or refund rejection."
                    ],
                    "instructions": [
                        "Check the user's region before applying refund rules.",
                        "Check order status before explaining refund eligibility.",
                    ],
                    "constraints": [
                        "Do not apply generic refund rules when region is unknown.",
                    ],
                    "evidence_refs": ["exp_001", "exp_004"],
                }
            ],
            "seed_skills": [],
            "error_patterns": [
                "Answering refund eligibility before checking region and order status."
            ],
            "output_guidance": ["First state what needs to be checked."],
        }
    )

    prompt = guidance.to_prompt()

    assert "Candidate Skills are unverified. Use them cautiously." in prompt
    assert "Refund Policy Handling [Caution: unverified, low weight]" in prompt
    assert "Evidence:" in prompt
    assert "- exp_001" in prompt
    assert "Verified Skills:\nNone." in prompt


def test_guidance_to_prompt_renders_verified_skill_exam_score() -> None:
    guidance = Guidance(
        {
            "verified_skills": [
                {
                    "name": "Refund Policy Handling",
                    "exam_score": 0.86,
                    "applies_when": [
                        "The user asks about refund eligibility or refund rejection."
                    ],
                    "instructions": [
                        "Check the user's region.",
                        "Check order status.",
                    ],
                    "constraints": ["Do not promise refund approval."],
                    "evidence_refs": ["exp_001", "exam_001"],
                }
            ],
            "candidate_skills": [],
            "seed_skills": [],
            "error_patterns": [
                "Promising refund approval without tool confirmation.",
            ],
            "output_guidance": ["Start with what has been checked."],
        }
    )

    prompt = guidance.to_prompt()

    assert "Refund Policy Handling [Verified, exam score: 0.86]" in prompt
    assert "Candidate Skills:\nNone." in prompt
    assert "- exam_001" in prompt
    assert "Promising refund approval without tool confirmation." in prompt


def test_python_sdk_resources_call_expected_api_paths(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_request(
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float,
    ) -> httpx.Response:
        calls.append(
            {
                "method": method,
                "url": url,
                "json": json,
                "params": params,
                "timeout": timeout,
            }
        )
        return httpx.Response(
            200,
            json={"ok": True},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(httpx, "request", fake_request)
    client = AgentGrowthClient("http://example.test/", timeout=17)

    assert client.experiences.get("exp_1") == {"ok": True}
    assert client.experiences.retry_extraction("exp_1") == {"ok": True}
    assert client.feedback.create(
        experience_id="exp_1",
        feedback_type="human_corrected",
        content="Check region.",
        score=0.2,
    ) == {"ok": True}
    assert client.cognitions.list(agent_id="agent_1", limit=10) == {"ok": True}
    assert client.cognitions.get("cog_1") == {"ok": True}
    assert client.cognitions.update_status("cog_1", "verified") == {"ok": True}
    assert client.skills.import_prompt(
        agent_id="agent_1",
        domain="support",
        intent="refund",
        prompt="Always check order status.",
    ) == {"ok": True}
    assert client.skills.build(
        agent_id="agent_1",
        domain="support",
        intent="refund",
        name="Refund Skill",
        cognition_ids=["cog_1"],
    ) == {"ok": True}
    assert client.skills.list(status="candidate", limit=5) == {"ok": True}
    assert client.skills.get("skill_1") == {"ok": True}
    assert client.skills.update("skill_1", procedure=["Check order status"]) == {"ok": True}
    assert client.skills.update_status("skill_1", "verified") == {"ok": True}
    assert client.skills.run_exam("skill_1", score=0.9) == {"ok": True}
    assert client.audit.get("skill", "skill_1") == {"ok": True}

    assert calls == [
        {
            "method": "GET",
            "url": "http://example.test/v1/experiences/exp_1",
            "json": None,
            "params": None,
            "timeout": 17,
        },
        {
            "method": "POST",
            "url": "http://example.test/v1/experiences/exp_1/extract",
            "json": None,
            "params": None,
            "timeout": 17,
        },
        {
            "method": "POST",
            "url": "http://example.test/v1/feedback",
            "json": {
                "experience_id": "exp_1",
                "feedback_type": "human_corrected",
                "content": "Check region.",
                "score": 0.2,
            },
            "params": None,
            "timeout": 17,
        },
        {
            "method": "GET",
            "url": "http://example.test/v1/cognitions",
            "json": None,
            "params": {
                "agent_id": "agent_1",
                "domain": None,
                "intent": None,
                "status": None,
                "limit": 10,
            },
            "timeout": 17,
        },
        {
            "method": "GET",
            "url": "http://example.test/v1/cognitions/cog_1",
            "json": None,
            "params": None,
            "timeout": 17,
        },
        {
            "method": "PATCH",
            "url": "http://example.test/v1/cognitions/cog_1/status",
            "json": {"status": "verified"},
            "params": None,
            "timeout": 17,
        },
        {
            "method": "POST",
            "url": "http://example.test/v1/skills/import_prompt",
            "json": {
                "agent_id": "agent_1",
                "domain": "support",
                "intent": "refund",
                "prompt": "Always check order status.",
            },
            "params": None,
            "timeout": 17,
        },
        {
            "method": "POST",
            "url": "http://example.test/v1/skills/build",
            "json": {
                "agent_id": "agent_1",
                "domain": "support",
                "intent": "refund",
                "name": "Refund Skill",
                "cognition_ids": ["cog_1"],
            },
            "params": None,
            "timeout": 17,
        },
        {
            "method": "GET",
            "url": "http://example.test/v1/skills",
            "json": None,
            "params": {
                "agent_id": None,
                "domain": None,
                "intent": None,
                "status": "candidate",
                "limit": 5,
            },
            "timeout": 17,
        },
        {
            "method": "GET",
            "url": "http://example.test/v1/skills/skill_1",
            "json": None,
            "params": None,
            "timeout": 17,
        },
        {
            "method": "PATCH",
            "url": "http://example.test/v1/skills/skill_1",
            "json": {"procedure": ["Check order status"]},
            "params": None,
            "timeout": 17,
        },
        {
            "method": "PATCH",
            "url": "http://example.test/v1/skills/skill_1/status",
            "json": {"status": "verified"},
            "params": None,
            "timeout": 17,
        },
        {
            "method": "POST",
            "url": "http://example.test/v1/skills/skill_1/exam",
            "json": {"evaluator": "manual_score", "score": 0.9, "cases": []},
            "params": None,
            "timeout": 17,
        },
        {
            "method": "GET",
            "url": "http://example.test/v1/audit/skill/skill_1",
            "json": None,
            "params": None,
            "timeout": 17,
        },
    ]
