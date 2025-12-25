#!/usr/bin/env python3
"""
Epstein Document Relationship Extractor
Extracts people, locations, dates and builds relationship graphs
"""

import csv
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

import spacy
import pandas as pd
from dateutil import parser as date_parser

# Known notable/powerful individuals to highlight
NOTABLE_PEOPLE = {
    # Politicians
    'bill clinton', 'hillary clinton', 'donald trump', 'barack obama',
    'george bush', 'al gore', 'tony blair', 'ehud barak', 'prince andrew',

    # Royalty
    'prince andrew', 'sarah ferguson', 'queen elizabeth',

    # Business/Tech
    'bill gates', 'elon musk', 'jeff bezos', 'les wexner', 'leon black',
    'mortimer zuckerman', 'tom pritzker', 'glenn dubin', 'reid hoffman',

    # Media/Entertainment
    'woody allen', 'kevin spacey', 'chris tucker', 'naomi campbell',
    'courtney love', 'mick jagger', 'david copperfield',

    # Scientists/Academics
    'stephen hawking', 'lawrence krauss', 'marvin minsky', 'george church',
    'steven pinker', 'alan dershowitz',

    # Legal
    'alan dershowitz', 'kenneth starr',

    # Key figures in the case
    'jeffrey epstein', 'ghislaine maxwell', 'jean luc brunel',
    'sarah kellen', 'nadia marcinkova', 'lesley groff',
    'virginia giuffre', 'virginia roberts', 'courtney wild',
}

# Normalize name variations
NAME_ALIASES = {
    'virginia roberts': 'virginia giuffre',
    'prince andrew': 'prince andrew duke of york',
    'bill clinton': 'william clinton',
    'donald j trump': 'donald trump',
    'donald j. trump': 'donald trump',
    'j. epstein': 'jeffrey epstein',
    'j epstein': 'jeffrey epstein',
    'g. maxwell': 'ghislaine maxwell',
    'g maxwell': 'ghislaine maxwell',
}

def normalize_name(name):
    """Normalize a name to lowercase and apply aliases"""
    name = name.lower().strip()
    # Remove titles
    for title in ['mr.', 'mr', 'ms.', 'ms', 'mrs.', 'mrs', 'dr.', 'dr', 'prof.', 'prof']:
        if name.startswith(title + ' '):
            name = name[len(title)+1:]
    return NAME_ALIASES.get(name, name)

def is_valid_person_name(name):
    """Filter out invalid person names"""
    name_lower = name.lower()
    # Must have at least 2 parts (first and last name)
    parts = name.split()
    if len(parts) < 2:
        return False
    # Filter out common false positives
    invalid_patterns = [
        'grand jury', 'united states', 'new york', 'palm beach',
        'southern district', 'exhibit', 'document', 'page',
        'fbi', 'doj', 'nypd', 'case', 'file', 'evidence',
    ]
    for pattern in invalid_patterns:
        if pattern in name_lower:
            return False
    # Must not be all uppercase document references
    if name.isupper() and len(name) < 20:
        return False
    return True

def extract_dates(text):
    """Extract dates from text"""
    dates = []
    # Common date patterns
    patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
        r'\b(\d{1,2}-\d{1,2}-\d{2,4})\b',
        r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
        r'\b(\d{4})\b',  # Just years
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Try to parse the date
                parsed = date_parser.parse(match, fuzzy=True)
                if 1990 <= parsed.year <= 2025:  # Reasonable date range
                    dates.append(parsed)
            except:
                pass

    return dates

def main():
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")

    # Increase max length for large documents
    nlp.max_length = 2000000

    csv_path = Path("dataset_text_extract - dataset_text_extract.csv")
    print(f"Loading dataset from {csv_path}...")

    # Data structures
    doc_entities = {}  # doc_id -> {people: [], locations: [], dates: [], orgs: []}
    person_docs = defaultdict(set)  # person -> set of doc_ids
    person_locations = defaultdict(Counter)  # person -> location counts
    person_dates = defaultdict(list)  # person -> list of dates
    co_occurrences = defaultdict(Counter)  # person -> {other_person: count}
    all_people = Counter()
    all_locations = Counter()

    # Read and process CSV
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_docs = len(rows)
    print(f"Processing {total_docs} documents...")

    for i, row in enumerate(rows):
        if i % 500 == 0:
            print(f"  Processing document {i}/{total_docs}...")

        doc_id = row['id']
        text = row['text'][:100000]  # Limit text length for processing

        if not text or len(text) < 50:
            continue

        # Process with spaCy
        try:
            doc = nlp(text)
        except:
            continue

        # Extract entities
        people = set()
        locations = set()
        orgs = set()

        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = ent.text.strip()
                if is_valid_person_name(name):
                    normalized = normalize_name(name)
                    people.add(normalized)
                    all_people[normalized] += 1
            elif ent.label_ in ('GPE', 'LOC'):
                loc = ent.text.strip()
                if len(loc) > 2:
                    locations.add(loc)
                    all_locations[loc] += 1
            elif ent.label_ == 'ORG':
                orgs.add(ent.text.strip())

        # Extract dates from text
        dates = extract_dates(text)

        # Store document entities
        doc_entities[doc_id] = {
            'people': list(people),
            'locations': list(locations),
            'dates': [d.isoformat() for d in dates[:10]],  # Limit dates
            'orgs': list(orgs)
        }

        # Build person relationships
        people_list = list(people)
        for person in people_list:
            person_docs[person].add(doc_id)
            for loc in locations:
                person_locations[person][loc] += 1
            for date in dates[:5]:
                person_dates[person].append(date)

        # Build co-occurrence matrix (people mentioned in same document)
        for j, p1 in enumerate(people_list):
            for p2 in people_list[j+1:]:
                co_occurrences[p1][p2] += 1
                co_occurrences[p2][p1] += 1

    print("\n=== Extraction Complete ===")
    print(f"Total unique people: {len(all_people)}")
    print(f"Total unique locations: {len(all_locations)}")

    # Filter to notable people and those with significant mentions
    notable_found = {}
    for person, count in all_people.items():
        is_notable = any(notable in person for notable in NOTABLE_PEOPLE)
        if is_notable or count >= 5:  # Either notable or mentioned 5+ times
            notable_found[person] = {
                'count': count,
                'is_notable': is_notable,
                'docs': list(person_docs[person])[:50],  # Limit doc list
                'locations': dict(person_locations[person].most_common(10)),
                'connections': dict(co_occurrences[person].most_common(20)),
                'date_range': None
            }
            # Get date range
            if person_dates[person]:
                dates = sorted(person_dates[person])
                notable_found[person]['date_range'] = {
                    'earliest': dates[0].isoformat(),
                    'latest': dates[-1].isoformat()
                }

    print(f"\nFiltered to {len(notable_found)} significant/notable people")

    # Print top people
    print("\n=== Top 30 Most Mentioned People ===")
    for person, count in all_people.most_common(30):
        notable_marker = " ***" if any(n in person for n in NOTABLE_PEOPLE) else ""
        print(f"  {person}: {count} mentions{notable_marker}")

    # Print top locations
    print("\n=== Top 20 Locations ===")
    for loc, count in all_locations.most_common(20):
        print(f"  {loc}: {count}")

    # Save extracted data
    output = {
        'people': notable_found,
        'top_locations': dict(all_locations.most_common(100)),
        'extraction_date': datetime.now().isoformat()
    }

    with open('extracted_entities.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("\nSaved extracted_entities.json")

    return notable_found, all_locations

if __name__ == '__main__':
    main()
