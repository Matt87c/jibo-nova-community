# Public export security review

**Result: PASS (static scope only)**

- Source comes only from five independent theme package folders, using a strict file allowlist.
- No private repository, `.git` history, NOVA adapter, `Talk to NOVA` source, live robot settings, or private logs were copied.
- Five theme-only release ZIPs rebuilt and validated against their source bytes and BEacon package format.
- Plain-text files and release archive text scanned for common private IP addresses, credentials, access tokens, private key headers, user home paths and email addresses.
- All included PNGs decoded and checked for embedded metadata.
- No findings in the static checks.

**Caveats:** This is not a complete forensic or supply-chain audit; it does not establish rights to third-party materials or prove on-device behavior. Review the public folder before publishing and perform physical Jibo QA before stable releases. Do not add private skills without a new audit.