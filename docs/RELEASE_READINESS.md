# Release readiness and acceptance

**Current status: release candidate only.** Automated source/ZIP/security checks are passing, but physical robot testing of all five exact distributable ZIPs has **not** been signed off. Keep initial GitHub releases marked **prerelease**; do not market them as production-tested or official BEacon Store approved until hardware acceptance is documented.

## Release model (single community repository)

A **community bundle release** attaches five independently installable ZIPs, a SHA256 checksum list, and release notes. Individual theme versions remain in their manifests; the bundle release uses a separate tag such as `community-rc-2026-11-01-1`. This avoids mistakenly renaming every theme to the same bundle version.

The GitHub Store's normal GitHub-source workflow uses the latest **stable release** of a **single-theme repository**, whereas this repository contains multiple themes. Bundle releases support manual downloading, not five native Store entries. For per-theme Store install/update, use separate release repositories or an alternate storefront approach agreed with BEacon maintainers.

## Automated acceptance

- [x] Each manifest has a distinct name and correct version, theme type and minimum jibo-tbd compatibility declaration.
- [x] Each ZIP is rebuilt deterministically and matches the source bytes, contains open/listening/closed image assets and no executable code.
- [x] All PNGs decode, have permissible dimensions, and contain no embedded metadata.
- [x] Static scan reports no common credentials, private network addresses, keys, or user home paths in the public snapshot.
- [x] SHA256SUMS generated for release assets.
- [ ] GitHub Actions on the exact public commit has completed successfully (pending source upload to GitHub).

Automated checks do not prove license ownership, operating behavior, or that a release can be installed on every robot.

## Hardware acceptance required before stable release

For **each** theme, download the **exact asset** from the release and fill in that theme's `docs/HARDWARE_TEST.md` with tester/date/build, SHA256 and observations. Confirm:

1. Installation and upgrades do not auto-apply or overwrite other themes.
2. The new open-eye texture is centered and the full range of gaze motion is not clipped.
3. Closed-eye, blink, petting, sleep and listening textures transition smoothly.
4. Hey Jibo, BEacon, Agent Mode, menus and Talk to NOVA continue operating.
5. Switch to None to return to stock appearance; restart/offline persistence works.
6. No black square border, visible seam, crash, frozen face, stuck audio or unexpected layout changes.

Promotion decision: **pending**. Maintain a known-good installed theme as rollback. No firmware, TLS, token, gateway or robot system changes are part of these theme tests.

## Licensing and attribution gate

The repository currently has an MIT license. Attribution must remain visible as Matt87c. Confirm all artwork, source and contributions can actually be redistributed under that license; third-party packages must retain their own notices. A clean security scan alone does not establish redistribution rights.