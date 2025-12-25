#!/usr/bin/env python3
"""
Extract text from PDF using pdfplumber properly
"""

import pdfplumber
from pathlib import Path

def main():
    pdf_path = Path('additional_data/doj_flight_logs.pdf')

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    print(f"Opening {pdf_path}...")

    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")

        for i, page in enumerate(pdf.pages):
            if i % 50 == 0:
                print(f"Processing page {i+1}/{len(pdf.pages)}...")

            text = page.extract_text()
            if text:
                all_text.append(f"\n=== PAGE {i+1} ===\n")
                all_text.append(text)

    full_text = '\n'.join(all_text)

    # Save extracted text
    output_file = 'flight_logs_extracted.txt'
    with open(output_file, 'w') as f:
        f.write(full_text)

    print(f"\nExtracted {len(full_text)} characters to {output_file}")
    print("\nFirst 3000 characters:")
    print("-" * 50)
    print(full_text[:3000])

if __name__ == '__main__':
    main()
