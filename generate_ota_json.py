#!/usr/bin/env python3
import argparse, hashlib, json, os, re, sys
from pathlib import Path

print("Running BloomOS OTA metadata generator v1.0")

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def read_prop(path,key):
    with open(path,"r",encoding="utf-8",errors="ignore") as f:
        for line in f:
            if line.startswith(key+"="):
                return line.strip().split("=",1)[1]
    return None

def ask(prompt, default=None):
    if default:
        v=input(f"{prompt} [{default}]: ").strip()
        return v or default
    return input(f"{prompt}: ").strip()

ap=argparse.ArgumentParser(description="Generate BloomOS OTA metadata JSON.")
ap.add_argument("--zip",dest="zip_path",help="Path to OTA zip")
ap.add_argument("--build-prop",help="Path to build.prop")
ap.add_argument("--output",help="Output JSON path")
ap.add_argument("--project",default="bloomoslabs",help="SourceForge project")
ap.add_argument("--repo-url",help="Override download URL template. Supports {project},{device},{version},{filename}")
ap.add_argument("--release-type",help="Override release type")
ap.add_argument("--force",action="store_true",help="Overwrite output")
ap.add_argument("--dry-run",action="store_true",help="Print JSON instead of writing")
args=ap.parse_args()

zip_path=args.zip_path or ask("Path to OTA ZIP")
zp=Path(zip_path)
if not zp.is_file():
    sys.exit(f"ZIP not found: {zp}")

bp=args.build_prop or ask("Path to build.prop")
bp=Path(bp)
if not bp.is_file():
    sys.exit(f"build.prop not found: {bp}")

m=re.match(r'^(?P<rom>.+)-(?P<version>\d+(?:\.\d+)+)-(?P<rtype>[A-Za-z0-9_]+)-(?P<device>[A-Za-z0-9_]+)-(?P<date>\d{8})\.zip$',zp.name)
if not m:
    sys.exit("Filename does not match expected format: BloomOS-<version>-<type>-<device>-<YYYYMMDD>.zip")

version=read_prop(bp,"ro.bloom.build.version") or read_prop(bp,"ro.lineage.build.version") or m.group("version")
release=args.release_type or os.environ.get("RELEASE_TYPE") or read_prop(bp,"ro.bloom.releasetype") or read_prop(bp,"ro.lineage.releasetype") or m.group("rtype")
timestamp=read_prop(bp,"ro.build.date.utc")
if timestamp is None:
    sys.exit("ro.build.date.utc not found in build.prop")

device=m.group("device")
filename=zp.name
size=zp.stat().st_size
digest=sha256(zp)

template=args.repo_url or "https://sourceforge.net/projects/{project}/files/{device}/{version}/{filename}/download"
url=template.format(project=args.project,device=device,version=version,filename=filename)

data={
    "response":[
        {
            "datetime":int(timestamp),
            "filename":filename,
            "id":digest,
            "romtype":release,
            "size":size,
            "url":url,
            "version":version
        }
    ]
}

if args.dry_run:
    print(json.dumps(data,indent=2))
    sys.exit(0)

out=args.output or f"devices/v1/{device}.json"
outp=Path(out)
outp.parent.mkdir(parents=True,exist_ok=True)

if outp.exists() and not args.force:
    ans=input(f"{outp} exists. Overwrite? [y/N]: ").strip().lower()
    if ans!="y":
        sys.exit("Cancelled.")

with open(outp,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2)
    f.write("\n")

print(f"Generated: {outp}")
print(f"Device      : {device}")
print(f"Version     : {version}")
print(f"Release Type: {release}")
print(f"SHA256      : {digest}")
print(f"Size        : {size} bytes")
