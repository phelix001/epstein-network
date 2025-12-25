#!/usr/bin/env python3
"""
Focused extraction - search for known people directly in documents
More accurate than NER for building relationship networks
"""

import csv
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

# Comprehensive list of people to search for
SEARCH_TARGETS = {
    # Core case figures
    'jeffrey epstein': {'display': 'Jeffrey Epstein', 'category': 'core', 'patterns': [
        r'\bjeffrey\s+e?\.?\s*epstein\b', r'\bepstein\b', r'\bjeffrey\s+epstein\b'
    ]},
    'ghislaine maxwell': {'display': 'Ghislaine Maxwell', 'category': 'core', 'patterns': [
        r'\bghislaine\s+maxwell\b', r'\bg\.?\s*maxwell\b', r'\bmaxwell\b'
    ]},

    # Accomplices/Associates
    'sarah kellen': {'display': 'Sarah Kellen', 'category': 'accomplice', 'patterns': [
        r'\bsarah\s+kellen\b', r'\bkellen\b'
    ]},
    'nadia marcinkova': {'display': 'Nadia Marcinkova', 'category': 'accomplice', 'patterns': [
        r'\bnadia\s+marcinkova\b', r'\bmarcinkova\b'
    ]},
    'lesley groff': {'display': 'Lesley Groff', 'category': 'accomplice', 'patterns': [
        r'\blesley\s+groff\b', r'\bgroff\b'
    ]},
    'jean-luc brunel': {'display': 'Jean-Luc Brunel', 'category': 'accomplice', 'patterns': [
        r'\bjean[\s\-]?luc\s+brunel\b', r'\bbrunel\b', r'\bjean[\s\-]?luc\b'
    ]},
    'adriana ross': {'display': 'Adriana Ross', 'category': 'accomplice', 'patterns': [
        r'\badriana\s+ross\b'
    ]},

    # Victims/Witnesses
    'virginia giuffre': {'display': 'Virginia Giuffre', 'category': 'victim', 'patterns': [
        r'\bvirginia\s+(?:giuffre|roberts)\b', r'\bgiuffre\b'
    ]},
    'courtney wild': {'display': 'Courtney Wild', 'category': 'victim', 'patterns': [
        r'\bcourtney\s+wild\b'
    ]},
    'annie farmer': {'display': 'Annie Farmer', 'category': 'victim', 'patterns': [
        r'\bannie\s+farmer\b'
    ]},
    'maria farmer': {'display': 'Maria Farmer', 'category': 'victim', 'patterns': [
        r'\bmaria\s+farmer\b'
    ]},
    'johanna sjoberg': {'display': 'Johanna Sjoberg', 'category': 'victim', 'patterns': [
        r'\bjohanna\s+sjoberg\b', r'\bsjoberg\b'
    ]},
    'jane doe': {'display': 'Jane Doe (Various)', 'category': 'victim', 'patterns': [
        r'\bjane\s+doe\b'
    ]},

    # Political Figures
    'bill clinton': {'display': 'Bill Clinton', 'category': 'political', 'patterns': [
        r'\bbill\s+clinton\b', r'\bpresident\s+clinton\b', r'\bwilliam\s+(?:jefferson\s+)?clinton\b'
    ]},
    'donald trump': {'display': 'Donald Trump', 'category': 'political', 'patterns': [
        r'\bdonald\s+(?:j\.?\s+)?trump\b', r'\btrump\b'
    ]},
    'prince andrew': {'display': 'Prince Andrew', 'category': 'political', 'patterns': [
        r'\bprince\s+andrew\b', r'\bandrew\s+duke\s+of\s+york\b', r'\bduke\s+of\s+york\b'
    ]},
    'ehud barak': {'display': 'Ehud Barak', 'category': 'political', 'patterns': [
        r'\behud\s+barak\b', r'\bbarak\b'
    ]},
    'george mitchell': {'display': 'George Mitchell', 'category': 'political', 'patterns': [
        r'\bgeorge\s+mitchell\b', r'\bsenator\s+mitchell\b'
    ]},
    'bill richardson': {'display': 'Bill Richardson', 'category': 'political', 'patterns': [
        r'\bbill\s+richardson\b', r'\bgovernor\s+richardson\b'
    ]},

    # Business/Finance
    'les wexner': {'display': 'Les Wexner', 'category': 'business', 'patterns': [
        r'\b(?:les(?:lie)?|lex)\s+wexner\b', r'\bwexner\b'
    ]},
    'leon black': {'display': 'Leon Black', 'category': 'business', 'patterns': [
        r'\bleon\s+black\b'
    ]},
    'glenn dubin': {'display': 'Glenn Dubin', 'category': 'business', 'patterns': [
        r'\bglenn\s+dubin\b', r'\bdubin\b'
    ]},
    'eva dubin': {'display': 'Eva Dubin', 'category': 'business', 'patterns': [
        r'\beva\s+(?:andersson[\s\-])?dubin\b'
    ]},
    'mortimer zuckerman': {'display': 'Mortimer Zuckerman', 'category': 'business', 'patterns': [
        r'\b(?:mortimer|mort)\s+zuckerman\b', r'\bzuckerman\b'
    ]},
    'tom pritzker': {'display': 'Tom Pritzker', 'category': 'business', 'patterns': [
        r'\btom\s+pritzker\b', r'\bpritzker\b'
    ]},
    'bill gates': {'display': 'Bill Gates', 'category': 'business', 'patterns': [
        r'\bbill\s+gates\b', r'\bgates\b'
    ]},
    'reid hoffman': {'display': 'Reid Hoffman', 'category': 'business', 'patterns': [
        r'\breid\s+hoffman\b'
    ]},
    'jes staley': {'display': 'Jes Staley', 'category': 'business', 'patterns': [
        r'\b(?:jes|james)\s+staley\b', r'\bstaley\b'
    ]},

    # Legal
    'alan dershowitz': {'display': 'Alan Dershowitz', 'category': 'legal', 'patterns': [
        r'\balan\s+dershowitz\b', r'\bdershowitz\b'
    ]},
    'kenneth starr': {'display': 'Kenneth Starr', 'category': 'legal', 'patterns': [
        r'\bkenneth\s+starr\b', r'\bken\s+starr\b'
    ]},
    'brad edwards': {'display': 'Brad Edwards', 'category': 'legal', 'patterns': [
        r'\bbrad\s+edwards\b'
    ]},
    'david boies': {'display': 'David Boies', 'category': 'legal', 'patterns': [
        r'\bdavid\s+boies\b', r'\bboies\b'
    ]},
    'alexander acosta': {'display': 'Alexander Acosta', 'category': 'legal', 'patterns': [
        r'\b(?:alexander|alex)\s+acosta\b', r'\bacosta\b'
    ]},

    # Academic/Science
    'stephen hawking': {'display': 'Stephen Hawking', 'category': 'academic', 'patterns': [
        r'\bstephen\s+hawking\b', r'\bhawking\b'
    ]},
    'marvin minsky': {'display': 'Marvin Minsky', 'category': 'academic', 'patterns': [
        r'\bmarvin\s+minsky\b', r'\bminsky\b'
    ]},
    'lawrence krauss': {'display': 'Lawrence Krauss', 'category': 'academic', 'patterns': [
        r'\blawrence\s+krauss\b', r'\bkrauss\b'
    ]},
    'george church': {'display': 'George Church', 'category': 'academic', 'patterns': [
        r'\bgeorge\s+church\b'
    ]},
    'steven pinker': {'display': 'Steven Pinker', 'category': 'academic', 'patterns': [
        r'\bsteven\s+pinker\b', r'\bpinker\b'
    ]},
    'joi ito': {'display': 'Joi Ito', 'category': 'academic', 'patterns': [
        r'\bjoi\s+ito\b', r'\bito\b'
    ]},

    # Entertainment
    'david copperfield': {'display': 'David Copperfield', 'category': 'entertainment', 'patterns': [
        r'\bdavid\s+copperfield\b', r'\bcopperfield\b'
    ]},
    'kevin spacey': {'display': 'Kevin Spacey', 'category': 'entertainment', 'patterns': [
        r'\bkevin\s+spacey\b', r'\bspacey\b'
    ]},
    'chris tucker': {'display': 'Chris Tucker', 'category': 'entertainment', 'patterns': [
        r'\bchris\s+tucker\b'
    ]},
    'naomi campbell': {'display': 'Naomi Campbell', 'category': 'entertainment', 'patterns': [
        r'\bnaomi\s+campbell\b'
    ]},
    'woody allen': {'display': 'Woody Allen', 'category': 'entertainment', 'patterns': [
        r'\bwoody\s+allen\b'
    ]},

    # Employees/Staff
    'juan alessi': {'display': 'Juan Alessi', 'category': 'staff', 'patterns': [
        r'\bjuan\s+alessi\b', r'\balessi\b'
    ]},
    'alfredo rodriguez': {'display': 'Alfredo Rodriguez', 'category': 'staff', 'patterns': [
        r'\balfredo\s+rodriguez\b'
    ]},

    # Journalists
    'julie brown': {'display': 'Julie K. Brown', 'category': 'journalist', 'patterns': [
        r'\bjulie\s+(?:k\.?\s+)?brown\b'
    ]},
}

# Locations to search for
LOCATIONS = [
    ('new york', 'New York'),
    ('manhattan', 'Manhattan'),
    ('palm beach', 'Palm Beach'),
    ('little st. james', 'Little St. James Island'),
    ('little saint james', 'Little St. James Island'),
    ('virgin islands', 'US Virgin Islands'),
    ('st. thomas', 'St. Thomas'),
    ('zorro ranch', 'Zorro Ranch, NM'),
    ('new mexico', 'New Mexico'),
    ('paris', 'Paris'),
    ('london', 'London'),
    ('ohio', 'Ohio'),
    ('florida', 'Florida'),
    ('miami', 'Miami'),
]

# Date patterns
DATE_PATTERNS = [
    (r'\b(199\d|200\d|201\d|202\d)\b', '%Y'),
    (r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b', None),
    (r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b', None),
]

def main():
    csv_path = Path("dataset_text_extract - dataset_text_extract.csv")
    print(f"Loading dataset from {csv_path}...")

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_docs = len(rows)
    print(f"Processing {total_docs} documents...")

    # Data structures
    person_docs = defaultdict(set)  # person -> set of doc_ids
    person_locations = defaultdict(Counter)  # person -> location counts
    person_years = defaultdict(Counter)  # person -> year counts
    co_occurrences = defaultdict(Counter)  # person -> {other_person: count}
    doc_people = {}  # doc_id -> list of people found

    for i, row in enumerate(rows):
        if i % 1000 == 0:
            print(f"  Processing document {i}/{total_docs}...")

        doc_id = row['id']
        text = row['text'].lower()

        if not text or len(text) < 20:
            continue

        # Find all people mentioned in this document
        people_in_doc = set()

        for person_key, info in SEARCH_TARGETS.items():
            for pattern in info['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    people_in_doc.add(info['display'])
                    person_docs[info['display']].add(doc_id)
                    break

        doc_people[doc_id] = list(people_in_doc)

        # Build co-occurrence matrix
        people_list = list(people_in_doc)
        for j, p1 in enumerate(people_list):
            for p2 in people_list[j+1:]:
                if p1 != p2:
                    co_occurrences[p1][p2] += 1
                    co_occurrences[p2][p1] += 1

        # Find locations for each person
        for loc_pattern, loc_display in LOCATIONS:
            if loc_pattern in text:
                for person in people_in_doc:
                    person_locations[person][loc_display] += 1

        # Find years
        for pattern, _ in DATE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if match.isdigit() and 1990 <= int(match) <= 2025:
                        for person in people_in_doc:
                            person_years[person][int(match)] += 1
                except:
                    pass

    print("\n=== Extraction Complete ===")
    print(f"Found {len([p for p in person_docs if len(person_docs[p]) > 0])} people mentioned in documents")

    # Build person data
    people_data = {}
    for person_key, info in SEARCH_TARGETS.items():
        display = info['display']
        if display in person_docs:
            docs = person_docs[display]
            people_data[display] = {
                'count': len(docs),
                'category': info['category'],
                'docs': list(docs)[:100],
                'locations': dict(person_locations[display].most_common(10)),
                'years': dict(sorted(person_years[display].items())),
                'connections': dict(co_occurrences[display].most_common(30)),
            }

    # Print summary
    print("\n=== People by Mention Count ===")
    sorted_people = sorted(people_data.items(), key=lambda x: -x[1]['count'])
    for name, info in sorted_people[:30]:
        cat = info['category']
        count = info['count']
        top_conns = list(info['connections'].keys())[:3]
        print(f"  {name} ({cat}): {count} docs, connections: {', '.join(top_conns)}")

    # Save data
    output = {
        'people': people_data,
        'extraction_date': datetime.now().isoformat(),
        'total_documents': total_docs,
    }

    with open('focused_entities.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nSaved focused_entities.json")

    return people_data

if __name__ == '__main__':
    main()
