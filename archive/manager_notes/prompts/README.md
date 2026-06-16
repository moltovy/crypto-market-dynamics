# prompts/

Ready-to-use agent prompts. Each file is a single, copy-pasteable prompt tailored to **this** repo. The numeric prefix is the standard execution order.

| #  | File                                    | Agent role               | Owner section in plan |
|----|-----------------------------------------|--------------------------|-----------------------|
| 01 | `01_data_cleaning_agent.md`             | Data cleaner             | §11.1, §11.2          |
| 02 | `02_exploratory_analysis_agent.md`      | Exploratory analyst      | §11.3                 |
| 03 | `03_quant_methods_agent.md`             | Quant econometrician     | §11.4                 |
| 04 | `04_visualization_agent.md`             | Viz engineer             | §11.6, §15            |
| 05 | `05_writing_agent.md`                   | Writer                   | §11.7                 |
| 06 | `06_cursor_workflow_agent.md`           | Workflow/rules engineer  | §12                   |
| 07 | `07_red_team_reviewer_agent.md`         | Red-team reviewer        | §11.8, §16            |
| 08 | `08_final_synthesis_agent.md`           | Final synthesis          | §11.9                 |

Shared scaffolds live under `templates/`:
- `templates/agent_preamble.md` — repo invariants every agent must observe.
- `templates/handoff.md` — the hand-off markdown contract between agents.
