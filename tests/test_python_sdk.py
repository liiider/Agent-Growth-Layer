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
