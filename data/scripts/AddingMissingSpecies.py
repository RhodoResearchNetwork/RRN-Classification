import csv
from pathlib import Path
from datetime import date

# --- CONFIG -------------------------------------------------------------

# Path to the classification CSV
CSV_PATH = Path("data/AccetpedRhodo.csv")

# Root folder containing your existing Markdown species pages
MD_ROOT = Path(r"C:\Users\alane\RRN\RRN-Classification\monograph_md")  # adjust to your repo layout

# Where to write new Markdown files (can be same as MD_ROOT)
OUTPUT_ROOT = MD_ROOT / "additions"

# CSV column names (adjust if your headers differ)
COL_TAXON_ID = "taxonID"
COL_SCI_NAME = "scientificName"
COL_AUTH = "scientificNameAuthorship"
COL_RANK = "taxonRank"
COL_STATUS = "taxonomicStatus"
COL_PARENT_ID = "parentNameUsageID"
COL_ACCEPTED_ID = "acceptedNameUsageID"
COL_NAME_PUB = "namePublishedIn"
COL_DOI = "doi"
COL_IPNI = "scientificNameID"  # IPNI ID often in a column like this

# --- HELPERS ------------------------------------------------------------

def read_existing_wfo_ids(md_root: Path) -> set[str]:
    """Scan all .md files and collect wfo_id values from front matter.
       Logs every ID found for debugging.
    """
    existing_ids = set()

    print("\n--- Scanning existing Markdown pages for wfo_id ---")

    for md_path in md_root.rglob("*.md"):
        try:
            text = md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"[WARN] Could not read file (encoding issue): {md_path}")
            continue

        # Must start with YAML front matter
        if not text.lstrip().startswith("---"):
            print(f"[WARN] No front matter in: {md_path}")
            continue

        parts = text.split("---", 2)
        if len(parts) < 3:
            print(f"[WARN] Malformed front matter in: {md_path}")
            continue

        front_matter = parts[1]

        found = False
        for line in front_matter.splitlines():
            if "wfo_id" in line.lower():
                # Extract value after colon
                raw_value = line.split(":", 1)[1].strip()

                # Remove quotes and trailing comments
                raw_value = raw_value.split("#")[0].strip()
                raw_value = raw_value.strip('"').strip("'")

                if raw_value:
                    existing_ids.add(raw_value)
                    print(f"[FOUND] {raw_value}  ←  {md_path}")
                else:
                    print(f"[WARN] Empty wfo_id in: {md_path}")

                found = True
                break

        if not found:
            print(f"[WARN] No wfo_id found in: {md_path}")

    print(f"--- Done scanning. Found {len(existing_ids)} IDs. ---\n")
    return existing_ids

def load_classification_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def is_accepted_species(row: dict) -> bool:
    rank = (row.get(COL_RANK) or "").strip().lower()
    status = (row.get(COL_STATUS) or "").strip().lower()
    return rank == "species" and status == "accepted"


def split_genus_species(scientific_name: str) -> tuple[str, str]:
    if not scientific_name:
        return "", ""

    # Normalise hybrid marker
    cleaned = scientific_name.replace(" × ", " ").replace("×", " ")

    parts = cleaned.strip().split()

    if len(parts) >= 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], ""
    else:
        return "", ""


def safe(row: dict, key: str) -> str:
    return (row.get(key) or "").strip()


def build_markdown(row: dict, created_date: str) -> str:
    sci_name = safe(row, COL_SCI_NAME)
    auth = safe(row, COL_AUTH)
    genus, species = split_genus_species(sci_name)

    taxon_id = safe(row, COL_TAXON_ID)
    parent_id = safe(row, COL_PARENT_ID)
    accepted_id = safe(row, COL_ACCEPTED_ID) or taxon_id
    name_published_in = safe(row, COL_NAME_PUB)
    doi = safe(row, COL_DOI)
    ipni_id = safe(row, COL_IPNI)

    # Front matter exactly as your template, populated where possible
    front_matter = f"""---
layout: default
title: "{sci_name} {auth}"
description: 
scientificname: "{sci_name}"
scientificnameauthorship: "{auth}"
genus: "{genus}"
subgenus: 
section: 
subsection: 
source: 'WFO December 2025'
identifier: "{taxon_id}"
author: WFO
created: "{created_date}"
rights_holder:
license:
tags: []
namepublishedin: "{name_published_in}"
doi: "{doi}"
wfo_id: "{taxon_id}"
wfo_parent_id: "{parent_id}"
wfo_accepted_id: "{accepted_id}"
ipni_id: "{ipni_id}"
verified:
---

### _{{{{ page.scientificname }}}}_ {{{{ page.scientificnameauthorship }}}}
 [{{{{ page.namepublishedin }}}}]({{{{ page.doi }}}})

{{{{ page.subgenus }}}} {{{{ page.section }}}} {{{{ page.subsection }}}}

**WFO ID:** [{{{{ page.wfo_id }}}}](https://list.worldfloraonline.org/{{{{ page.wfo_id }}}})

**IPNI ID:** [{{{{ page.ipni_id }}}}](https://www.ipni.org/n/{{{{ page.ipni_id }}}})

Verified by: {{{{ page.verified }}}}

## Vernacular names


## Description


## Distribution


## Altitude


## Habitat


## Nomenclatural History
                       

## Notes

## References
"""
    return front_matter


def make_filename(scientific_name: str) -> str:
    genus, species = split_genus_species(scientific_name)
    genus = genus.lower()
    species = species.lower()
    if genus and species:
        return f"{genus}_{species}.md"
    elif genus:
        return f"{genus}.md"
    else:
        return "unnamed.md"


# --- MAIN ---------------------------------------------------------------

def main():
    print("Loading existing WFO IDs from Markdown...")
    existing_ids = read_existing_wfo_ids(MD_ROOT)
    print(f"Found {len(existing_ids)} existing wfo_id values.")

    print("Loading classification CSV...")
    rows = load_classification_rows(CSV_PATH)
    print(f"Loaded {len(rows)} rows from CSV.")

    today = date.today().isoformat()
    created_count = 0

    for row in rows:
        taxon_id = safe(row, COL_TAXON_ID)
        if not taxon_id:
            continue

        if taxon_id in existing_ids:
            # Already have a page for this WFO ID
            continue

        if not is_accepted_species(row):
            continue

        sci_name = safe(row, COL_SCI_NAME)
        if not sci_name:
            continue

        filename = make_filename(sci_name)
        out_path = OUTPUT_ROOT / filename

        if out_path.exists():
            # Safety: don't overwrite anything
            continue

        md_content = build_markdown(row, created_date=today)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_content, encoding="utf-8")
        created_count += 1
        print(f"Created: {out_path}")

    print(f"Done. Created {created_count} new Markdown files.")

if __name__ == "__main__":
    main()