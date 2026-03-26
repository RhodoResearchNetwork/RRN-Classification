import csv
import os
import yaml
import re

# --- CONFIG ---
CSV_PATH = r"data\subgens.csv"
MD_ROOT = "monograph_md"
DEBUG = True   # Turn debug on/off

# --- Load CSV into a lookup dict keyed by taxonID ---
lookup = {}
with open(CSV_PATH, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    if DEBUG:
        print("CSV fieldnames:", reader.fieldnames)

    for row in reader:
        taxonID = row["taxonID"].strip()
        lookup[taxonID] = {
            "subgenus": row.get("subgenus") or None,
            "section": row.get("section") or None,
            "subsection": row.get("subsection") or None
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

        # Extract taxonID from YAML
        yaml_taxonID = data.get("wfo_id")

        if not yaml_taxonID:
            if DEBUG:
                print(f"[ERROR] {fname}: YAML has no taxonID field")
            continue

        if yaml_taxonID not in lookup:
            if DEBUG:
                print(f"[SKIP] {yaml_taxonID} (from {fname}) not found in CSV")
            continue

        row = lookup[yaml_taxonID]

        # Track changes
        changed = False
        changes = {}

        for key, value in row.items():
            if value not in (None, "", "None"):
                old = data.get(key)
                if old != value:
                    data[key] = value
                    changed = True
                    changes[key] = (old, value)

        if not changed:
            if DEBUG:
                print(f"[NO CHANGE] {yaml_taxonID} ({fname})")
            continue

        # Rebuild YAML
        new_yaml = yaml.dump(data, sort_keys=False).strip()
        new_text = f"---\n{new_yaml}\n---\n{body}"

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

        print(f"[UPDATED] {yaml_taxonID} ({fname})")
        if DEBUG:
            for k, (old, new) in changes.items():
                print(f"   - {k}: {old} → {new}")