---
license: mit
language:
- en
tags:
- epstein
- epstein-data
- dataset
- fbi
- journalism
---

# FULL_EPSTEIN_INDEX

# CONTENT WARNING: This repository contains graphic and highly sensitive material regarding sexual abuse, exploitation, trafficking, and violence. It also contains unverified allegations and raw witness statements. User discretion is strongly advised.

## Overview

Note. There is ALOT of data. OCR made mistakes scanning the files. So that being said, there is a lot of noise in the dataset, whether it be from OCR taking words out of normal 'pictures' from the pdf's, or character recognition failure. Feel free to contribute, clean up, add too, etc. 

You can view ALL raw files [here.](https://drive.google.com/drive/folders/18tIY9QEGUZe0q_AFAxoPnnVBCWbqHm2p?usp=drive_link) This includes all releases, from all government bodies, from all timelines.

This is a comprehensive, unified research archive aggregating public releases related to the Jeffrey Epstein estate and associated investigations.

This repository expands upon earlier archives (such as the initial November 2025 House Oversight release) by integrating the First Phase of Declassified Epstein Files released by the Department of Justice. Unlike previous datasets restricted to scanned emails, this index combines:

House Oversight Documents: ~20,000 pages of emails and estate records (Nov 2025).
DOJ Disclosures: Flight logs, contact books (redacted), and the "Masseuse List."
Multimedia Evidence: BOP video footage and audio recordings from the Maxwell Proffer sessions.
FBI releases, Customs and Border Patrol releases, etc.
Note on Updates: This index is a living archive. As additional phases of files are declassified and released by government bodies, they will be processed, indexed, and added to this repository.

The repository is organized to facilitate open-source intelligence (OSINT) analysis and research.

Always cross-reference with the original raw files.

## Usage Guidelines
This dataset is intended for research, investigative journalism, and legal analysis. By accessing this repository, you agree to the following ethical guidelines:

## User Responsibilities
Verify Facts: Much of this data consists of raw evidence, notes, and unverified allegations. Do not present search results as established fact without corroboration.
Respect Privacy: Adhere to all redactions found in the source documents. Do not attempt to use this data to doxx or harass individuals.
Victim Dignity: Treat all information regarding potential victims with extreme care and respect.

## Prohibited Uses
No Fine-Tuning: Do not use this dataset to train or fine-tune generative AI models. The risk of generating hallucinations regarding sensitive legal matters is too high.
No Harassment: Do not use this tool to target private individuals.
No Commercial Exploitation: This data is for public interest and educational purposes.

## Sources
This index aggregates public domain releases from:
U.S. House Committee on Oversight and Accountability (Nov 12, 2025 Release)
U.S. Department of Justice (First Phase Declassification, Flight Logs, Maxwell Proffer Material, Dec 2025 Release)
All FBI, Border Patrol, and other government body releases

## Legal & Disclaimer
Disclaimer: This repository is an independent collection and is not an official service of the U.S. Government.

## Copyright: 
Original government documents are generally in the public domain or released under Fair Use principles for research. The organizing scripts and index structure are licensed under the MIT License.

*Liability: The maintainers of FULL_EPSTEIN_INDEX claim no ownership over the underlying documents and assume no liability for the use, misuse, or interpretation of this data. Users are solely responsible for compliance with applicable laws and privacy regulations.* 

To contribute corrections to transcripts or metadata, please open a Pull Request citing the specific File ID.

---

## Interactive Network Analysis (Added Dec 2025)

### Live Demo

**[Open the Interactive Network Graph](https://phelix001.github.io/epstein-network/epstein_network_timeline.html)**

- **Click any node** to open Wikipedia
- **Use the timeline slider** to filter by year (1994-2025)
- **Hover** for details on each person

### Key Findings from DataSet 8 Analysis

Extracted improperly redacted content from DOJ DataSet 8 (10,593 PDFs). Documents have "redaction" as visual overlays without removing underlying text.

#### Discovered Hidden Content:

- **936 unique email addresses** extracted
- **23,383 names** identified
- **Ghislaine Maxwell's personal email**: `gmax1@mindspring.com`
- **2002 email chain** discussing arranging "girls" in Peru (Document: EFTA00011438)
- **Epstein's Sex Offender Registry** fully extractable (victim ages: 14, 16)
- **11 email addresses** belonging to Epstein including `LITTLESTJEFF@YAHOO.COM`
- **Encrypted messaging apps**: Signal, Telegram, WhatsApp, Confide

See [REDDIT_REPORT.md](REDDIT_REPORT.md) for top 50 findings with sources.

### Network Statistics

| Metric | Value |
|--------|-------|
| Individuals Mapped | 47 |
| Connections Documented | 112 |
| Documents Analyzed | 19,154 |
| Year Range | 1994-2025 |

### Categories in Network

- **Core** (red): Jeffrey Epstein, Ghislaine Maxwell
- **Accomplices** (orange): Staff members
- **Victims** (purple): Virginia Giuffre, Jane Doe
- **Political** (blue): Prince Andrew, Bill Clinton, Donald Trump
- **Legal** (yellow): Defense attorneys, prosecutors, judges
- **Family** (orange): Mark Epstein, Isabel Maxwell
- **Associates** (purple): Stan Pottinger, Juanesteban Ganoza
- **Financial** (teal): Deutsche Bank

### Analysis Files

| File | Description |
|------|-------------|
| `epstein_network_timeline.html` | Interactive visualization (open in browser) |
| `focused_entities.json` | Network data with connections |
| `dataset8_redacted_scan.json` | Full extraction results from DataSet 8 |
| `dataset8_emails.csv` | All 936 emails extracted |
| `dataset8_all_names.csv` | All names with document sources |
| `REDDIT_REPORT.md` | Top 50 findings report |
| `DATASET8_HIDDEN_CONTENT_REPORT.md` | Technical analysis |

### Source Links

| Source | Link |
|--------|------|
| HuggingFace Dataset | [theelderemo/FULL_EPSTEIN_INDEX](https://huggingface.co/datasets/theelderemo/FULL_EPSTEIN_INDEX) |
| Raw Files (Google Drive) | [All Releases](https://drive.google.com/drive/folders/18tIY9QEGUZe0q_AFAxoPnnVBCWbqHm2p) |
| DOJ FOIA DataSets | [justice.gov FOIA](https://www.justice.gov/archives/jm/foia-update-foia-contacts-department-justice) |
| WikiEpstein | [wikiepstein.com](https://wikiepstein.com/) |

### How to Run Analysis

```bash
# Clone repo
git clone https://github.com/yourusername/epstein-network.git
cd epstein-network

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pdfplumber

# Download DOJ DataSet 8 and extract to additional_data/
# Run extraction
python scan_redacted_content.py

# Rebuild visualization
python build_timeline_graph.py
```

### Methodology

1. Downloaded DOJ FOIA DataSets 1-8 (~12.4 GB)
2. Extracted text from 10,593 PDFs using pdfplumber
3. Pattern matched for emails, names, phone numbers
4. Cross-referenced with known individuals
5. Built network graph with vis-network.js

### Why Redactions Failed

Many DOJ documents use a flawed redaction method:
- Black boxes overlaid on text layer
- Underlying text NOT removed from PDF
- Copy/paste or programmatic extraction reveals content

This is a known issue in government document releases.
