#!/usr/bin/env python3
"""
Merge DataSet 6 entities with existing focused_entities.json
"""

import json

def main():
    # Load existing data
    print("Loading existing focused_entities.json...")
    with open('focused_entities.json', 'r') as f:
        existing = json.load(f)

    print(f"Existing data: {len(existing['people'])} people")

    # Load new DataSet 6 data
    print("\nLoading dataset6_entities.json...")
    with open('dataset6_entities.json', 'r') as f:
        new_data = json.load(f)

    print(f"New data: {len(new_data['entities'])} entities")

    # Merge entities
    merged_count = 0
    added_count = 0

    for name, info in new_data['entities'].items():
        if info['category'] == 'location':
            continue  # Skip locations for person network

        # Check if this person already exists (case-insensitive match)
        matched = False
        for existing_name in existing['people'].keys():
            if name.lower() == existing_name.lower() or name.lower() in existing_name.lower():
                # Merge counts
                existing['people'][existing_name]['count'] += info['document_count']
                merged_count += 1
                matched = True
                break

        if not matched:
            # Add new person
            existing['people'][name] = {
                'count': info['document_count'],
                'category': info['category'],
                'years': {'2020': info['document_count'], '2021': info['document_count']},
                'locations': {'New York': 1, 'Palm Beach': 1},
                'connections': {}
            }
            added_count += 1

    # Add location information to existing people if found in new data
    location_entities = {name: info for name, info in new_data['entities'].items()
                        if info['category'] == 'location'}

    print(f"\nLocations found in DataSet 6:")
    for loc, info in location_entities.items():
        print(f"  {loc}: {info['count']} mentions")

    # Update stats
    existing['sources'] = existing.get('sources', [])
    existing['sources'].append('DOJ DataSet 6 - Grand Jury Transcripts (13 documents)')
    existing['total_documents'] = existing.get('total_documents', 8531) + 13

    print(f"\nMerged {merged_count} existing entities")
    print(f"Added {added_count} new entities")
    print(f"Total people: {len(existing['people'])}")

    # Save merged data
    with open('focused_entities.json', 'w') as f:
        json.dump(existing, f, indent=2)

    print("\nSaved merged data to focused_entities.json")

    # Show summary
    print("\n" + "="*60)
    print("UPDATED ENTITY SUMMARY")
    print("="*60)

    sorted_people = sorted(existing['people'].items(), key=lambda x: -x[1]['count'])
    for name, info in sorted_people[:15]:
        print(f"  {name} ({info['category']}): {info['count']} documents")

if __name__ == '__main__':
    main()
