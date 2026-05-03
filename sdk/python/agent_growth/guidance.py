from typing import Any


class Guidance:
    def __init__(self, guidance: dict[str, Any]) -> None:
        self.guidance = guidance

    def to_prompt(self) -> str:
        sections = [
            "Runtime Guidance",
            self._render_verified_skills(),
            self._render_candidate_skills(),
            self._render_seed_skills(),
            self._render_error_patterns(),
            self._render_output_guidance(),
        ]
        return "\n\n".join(section for section in sections if section)

    def _render_verified_skills(self) -> str:
        skills = self.guidance.get("verified_skills", [])
        if not skills:
            return "Verified Skills:\nNone."
        return "Verified Skills:\n" + _render_numbered_skills(skills, status="verified")

    def _render_candidate_skills(self) -> str:
        skills = self.guidance.get("candidate_skills", [])
        if not skills:
            return "Candidate Skills:\nNone."

        return (
            "Candidate Skills:\n"
            "Candidate Skills are unverified. Use them cautiously.\n\n"
            + _render_numbered_skills(skills, status="candidate")
        )

    def _render_seed_skills(self) -> str:
        skills = self.guidance.get("seed_skills", [])
        if not skills:
            return "Seed Skills:\nNone."
        return "Seed Skills:\n" + _render_numbered_skills(skills, status="seed")

    def _render_error_patterns(self) -> str:
        patterns = self.guidance.get("error_patterns", [])
        if not patterns:
            return "Error Patterns to Avoid:\nNone."
        return "Error Patterns to Avoid:\n" + _render_bullets(patterns)

    def _render_output_guidance(self) -> str:
        guidance = self.guidance.get("output_guidance", [])
        if not guidance:
            return ""
        return "Output Guidance:\n" + _render_bullets(guidance)


def _render_numbered_skills(skills: list[dict[str, Any]], *, status: str) -> str:
    rendered = []
    for index, skill in enumerate(skills, start=1):
        lines = [f"{index}. {_render_skill_title(skill, status=status)}"]

        applies_when = skill.get("applies_when")
        if applies_when:
            lines.append(f"Use when: {applies_when[0]}")

        instructions = skill.get("instructions", [])
        if instructions:
            lines.append("Instructions:")
            lines.append(_render_bullets(instructions))

        constraints = skill.get("constraints", [])
        if constraints:
            lines.append("Constraints:")
            lines.append(_render_bullets(constraints))

        evidence_refs = skill.get("evidence_refs", [])
        if evidence_refs:
            lines.append("Evidence:")
            lines.append(_render_bullets(evidence_refs))

        rendered.append("\n".join(lines))

    return "\n\n".join(rendered)


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_skill_title(skill: dict[str, Any], *, status: str) -> str:
    name = skill.get("name", skill.get("id", "Unnamed Skill"))

    if status == "candidate":
        weight = skill.get("weight", "unknown")
        return f"{name} [Caution: unverified, {weight} weight]"

    if status == "verified":
        exam_score = skill.get("exam_score")
        if exam_score is None:
            latest_exam = skill.get("latest_exam") or {}
            exam_score = latest_exam.get("score")

        if exam_score is None:
            return f"{name} [Verified]"

        return f"{name} [Verified, exam score: {exam_score:.2f}]"

    return name
