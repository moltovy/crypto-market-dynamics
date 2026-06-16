# Manual CI Check Instructions

## Prerequisite

Create the PR from `portfolio_v2` into `main`.

## Check CI With GitHub CLI

```powershell
cd "C:/Dev/Projects/Crypto Analysis"
gh pr checks --watch
```

If you need run-level detail:

```powershell
gh run list --branch portfolio_v2 --limit 10
gh run view <run-id> --log-failed
```

Expected jobs:

- CI quality job with `uv sync --all-extras`
- pytest
- mypy
- focused Ruff

The manual portfolio smoke workflow is intentionally triggered manually:

```powershell
gh workflow run portfolio-smoke.yml --ref portfolio_v2
gh run list --workflow portfolio-smoke.yml --branch portfolio_v2 --limit 5
```

## Check CI In Browser

Open:

```text
https://github.com/moltovy/Crypto-Research-Paper-Data-Factors-Analysis-/actions
```

Filter by branch `portfolio_v2`.

## If CI Fails

1. Open the failed job log.
2. Identify the exact failing command.
3. Fix only the smallest release blocker.
4. Do not modify `Data/`.
5. Do not add new analytics.
6. Run the local equivalent.
7. Commit and push.

If the only issue is broad legacy lint, keep CI focused on maintained portfolio
paths and document the legacy cleanup as future work.
