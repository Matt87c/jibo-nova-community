#!/usr/bin/env python3
"""Finalize the seven already-open BEacon documentation PRs.

Default: inspect state without making changes.
--apply: correct stale Sentient 'candidate' wording, clarify immutable
release-ZIP documentation, wait for passing CI, then merge each PR.

Requires GitHub CLI signed in as Matt87c, plus Git. Does not edit
artwork, theme manifest, source ZIP, release tag, release asset or Jibo.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import time

OWNER = "Matt87c"
BRANCH = "docs/stable-community-release-readiness"
REPOS = (
    ("jibo-nova-core-holographic-theme", 1, "v1.0.2"),
    ("jibo-quantum-iris-cybernetic-theme", 1, "v1.0.1"),
    ("jibo-nova-halo-theme", 1, "v1.0.3"),
    ("jibo-nova-core-theme", 1, "v1.0.1"),
    ("jibo-quantum-iris-theme", 1, "v1.0.1"),
    ("jibo-nova-sentient-eye-theme", 2, "v1.0.1"),
    ("jibo-nova-sentient-orb-theme", 2, "v1.0.1"),
)
ALLOWED = {"README.md", "docs/STORE.md", "docs/HARDWARE_TEST.md"}
OLD_SENTIENT = (
    "Version: 1.0.1. This is a candidate pending Jibo hardware acceptance."
)
NEW_SENTIENT = (
    "Version: 1.0.1. Stable community release; the maintainer reports "
    "testing on a physical Jibo."
)
DOC_NOTE = (
    "\n\n**Documentation note:** This README describes the current repository. "
    "Existing versioned release ZIPs remain immutable and may include "
    "the README snapshot from their original publication.\n"
)


def run(*argv, cwd=None):
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError("{} failed: {}".format(
            " ".join(argv), (result.stderr or result.stdout)[-1000:]))
    return result.stdout.strip()


def api(endpoint):
    return json.loads(run("gh", "api", endpoint))


def pr_info(repo, number):
    return api("repos/{}/pulls/{}".format(repo, number))


def release_signature(repo, tag):
    release = api("repos/{}/releases/tags/{}".format(repo, tag))
    expected_asset = repo.split("/")[-1] + ".zip"
    match = [asset for asset in release.get("assets", [])
             if asset.get("name") == expected_asset]
    if release.get("draft") or release.get("prerelease") or not match:
        raise RuntimeError("Missing public stable ZIP release: {} {}".format(repo, tag))
    asset = match[0]
    return (release["id"], release["tag_name"], asset["id"],
            asset["size"], asset.get("digest"))


def changed_files(repo, number):
    items = api("repos/{}/pulls/{}/files?per_page=100".format(repo, number))
    paths = {item["filename"] for item in items}
    if len(items) != 3 or paths != ALLOWED or any(
            item.get("status") != "modified" for item in items):
        raise RuntimeError("Unexpected changed files: {} #{}: {}".format(
            repo, number, sorted(paths)))
    return paths


def amend_review_branch(repo, sentient):
    with tempfile.TemporaryDirectory(prefix="jibo-doc-finalize-") as temporary:
        folder = Path(temporary) / "repo"
        run("gh", "repo", "clone", repo, str(folder))
        run("git", "fetch", "origin", BRANCH, cwd=folder)
        run("git", "checkout", "-b", BRANCH, "origin/" + BRANCH, cwd=folder)
        readme = folder / "README.md"
        content = readme.read_text(encoding="utf-8-sig")
        revised = content
        if sentient:
            if OLD_SENTIENT in revised:
                revised = revised.replace(OLD_SENTIENT, NEW_SENTIENT)
            elif NEW_SENTIENT not in revised:
                raise RuntimeError("Unexpected Sentient README version text: " + repo)
        if DOC_NOTE.strip() not in revised:
            revised = revised.rstrip() + DOC_NOTE
        if revised == content:
            sha = run("git", "rev-parse", "HEAD", cwd=folder)
            print("README already corrected: {} at {}".format(repo, sha[:12]), flush=True)
            return sha
        with readme.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(revised)
        run("git", "diff", "--check", cwd=folder)
        dirty = run("git", "diff", "--name-only", cwd=folder).splitlines()
        if dirty != ["README.md"]:
            raise RuntimeError("Unexpected local edits in {}: {}".format(repo, dirty))
        run("git", "add", "README.md", cwd=folder)
        run("git", "commit", "-m",
            "Clarify stable hardware status and immutable release ZIP", cwd=folder)
        run("git", "push", "origin", BRANCH, cwd=folder)
        sha = run("git", "rev-parse", "HEAD", cwd=folder)
        print("UPDATED REVIEW BRANCH: {} at {}".format(repo, sha[:12]), flush=True)
        return sha


def wait_for_pr_head(repo, number, expected_sha):
    """Wait for GitHub's PR endpoint to see the pushed head, not a stale earlier head."""
    for attempt in range(24):
        pr = pr_info(repo, number)
        if pr.get("state") != "open":
            raise RuntimeError("PR unexpectedly closed: {}".format(repo))
        current = pr["head"]["sha"]
        if current == expected_sha:
            return pr
        if attempt < 23:
            print("Waiting for PR head to catch up: {} current={} expected={}".format(
                repo, current[:12], expected_sha[:12]), flush=True)
            time.sleep(5)
    raise RuntimeError("PR head did not advance; leaving PR open: {}".format(repo))


def wait_for_success(repo, sha):
    endpoint = "repos/{}/actions/runs?head_sha={}&per_page=40".format(repo, sha)
    for attempt in range(24):
        runs = api(endpoint).get("workflow_runs", [])
        matches = [r for r in runs
                   if r.get("head_sha") == sha
                   and r.get("name") == "Validate BEacon theme"]
        if any(r.get("status") == "completed" and
               r.get("conclusion") == "success" for r in matches):
            print("CI PASSED:", repo, sha[:12], flush=True)
            return
        if any(r.get("status") == "completed" and
               r.get("conclusion") not in (None, "success")
               for r in matches):
            raise RuntimeError("Failing CI for {} {}".format(repo, sha))
        if attempt < 23:
            time.sleep(10)
    raise RuntimeError("CI not complete; leave PR open and retry: {}".format(repo))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Fix review branches and merge all seven checked PRs")
    args = parser.parse_args()
    if args.apply and run("gh", "api", "user", "--jq", ".login").lower() != OWNER.lower():
        raise RuntimeError("Expected GitHub CLI account Matt87c")
    for name, number, tag in REPOS:
        repo = OWNER + "/" + name
        before = release_signature(repo, tag)
        pr = pr_info(repo, number)
        if pr.get("merged"):
            print("ALREADY MERGED: {} #{}".format(repo, number), flush=True)
            continue
        if pr.get("state") != "open" or pr["base"]["ref"] != "main" or (
                pr["head"]["ref"] != BRANCH):
            raise RuntimeError("Unexpected PR state/base/head: {} #{}".format(repo, number))
        changed_files(repo, number)
        if not args.apply:
            print("READY: {} PR #{} head={} tag={}".format(
                repo, number, pr["head"]["sha"][:12], tag), flush=True)
            continue
        sha = amend_review_branch(
            repo, name.endswith(("sentient-eye-theme", "sentient-orb-theme")))
        pr = wait_for_pr_head(repo, number, sha)
        changed_files(repo, number)
        wait_for_success(repo, sha)
        if wait_for_pr_head(repo, number, sha)["head"]["sha"] != sha:
            raise RuntimeError("PR head changed after CI: {}".format(repo))
        # Merge only a reviewed, successful, three-file documentation PR.
        print("MERGING: {} #{}".format(repo, number), flush=True)
        run("gh", "pr", "merge", str(number), "--repo", repo,
            "--squash", "--delete-branch")
        merged = pr_info(repo, number)
        if not merged.get("merged"):
            raise RuntimeError("Merge not confirmed: {}".format(repo))
        after = release_signature(repo, tag)
        if after != before:
            raise RuntimeError("Stable release asset was unexpectedly changed: {}".format(repo))
        print("MERGED / RELEASE UNCHANGED: {} PR #{}".format(repo, number), flush=True)
    print("Complete. Only documentation PRs were merged; current stable releases and artwork are unchanged.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        raise SystemExit("STOP: " + str(exc))
