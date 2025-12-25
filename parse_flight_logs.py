#!/usr/bin/env python3
"""
Parse DOJ flight logs PDF to extract passenger names and flight details
"""

import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

def extract_text_from_pdf(pdf_path):
    """Use pdfplumber to extract text from PDF"""
    result = subprocess.run(
        ['pdfplumber', str(pdf_path)],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_flight_logs(text):
    """Parse the extracted text to find flight information"""
    flights = []
    passengers = defaultdict(lambda: {'count': 0, 'flights': []})

    # Common patterns in flight logs
    # Date patterns
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'

    # Look for passenger names - typically capitalized words
    # Filter out common non-name words
    skip_words = {
        'FLIGHT', 'LOG', 'PASSENGER', 'PASSENGERS', 'DATE', 'AIRCRAFT',
        'DEPARTURE', 'ARRIVAL', 'FROM', 'TO', 'THE', 'AND', 'FOR',
        'SCHEDULE', 'MANIFEST', 'CREW', 'PILOT', 'PAGE', 'EXHIBIT',
        'TOTAL', 'HOURS', 'MINUTES', 'TIME', 'FILED', 'DOCUMENT',
        'REDACTED', 'FBI', 'DOJ', 'FOIA', 'REQUEST', 'GOVERNMENT',
        'JEFFREY', 'EPSTEIN', 'MAXWELL', 'GHISLAINE'  # We already know these
    }

    # Known locations to skip
    locations = {
        'NEW YORK', 'MIAMI', 'PALM BEACH', 'FLORIDA', 'ST THOMAS',
        'VIRGIN ISLANDS', 'TETERBORO', 'PARIS', 'LONDON', 'COLUMBUS',
        'OHIO', 'BEDFORD', 'SANTA FE', 'NEW MEXICO', 'AZORES'
    }

    # Extract potential names (2-3 capitalized words)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'

    lines = text.split('\n')
    current_date = None
    current_route = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for dates
        date_match = re.search(date_pattern, line)
        if date_match:
            current_date = date_match.group(1)

        # Look for routes (FROM -> TO patterns)
        route_match = re.search(r'([A-Z][A-Z\s]+)\s*(?:to|->|=>)\s*([A-Z][A-Z\s]+)', line, re.I)
        if route_match:
            current_route = f"{route_match.group(1).strip()} -> {route_match.group(2).strip()}"

        # Extract potential names
        names = re.findall(name_pattern, line)
        for name in names:
            # Skip if it's a location or common word
            name_upper = name.upper()
            if any(skip in name_upper for skip in skip_words):
                continue
            if any(loc in name_upper for loc in locations):
                continue
            if len(name) < 5:  # Skip very short matches
                continue

            passengers[name]['count'] += 1
            if current_date or current_route:
                passengers[name]['flights'].append({
                    'date': current_date,
                    'route': current_route
                })

    return dict(passengers)

def main():
    pdf_path = Path('additional_data/doj_flight_logs.pdf')

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)

    print(f"Extracted {len(text)} characters of text")

    # Save raw text for inspection
    with open('flight_logs_text.txt', 'w') as f:
        f.write(text)
    print("Saved raw text to flight_logs_text.txt")

    # Parse for passengers
    print("\nParsing for passenger names...")
    passengers = parse_flight_logs(text)

    # Sort by count
    sorted_passengers = sorted(passengers.items(), key=lambda x: -x[1]['count'])

    print(f"\nFound {len(passengers)} potential names")
    print("\nTop 30 most frequent names:")
    print("-" * 40)

    for name, info in sorted_passengers[:30]:
        print(f"  {name}: {info['count']} mentions")

    # Save results
    output = {
        'total_names': len(passengers),
        'passengers': passengers
    }

    with open('flight_log_passengers.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved full results to flight_log_passengers.json")

if __name__ == '__main__':
    main()
