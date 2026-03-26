import csv
import os
import yaml
import re

# --- CONFIG ---
CSV_PATH = r"data\subgens.csv"
MD_ROOT = "monograph_md"
DEBUG = True

# --- Load CSV into lookup keyed by scientific name ---
lookup = {}
with open(CSV_PATH, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    if DEBUG:
        print("CSV fieldnames:", reader.fieldnames)

    for row in reader:
        sci = row["scianem"].strip()
        lookup[sci] = {
            "wfo_id": row.get("taxonID") or None,
            "scientificnameauthorship": row.get("auth") or None
        }

if DEBUG:
    print(f"Loaded {len(lookup)} classification rows from CSV")

# Regex to capture YAML front matter safely
yaml_re = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

# --- Walk markdown files ---
for root, dirs, files in os.walk(MD_ROOT):
    for fname in files:
        if not fname.endswith(".md"):
            continue

        path = os.path.join(root, fname)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        match = yaml_re.match(text)
        if not match:
            print(f"[ERROR] {path}: YAML front matter not detected")
            continue

        yaml_block, body = match.groups()
        data = yaml.safe_load(yaml_block) or {}

        # Extract scientificname from YAML
        yaml_sciname = data.get("scientificname")

        if not yaml_sciname:
            if DEBUG:
                print(f"[ERROR] {fname}: YAML has no scientificname field")
            continue

        if yaml_sciname not in lookup:
            if DEBUG:
                print(f"[SKIP] {yaml_sciname} (from {fname}) not found in CSV")
            continue

        row = lookup[yaml_sciname]
        new_auth = row.get("scientificnameauthorship")

        # --- Only update authorship if YAML field is empty ---
        old_auth = data.get("scientificnameauthorship")
        empty_values = (None, "", "None", "null")

        if old_auth not in empty_values:
            if DEBUG:
                print(f"[NO CHANGE] {yaml_sciname} ({fname}) — authorship already set")
            continue

        if new_auth in empty_values:
            if DEBUG:
                print(f"[SKIP] {yaml_sciname} ({fname}) — CSV has no authorship")
            continue

        # Update YAML authorship
        data["scientificnameauthorship"] = new_auth

        # Update title field
        new_title = f"{yaml_sciname} {new_auth}"
        data["title"] = new_title

        # Rebuild YAML
        new_yaml = yaml.dump(data, sort_keys=False).strip()
        new_text = f"---\n{new_yaml}\n---\n{body}"

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

        print(f"[UPDATED] {yaml_sciname} ({fname})")
        if DEBUG:
            print(f"   - scientificnameauthorship: {old_auth} → {new_auth}")
            print(f"   - title updated to: {new_title}")