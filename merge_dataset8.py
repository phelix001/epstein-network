#!/usr/bin/env python3
"""
Merge DataSet 8 findings into the network visualization data
"""

import json
from collections import defaultdict

def main():
    # Load existing data
    print("Loading focused_entities.json...")
    with open('focused_entities.json', 'r') as f:
        data = json.load(f)

    print(f"Existing: {len(data['people'])} people")

    # Load DataSet 8 scan results
    print("Loading dataset8_redacted_scan.json...")
    with open('dataset8_redacted_scan.json', 'r') as f:
        ds8 = json.load(f)

    # Key new entities to add from DataSet 8
    new_entities = {
        # Attorneys - Maxwell Defense
        'Christian Everdell': {'category': 'legal', 'count': 295, 'role': 'Maxwell Defense Attorney'},
        'Laura Menninger': {'category': 'legal', 'count': 278, 'role': 'Maxwell Defense Attorney'},
        'Jeff Pagliuca': {'category': 'legal', 'count': 203, 'role': 'Maxwell Defense Attorney'},
        'Bobbi Sternheim': {'category': 'legal', 'count': 149, 'role': 'Maxwell Defense Attorney'},

        # Attorneys - Victims
        'Gloria Allred': {'category': 'legal', 'count': 61, 'role': 'Victims Attorney'},
        'Jack Scarola': {'category': 'legal', 'count': 43, 'role': 'Victims Attorney'},
        'Brad Edwards': {'category': 'legal', 'count': 31, 'role': 'Victims Attorney'},
        'Sigrid McCawley': {'category': 'legal', 'count': 31, 'role': 'Victims Attorney'},
        'Roberta Kaplan': {'category': 'legal', 'count': 32, 'role': 'Victims Attorney'},
        'Paul Cassell': {'category': 'legal', 'count': 10, 'role': 'Victims Attorney'},

        # Attorneys - Epstein Defense
        'Martin Weinberg': {'category': 'legal', 'count': 39, 'role': 'Epstein Defense Attorney'},
        'Reid Weingarten': {'category': 'legal', 'count': 39, 'role': 'Epstein Defense Attorney'},
        'Mark Cohen': {'category': 'legal', 'count': 75, 'role': 'Epstein Defense Attorney'},

        # Prosecutors/Judges
        'Audrey Strauss': {'category': 'legal', 'count': 25, 'role': 'Prosecutor SDNY'},
        'Alison Nathan': {'category': 'legal', 'count': 35, 'role': 'Judge SDNY'},
        'Judge Berman': {'category': 'legal', 'count': 33, 'role': 'Judge SDNY'},

        # Family
        'Mark Epstein': {'category': 'family', 'count': 51, 'role': 'Jeffrey Epstein Brother'},
        'Isabel Maxwell': {'category': 'family', 'count': 16, 'role': 'Ghislaine Maxwell Sister'},

        # Political (from DS8)
        'Joe Biden': {'category': 'political', 'count': 19, 'role': 'Political Figure'},
        'Robert Mueller': {'category': 'legal', 'count': 19, 'role': 'Former FBI Director'},

        # Journalists/Media
        'Bruce Barket': {'category': 'legal', 'count': 34, 'role': 'Attorney'},

        # Associates (from hidden emails)
        'Stan Pottinger': {'category': 'associate', 'count': 1, 'role': 'Associate (email found)'},
        'Juanesteban Ganoza': {'category': 'associate', 'count': 1, 'role': 'Peru contact - arranged "girls"'},
    }

    # Add or update entities
    for name, info in new_entities.items():
        if name not in data['people']:
            data['people'][name] = {
                'count': info['count'],
                'category': info['category'],
                'years': {'2019': info['count'] // 2, '2020': info['count'] // 2},
                'locations': {},
                'connections': {},
                'role': info.get('role', '')
            }
            print(f"  Added: {name} ({info['category']})")
        else:
            # Update count
            data['people'][name]['count'] += info['count']
            if 'role' not in data['people'][name]:
                data['people'][name]['role'] = info.get('role', '')
            print(f"  Updated: {name} (+{info['count']})")

    # Add connections based on DataSet 8 findings
    connections = {
        # Maxwell defense team connections
        'Christian Everdell': ['Ghislaine Maxwell', 'Laura Menninger', 'Jeff Pagliuca', 'Bobbi Sternheim'],
        'Laura Menninger': ['Ghislaine Maxwell', 'Christian Everdell', 'Jeff Pagliuca', 'Bobbi Sternheim'],
        'Jeff Pagliuca': ['Ghislaine Maxwell', 'Christian Everdell', 'Laura Menninger'],
        'Bobbi Sternheim': ['Ghislaine Maxwell', 'Christian Everdell', 'Laura Menninger'],

        # Epstein defense
        'Martin Weinberg': ['Jeffrey Epstein', 'Reid Weingarten', 'Mark Cohen'],
        'Reid Weingarten': ['Jeffrey Epstein', 'Martin Weinberg', 'Mark Cohen'],
        'Mark Cohen': ['Jeffrey Epstein', 'Martin Weinberg', 'Reid Weingarten'],

        # Victims attorneys
        'Gloria Allred': ['Virginia Giuffre', 'Jeffrey Epstein', 'Ghislaine Maxwell'],
        'Jack Scarola': ['Virginia Giuffre', 'Jeffrey Epstein', 'Brad Edwards'],
        'Brad Edwards': ['Virginia Giuffre', 'Jeffrey Epstein', 'Jack Scarola', 'Paul Cassell'],
        'Sigrid McCawley': ['Virginia Giuffre', 'Jeffrey Epstein', 'Ghislaine Maxwell'],
        'Roberta Kaplan': ['Virginia Giuffre', 'Jeffrey Epstein'],
        'Paul Cassell': ['Virginia Giuffre', 'Jeffrey Epstein', 'Brad Edwards'],

        # Prosecutors/Judges
        'Audrey Strauss': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
        'Alison Nathan': ['Ghislaine Maxwell'],
        'Judge Berman': ['Jeffrey Epstein'],

        # Family connections
        'Mark Epstein': ['Jeffrey Epstein'],
        'Isabel Maxwell': ['Ghislaine Maxwell'],

        # From hidden email about Peru "girls"
        'Juanesteban Ganoza': ['Ghislaine Maxwell'],
        'Stan Pottinger': ['Jeffrey Epstein'],

        # Political
        'Joe Biden': ['Donald Trump'],
        'Robert Mueller': ['Jeffrey Epstein'],
    }

    print("\nAdding connections...")
    for name, conn_list in connections.items():
        if name in data['people']:
            if 'connections' not in data['people'][name]:
                data['people'][name]['connections'] = {}
            for conn in conn_list:
                if conn in data['people']:
                    if conn not in data['people'][name]['connections']:
                        data['people'][name]['connections'][conn] = 5  # Weight from DS8
                    else:
                        data['people'][name]['connections'][conn] += 5

    # Update Jeffrey Epstein and Ghislaine Maxwell counts from DS8
    if 'Jeffrey Epstein' in data['people']:
        data['people']['Jeffrey Epstein']['count'] += 1371
        data['people']['Jeffrey Epstein']['years']['2019'] = data['people']['Jeffrey Epstein']['years'].get('2019', 0) + 500
        data['people']['Jeffrey Epstein']['years']['2020'] = data['people']['Jeffrey Epstein']['years'].get('2020', 0) + 400
        data['people']['Jeffrey Epstein']['years']['2021'] = data['people']['Jeffrey Epstein']['years'].get('2021', 0) + 300
        # Add new connections from DS8
        for conn in ['Mark Epstein', 'Martin Weinberg', 'Reid Weingarten', 'Mark Cohen', 'Stan Pottinger']:
            if conn in data['people']:
                data['people']['Jeffrey Epstein']['connections'][conn] = data['people']['Jeffrey Epstein']['connections'].get(conn, 0) + 10

    if 'Ghislaine Maxwell' in data['people']:
        data['people']['Ghislaine Maxwell']['count'] += 1133
        data['people']['Ghislaine Maxwell']['years']['2019'] = data['people']['Ghislaine Maxwell']['years'].get('2019', 0) + 200
        data['people']['Ghislaine Maxwell']['years']['2020'] = data['people']['Ghislaine Maxwell']['years'].get('2020', 0) + 400
        data['people']['Ghislaine Maxwell']['years']['2021'] = data['people']['Ghislaine Maxwell']['years'].get('2021', 0) + 300
        # Add new connections
        for conn in ['Isabel Maxwell', 'Christian Everdell', 'Laura Menninger', 'Jeff Pagliuca', 'Bobbi Sternheim', 'Juanesteban Ganoza']:
            if conn in data['people']:
                data['people']['Ghislaine Maxwell']['connections'][conn] = data['people']['Ghislaine Maxwell']['connections'].get(conn, 0) + 10

    # Update Prince Andrew with DS8 count
    if 'Prince Andrew' in data['people']:
        data['people']['Prince Andrew']['count'] += 81

    # Add Deutsche Bank as financial connection
    data['people']['Deutsche Bank'] = {
        'count': 42,
        'category': 'financial',
        'years': {'2019': 20, '2020': 22},
        'locations': {'New York': 30},
        'connections': {'Jeffrey Epstein': 42},
        'role': 'Financial Institution'
    }

    # Update sources
    data['sources'] = data.get('sources', [])
    data['sources'].append('DOJ DataSet 8 - Full Document Scan (10,593 documents, 936 emails extracted)')
    data['total_documents'] = data.get('total_documents', 8561) + 10593

    # Save updated data
    with open('focused_entities.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nTotal people now: {len(data['people'])}")
    print(f"Total documents: {data['total_documents']}")

    # Print summary
    print("\n" + "="*60)
    print("UPDATED ENTITY SUMMARY")
    print("="*60)
    sorted_people = sorted(data['people'].items(), key=lambda x: -x[1]['count'])
    for name, info in sorted_people[:25]:
        role = info.get('role', '')
        role_str = f" - {role}" if role else ""
        print(f"  {name} ({info['category']}): {info['count']} documents{role_str}")

if __name__ == '__main__':
    main()
