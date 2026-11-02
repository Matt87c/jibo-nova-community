# Publishing this existing public GitHub repository

Target: https://github.com/Matt87c/jibo-nova-community

**Never** change the private `Matt87c/jibo-nova` repository, copy its `.git` directory, or expose live robot/NOVA configuration.

## 1. Commit the audited source and ZIPs

Use the isolated publishing snapshot. Never clone the private repo for this step.

- Run `python -m pip install Pillow==11.3.0`, then `python scripts/validate_all.py`.
- Use `scripts/Import-To-Existing-Public-Repo.ps1` to import into a clone of only the public repo, or follow its manual instructions.
- Inspect the diff before pushing. Keep GitHub's existing root MIT LICENSE untouched.
- Confirm `themes/<slug>/dist/<slug>.zip` is actually committed and downloadable.

## 2. Publish a prerelease

After the source is pushed and CI is green, in **GitHub > Actions > Publish Jibo NOVA Community prerelease > Run workflow**, enter a unique tag such as `community-rc-2026-11-01-1`.

The workflow rebuilds/validates all themes, scans for common secrets, verifies reproducibility, and attaches five installable ZIPs plus `SHA256SUMS.txt` to the prerelease.

**Do not promote to stable until** the five hardware acceptance checklists are signed off on the actual Jibo. See `docs/RELEASE_READINESS.md`.

## 3. Understand Store indexing

A combined monorepo GitHub release supports manual downloads. The native BEacon GitHub-source Store generally expects one theme per repository with a published stable release; discuss independent release repos or a maintainer-approved storefront with the 5x1 developer for Store-wide install/update.
