#!/usr/bin/env python3
"""
Merge all extracted dataset entities with focused_entities.json
"""

import json
from collections import defaultdict

def main():
    # Load existing data
    print("Loading existing focused_entities.json...")
    with open('focused_entities.json', 'r') as f:
        existing = json.load(f)

    print(f"Existing data: {len(existing['people'])} people")

    # Load DataSet 6 and 7
    datasets = []
    for ds in ['dataset6_entities.json', 'dataset7_entities.json']:
        try:
            with open(ds, 'r') as f:
                data = json.load(f)
                datasets.append((ds, data))
                print(f"Loaded {ds}: {len(data['entities'])} entities")
        except FileNotFoundError:
            print(f"Warning: {ds} not found")

    # Track new people to add
    new_people = {}
    merge_counts = defaultdict(int)

    for ds_name, data in datasets:
        for name, info in data['entities'].items():
            if info['category'] == 'location':
                continue

            # Try to match with existing
            matched = False
            for existing_name in list(existing['people'].keys()):
                if name.lower() == existing_name.lower():
                    existing['people'][existing_name]['count'] += info['document_count']
                    merge_counts[existing_name] += info['document_count']
                    matched = True
                    break
                # Partial match for last names
                if len(name.split()) == 1 and name.lower() in existing_name.lower():
                    existing['people'][existing_name]['count'] += info['document_count']
                    merge_counts[existing_name] += info['document_count']
                    matched = True
                    break

            if not matched and info['count'] >= 2:  # Only add if mentioned 2+ times
                if name not in new_people:
                    new_people[name] = {
                        'count': info['document_count'],
                        'category': info['category'],
                        'years': {'2007': info['document_count']} if 'dataset7' in ds_name else {'2020': info['document_count']},
                        'locations': {},
                        'connections': {'Jeffrey Epstein': info['document_count']}
                    }
                else:
                    new_people[name]['count'] += info['document_count']

    # Add new people
    for name, info in new_people.items():
        if name not in existing['people']:
            existing['people'][name] = info
            print(f"  Added: {name} ({info['category']})")

    # Add connections between lawyers who appear together
    lawyers = ['Kenneth Starr', 'Ken Starr', 'Jay Lefkowitz', 'Alan Dershowitz',
               'Roy Black', 'Gerald Lefcourt', 'Martin Weinberg', 'Alexander Acosta']
    for lawyer in lawyers:
        if lawyer in existing['people']:
            for other in lawyers:
                if other in existing['people'] and other != lawyer:
                    if 'connections' not in existing['people'][lawyer]:
                        existing['people'][lawyer]['connections'] = {}
                    if other not in existing['people'][lawyer]['connections']:
                        existing['people'][lawyer]['connections'][other] = 1

    # Update sources
    existing['sources'] = existing.get('sources', [])
    existing['sources'].append('DOJ DataSet 7 - Grand Jury Testimony 2007 (17 documents)')
    existing['total_documents'] = existing.get('total_documents', 8531) + 17

    # Save
    with open('focused_entities.json', 'w') as f:
        json.dump(existing, f, indent=2)

    print(f"\nTotal people now: {len(existing['people'])}")
    print("\nMerged counts:")
    for name, count in sorted(merge_counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: +{count}")

    print("\n" + "="*60)
    print("UPDATED ENTITY SUMMARY")
    print("="*60)
    sorted_people = sorted(existing['people'].items(), key=lambda x: -x[1]['count'])
    for name, info in sorted_people[:20]:
        print(f"  {name} ({info['category']}): {info['count']} documents")

if __name__ == '__main__':
    main()
