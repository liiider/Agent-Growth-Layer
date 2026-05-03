# Enterprise QA Example

This example shows the intended V0.3 enterprise QA pattern:

1. Capture a failed or corrected QA answer as an experience.
2. Extract candidate cognition with evidence refs.
3. Build a candidate skill from repeated QA failure patterns.
4. Run a manual or LLM-judge exam before promoting the skill.
5. Use verified guidance in later enterprise QA runs.

The important boundary is that candidate guidance is visible but labeled as unverified until an exam promotes it.
