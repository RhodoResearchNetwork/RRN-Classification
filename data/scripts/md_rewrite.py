import os
import yaml

INPUT_DIR = "monograph_md"  # Directory with your markdown files

# Literal block to insert — preserved exactly as written
INSERT_BLOCK = """### _{{ page.scientificname }}_ {{ page.scientificauthorship }}
 {{ page.namepublishedin }}

{{ page.subfamily }} {{ page.section }} {{ page.subsection }}

**WFO ID:** [{{ page.wfo_id }}](https://list.worldfloraonline.org/{{ page.wfo_id }})

**IPNI ID:** [{{ page.ipni_id }}](https://www.ipni.org/n/{{ page.ipni_id }})

Verified by: {{ page.verified }}
"""

def load_yaml_frontmatter(lines):
    """Extract YAML frontmatter and return end index"""
    if lines[0].strip() != "---":
        return {}, 0
    end_index = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), -1)
    yaml_block = lines[1:end_index]
    data = yaml.safe_load("\n".join(yaml_block)) if end_index > 0 else {}
    return data, end_index + 1

def clean_headers(body_lines):
    """Remove the first two markdown headers"""
    cleaned = []
    headers_removed = 0
    for line in body_lines:
        if headers_removed < 2 and line.strip().startswith("#"):
            headers_removed += 1
            continue
        cleaned.append(line)
    return cleaned

def simplify_filename(filename):
    """Keep only genus_species from original filename"""
    stem = os.path.splitext(filename)[0]
    parts = stem.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}.md"
    return stem + ".md"

def rewrite_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    _, body_start = load_yaml_frontmatter(lines)
    body = clean_headers(lines[body_start:])
    new_lines = lines[:body_start] + [INSERT_BLOCK + "\n"] + body

    # Rename file using simplified filename
    original_filename = os.path.basename(filepath)
    new_filename = simplify_filename(original_filename)
    new_path = os.path.join(INPUT_DIR, new_filename)

    with open(new_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    # Remove original if renamed
    if new_path != filepath:
        os.remove(filepath)
        print(f"✔ Renamed: {original_filename} → {new_filename}")
    else:
        print(f"✔ Updated: {original_filename}")

def process_all_markdown():
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            rewrite_file(os.path.join(INPUT_DIR, filename))

if __name__ == "__main__":
    process_all_markdown()