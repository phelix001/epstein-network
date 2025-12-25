#!/usr/bin/env python3
"""
Extract text from DataSet 5 PDFs and run entity extraction
"""

import pdfplumber
import json
import re
from pathlib import Path
from collections import defaultdict

# Known individuals to search for (expanded list)
KNOWN_PEOPLE = {
    # Core
    'Jeffrey Epstein': 'core',
    'Epstein': 'core',
    'Ghislaine Maxwell': 'accomplice',
    'Maxwell': 'accomplice',
    'Jean-Luc Brunel': 'accomplice',
    'Brunel': 'accomplice',

    # Victims
    'Virginia Giuffre': 'victim',
    'Virginia Roberts': 'victim',
    'Giuffre': 'victim',
    'Sarah Ransome': 'victim',
    'Courtney Wild': 'victim',
    'Annie Farmer': 'victim',
    'Maria Farmer': 'victim',

    # Political
    'Bill Clinton': 'political',
    'Clinton': 'political',
    'Donald Trump': 'political',
    'Trump': 'political',
    'Prince Andrew': 'political',
    'Andrew': 'political',
    'Ehud Barak': 'political',
    'Barak': 'political',
    'Bill Richardson': 'political',
    'George Mitchell': 'political',

    # Business
    'Leslie Wexner': 'business',
    'Wexner': 'business',
    'Bill Gates': 'business',
    'Gates': 'business',
    'Leon Black': 'business',
    'Jes Staley': 'business',
    'Glenn Dubin': 'business',
    'Eva Dubin': 'business',
    'Thomas Pritzker': 'business',
    'Mortimer Zuckerman': 'business',

    # Legal
    'Alan Dershowitz': 'legal',
    'Dershowitz': 'legal',
    'Kenneth Starr': 'legal',
    'Alex Acosta': 'legal',
    'David Boies': 'legal',

    # Academic
    'Lawrence Krauss': 'academic',
    'Marvin Minsky': 'academic',
    'Stephen Hawking': 'academic',
    'Noam Chomsky': 'academic',
    'Steven Pinker': 'academic',

    # Staff
    'Sarah Kellen': 'staff',
    'Kellen': 'staff',
    'Lesley Groff': 'staff',
    'Nadia Marcinkova': 'staff',
    'Adriana Ross': 'staff',

    # Entertainment
    'Kevin Spacey': 'entertainment',
    'Naomi Campbell': 'entertainment',
    'Chris Tucker': 'entertainment',

    # Locations/Properties
    'Little St. James': 'location',
    'Zorro Ranch': 'location',
    'Palm Beach': 'location',
    '9 East 71st': 'location',
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
    found = defaultdict(lambda: {'count': 0, 'category': '', 'documents': []})

    for name, category in KNOWN_PEOPLE.items():
        # Case insensitive search
        pattern = r'\b' + re.escape(name) + r'\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found[name]['count'] += len(matches)
            found[name]['category'] = category
            found[name]['documents'].append(doc_id)

    return dict(found)

def extract_dates(text):
    """Extract dates from text"""
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
    ]

    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))

    return dates

def main():
    pdf_dir = Path('additional_data/dataset5_sample/VOL00005/IMAGES/0001')

    if not pdf_dir.exists():
        print(f"Error: {pdf_dir} not found")
        return

    pdf_files = list(pdf_dir.glob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files")

    all_entities = defaultdict(lambda: {'count': 0, 'category': '', 'documents': []})
    all_text = []
    processed = 0
    errors = 0

    for i, pdf_file in enumerate(pdf_files):
        if i % 20 == 0:
            print(f"Processing {i+1}/{len(pdf_files)}...")

        doc_id = pdf_file.stem
        text = extract_text_from_pdf(pdf_file)

        if text.startswith("Error:"):
            errors += 1
            continue

        processed += 1
        all_text.append(f"\n=== {doc_id} ===\n{text}")

        # Extract entities
        entities = extract_entities(text, doc_id)
        for name, info in entities.items():
            all_entities[name]['count'] += info['count']
            all_entities[name]['category'] = info['category']
            all_entities[name]['documents'].extend(info['documents'])

    print(f"\nProcessed {processed} PDFs ({errors} errors)")

    # Save all extracted text
    with open('dataset5_text.txt', 'w') as f:
        f.write('\n'.join(all_text))
    print(f"Saved extracted text to dataset5_text.txt")

    # Sort by count
    sorted_entities = sorted(all_entities.items(), key=lambda x: -x[1]['count'])

    print(f"\n{'='*60}")
    print("ENTITIES FOUND IN DATASET 5")
    print('='*60)

    for name, info in sorted_entities:
        if info['count'] > 0:
            unique_docs = len(set(info['documents']))
            print(f"  {name} ({info['category']}): {info['count']} mentions in {unique_docs} documents")

    # Save results
    output = {
        'total_documents': processed,
        'entities': {k: {'count': v['count'], 'category': v['category'], 'document_count': len(set(v['documents']))}
                    for k, v in all_entities.items() if v['count'] > 0}
    }

    with open('dataset5_entities.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved entity data to dataset5_entities.json")

    # Show sample text from first few docs
    print(f"\n{'='*60}")
    print("SAMPLE TEXT FROM FIRST 3 DOCUMENTS")
    print('='*60)

    for pdf_file in pdf_files[:3]:
        text = extract_text_from_pdf(pdf_file)
        print(f"\n--- {pdf_file.stem} ---")
        print(text[:1000] if len(text) > 1000 else text)
        print("...")

if __name__ == '__main__':
    main()
