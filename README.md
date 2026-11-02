# Jibo NOVA Community

Open-source eye themes and future community skills for Jibo robots running **5x1/OpenJibo** and **BEacon**. Created and maintained by [Matt87c](https://github.com/Matt87c).

> **Community releases only.** This public project does not contain the developer's personal Jibo robot configuration, NOVA/OpenClaw gateway, adapter authentication, secrets, private network details, or robot data. It is deliberately separate from the private `jibo-nova` project.

## Download the themes

| Theme | Version | Direct installable ZIP |
| --- | --- | --- |
| NOVA Core Holographic (large cyan, almond eye) | 1.0.2 | [ZIP](themes/jibo-nova-core-holographic-theme/dist/jibo-nova-core-holographic-theme.zip) |
| Quantum Iris Cybernetic (purple almond eye) | 1.0.1 | [ZIP](themes/jibo-quantum-iris-cybernetic-theme/dist/jibo-quantum-iris-cybernetic-theme.zip) |
| NOVA Halo | 1.0.3 | [ZIP](themes/jibo-nova-halo-theme/dist/jibo-nova-halo-theme.zip) |
| NOVA Core (original enlarged design) | 1.0.1 | [ZIP](themes/jibo-nova-core-theme/dist/jibo-nova-core-theme.zip) |
| Quantum Iris (original enlarged design) | 1.0.1 | [ZIP](themes/jibo-quantum-iris-theme/dist/jibo-quantum-iris-theme.zip) |

**Manual BEacon installation:** In BEacon go to **Store → Themes → ⋯ → Upload Theme ZIP**. Select a downloaded theme ZIP, then select the installed theme and **Apply**. The previous stock appearance can be restored with **None**. Do not extract the ZIP before uploading.

Each theme includes a manifest, source artwork, a banner, build instructions, release validation, and developer attribution. The packages are **themes, not executable skills**.

## Community skills

The [`skills/`](skills/) directory is reserved for reusable, independently reviewed skills. **Talk to NOVA is not published here.** It currently depends on a private home installation and needs a separate source, security, architecture, and licensing review before any public version can be offered. No example skill ZIP is being misrepresented as an installable public product.

## Project layout

```text
themes/
  jibo-nova-core-holographic-theme/
  jibo-quantum-iris-cybernetic-theme/
  jibo-nova-halo-theme/
  jibo-nova-core-theme/
  jibo-quantum-iris-theme/
skills/
scripts/
.github/workflows/
```

## Rebuilding and testing

Run `python -m pip install Pillow==11.3.0` and `python scripts/validate_all.py`. This builds and verifies the five included ZIPs using the same files the user downloads. GitHub Actions runs the same checks on pushes and pull requests.

## Compatibility and Store notes

Themes target the BEam/BEacon theme interface (`jibo-tbd` 3.1.6+). Native Jibo eye movement is retained. These packages passed static checks, but physical robot QA for these exact builds is still recommended before claiming verified support.

The BEacon Store's native GitHub release discovery is typically designed around **one theme or skill per repository**. This collection is a single public home for code and manual ZIP downloads. To offer independent **Store install/update** entries later, maintain separate public release repositories or another storefront structure accepted by the maintainers. A public GitHub release for this monorepo alone is not a guarantee of in-Store discovery.

## Security and contributions

See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before sending contributions. Never upload local logs, device backups, certificates, credentials, network configuration, or `.env` files. No private Git history is copied into this repository.

**License:** MIT for included community theme materials; third-party materials retain their own licenses, where applicable. Verify rights before adding future third-party assets.