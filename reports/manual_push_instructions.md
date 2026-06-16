# Manual Push Instructions

## Current Blocker

Local branch `portfolio_v2` is ready, but the automated push was rejected by
GitHub because the active OAuth token lacks the `workflow` scope required to
create or update files under `.github/workflows/`.

Command run:

```powershell
git push -u origin portfolio_v2
```

Observed error:

```text
remote rejected] portfolio_v2 -> portfolio_v2 (refusing to allow an OAuth App to create or update workflow `.github/workflows/ci.yml` without `workflow` scope)
error: failed to push some refs to 'https://github.com/moltovy/Crypto-Research-Paper-Data-Factors-Analysis-.git'
```

`gh auth status` showed the active token scopes as:

```text
'gist', 'read:org', 'repo'
```

## Fix Token Scope

Run:

```powershell
gh auth refresh -h github.com -s workflow
```

Complete the browser authorization flow if prompted. Then confirm:

```powershell
gh auth status
```

Expected scope list should include `workflow` along with `repo`.

## Push Branch

After refreshing the token:

```powershell
cd "C:/Dev/Projects/Crypto Analysis"
git status --short
git status --short -- Data
git push -u origin portfolio_v2
```

Expected:

```text
branch 'portfolio_v2' set up to track 'origin/portfolio_v2'
```

Verify the remote branch:

```powershell
git ls-remote --heads origin portfolio_v2
```

Expected: one line containing the remote commit hash and
`refs/heads/portfolio_v2`.
