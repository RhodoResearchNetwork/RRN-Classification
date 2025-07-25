import xml.etree.ElementTree as ET
from html import unescape
from jinja2 import Template
from bs4 import BeautifulSoup
import os
import re

# --- Markdown Template ---
md_template = Template("""---
scientific name: "{{ scientific_name }}"
genus: "{{ genus }}"
family: "{{ family }}"
order: "{{ order }}"
kingdom: "{{ kingdom }}"
source: "Edinburgh Rhododendron Monographs – Royal Botanic Garden Edinburgh"
identifier: "https://data.rbge.org.uk/service/factsheets/Edinburgh_Rhododendron_Monographs.xhtml"
author: "{{ author }}"
created: "{{ created }}"
rights holder: "{{ rights_holder }}"
license: "{{ license }}"
tags: ["taxonomy", "Rhododendron"]
name published in: "{{ primary_reference }}"
doi: "{{ doi }}"
wfo id : "{{ taxonid }}"
wfo parent id: "{{ parent_id }}"
wfo accepted id: "{{ accepted_id }}" #if synonym probably needs to be archived.                      
ipni id: "{{ ipni_id }}"
verified:
---

                       

# {{ scientific_name }}

## Description
{{ description }}

## Distribution
{{ distribution }}

## Altitude
{{ altitude }}

## Habitat
{{ habitat }}

## Nomenclatural History
{{ nomenclatural_history }}
                       
## Notes
{{ notes }}

## References
{% if secondary_reference %}
{{ secondary_reference }}
{% else %}
_No additional reference available._
{% endif %}
""")

# --- Helper Functions ---
def extract_text(elem, tag, ns):
    found = elem.find(tag, ns)
    return found.text.strip() if found is not None and found.text else ""

def clean_html(raw_html):
    text = unescape(raw_html)
    soup = BeautifulSoup(text, "html.parser")

    # Remove unwanted wrappers
    for tag in soup.find_all(['div', 'p']):
        tag.unwrap()

    # Replace span with class="rank" by literal text
    for span in soup.find_all('span', class_='rank'):
        span.replace_with(' var. ')

    # Convert <i>, <strong> to Markdown
    for tag in soup.find_all(['i', 'em']):
        tag.insert_before('*')
        tag.insert_after('*')
        tag.unwrap()

    for tag in soup.find_all(['b', 'strong']):
        tag.insert_before('**')
        tag.insert_after('**')
        tag.unwrap()

    # Remove any other span tags but keep content
    for span in soup.find_all('span'):
        span.unwrap()

    # Return clean text
    return soup.get_text(separator=' ', strip=True)

def sanitize_filename(name):
    safe = re.sub(r'[<>:"/\\|?*]', '', name)
    safe = re.sub(r'\s+', '_', safe)
    return safe

# --- Taxon Parser ---
def parse_taxon(taxon, ns):
    scientific_name = extract_text(taxon, 'dwc:ScientificName', ns)
    if not scientific_name:
        print("⚠️ Skipping taxon: missing scientific name")
        return None, None

    genus = extract_text(taxon, 'dwc:Genus', ns)
    family = extract_text(taxon, 'dwc:Family', ns)
    order = extract_text(taxon, 'dwc:Order', ns)
    kingdom = extract_text(taxon, 'dwc:Kingdom', ns)
    identifier = extract_text(taxon, 'dcterms:identifier', ns)
    source = extract_text(taxon, 'dc:source', ns)

    # Extract and split references
    references = [ref.text.strip() for ref in taxon.findall('eol:reference', ns) if ref.text]
    primary_reference = references[0] if len(references) > 0 else ""
    secondary_reference = references[1] if len(references) > 1 else ""

    # Section extraction
    sections = {'description': '', 'distribution': '', 'habitat': '', 'nomenclatural_history': ''}
    title_map = {
        'diagnostic description': 'description',
        'description': 'description',
        'distribution': 'distribution',
        'habitat': 'habitat',
        'nomenclatural history': 'nomenclatural_history'
    }
    
    data_objects = taxon.findall('eol:dataObject', ns)
    author = created = license = rights_holder = ""

    if data_objects:
        # Extract from the first dataObject (can enhance to aggregate later)
        first_obj = data_objects[0]
        author_elem = first_obj.find("eol:agent[@role='author']", ns)
        author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""

        created = extract_text(first_obj, 'dcterms:created', ns)
        license = extract_text(first_obj, 'license', ns)
        rights_holder = extract_text(first_obj, 'dcterms:rightsHolder', ns)

    for obj in taxon.findall('eol:dataObject', ns):
        title = extract_text(obj, 'dc:title', ns).lower()
        key = title_map.get(title)
        if key:
            raw_html = extract_text(obj, 'dc:description', ns)
            sections[key] = clean_html(raw_html)

    print(f"🧬 Parsed taxon: {scientific_name}")
    return md_template.render(
            scientific_name=scientific_name,
            genus=genus,
            family=family,
            order=order,
            kingdom=kingdom,
            source=source,
            identifier=identifier,
            author=author,
            created=created,
            rights_holder=rights_holder,
            license=license,
            primary_reference=primary_reference,
            secondary_reference=secondary_reference,
            description=sections['description'],
            distribution=sections['distribution'],
            habitat=sections['habitat'],
            altitude="",  # Placeholder
            nomenclatural_history=sections['nomenclatural_history'],
            notes=""
        ), scientific_name

# --- Main Execution ---
def main(xml_path, output_dir="monograph_md"):
    print(f"📂 Loading XML: {xml_path}")
    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError:
        print(f"❌ File not found: {xml_path}")
        return
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return

    root = tree.getroot()
    ns = {
        'eol': "http://www.eol.org/transfer/content/0.3",
        'dc': "http://purl.org/dc/elements/1.1/",
        'dcterms': "http://purl.org/dc/terms/",
        'dwc': "http://rs.tdwg.org/dwc/dwcore/"
    }

    os.makedirs(output_dir, exist_ok=True)
    taxa = root.findall('eol:taxon', ns)
    print(f"🔍 Found {len(taxa)} taxon elements")

    count = 0
    for taxon in taxa:
        md_content, sci_name = parse_taxon(taxon, ns)
        if not md_content or not sci_name:
            continue

        safe_name = sanitize_filename(sci_name)
        if safe_name != sci_name:
            print(f"🧹 Sanitized filename: '{sci_name}' → '{safe_name}'")

        filename = f"{safe_name.lower()}.md"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"✅ Saved: {filepath}")
            count += 1
        except OSError as e:
            print(f"❌ Failed to write '{filename}': {e}")

    print(f"\n📊 Summary: {count} Markdown files written to '{output_dir}'")

# --- Run ---
if __name__ == "__main__":
    main("EdinburghMonograph\edinburgh_monograph.xml")