import os
import yaml
import csv

INPUT_DIR = "monograph_md"
CLASSIFICATION_CSV = "data/classifciation.csv"
UNMATCHED_LOG = "unmatched_taxa.log"

def load_classification_map(csv_path):
    """Build dict mapping 'Name Authorship' → enrichment data"""
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("scientificName", "").strip()
            author = row.get("scientificNameAuthorship", "").strip()
            full_key = f"{name} {author}".strip()
            mapping[full_key] = {
                "wfo_id": row.get("taxonID", "").strip(),
                "ipni_id": row.get("scientificNameID", "").strip(),
                "scientificnameauthorship": author
            }
    return mapping

def extract_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, 0, lines
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), -1)
    yaml_block = lines[1:end]
    data = yaml.safe_load("\n".join(yaml_block)) if end > 0 else {}
    return data or {}, end + 1, lines[end + 1:]

def dump_frontmatter(data):
    yaml_text = yaml.dump(data, sort_keys=False, allow_unicode=True)
    return ["---\n"] + [line + "\n" for line in yaml_text.splitlines()] + ["---\n"]

def update_markdown_file(filepath, name_map, unmatched_log):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    meta, body_start, body = extract_frontmatter(lines)
    name = meta.get("scientificname", "").strip()
    author = meta.get("authorship", "").strip()
    full_key = f"{name} {author}".strip()

    match = name_map.get(full_key)
    if match:
        for field in ["wfo_id", "ipni_id", "scientificnameauthorship"]:
            if match.get(field):
                meta[field] = match[field]

        new_lines = dump_frontmatter(meta) + body
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"✔ {os.path.basename(filepath)} → wfo_id: {match['wfo_id']} | ipni_id: {match['ipni_id']} | authorship: {match['scientificnameauthorship']}")
    else:
        with open(unmatched_log, 'a', encoding='utf-8') as log:
            log.write(f"{os.path.basename(filepath)} → {full_key}\n")
        print(f"⚠ No match for: {full_key}")

def process_all_files():
    name_map = load_classification_map(CLASSIFICATION_CSV)
    open(UNMATCHED_LOG, 'w', encoding='utf-8').close()
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            update_markdown_file(os.path.join(INPUT_DIR, filename), name_map, UNMATCHED_LOG)

if __name__ == "__main__":
    process_all_files()