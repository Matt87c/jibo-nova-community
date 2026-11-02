# Quantum Iris Cybernetic

A purple-violet cybernetic eye with geometric rings, a blue central iris, and a soft glowing almond-shaped outline.

- **Version:** 1.0.1 (updates 1.0.0)
- **Author:** [Matt87c](https://github.com/Matt87c)
- **Platform:** Jibo 5x1/OpenJibo with BEacon theme support
- **Minimum jibo-tbd version:** 3.1.6
- **Eye scale:** 122% of stock

## What's new in v1.0.1

- Replaced the screenshot crop with standalone transparent black-blended almond eye artwork, eliminating square edges.
- Added matching **face/eyeClosed.png** and tuned **face/eyeListening.png**.
- Eye size stays at 122%.

## Install or upgrade

Open **BEacon > Store > Themes > three-dot menu > Upload Theme ZIP** and select this ZIP file as-is.
The manifest name is unchanged, so BEacon can update the existing **Quantum Iris Cybernetic** theme.
After import, select the theme and click **Apply**. If your older theme remains active, re-apply the updated theme.
Select **None** in BEacon to restore the original Jibo eye, or switch to another installed theme.

## What the theme does (and doesn't)

This is a **visual-only** theme. It contains no executable code, network addresses, credentials, or personal setup information. It modifies only face appearance through the official declarative theme contract.

The native Jibo renderer still controls gaze, blink animation, listening behavior, eye geometry, and state changes. The images will deform dynamically on the robot; no physical-device regression test was done here.

| File | Purpose |
| --- | --- |
| `face/eye.png` | Idle/open appearance |
| `face/eyeListening.png` | Native listening appearance |
| `face/eyeClosed.png` | Native closed/blink texture |
| `face/face.json` | Black background and eye scale |
| `manifest.json` | Package identifier and version |

Theme format: https://github.com/Jibo-Revival-Group/BEam/blob/master/docs/themes.md
