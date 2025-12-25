#!/usr/bin/env python3
"""
Extract text from DataSet 7 PDFs and run entity extraction
"""

import pdfplumber
import json
import re
from pathlib import Path
from collections import defaultdict

# Extended list of known individuals
KNOWN_PEOPLE = {
    # Core
    'Jeffrey Epstein': 'core', 'Epstein': 'core',
    'Ghislaine Maxwell': 'accomplice', 'Maxwell': 'accomplice',
    'Jean-Luc Brunel': 'accomplice', 'Brunel': 'accomplice',

    # Victims
    'Virginia Giuffre': 'victim', 'Virginia Roberts': 'victim', 'Giuffre': 'victim',
    'Sarah Ransome': 'victim', 'Courtney Wild': 'victim',
    'Annie Farmer': 'victim', 'Maria Farmer': 'victim', 'Jane Doe': 'victim',

    # Political
    'Bill Clinton': 'political', 'Clinton': 'political',
    'Donald Trump': 'political', 'Trump': 'political',
    'Prince Andrew': 'political', 'Andrew': 'political',
    'Ehud Barak': 'political', 'Bill Richardson': 'political',
    'George Mitchell': 'political',

    # Business
    'Leslie Wexner': 'business', 'Wexner': 'business',
    'Bill Gates': 'business', 'Leon Black': 'business',
    'Jes Staley': 'business', 'Glenn Dubin': 'business',
    'Eva Dubin': 'business', 'Thomas Pritzker': 'business',
    'Mortimer Zuckerman': 'business',

    # Legal
    'Alan Dershowitz': 'legal', 'Dershowitz': 'legal',
    'Kenneth Starr': 'legal', 'Ken Starr': 'legal',
    'Alex Acosta': 'legal', 'Alexander Acosta': 'legal',
    'David Boies': 'legal', 'Jack Goldberger': 'legal',
    'Jay Lefkowitz': 'legal', 'Roy Black': 'legal',
    'Martin Weinberg': 'legal', 'Gerald Lefcourt': 'legal',

    # Academic
    'Lawrence Krauss': 'academic', 'Marvin Minsky': 'academic',
    'Stephen Hawking': 'academic', 'Noam Chomsky': 'academic',
    'Steven Pinker': 'academic', 'Joi Ito': 'academic',

    # Staff
    'Sarah Kellen': 'staff', 'Lesley Groff': 'staff',
    'Nadia Marcinkova': 'staff', 'Adriana Ross': 'staff',
    'Juan Alessi': 'staff', 'Alfredo Rodriguez': 'staff',

    # Entertainment
    'Kevin Spacey': 'entertainment', 'Naomi Campbell': 'entertainment',
    'Chris Tucker': 'entertainment',

    # Law Enforcement / Prosecutors
    'Barry Krischer': 'legal', 'Michael Reiter': 'legal',

    # Locations
    'Little St. James': 'location', 'Zorro Ranch': 'location',
    'Palm Beach': 'location', 'New Mexico': 'location',
    'Virgin Islands': 'location', 'Teterboro': 'location',
}

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return '\n'.join(text_parts)
    except Exception as e:
        return f"Error: {e}"

def extract_entities(text, doc_id):
    """Extract known entities from text"""
    found = defaultdict(lambda: {'count': 0, 'category': '', 'documents': [], 'contexts': []})

    for name, category in KNOWN_PEOPLE.items():
        pattern = r'\b' + re.escape(name) + r'\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            found[name]['count'] += 1
            found[name]['category'] = category
            if doc_id not in found[name]['documents']:
                found[name]['documents'].append(doc_id)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace('\n', ' ')
            if len(found[name]['contexts']) < 3:
                found[name]['contexts'].append(context)

    return dict(found)

def main():
    pdf_dir = Path('additional_data/dataset7_sample/VOL00007/IMAGES/0001')

    if not pdf_dir.exists():
        print(f"Error: {pdf_dir} not found")
        return

    pdf_files = list(pdf_dir.glob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files")

    all_entities = defaultdict(lambda: {'count': 0, 'category': '', 'documents': [], 'contexts': []})
    all_text = []
    processed = 0
    total_chars = 0

    for i, pdf_file in enumerate(sorted(pdf_files, key=lambda x: x.stat().st_size, reverse=True)):
        print(f"Processing {i+1}/{len(pdf_files)}: {pdf_file.name} ({pdf_file.stat().st_size // 1024}KB)...")

        doc_id = pdf_file.stem
        text = extract_text_from_pdf(pdf_file)

        if text.startswith("Error:"):
            print(f"  Error: {text}")
            continue

        processed += 1
        total_chars += len(text)
        all_text.append(f"\n{'='*60}\n=== {doc_id} ===\n{'='*60}\n{text}")

        entities = extract_entities(text, doc_id)
        for name, info in entities.items():
            all_entities[name]['count'] += info['count']
            all_entities[name]['category'] = info['category']
            all_entities[name]['documents'].extend(info['documents'])
            all_entities[name]['contexts'].extend(info['contexts'])

    print(f"\nProcessed {processed} PDFs")
    print(f"Total text extracted: {total_chars:,} characters")

    with open('dataset7_text.txt', 'w') as f:
        f.write('\n'.join(all_text))
    print(f"Saved extracted text to dataset7_text.txt")

    sorted_entities = sorted(all_entities.items(), key=lambda x: -x[1]['count'])

    print(f"\n{'='*60}")
    print("ENTITIES FOUND IN DATASET 7")
    print('='*60)

    for name, info in sorted_entities:
        if info['count'] > 0:
            unique_docs = len(set(info['documents']))
            print(f"\n  {name} ({info['category']}): {info['count']} mentions in {unique_docs} documents")
            if info['contexts']:
                print(f"    Context: ...{info['contexts'][0][:80]}...")

    output = {
        'source': 'DOJ DataSet 7 - Grand Jury Testimony 2007',
        'total_documents': processed,
        'total_characters': total_chars,
        'entities': {k: {
            'count': v['count'],
            'category': v['category'],
            'document_count': len(set(v['documents'])),
            'sample_contexts': v['contexts'][:3]
        } for k, v in all_entities.items() if v['count'] > 0}
    }

    with open('dataset7_entities.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved entity data to dataset7_entities.json")

if __name__ == '__main__':
    main()
