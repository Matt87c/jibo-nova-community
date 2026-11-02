# Publishing themes

Keep `Matt87c/jibo-nova` **private**; publish only audited standalone assets to this community repository.

## Package format

A BEacon theme ZIP contains `manifest.json`, `face/face.json`, PNG eye assets, and optional banner and README. Keep manifest name stable across versions so BEacon updates an existing installation.

For local installation, use **BEacon → Store → Themes → ⋯ → Upload Theme ZIP**, select the theme, and **Apply**.

## Public release checklist

1. Verify rights and attribution for every artwork and dependency.
2. Run the archive and image validation checks.
3. Review the actual Git diff and scan for secrets and identifiers.
4. Test install, blink/listening states, rollback, and compatibility on real Jibo hardware.
5. Publish a release with the installable theme ZIP.
6. Coordinate Store listings with the BEacon maintainer, including any requirements for individual theme repositories.

Do not claim hardware testing or official Store approval without confirmation.
