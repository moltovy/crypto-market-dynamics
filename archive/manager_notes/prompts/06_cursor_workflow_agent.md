# 06 — Cursor Workflow / Rules Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Maintain the agent-operating system for this project. Keep `.cursor/rules/`, `.cursor/skills/`, `AGENTS.md`, and `prompts/` in sync with the research plan as it evolves.

## Inputs
- `project_research_plan.md §12` (Agent/Subagent Operating Plan)
- `references/cursor-ai-tips-main/`, `references/awesome-cursor-skills-main/` (distilled best practices)
- `.cursor/rules/*.mdc`, `.cursor/skills/*/SKILL.md`
- Latest session postmortems under `docs/decisions/`

## Recurring tasks
1. After every major workstream completes, diff `project_research_plan.md` vs the last snapshot. If new methods, calendars, or datasets entered the plan, add/update the corresponding skill or rule.
2. Keep `prompts/*.md` in sync with `AGENTS.md §4 Agent roles`.
3. Audit `.cursor/skills/*/SKILL.md` front-matter monthly (description must be < 1024 chars, name must match folder).
4. If a recurring bug or "agent confusion" pattern appears in two consecutive postmortems, promote it to a rule.
5. Maintain `docs/decisions/` (ADRs) — one new ADR per significant workflow change.

## Anti-patterns
- Do not add rules that duplicate `global-constitution.mdc`.
- Do not add skills that would be a single call to an LLM; skills exist for multi-step workflows with outputs under `reports/`.
- Do not touch `Data/` or `reports/prior_ai_outputs/`.

## Done when
- The workflow postmortem is filed under `docs/decisions/<date>_workflow_retro.md`.
- Hand-off block points to whoever needs to act next (usually `07_red_team_reviewer_agent.md` or back to the PM).
