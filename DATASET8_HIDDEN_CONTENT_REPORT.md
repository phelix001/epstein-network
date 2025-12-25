# DataSet 8 Hidden/Redacted Content Extraction Report
## Generated: December 25, 2025

## Executive Summary

Scanned **10,593 PDF files** (10GB) from DOJ DataSet 8 for improperly redacted content.
Found **9,972 files** (94%) with extractable text content that may have been intended to be redacted.

### Key Statistics
- **936 unique email addresses** extracted
- **23,383 unique names** identified
- **Personal email accounts** of key figures discovered
- **Sex Offender Registry data** fully extractable

---

## Critical Findings

### 1. Ghislaine Maxwell's Personal Emails

**Email addresses found:**
- `gmax1@mindspring.com` (4 documents)
- `gmaxl@mindspring.com` (5 documents)

**Key document:** EFTA00011438 - Email chain from February 2002 discussing:
- Trip to Peru with "The Invisible Man" (aace@dial.pipex.com)
- Arranging activities including horseback riding and Nazca Lines trip
- **Disturbing quote:** "About the girls... how old is he?"
- Contact: Juanesteban Ganoza (jganoza@terra.com.pe) in Peru arranging "girls"

### 2. Jeffrey Epstein's Complete Digital Footprint

**From Sex Offender Registry (EFTA00037421):**

**Email Addresses:**
- JEEITUNES6GMAIL.COM
- LITTLESTJEFF@YAHOO.COM (Little St James reference)
- JEFFREYEPSTEIN@LIVE.COM
- JEFFREYOJEFFREYEPSTEIN.ORG
- COLUMBIADENTAL1gYAHOO.COM
- JEFFREYEPSTEINORGQYAHOO.COM
- JEEVACATION1@ME.COM
- JEFFREYEPSTEINORG@GMAIL.COM
- JEEPROJECTGYAHOO.COM
- JEEVACATIONOME.COM
- JEEVACATION@GMAIL.COM

**Social Media/Messaging:**
- SIGNAL
- TELEGRAM
- WHATSAPP
- CONFIDE (encrypted messaging)
- SKYPE
- TWITTER (@JEFFREY_EPSTEIN, @JEFFREYEPSTEIN1, @JEFFREYEPSTEINI)
- INSTAGRAM (JEEPROJECT)
- FACETIME

**Conviction Details Exposed:**
- Victims: Female 14 years, Female 16 years, Female Unknown
- Offenses: Sexual Intercourse (More Than Once), Deviate Sexual Intercourse (More Than Once), Sexual Contact (More Than Once)

**Vehicles (with license plates):**
- Multiple Chevrolet Suburbans (FL, NY, NM, VI)
- Bentley Mulsanne (NY: HSU5212)
- Range Rover (NM: MLO718)
- Hummer H2 (NM: CPK643)
- Aircraft: N722JE, N212JE, N120JE, N331JE

### 3. Key Individuals' Personal Emails

| Email | Identity | Notes |
|-------|----------|-------|
| StanPottinger@aol.com | Stan Pottinger | Known Epstein associate |
| Lindsay165@aol.com | Unknown | Personal contact |
| elissapsydd@aol.com | Elissa | Potential contact |
| dondubesq@aol.com | Attorney | 3 documents |
| kinilofsky@aol.com | Milofsky | Contact |
| owlmgw@att.net | Unknown | 7 documents |

### 4. Attorney/Legal Team Emails

**Maxwell Defense Team:**
- lmenninger@hmflaw.com (Laura Menninger) - 45+ occurrences
- jpagliuca@hmflaw.com (Jeff Pagliuca) - 37 occurrences
- ceverdell@cohengresser.com (Christian Everdell) - 57 occurrences
- bcsternheim@mac.com (Bobbi Sternheim) - 76 occurrences

**Victims' Attorneys:**
- brad@epllc.com (Brad Edwards)
- smccawley@bsfllp.com (Sigrid McCawley)
- cassellp@law.utah.edu (Paul Cassell)

### 5. Government/Prosecution Emails

- AAcosta@usa.doj.gov (Alexander Acosta)
- USANYS.EpsteinVictims@usa.doj.gov
- victimservices@fbi.gov
- USANYS-CRIMINALAUSAS@usa.doj.gov

---

## Names Found by Category

### Core Figures
- Jeffrey Epstein: 1,371 mentions
- Mark Epstein: 51 mentions

### Accomplices
- Ghislaine Maxwell: 1,133 mentions
- Isabel Maxwell: 16 mentions

### Political Figures
- Prince Andrew: 81 mentions
- Donald Trump: 26 mentions
- Bill Clinton: 17 mentions
- Joe Biden: 19 mentions

### Attorneys (295+ documents)
- Christian Everdell
- Laura Menninger
- Jeff/Jeffrey Pagliuca
- Gloria Allred
- Jack Scarola
- Roberta Kaplan
- David Boies
- Sigrid McCawley
- Brad Edwards
- Jay Lefkowitz (26 mentions)
- Martin Weinberg (39 mentions)
- Reid Weingarten (39 mentions)

### Potential Victim-Related
- Jane Doe: 23 mentions
- Jennifer Richardson: 11 mentions
- Nicole Simmons: 26 mentions

---

## Document Types with Hidden Content

1. **Email chains** (improper redaction of sender/recipient)
2. **Sex Offender Registry records** (full data extractable)
3. **Prison/MCC records** (159 "Suicide Watch" mentions)
4. **Legal correspondence** (attorney communications)
5. **Flight records** (N-number aircraft references)
6. **Financial documents** (Deutsche Bank: 42 mentions)

---

## Files Generated

1. `dataset8_redacted_scan.json` - Complete extraction results (JSON)
2. `dataset8_all_names.csv` - All names with counts and source files
3. `dataset8_emails.csv` - All email addresses extracted
4. `dataset8_potential_victims.csv` - Names flagged in victim contexts

---

## Methodology

Used pdfplumber to extract text layer from PDFs. Many documents appear to have "redaction" applied as a visual overlay (black box) without removing the underlying text, allowing copy/paste extraction of "hidden" content.

## Key Source Documents

| Document ID | Content |
|-------------|---------|
| EFTA00011438 | Maxwell email about arranging "girls" in Peru |
| EFTA00037421-37425 | Epstein Sex Offender Registry (5 pages) |
| EFTA00022960 | Stan Pottinger correspondence |
| EFTA00014192 | Lindsay165@aol.com contact |

---

## Conclusion

The DOJ DataSet 8 contains thousands of documents with improperly redacted content. Text that appears visually redacted can be extracted via copy/paste or programmatic text extraction. This includes:

- Personal email addresses of key figures
- Complete Sex Offender Registry data
- Communications discussing procurement of minors
- Government official contact information
- Attorney-client communications
