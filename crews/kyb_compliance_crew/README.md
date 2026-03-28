# KYB Compliance Verification Crew

A CrewAI crew that performs Know Your Business (KYB) verification using [Strale](https://strale.dev) for company data lookup, VAT validation, and compliance screening.

## What it does

Three agents work sequentially to verify a business entity:

1. **Company Data Researcher** — Looks up official registry data and validates VAT numbers
2. **Compliance Screening Analyst** — Screens against sanctions lists, PEP databases, and adverse media
3. **KYB Report Writer** — Synthesizes findings into a structured verification report with risk assessment

## Capabilities used

This crew uses [crewai-strale](https://pypi.org/project/crewai-strale/) to access:

- **Company registry data** across 27 countries (Nordic, EU, US, UK, AU)
- **VAT validation** via EU VIES
- **Sanctions screening** against OFAC, EU, UN, UK OFSI (120+ sources)
- **PEP screening** — Politically Exposed Persons database
- **Adverse media** — news coverage screening across 235,000+ sources

## Setup

```bash
# Install dependencies
pip install crewai-strale

# Set your API keys
export STRALE_API_KEY=sk_live_...    # get at https://strale.dev/signup
export OPENAI_API_KEY=sk-...         # for the LLM
```

## Run

```bash
# Default: verifies Spotify AB (Swedish company)
python -m kyb_compliance_crew.main

# Or customize in main.py:
inputs = {
    "company_id": "08804411",        # UK company number
    "company_name": "Revolut Ltd",
    "country": "UK",
}
```

## Example output

```
KYB VERIFICATION REPORT
============================================================
Company: Spotify AB
Registration: 556703-7485 (Active)
Jurisdiction: Sweden
VAT: SE556703748501 (Valid)

Sanctions: CLEAR — no matches found
PEP: CLEAR — no matches found
Adverse Media: LOW RISK — 0 financial crime hits

Risk Assessment: LOW
Recommendation: APPROVE

Sources: Bolagsverket (SE), EU VIES, Dilisense AML
```

## How Strale tools work

`crewai-strale` exposes 250+ capabilities as CrewAI tools. The agents discover and call the right tools automatically based on their task descriptions. Each result includes a quality score (SQS) and data provenance.

Free capabilities (no API key needed): `iban-validate`, `email-validate`, `dns-lookup`, `json-repair`, `url-to-markdown`.
