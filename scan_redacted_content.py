#!/usr/bin/env python3
"""
Comprehensive scanner for hidden/redacted content in DataSet 8 PDFs.
Extracts ALL names, emails, phone numbers, and other potentially redacted info.
"""

import pdfplumber
import json
import re
import csv
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

# Patterns for extracting potentially sensitive information
PATTERNS = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
    'ssn': re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
    'date': re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE),
    'address': re.compile(r'\b\d+\s+[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way)\b', re.IGNORECASE),
}

# Name patterns - more aggressive to catch potential victims
NAME_PATTERNS = [
    # Full names with titles
    re.compile(r'\b(?:Ms?\.?|Mrs\.?|Miss|Mr\.?|Dr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'),
    # Standard full names (First Last or First Middle Last)
    re.compile(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]{2,})\b'),
    # Names in email contexts (before @)
    re.compile(r'\b([A-Z][a-z]+[._][A-Z][a-z]+)@'),
    # Names after "From:", "To:", "Cc:", etc.
    re.compile(r'(?:From|To|Cc|Bcc|Sent by|By):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', re.IGNORECASE),
]

# Known individuals to categorize
KNOWN_PEOPLE = {
    'Jeffrey Epstein': 'core', 'Epstein': 'core',
    'Ghislaine Maxwell': 'accomplice', 'Maxwell': 'accomplice',
    'Jean-Luc Brunel': 'accomplice', 'Brunel': 'accomplice',
    'Virginia Giuffre': 'victim', 'Virginia Roberts': 'victim', 'Giuffre': 'victim',
    'Sarah Ransome': 'victim', 'Courtney Wild': 'victim',
    'Annie Farmer': 'victim', 'Maria Farmer': 'victim',
    'Bill Clinton': 'political', 'Clinton': 'political',
    'Donald Trump': 'political', 'Trump': 'political',
    'Prince Andrew': 'political', 'Andrew': 'political',
    'Ehud Barak': 'political', 'Bill Richardson': 'political',
    'George Mitchell': 'political',
    'Leslie Wexner': 'business', 'Wexner': 'business',
    'Bill Gates': 'business', 'Leon Black': 'business',
    'Glenn Dubin': 'business', 'Eva Dubin': 'business',
    'Alan Dershowitz': 'legal', 'Dershowitz': 'legal',
    'Kenneth Starr': 'legal', 'Ken Starr': 'legal',
    'Alexander Acosta': 'legal', 'Alex Acosta': 'legal',
    'Sarah Kellen': 'staff', 'Lesley Groff': 'staff',
    'Nadia Marcinkova': 'staff', 'Adriana Ross': 'staff',
}

# Attorney names to flag separately (might appear in redacted sections)
ATTORNEY_NAMES = [
    'Christian Everdell', 'Laura Menninger', 'Jeff Pagliuca', 'Jeffrey Pagliuca',
    'Roberta Kaplan', 'Alexandra Conlon', 'Gloria Allred', 'Audrey Strauss',
    'Geoffrey Berman', 'Maurene Comey', 'Alison Moe', 'David Boies',
    'Sigrid McCawley', 'Bradley Edwards', 'Paul Cassell', 'Jack Scarola',
]

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
        return f"ERROR: {e}"

def extract_all_names(text):
    """Extract all potential names from text"""
    names = set()
    for pattern in NAME_PATTERNS:
        for match in pattern.finditer(text):
            name = match.group(1) if match.groups() else match.group(0)
            name = name.strip()
            # Filter out common false positives
            if len(name) > 5 and not any(x in name.lower() for x in ['document', 'exhibit', 'page', 'court', 'states', 'united', 'district', 'southern']):
                names.add(name)
    return names

def categorize_name(name):
    """Categorize a name if known"""
    for known, category in KNOWN_PEOPLE.items():
        if known.lower() in name.lower() or name.lower() in known.lower():
            return category
    for attorney in ATTORNEY_NAMES:
        if attorney.lower() in name.lower() or name.lower() in attorney.lower():
            return 'attorney'
    return 'unknown'

def scan_pdf(pdf_path):
    """Scan a single PDF for all extractable content"""
    result = {
        'file': str(pdf_path),
        'file_id': pdf_path.stem,
        'text_length': 0,
        'emails': [],
        'phones': [],
        'names': [],
        'addresses': [],
        'dates': [],
        'known_people': [],
        'potential_victims': [],
        'attorneys': [],
        'has_content': False,
        'error': None
    }

    text = extract_text_from_pdf(pdf_path)

    if text.startswith("ERROR:"):
        result['error'] = text
        return result

    result['text_length'] = len(text)
    result['has_content'] = len(text) > 100

    if not result['has_content']:
        return result

    # Extract emails
    for match in PATTERNS['email'].finditer(text):
        email = match.group(0)
        if email not in result['emails']:
            result['emails'].append(email)

    # Extract phones
    for match in PATTERNS['phone'].finditer(text):
        phone = match.group(0)
        if phone not in result['phones']:
            result['phones'].append(phone)

    # Extract addresses
    for match in PATTERNS['address'].finditer(text):
        addr = match.group(0)
        if addr not in result['addresses']:
            result['addresses'].append(addr)

    # Extract dates
    for match in PATTERNS['date'].finditer(text):
        date = match.group(0)
        if date not in result['dates']:
            result['dates'].append(date)

    # Extract names and categorize
    names = extract_all_names(text)
    for name in names:
        category = categorize_name(name)
        if category in ['core', 'accomplice', 'victim', 'political', 'business', 'staff']:
            result['known_people'].append({'name': name, 'category': category})
        elif category == 'attorney':
            result['attorneys'].append(name)
        else:
            # Check if this could be a victim name (female first names, etc.)
            female_indicators = ['she', 'her', 'miss', 'ms', 'mrs', 'woman', 'girl', 'female']
            context_start = text.lower().find(name.lower())
            if context_start > 0:
                context = text[max(0, context_start-200):context_start+200].lower()
                if any(ind in context for ind in female_indicators + ['victim', 'minor', 'massage', 'recruit']):
                    result['potential_victims'].append(name)
                else:
                    result['names'].append(name)
            else:
                result['names'].append(name)

    return result

def process_batch(pdf_files, batch_num, total_batches):
    """Process a batch of PDFs"""
    results = []
    for i, pdf_path in enumerate(pdf_files):
        if i % 100 == 0:
            print(f"  Batch {batch_num}/{total_batches}: {i}/{len(pdf_files)}", flush=True)
        result = scan_pdf(pdf_path)
        if result['has_content'] or result['error']:
            results.append(result)
    return results

def main():
    pdf_dir = Path('additional_data/dataset8_full/VOL00008/IMAGES')

    if not pdf_dir.exists():
        print(f"Error: {pdf_dir} not found")
        return

    # Find all PDFs
    pdf_files = list(pdf_dir.rglob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files to scan")

    # Track all findings
    all_results = []
    all_emails = defaultdict(list)  # email -> list of file_ids
    all_phones = defaultdict(list)
    all_names = defaultdict(lambda: {'count': 0, 'files': [], 'category': 'unknown'})
    potential_victims = defaultdict(list)

    # Process in batches
    batch_size = 500
    batches = [pdf_files[i:i+batch_size] for i in range(0, len(pdf_files), batch_size)]
    total_batches = len(batches)

    print(f"Processing {total_batches} batches of ~{batch_size} files each...")

    processed = 0
    with_content = 0
    errors = 0

    for batch_num, batch in enumerate(batches, 1):
        print(f"\nBatch {batch_num}/{total_batches}...")

        for pdf_path in batch:
            if processed % 500 == 0:
                print(f"  Progress: {processed}/{len(pdf_files)} files ({with_content} with content, {errors} errors)", flush=True)

            result = scan_pdf(pdf_path)
            processed += 1

            if result['error']:
                errors += 1
                continue

            if result['has_content']:
                with_content += 1
                all_results.append(result)

                # Aggregate emails
                for email in result['emails']:
                    all_emails[email].append(result['file_id'])

                # Aggregate phones
                for phone in result['phones']:
                    all_phones[phone].append(result['file_id'])

                # Aggregate names
                for name in result['names'] + [p['name'] for p in result['known_people']] + result['attorneys']:
                    all_names[name]['count'] += 1
                    all_names[name]['files'].append(result['file_id'])
                    if result['known_people']:
                        for p in result['known_people']:
                            if p['name'] == name:
                                all_names[name]['category'] = p['category']
                    elif name in result['attorneys']:
                        all_names[name]['category'] = 'attorney'

                # Track potential victims
                for name in result['potential_victims']:
                    potential_victims[name].append(result['file_id'])

    print(f"\n{'='*60}")
    print("SCAN COMPLETE")
    print('='*60)
    print(f"Total files processed: {processed}")
    print(f"Files with extractable content: {with_content}")
    print(f"Files with errors: {errors}")

    # Save comprehensive results
    output = {
        'summary': {
            'total_files': processed,
            'files_with_content': with_content,
            'errors': errors,
            'unique_emails': len(all_emails),
            'unique_phones': len(all_phones),
            'unique_names': len(all_names),
            'potential_victims_found': len(potential_victims)
        },
        'emails': {k: {'count': len(v), 'files': v[:10]} for k, v in sorted(all_emails.items(), key=lambda x: -len(x[1]))},
        'phones': {k: {'count': len(v), 'files': v[:10]} for k, v in sorted(all_phones.items(), key=lambda x: -len(x[1]))},
        'names': {k: v for k, v in sorted(all_names.items(), key=lambda x: -x[1]['count']) if v['count'] >= 2},
        'potential_victims': {k: {'count': len(v), 'files': v} for k, v in sorted(potential_victims.items(), key=lambda x: -len(x[1]))},
        'detailed_results': all_results[:1000]  # Save first 1000 detailed results
    }

    with open('dataset8_redacted_scan.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved full results to dataset8_redacted_scan.json")

    # Create CSV of all unique names for easy review
    with open('dataset8_all_names.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Category', 'Mention Count', 'Sample Files'])
        for name, info in sorted(all_names.items(), key=lambda x: -x[1]['count']):
            if info['count'] >= 2:
                writer.writerow([name, info['category'], info['count'], '; '.join(info['files'][:5])])
    print(f"Saved name list to dataset8_all_names.csv")

    # Create CSV of potential victim names
    with open('dataset8_potential_victims.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Mention Count', 'Files'])
        for name, files in sorted(potential_victims.items(), key=lambda x: -len(x[1])):
            writer.writerow([name, len(files), '; '.join(files)])
    print(f"Saved potential victims to dataset8_potential_victims.csv")

    # Create CSV of all emails
    with open('dataset8_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Email', 'Occurrences', 'Sample Files'])
        for email, files in sorted(all_emails.items(), key=lambda x: -len(x[1])):
            writer.writerow([email, len(files), '; '.join(files[:10])])
    print(f"Saved emails to dataset8_emails.csv")

    # Print summary
    print(f"\n{'='*60}")
    print("TOP FINDINGS")
    print('='*60)

    print("\n--- TOP 30 NAMES ---")
    for name, info in list(sorted(all_names.items(), key=lambda x: -x[1]['count']))[:30]:
        print(f"  {name} ({info['category']}): {info['count']} mentions")

    print("\n--- TOP 20 EMAILS ---")
    for email, files in list(sorted(all_emails.items(), key=lambda x: -len(x[1])))[:20]:
        print(f"  {email}: {len(files)} occurrences")

    print("\n--- POTENTIAL VICTIM NAMES ---")
    for name, files in list(sorted(potential_victims.items(), key=lambda x: -len(x[1])))[:20]:
        print(f"  {name}: {len(files)} mentions")

    print("\n--- TOP 10 PHONES ---")
    for phone, files in list(sorted(all_phones.items(), key=lambda x: -len(x[1])))[:10]:
        print(f"  {phone}: {len(files)} occurrences")

if __name__ == '__main__':
    main()
