import csv
import os
import yaml
import re

# --- CONFIG ---
CSV_PATH = r"data\classification.csv"
MD_ROOT = "monograph_md"
DEBUG = True

# --- Load CSV into lookup keyed by taxonID (WFO ID) ---
lookup = {}
with open(CSV_PATH, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    if DEBUG:
        print("CSV fieldnames:", reader.fieldnames)

    for row in reader:
        wfo = row["taxonID"].strip()
        lookup[wfo] = {
            "ipni_id": row.get("scientificNameID") or None
        }

if DEBUG:
    print(f"Loaded {len(lookup)} rows from CSV")

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

        # Extract wfo_ID from YAML
        yaml_wfo = data.get("wfo_id")

        if not yaml_wfo:
            if DEBUG:
                print(f"[ERROR] {fname}: YAML has no wfo_ID field")
            continue

        if yaml_wfo not in lookup:
            if DEBUG:
                print(f"[SKIP] {yaml_wfo} (from {fname}) not found in CSV")
            continue

        row = lookup[yaml_wfo]
        new_ipni = row["ipni_id"]

        # --- Only update if YAML ipni_id is empty ---
        old_ipni = data.get("ipni_id")
        empty_values = (None, "", "None", "null")

        if old_ipni not in empty_values:
            if DEBUG:
                print(f"[NO CHANGE] {yaml_wfo} ({fname}) — ipni_id already set")
            continue

        if new_ipni in empty_values:
            if DEBUG:
                print(f"[SKIP] {yaml_wfo} ({fname}) — CSV has no scientificNameID")
            continue

        # Update YAML
        data["ipni_id"] = new_ipni

        # Rebuild YAML
        new_yaml = yaml.dump(data, sort_keys=False).strip()
        new_text = f"---\n{new_yaml}\n---\n{body}"

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

        print(f"[UPDATED] {yaml_wfo} ({fname})")
        if DEBUG:
            print(f"   - ipni_id: {old_ipni} → {new_ipni}")