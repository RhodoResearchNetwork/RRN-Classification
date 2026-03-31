import csv
import os
import yaml

# --- CONFIG ---
CSV_PATH = "data/AccetpedRhodo.csv"
MD_ROOT = "monograph_md/additions"   # folder containing your .md files

print("Loading CSV:", CSV_PATH)

# --- LOAD CSV INTO DICT BY taxonID ---
csv_by_id = {}
with open(CSV_PATH, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("CSV columns:", reader.fieldnames)
    for row in reader:
        taxon_id = row.get("taxonID", "").strip()
        if taxon_id:
            csv_by_id[taxon_id] = row

print("Loaded rows:", len(csv_by_id))
print("Walking MD root:", MD_ROOT)
print()

# --- WALK MARKDOWN FILES ---
for root, dirs, files in os.walk(MD_ROOT):
    for fname in files:
        if not fname.endswith(".md"):
            continue

        path = os.path.join(root, fname)
        print("Processing:", path)

        with open(path, encoding="utf-8") as f:
            text = f.read()

        # split front matter
        if not text.startswith("---"):
            print("  No front matter found, skipping")
            continue

        parts = text.split("---", 2)
        if len(parts) < 3:
            print("  Front matter malformed, skipping")
            continue

        fm_text = parts[1]
        body = parts[2]

        fm = yaml.safe_load(fm_text) or {}

        wfo_id = str(fm.get("wfo_id", "")).strip()
        print("  wfo_id:", wfo_id)

        if not wfo_id:
            print("  No wfo_id in front matter, skipping")
            continue

        # lookup CSV row
        row = csv_by_id.get(wfo_id)
        if not row:
            print("  No CSV match for this wfo_id")
            continue

        csv_subgenus = row.get("subgenus", "").strip()
        print("  CSV subgenus:", repr(csv_subgenus))
        print("  FM subgenus:", repr(fm.get("subgenus")))

        updated = False

        # populate only if missing
        value = fm.get("subgenus")

        if csv_subgenus:
            if value is None or str(value).strip() == "" or str(value).strip().lower() == "none":
                print("  → Updating subgenus")
                fm["subgenus"] = csv_subgenus
                updated = True
            else:
                print("  Subgenus already present, not overwriting")
        else:
            print("  CSV has no subgenus for this taxon")

        # write back only if changed
        if updated:
            new_fm_text = yaml.safe_dump(fm, sort_keys=False).strip()
            new_text = f"---\n{new_fm_text}\n---{body}"
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            print("  ✔ Updated and saved")
        else:
            print("  No update needed")

        print()  # blank line between files