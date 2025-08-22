import os
import yaml
import csv

INPUT_DIR = "monograph_md"
DATA_DIR = "data"

# Map output field → (CSV path, source field in CSV)
ID_SOURCES = {
    "wfo_id": (r"data\classification.csv", "taxonID"),
    "ipni_id": (r"data\classification.csv", "scientificNameID"),
    "wfo_parent_id": (r"data\classification.csv", "parentNameUsageID"),
    "wfo_accepted_id": (r"data\classification.csv", "acceptedNameUsageID")
}

def load_id_map(csv_path, source_field):
    """Build dict mapping 'Name Authorship' → ID"""
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("scientificName", "").strip()
            author = row.get("scientificNameAuthorship", "").strip()
            full_key = f"{name} {author}".strip()
            taxonid = row.get(source_field, "").strip()
            if full_key and taxonid:
                mapping[full_key] = taxonid
    return mapping

def extract_frontmatter(lines):
    """Extract YAML frontmatter from lines"""
    if not lines or lines[0].strip() != "---":
        return {}, 0, lines
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), -1)
    yaml_block = lines[1:end]
    data = yaml.safe_load("\n".join(yaml_block)) if end > 0 else {}
    return data or {}, end + 1, lines[end + 1:]

def dump_frontmatter(data):
    """Convert dict to YAML frontmatter lines"""
    yaml_text = yaml.dump(data, sort_keys=False, allow_unicode=True)
    return ["---\n"] + [line + "\n" for line in yaml_text.splitlines()] + ["---\n"]

def update_markdown_file(filepath, id_maps):
    """Inject multiple IDs based on name + authorship"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    meta, body_start, body = extract_frontmatter(lines)
    name = meta.get("scientificname", "").strip()
    author = meta.get("authorship", "").strip()
    full_key = f"{name} {author}".strip()

    updated = False
    for id_field, id_map in id_maps.items():
        taxonid = id_map.get(full_key)
        if taxonid:
            meta[id_field] = taxonid
            updated = True
            print(f"✔ {os.path.basename(filepath)} → {id_field} set to {taxonid}")
        else:
            print(f"⚠ {os.path.basename(filepath)} → No match for {id_field}: {full_key}")

    if updated:
        new_lines = dump_frontmatter(meta) + body
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

def process_all_files():
    id_maps = {
        id_field: load_id_map(csv_path, source_field)
        for id_field, (csv_path, source_field) in ID_SOURCES.items()
    }
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            update_markdown_file(os.path.join(INPUT_DIR, filename), id_maps)

if __name__ == "__main__":
    process_all_files()