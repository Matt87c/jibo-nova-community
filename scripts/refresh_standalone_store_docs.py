#!/usr/bin/env python3
"""Review historical source and prepare non-destructive documentation PRs for seven Jibo themes."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile
from io import BytesIO

OWNER="Matt87c"
BRANCH="docs/stable-community-release-readiness"
ITEMS=[
("jibo-nova-core-holographic-theme","NOVA Core Holographic","1.0.2","Large cyan holographic iris and radial HUD detail, 135% eye size"),
("jibo-quantum-iris-cybernetic-theme","Quantum Iris Cybernetic","1.0.1","Purple-violet cybernetic iris, glowing geometric rings and custom eye states"),
("jibo-nova-halo-theme","NOVA Halo","1.0.3","Friendly cyan-and-white futuristic eye with matching blink and listening assets"),
("jibo-nova-core-theme","NOVA Core","1.0.1","Original cyan-blue NOVA Core eye with custom blinking and listening textures"),
("jibo-quantum-iris-theme","Quantum Iris","1.0.1","Purple geometric eye theme with dedicated open, closed and listening textures"),
("jibo-nova-sentient-eye-theme","NOVA Sentient Eye","1.0.1","Original custom cyan Sentient Eye design with matching repaired blink"),
("jibo-nova-sentient-orb-theme","NOVA Sentient Orb","1.0.1","Original custom cyan Sentient Orb design with matching repaired blink")
]
PATTERNS={
    "GitHub credential":rb"(?:gh[pousr]_[A-Za-z0-9_]{16,}|github_pat_[A-Za-z0-9_]{16,})",
    "API credential":rb"(?:sk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{18,}|(?:AKIA|ASIA)[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{15,})",
    "PEM private key":rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Private network IP":rb"(?<![0-9])(?:192\.168\.\d{1,3}\.\d{1,3}|10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![0-9])",
    "Inline password/token":rb"(?i)(?:password|auth_token|api_key|secret_key|access_token)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"
}
def run(*argv,cwd=None):
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace")
    if p.returncode: raise RuntimeError("{}: {}".format(argv[0],(p.stderr or p.stdout)[-800:]))
    return p.stdout.strip()
def scan(label,data):
    return [(label,k) for k,pattern in PATTERNS.items() if re.search(pattern,data)]
def audit_history(folder):
    entries=run("git","rev-list","--objects","--all",cwd=folder).splitlines()
    findings=[]; count=0; seen=set()
    for line in entries:
        oid,sep,path=line.partition(" ")
        if not sep or oid in seen: continue
        seen.add(oid)
        if run("git","cat-file","-t",oid,cwd=folder)!="blob":continue
        size=int(run("git","cat-file","-s",oid,cwd=folder))
        if size>16000000:
            findings.append((path,"Oversized unscanned blob"));continue
        blob=subprocess.run(["git","cat-file","blob",oid],cwd=folder,check=True,stdout=subprocess.PIPE).stdout
        count+=1
        if path.lower().endswith(".zip"):
            try:
                with ZipFile(BytesIO(blob)) as z:
                    for member in z.infolist():
                        if member.file_size>16000000:
                            findings.append((path+":"+member.filename,"Oversized ZIP entry"));continue
                        if member.filename.lower().endswith((".md",".json",".txt",".py",".yml",".yaml",".sh",".js",".env")):
                            findings.extend(scan(path+":"+member.filename,z.read(member)))
            except Exception: findings.append((path,"ZIP could not be scanned"))
        elif not path.lower().endswith((".png",".jpg",".jpeg",".webp",".gif")):
            findings.extend(scan(path,blob))
    return count,findings

def read(folder,path):
    return (folder/path).read_text(encoding="utf-8-sig")
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    if args.apply and run("gh","api","user","--jq",".login").lower()!=OWNER.lower():
        raise RuntimeError("Authenticate GitHub CLI as Matt87c first")
    with tempfile.TemporaryDirectory(prefix="jibo-store-review-") as tmp:
        for slug,title,version,description in ITEMS:
            repo=OWNER+"/"+slug;folder=Path(tmp)/slug
            run("gh","repo","clone",repo,str(folder))
            manifest=json.loads(read(folder,"manifest.json"))
            if (manifest.get("version"),manifest.get("name"),manifest.get("type"))!=(version,title,"theme"):
                raise RuntimeError("Manifest unexpectedly changed in "+repo)
            release=json.loads(run("gh","api","repos/"+repo+"/releases/latest"))
            if release["tag_name"]!="v"+version or release["prerelease"] or slug+".zip" not in [a["name"] for a in release["assets"]]:
                raise RuntimeError("Stable release and asset verification failed: "+repo)
            count,findings=audit_history(folder)
            print("AUDITED:",repo,"historical blobs:",count,"findings:",len(findings),flush=True)
            for path,kind in findings: print("  REVIEW:",kind,"in",path,flush=True)
            if findings:raise RuntimeError("Historical scan identified potential issues; stopped")
            # Released assets, current theme art and manifest must remain untouched.
            protected=["manifest.json","face/face.json","face/eye.png","face/eyeClosed.png","face/eyeListening.png","dist/"+slug+".zip"]
            saved={p:(folder/p).read_bytes() for p in protected}
            original=read(folder,"README.md")
            updated=original.replace(
                "Version: 1.0.0. This is a candidate pending Jibo hardware acceptance.",
                "Version: 1.0.1. Stable community release; maintainer reports Jibo testing.")
            updated=updated.replace(
                "Hardware testing of this exact public release package has **not yet been confirmed**. Check eye clipping, blink and listening states on the robot before requesting a public Store catalog listing.",
                "Maintainer reports testing on a physical Jibo; detailed individual checklist results have not been independently verified.")
            updated=updated.replace(
                "no physical-device regression test was done here.",
                "maintainer reports testing on physical Jibo; the full acceptance checklist has not been independently verified.")
            updated=updated.rstrip()+"\n\n## Stable community release\n\n"
            updated+="Latest stable release: https://github.com/"+repo+"/releases/latest\n\n"
            updated+="Version: "+version+". The maintainer reports testing this theme on a physical Jibo. "
            updated+="Detailed test scenarios in docs/HARDWARE_TEST.md remain unverified unless recorded. "
            updated+="This is a community theme by Matt87c, not an official 5x1 or BEacon Store listing.\n"
            (folder/"README.md").write_text(updated,encoding="utf-8",newline="\n")
            store="# BEacon Store submission: "+title+"\n\n"
            store+="Developer: Matt87c\n\nStandalone repository: https://github.com/"+repo+"\n\n"
            store+="Current stable version: "+version+"\n\nMinimum jibo-tbd version: 3.1.6\n\n"
            store+="Release asset: "+slug+".zip\n\n"
            store+="## Download and installation\n\nDownload the release ZIP (not the source ZIP) at "
            store+="https://github.com/"+repo+"/releases/latest . In BEacon select Store > Themes > "
            store+="three-dot menu > Upload Theme ZIP, upload the ZIP, select the theme and Apply. "
            store+="Choose None to restore the original eye.\n\n"
            store+="## Store review status\n\nThis is a public standalone repository with one theme, "
            store+="a root manifest.json, and a stable GitHub release. The maintainer reports testing "
            store+="on Jibo, but individual checklist entries are not independently verified. "
            store+="A stable GitHub release does not establish acceptance into the BEacon Store; "
            store+="listing and indexing are controlled by the maintainers.\n\n"
            store+="The theme contains visual assets only; no credentials, private runtime configuration "
            store+="or native robot skill code. This documentation update does not modify the existing "
            store+="release ZIP or version tag.\n\n"
            store+="Format: https://github.com/Jibo-Revival-Group/BEam/blob/master/docs/themes.md\n"
            (folder/"docs/STORE.md").write_text(store,encoding="utf-8",newline="\n")
            test=read(folder,"docs/HARDWARE_TEST.md")
            test=re.sub(r"^# Hardware acceptance record: .+$",
                        "# Hardware acceptance record: "+title+" v"+version,test,count=1,flags=re.M)
            test=test.replace("Target: real Jibo",
                "## Reported test status\n\n"
                "The maintainer reports Jibo hardware testing and has published a stable community release. "
                "Individual checks below have not been attested or independently verified; "
                "record PASS only after verifying each scenario.\n\nTarget: real Jibo",1)
            (folder/"docs/HARDWARE_TEST.md").write_text(test,encoding="utf-8",newline="\n")
            if any((folder/p).read_bytes()!=blob for p,blob in saved.items()):
                raise RuntimeError("Protected art/manifest/release changed in "+repo)
            run("git","diff","--check",cwd=folder)
            print(run("git","diff","--stat",cwd=folder),flush=True)
            if not args.apply:
                print("DRY RUN: no remote edits",flush=True);continue
            branches=json.loads(run("gh","api","repos/"+repo+"/pulls?state=open"))
            if any(p["head"]["ref"]==BRANCH for p in branches):
                raise RuntimeError("Existing documentation PR; resolve before retry: "+repo)
            run("git","checkout","-b",BRANCH,cwd=folder)
            run("git","add","README.md","docs/STORE.md","docs/HARDWARE_TEST.md",cwd=folder)
            run("git","commit","-m","Refresh stable release descriptions and standalone Store notes",cwd=folder)
            run("git","push","-u","origin",BRANCH,cwd=folder)
            url=run("gh","pr","create","--repo",repo,"--head",BRANCH,"--base","main",
                    "--title","Update stable theme documentation for BEacon Store review",
                    "--body","Documentation-only changes. Updated README and standalone Store instructions; corrected hardware-test checklist version. Historical tracked Git blobs checked for common credential/private-IP signatures. Original art, manifest, release ZIP and tags unchanged.")
            print("PR CREATED:",url,flush=True)
            # Existing About descriptions were accurate; improve them with a specific description.
            run("gh","repo","edit",repo,"--description",description+". By Matt87c.")
            print("ABOUT UPDATED:",repo,flush=True)
    print("Done. No released ZIPs or Jibo settings changed.",flush=True)
if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,OSError) as e:raise SystemExit("STOP: "+str(e))
