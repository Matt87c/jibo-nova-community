# Standalone BEacon repository migration

ZaneThePython maintains independent repositories for themes (e.g. Rewind16Theme) and skills (e.g. JiboPomodoro). Each has its own root-level `manifest.json`, source, and GitHub releases. The native Store's GitHub-source workflow is better served by one installable package per repo.

## Current source and scope

This repo holds **seven** themes in `themes/catalog.json`. It remains the unchanged public catalog and historical archive. The private `Matt87c/jibo-nova` harness, deployed Talk to NOVA, Hub gateway and robot configuration are not in scope.

## Safe migration

1. Install Git, GitHub CLI (`gh`), Python 3.11+ and Pillow 11.3.0 on an authenticated workstation. Configure `git user.name` and `git user.email`.
2. From this repo or another copy, run `python scripts/split_to_standalone.py` to preview the seven target names. The utility does not modify anything by default.
3. Inspect the source and automated validation workflow. Run `gh auth status` and verify the authenticated account is Matt87c.
4. Run `python scripts/split_to_standalone.py --apply` after review. This clones the **public** repository, validates all seven source packages, and for each not-yet-existing name creates a public repo using `git subtree split` to retain that theme's history. It then adds MIT license and per-theme validation CI.
5. Check GitHub Actions in each repo. Upload and test the exact distributable ZIP on Jibo (install, eye size, gaze, blinking, native Hey Jibo, NOVA, reboot, rollback). Record `docs/HARDWARE_TEST.md` results.
6. **Only after hardware signoff**, create an individual stable release per repo and attach exactly that theme's validated ZIP. Confirm BEacon can index and update the release.
7. Update the community README/catalog to point to each standalone repo once verified.

## Safety and non-goals

- Never delete, rename, archive, or force-push the community repo; retain existing releases and source during migration.
- Never automatically overwrite an existing new theme repo: the utility skips existing names, so review incomplete migrations manually.
- No robot/NOVA tokens, local IPs, private keys, backups, or deployed adapter code belong in public repositories.
- Do not publish `Talk to NOVA` publicly without a separate source/security/licensing review.
- Independent repositories alone do not make untested packages production-ready.
- GitHub repository creation is not available through the connected integration in this session. The script performs it using authenticated `gh` on a workstation.
