# release.py

Uploads BloomOS OTA packages to SourceForge.

The script automatically:

* Uploads OTA ZIPs using `rsync`.
* Creates missing directories on SourceForge.
* Generates the final public download URL.
* Supports both interactive and command-line usage.

---

## Requirements

* `rsync`
* SourceForge File Release System (FRS) access
* SSH key configured for SourceForge uploads

---

## Basic Usage

```bash
python3 release.py
```

The script will interactively ask for:

* Device codename
* BloomOS version
* OTA ZIP path

---

## Command Line Options

### Display help

```bash
python3 release.py --help
```

---

### Specify device

```bash
python3 release.py \
    --device OP4C7D
```

---

### Specify version

```bash
python3 release.py \
    --version 1.0
```

---

### Specify OTA ZIP

```bash
python3 release.py \
    --zip out/target/product/OP4C7D/BloomOS-1.0-EXPERIMENTAL-OP4C7D-20260618.zip
```

---

### Override SourceForge project

```bash
python3 release.py \
    --project bloomoslabs
```

---

### Override SourceForge username

```bash
python3 release.py \
    --user bloomoslabs
```

---

### Preview upload without uploading

```bash
python3 release.py --dry-run
```

This prints:

* SourceForge upload destination
* Upload command
* Final download URL

without uploading any files.

---

## Example

```bash
python3 release.py \
    --device OP4C7D \
    --version 1.0 \
    --zip out/target/product/OP4C7D/BloomOS-1.0-EXPERIMENTAL-OP4C7D-20260618.zip
```

---

## Typical Release Workflow

1. Build the BloomOS OTA ZIP.
2. Run `release.py` to upload the OTA ZIP to SourceForge.
3. Run `generate_ota_json.py` to generate the OTA metadata.
4. Commit the updated JSON to the OTA repository.
5. Push the OTA repository to GitHub.
6. GitHub Pages publishes the updated OTA metadata.
7. BloomOS Updater detects the new release automatically.

---

## Future Tools

This repository is intended to contain additional release automation tools, such as:

* `generate_changelog.py` — Generate OTA changelogs.
* Additional tooling as BloomOS release infrastructure evolves.
