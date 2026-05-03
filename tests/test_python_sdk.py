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
