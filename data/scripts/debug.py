from pathlib import Path
from collections import defaultdict
import csv

# -----------------------------
# CONFIG
# -----------------------------
CSV_PATH = Path("data\AccetpedRhodo.csv")
MD_ROOT = Path("monograph_md")

COL_TAXON_ID = "taxonID"
COL_RANK = "taxonRank"
COL_STATUS = "taxonomicStatus"

# -----------------------------
# HELPERS
# -----------------------------
def safe(row, key):
    return (row.get(key) or "").strip()

def load_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

# -----------------------------
# 1. Load CSV and build accepted species ID set
# -----------------------------
rows = load_csv(CSV_PATH)

accepted_ids = {
    safe(r, COL_TAXON_ID)
    for r in rows
    if safe(r, COL_RANK).lower() == "species"
       and safe(r, COL_STATUS).lower() == "accepted"
}

print(f"Accepted species in CSV: {len(accepted_ids)}")

# -----------------------------
# 2. Scan Markdown files for wfo_id values
# -----------------------------
id_to_files = defaultdict(list)

for md_path in MD_ROOT.rglob("*.md"):
    try:
        text = md_path.read_text(encoding="utf-8")
    except:
        continue

    if not text.lstrip().startswith("---"):
        continue

    parts = text.split("---", 2)
    if len(parts) < 3:
        continue

    front = parts[1]

    for line in front.splitlines():
        if "wfo_id" in line.lower():
            raw = line.split(":", 1)[1].strip()
            raw = raw.split("#")[0].strip()
            raw = raw.strip('"').strip("'")
            if raw:
                id_to_files[raw].append(md_path)
            break

md_ids = set(id_to_files.keys())
print(f"Markdown pages scanned: {len(md_ids)}")

# -----------------------------
# 3. Find Markdown pages whose IDs are NOT accepted
# -----------------------------
orphans = md_ids - accepted_ids

print(f"\nMarkdown pages with non-accepted WFO IDs: {len(orphans)}")

for oid in sorted(orphans):
    print(f"\n{oid}")
    for p in id_to_files[oid]:
        print(f"   → {p}")