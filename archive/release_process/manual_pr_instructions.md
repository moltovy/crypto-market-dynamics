# Manual PR Instructions

## Prerequisite

Push `portfolio_v2` first. If push is blocked by missing workflow scope, follow
`reports/manual_push_instructions.md`.

## Create PR With GitHub CLI

```powershell
cd "C:/Dev/Projects/Crypto Analysis"
gh pr create --base main --head portfolio_v2 --title "Build Crypto Market Factor Lab portfolio releases v2.1/v2.2" --body-file reports/pr_summary_portfolio_v2.md
```

## Create PR In Browser

Open:

```text
https://github.com/moltovy/Crypto-Research-Paper-Data-Factors-Analysis-/compare/main...portfolio_v2?expand=1
```

Use:

- Title: `Build Crypto Market Factor Lab portfolio releases v2.1/v2.2`
- Body: paste the contents of `reports/pr_summary_portfolio_v2.md`

## After PR Creation

Record the PR URL in:

- `reports/final_public_readiness_audit.md`
- `reports/pr_summary_portfolio_v2.md`

Then commit and push the metadata update:

```powershell
git add reports/final_public_readiness_audit.md reports/pr_summary_portfolio_v2.md
git commit -m "docs: record PR publication details"
git push
```
