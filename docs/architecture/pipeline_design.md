# Pipeline Design

The public reproduction path is intentionally short:

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_all.py
```

`scripts/run_all.py` delegates to `scripts/export_outputs.py`, which copies the
tracked, maintained analysis artifacts into the canonical `outputs/` layout and
writes `outputs/manifest.json`.

Legacy analysis scripts remain available for deeper regeneration and audit
work, but the README exposes one public command path.
