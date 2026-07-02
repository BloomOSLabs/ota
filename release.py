#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

print("Running BloomOS release script v1.0")


def ask(prompt, default=None):
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    return input(f"{prompt}: ").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Upload BloomOS OTA packages to SourceForge."
    )

    parser.add_argument(
        "--device",
        help="Device codename (e.g. OP4C7D)"
    )

    parser.add_argument(
        "--version",
        help="BloomOS version (e.g. 1.0)"
    )

    parser.add_argument(
        "--zip",
        dest="zip_path",
        help="Path to OTA ZIP"
    )

    parser.add_argument(
        "--project",
        default="bloomoslabs",
        help="SourceForge project name"
    )

    parser.add_argument(
        "--user",
        default="bloomoslabs",
        help="SourceForge username"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the rsync command without uploading"
    )

    parser.add_argument(
        "--generate-json",
        action="store_true",
        help="Run generate_ota_json.py after a successful upload"
    )
    
    parser.add_argument(
        "--build-prop",
        help="Path to build.prop for OTA metadata generation"
    )

    args = parser.parse_args()
    
    if args.dry_run:
        print("Dry run enabled.")
        print()
        missing = []
    
        if not args.device:
            missing.append("--device")
    
        if not args.version:
            missing.append("--version")
    
        if not args.zip_path:
            missing.append("--zip")
    
        if args.generate_json and not args.build_prop:
            missing.append("--build-prop")
    
        if missing:
            parser.error(
                "--dry-run requires the following arguments: "
                + ", ".join(missing)
            )
    
        device = args.device
        version = args.version
        zip_path = Path(args.zip_path).expanduser().resolve()
    
    else:
        device = args.device or ask("Device")
        version = args.version or ask("Version")
        zip_input = args.zip_path or ask("Path to OTA ZIP")
        zip_path = Path(zip_input).expanduser().resolve()

    if not zip_path.exists():
        print(f"\nError: File not found:\n{zip_path}")
        sys.exit(1)

    if shutil.which("rsync") is None:
        print("Error: rsync is not installed or not found in PATH.")
        sys.exit(1)

    remote = (
        f"/home/frs/project/"
        f"{args.project}/"
        f"{device}/"
        f"{version}"
    )

    download_url = (
        f"https://downloads.sourceforge.net/project/"
        f"{args.project}/"
        f"{device}/"
        f"{version}/"
        f"{zip_path.name}"
    )

    
    command = [
        "rsync",
        "-avP",
        str(zip_path),
        f"{args.user}@frs.sourceforge.net:{remote}/"
    ]

    print()
    print("Upload Summary")
    print("==============")
    print(f"Device       : {device}")
    print(f"Version      : {version}")
    print(f"Project      : {args.project}")
    print(f"User         : {args.user}")
    print(f"File         : {zip_path.name}")
    print(f"Remote Path  : {remote}")
    print()

    if not args.dry_run:
        try:
            subprocess.run(command, check=True)
            print()
            print("Upload complete.")
            print()
        except subprocess.CalledProcessError:
            print("\nUpload failed.")
            sys.exit(1)


    print("Upload command:")
    print(" ".join(command))
    print()
    print("Download URL:")
    print(download_url)

    if args.dry_run:    
        generate = args.generate_json
    
        if not generate:
            response = input(
                "\nGenerate OTA metadata now? [y/N]: "
            ).strip().lower()
            generate = response == "y"
    
        if generate:
            script = Path(__file__).parent / "generate_ota_json.py"
    
            command = [
                sys.executable,
                str(script),
                "--zip",
                str(zip_path),
                "--build-prop",
                args.build_prop,
                "--project",
                args.project,
                "--dry-run",
            ]
    
            print()
            subprocess.run(command, check=True)
    
        return


if __name__ == "__main__":
    main()
