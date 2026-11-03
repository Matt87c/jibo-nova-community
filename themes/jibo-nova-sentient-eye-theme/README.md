# NOVA Sentient Eye

A Jibo-inspired, futuristic cyan-and-electric-blue almond-shaped AI eye with a glossy central pupil, luminous iris, and subtle precision-HUD detailing. Created by **[Matt87c](https://github.com/Matt87c)** for Jibo robots running 5x1/OpenJibo with BEacon.

**Status:** release candidate; automated checks and physical-robot acceptance must pass before claiming production readiness or official BEacon Store approval. This is an independent community theme, not an official 5x1/Jibo release.

- **Version:** 1.0.2 (updates 1.0.1)
- **Supported theme API:** jibo-tbd 3.1.6 or later
- **Native eye size:** 135% of stock
- **Theme category:** visual-only, no executable skill code
- **Developer:** Matt87c
- **License:** MIT for repository-owned theme materials; verify the rights for any added third-party artwork

## What's new in 1.0.2

The original v1.0.0 included `face/eyeListening.png`, but it was byte-for-byte identical to the idle `face/eye.png`. The packaging now creates a distinct blue-lit iris and illuminated listening ring from the original selected-eye artwork, preserving the exact alpha silhouette. The eye's normal and closed states remain unchanged. The owner confirms both candidate themes function locally on Jibo; remaining hardware checklist items are not attested.

## Install or upgrade

Download **`jibo-nova-sentient-eye-theme.zip`** from the theme's `dist/` folder after a validated build or from an attached community release asset. Do not download GitHub's repository source ZIP. In **BEacon → Store → Themes → ⋯ → Upload Theme ZIP**, select the package, then choose **NOVA Sentient Eye → Apply**. An upload should not modify the selected theme until applied. Choose **None** to return to the stock eye.

For a personal test, keep a copy of the last working installed theme. Do not change Jibo firmware, 5x1 native packages, microphone, TLS trust, OpenClaw, or NOVA adapter configuration.

## Included assets

| Asset | Behavior |
| --- | --- |
| `face/eye.png` | Original open/idle almond-shaped AI eye |
| `face/eyeListening.png` | **Distinct, blue-lit inner iris** during listening |
| `face/eyeClosed.png` | Closed/blinking eye |
| `face/face.json` | Black background and 135% eye size |
| `manifest.json` | Theme name, version, API compatibility |
| `banner.png` | Store preview artwork |

## Build, validation, and limitations

Requires Python 3.9+ with Pillow 11.3.0. From the repository root:

```bash
python -m pip install Pillow==11.3.0
python scripts/build_release.py
python scripts/validate_release.py
python scripts/validate_all.py
```

`scripts/generate_listening.py` deterministically produces the blue native listening artwork directly from `face/eye.png`. It ships **no executable code** in the theme ZIP. Validation checks PNG decode, image size, metadata, matching transparent silhouette, a visibly distinct iris, package integrity, and exact generated content. Automated checks **do not prove the appearance or state transitions on physical Jibo**.

**Hardware sign-off:** follow [docs/HARDWARE_TEST.md](docs/HARDWARE_TEST.md) on the exact ZIP. Confirm eye centering, no clipped outer housing or square border, native gaze/blink/listening, Talk to NOVA listening-to-speaking transitions, other skills, rollback, and restart behavior. Record tester, date, build and checksum. Until then, treat this as a release candidate.

## BEacon Store distribution

This theme belongs to the [Jibo NOVA Community](https://github.com/Matt87c/jibo-nova-community) multi-theme repository. Its ZIP supports manual BEacon upload. A community monorepo release does not automatically create a separate Store discovery entry; an independently released theme repository or maintainer-approved storefront path may be needed for Store install/update. See [Store notes](../../docs/RELEASE_READINESS.md).

**Developer:** Matt87c. Community visual theme only; not endorsed by the official Jibo or 5x1 maintainers.
