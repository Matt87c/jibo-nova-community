#!/usr/bin/env python3
"""Keep original BEacon eye designs; repair shared blink assets in two Sentient themes.

Default: read-only repo audit plus offline candidate validation.
--apply: push two correction branches and create reviewable pull requests.
No new eye designs, no robot modifications, no stable releases.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image

OWNER = "Matt87c"
TARGETS = {
    "jibo-nova-sentient-eye-theme": "24cf529a3bdc7d7545844830516cced8434efa5402b046beae2e008bbdaae588",
    "jibo-nova-sentient-orb-theme": "12ade8239aa1dd744e81141d33fb93c2dee05eb15ad4d7a77010520ac29fda5c",
}
AUDIT_ONLY = ("jibo-quantum-iris-theme", "jibo-nova-halo-theme")
GENERIC_CLOSED_SHA = "0f8b7d786e1e202983840225c0e5e534095a6b49b1ba05a3f70462599e8d7587"
BRANCH = "fix/sentient-theme-consistent-blink-v1.0.1"


def run(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Command failed: {}\n{}".format(" ".join(args),
                                                            (result.stderr or result.stdout)[-1000:]))
    return result.stdout.strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source(folder, name):
    meta = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if meta.get("type") != "theme":
        raise ValueError("Unexpected theme type: " + name)
    for rel in ("face/eye.png", "face/eyeListening.png", "face/eyeClosed.png",
                "face/face.json", "scripts/build_release.py", "scripts/validate_release.py"):
        if not (folder / rel).is_file():
            raise ValueError("Required theme file missing: " + rel)
    main = sha(folder / "face/eye.png")
    listening = sha(folder / "face/eyeListening.png")
    blink = sha(folder / "face/eyeClosed.png")
    print("{} v{} listening=same-as-idle:{} generic-shared-blink:{}".format(
        name, meta["version"], main == listening, blink == GENERIC_CLOSED_SHA), flush=True)
    return meta, main, blink


def update_sentient(folder, name, expected_eye_sha):
    meta, main, blink = verify_source(folder, name)
    if meta["version"] != "1.0.0" or main != expected_eye_sha or blink != GENERIC_CLOSED_SHA:
        raise ValueError("Original version/artwork changed; refuse to overwrite: " + name)

    # Preserve both original custom eye textures and configuration EXACTLY.
    preserved = {rel: sha(folder / rel) for rel in (
        "face/eye.png", "face/eyeListening.png", "face/face.json")}
    with Image.open(folder / "face/eye.png") as image:
        src = image.convert("RGBA")
    if src.width != src.height or src.width > 4096:
        raise ValueError("Unexpected eye texture dimensions")
    w, h = src.size
    compressed = src.resize((w, round(h * 0.075)), Image.Resampling.LANCZOS)
    closed = Image.new("RGBA", src.size, (0, 0, 0, 0))
    closed.alpha_composite(compressed, (0, (h - compressed.height) // 2))
    closed.save(folder / "face/eyeClosed.png", format="PNG", optimize=True)

    meta["version"] = "1.0.1"
    (folder / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    readme = folder / "README.md"
    old = readme.read_text(encoding="utf-8")
    if "Version: 1.0.0." not in old:
        raise ValueError("README version anchor changed")
    readme.write_text(old.replace("Version: 1.0.0.", "Version: 1.0.1.")
                        .replace("A stock-inspired futuristic cyan AI eye",
                                 "A custom futuristic cyan AI eye"), encoding="utf-8")
    history = folder / "CHANGELOG.md"
    previous = history.read_text(encoding="utf-8") if history.exists() else ""
    history.write_text("## 1.0.1 - Consistent custom blink\n"
                       "- Closed eye derives entirely from this theme's existing eye.png.\n"
                       "- Original idle/listening artwork and configuration are unchanged.\n"
                       "- Hardware testing pending.\n\n" + previous, encoding="utf-8")

    for rel, expected in preserved.items():
        if sha(folder / rel) != expected:
            raise RuntimeError("Protected existing asset changed unexpectedly: " + rel)
    run(sys.executable, "scripts/build_release.py", cwd=folder)
    run(sys.executable, "scripts/validate_release.py", cwd=folder)
    run("git", "diff", "--check", cwd=folder)
    print("PASS: original designs preserved; themed blink rebuilt and validated:", name, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create reviewable PRs")
    args = parser.parse_args()
    if args.apply:
        login = run("gh", "api", "user", "--jq", ".login")
        if login.lower() != OWNER.lower():
            raise RuntimeError("Expected GitHub account Matt87c, found " + login)

    with tempfile.TemporaryDirectory(prefix="jibo-existing-designs-") as temp:
        for name in (*TARGETS, *AUDIT_ONLY):
            folder = Path(temp) / name
            run("git", "clone", "--depth", "1",
                "https://github.com/{}/{}.git".format(OWNER, name), str(folder))
            if run("git", "status", "--porcelain", cwd=folder):
                raise RuntimeError("Unexpected dirty repository: " + name)
            if name in AUDIT_ONLY:
                verify_source(folder, name)
                continue   # KEEP Quantum Iris and NOVA Halo artwork unchanged.
            update_sentient(folder, name, TARGETS[name])
            if not args.apply:
                print("DRY RUN, no remote change:", name, flush=True)
                continue
            run("git", "checkout", "-b", BRANCH, cwd=folder)
            run("git", "add", "face/eyeClosed.png", "manifest.json", "README.md",
                "CHANGELOG.md", cwd=folder)
            run("git", "add", "-f", "dist/{}.zip".format(name), cwd=folder)
            run("git", "commit", "-m",
                "Match closed-eye state to existing Sentient artwork (v1.0.1)", cwd=folder)
            run("git", "push", "-u", "origin", BRANCH, cwd=folder)
            url = run("gh", "pr", "create", "--repo", "{}/{}".format(OWNER, name),
                      "--base", "main", "--head", BRANCH,
                      "--title", "Preserve custom eye design in blink state (v1.0.1)",
                      "--body", "Uses the EXISTING idle eye texture to create a matching closed-eye state. "
                      "Original idle and listening assets plus face configuration remain byte-for-byte unchanged. "
                      "Version bumped and package statically validated. "
                      "No new design or stock eye textures. Physical Jibo QA pending.")
            print("PR CREATED:", url, flush=True)
    print("Done. No live Jibo or NOVA changes.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit("STOP: " + str(error))
