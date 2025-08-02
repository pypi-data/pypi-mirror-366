# Annex IV‑as‑Code (annex4ac)
Project code and files located at https://github.com/ai-act-cli/annex4ac

Generate and validate EU AI Act Annex IV technical documentation straight from your CI. 

100% local by default.

SaaS/PDF unlocks with a licence key .

> **⚠️ Legal Disclaimer:** This software is provided for informational and compliance assistance purposes only. It is not legal advice and should not be relied upon as such. Users are responsible for ensuring their documentation meets all applicable legal requirements and should consult with qualified legal professionals for compliance matters. The authors disclaim any liability for damages arising from the use of this software.

> **🔒 Data Protection:** All processing occurs locally on your machine. No data leaves your system.

---

## 🚀 Quick‑start

```bash
# 1 Install (Python 3.9+)
pip install annex4ac

# 2 Pull the latest Annex IV layout
annex4ac fetch-schema annex_template.yaml

# 3 Fill in the YAML → validate
cp annex_template.yaml my_annex.yaml
$EDITOR my_annex.yaml
annex4ac validate my_annex.yaml   # "Validation OK!" or exit 1

# Optional: Check if document is stale (heuristic, not legal requirement)
annex4ac validate my_annex.yaml --stale-after 30  # Warn if older than 30 days
annex4ac validate my_annex.yaml --stale-after 180 --strict-age  # Fail CI if older than 180 days

# 4 Generate output (PDF requires license)
# HTML (free) - automatically validates before generation
annex4ac generate my_annex.yaml --output annex_iv.html --fmt html

# DOCX (free) - automatically validates before generation
annex4ac generate my_annex.yaml --output annex_iv.docx --fmt docx

# PDF (Pro - requires license) - automatically validates before generation
export ANNEX4AC_LICENSE="your_jwt_token_here"
annex4ac generate my_annex.yaml --output annex_iv.pdf --fmt pdf

# Skip validation if needed (not recommended)
annex4ac generate my_annex.yaml --output annex_iv.pdf --fmt pdf --skip-validation
```

> **License System:** Pro features require a JWT license token. Contact support to obtain your token, then set it as the `ANNEX4AC_LICENSE` environment variable. See [LICENSE_SYSTEM.md](LICENSE_SYSTEM.md) for details.

> **Hint :** You only need to edit the YAML once per model version—CI keeps it green.

---

## ✨ Features

* **Always up‑to‑date** – every run pulls the latest Annex IV HTML from the official AI Act Explorer.
* **Schema‑first** – YAML scaffold mirrors the **9 numbered sections** adopted in the July 2024 Official Journal.
* **Fail‑fast CI** – `annex4ac validate` exits 1 when a mandatory field is missing, so a GitHub Action can block the PR.
* **Zero binaries** – ReportLab renders the PDF; no LaTeX, no system packages.
* **Freemium** – `fetch-schema` & `validate` are free; `generate` (PDF) requires `ANNEX4AC_LICENSE`.
* **Built-in rule engine** – business-logic validation runs locally via pure Python.
* **EU-compliant formatting** – proper list punctuation (semicolons and periods) and ordered list formatting (a), (b), (c) according to EU drafting rules.
* **Retention tracking** – automatic 10-year retention period calculation and metadata embedding (Article 18 compliance).
* **Freshness validation** – configurable document staleness (not a legal requirement, but techdoc must be kept up-to-date according to Art. 11).
* **PDF/A-2b support** – optional archival PDF format with embedded ICC profiles for long-term preservation.
* **Unified text processing** – consistent handling of escaped characters and list formatting across all formats (PDF/HTML/DOCX).
* **Auto-validation** – `annex4ac generate` automatically validates YAML before generation, ensuring compliance.
* **Compliance review** – `annex4ac review` analyzes PDF technical documentation for missing sections, contradictions, and compliance issues.

---

## 🛠 Requirements

- Python 3.9+
- [reportlab](https://www.reportlab.com/documentation) (PDF, Pro)
- [pydantic](https://docs.pydantic.dev) (schema validation)
- [typer](https://typer.tiangolo.com) (CLI)
- [pyyaml](https://pyyaml.org/) (YAML)

---

## 🗂 Required YAML fields (June 2024 format)

| Key                      | Annex IV § |
| ------------------------ | ---------- |
| `risk_level`             | —          | "high", "limited", "minimal" — determines required sections |
| `use_cases`              | —          | List of tags (Annex III) for auto high-risk. Acceptable values: employment_screening, biometric_id, critical_infrastructure, education_scoring, justice_decision, migration_control |
| `system_overview`        |  1         |
| `development_process`    |  2         |
| `system_monitoring`      |  3         |
| `performance_metrics`    |  4         |
| `risk_management`        |  5         |
| `changes_and_versions`   |  6         |
| `standards_applied`      |  7         |
| `compliance_declaration` |  8         |
| `post_market_plan`       |  9         |
| `enterprise_size`        | —          | `"sme"`, `"mid"`, `"large"` – enterprise size classification (Art. 11 exemption). |
| `placed_on_market`       | —          | ISO datetime when the AI system was placed on market (required for retention calculation). |
| `last_updated`           | —          | ISO datetime of last documentation update (for optional freshness heuristic). |

---

## 🛠 Commands

| Command        | What it does                                                                  |
| -------------- | ----------------------------------------------------------------------------- |
| `fetch-schema` | Download the current Annex IV HTML, convert to YAML scaffold `annex_schema.yaml`. |
| `validate`     | Validate your YAML against the Pydantic schema and built-in Python rules. Exits 1 on error. Supports `--sarif` for GitHub annotations, `--stale-after` for optional freshness heuristic, and `--strict-age` for strict age checking.             |
| `generate`     | Render PDF (Pro), HTML, or DOCX from YAML. Automatically validates before generation. PDF requires license, HTML/DOCX are free. |
| `review`       | Analyze PDF technical documentation for compliance issues, missing sections, and contradictions between documents. Returns structured output with errors and warnings. |

Run `annex4ac --help` for full CLI.

---

## 🆕 New Features

### Enhanced Schema Generation
The `fetch-schema` command now generates a more comprehensive YAML template with:
- **All mandatory fields** included with proper defaults
- **Clear descriptions** for each field with examples
- **Use cases from Annex III** with full list of available tags
- **Better formatting** with proper spacing and alignment
- **Helpful comments** explaining what each field means and how to fill it

### EU-Compliant List Formatting
Lists are automatically formatted according to EU drafting rules:
- Ordered lists: `(a) ...; (b) ...; (c) ...`
- Unordered lists: `• ...; • ...; • ...`
- **Hierarchical lists**: Support for nested structure with `(a)` + `-` subitems
- Proper punctuation with semicolons and final periods
- **Cross-format consistency**: Same list structure in PDF, HTML, and DOCX

### Retention and Freshness Tracking
- **10-year retention**: Automatic calculation and metadata embedding according to Article 18(1)
- **Freshness heuristic**: `--stale-after N` (optional, disabled by default) or `--strict-age` for CI enforcement
- **Environment variable**: Set `ANNEX4AC_STALE_AFTER=180` to enable stale-after by default
- **Legal compliance**: Meets Article 18 (retention) requirements; freshness is a maintenance heuristic, not a legal requirement
- **Legal accuracy**: Retention period calculated from `placed_on_market` date

### Unified Text Processing
All formats (PDF/HTML/DOCX) now use consistent text processing:
- Automatic handling of escaped characters (`\\n` → `\n`)
- Proper list detection and formatting
- YAML flow scalar restoration
- EU-compliant punctuation

### PDF/A-2b Archival Support
Enable archival PDF generation with:

```bash
# Generate PDF/A-2b for long-term preservation
annex4ac generate my_annex.yaml --fmt pdf --pdfa

# PDF/A-2b includes:
# - Embedded sRGB ICC profile
# - XMP metadata
# - ISO 19005-2:2011 compliance
# - 10-year retention metadata
```

**Legal compliance**: PDF/A-2b format ensures documents remain accessible and visually identical for decades, meeting archival requirements under Article 18 of Regulation 2024/1689.

### Automatic Compliance Review
The new `review` command analyzes PDF technical documentation for compliance issues:

```bash
# Review single PDF file
annex4ac review technical_doc.pdf

# Review multiple PDF files for contradictions
annex4ac review doc1.pdf doc2.pdf doc3.pdf
```

**Features:**
- **Annex IV section validation**: Checks for all 9 required sections with specific section numbers
- **High-risk system detection**: Identifies biometric/law enforcement systems not properly labeled as high-risk
- **GDPR compliance analysis**: Detects indefinite data retention, missing consent/lawful basis, and missing data subject rights
- **Contradiction detection**: Finds internal contradictions and cross-document inconsistencies
- **Comprehensive compliance checks**: Analyzes transparency, bias detection, and security measures
- **Cross-document analysis**: Compares system names, versions, and risk assessments across multiple documents
- **PDF text extraction**: Supports PyPDF2, pdfplumber, and PyMuPDF for robust text extraction
- **Legal disclaimer**: Includes appropriate disclaimers about automated analysis

### Structured Response Format
The review functionality now returns structured data with:
- **Error/Warning classification**: Issues are categorized by severity
- **Section mapping**: Missing Annex IV sections are tagged with specific section numbers
- **Cross-document analysis**: Contradictions between documents are identified
- **JSON API support**: Structured responses for integration with web applications

### List Formatting Examples

#### Hierarchical Lists (EU-Compliant)
```yaml
development_process: |
  (a) Requirements analysis phase (3 months):
      - Stakeholder interviews and requirements gathering
      - Technical feasibility assessment
      - Risk analysis and compliance review
  
  (b) Design and architecture phase (4 months):
      - System architecture design
      - Data flow and security design
      - Integration planning
```

#### Regular Bulleted Lists
```yaml
standards_applied: |
  Compliance with international standards:
  
  - ISO 27001: Information security management
  - IEEE 2857: AI system development guidelines
  - GDPR: Data protection and privacy
  - ISO 9001: Quality management systems
  - Internal AI ethics guidelines and policies
```

Both formats are supported across all output formats (PDF, HTML, DOCX) with consistent rendering.

### API Functions for HTTP Requests

The package provides API functions for handling HTTP requests:

```python
from annex4ac.review import (
    handle_multipart_review_request,
    handle_text_review_request,
    create_review_response
)

# Handle multipart/form-data request
headers = {'Content-Type': 'multipart/form-data; boundary=...'}
body = b'...'  # multipart form data
result = handle_multipart_review_request(headers, body)

# Handle text review request
result = handle_text_review_request("AI system text content", "document.txt")

# Create structured response
response = create_review_response(issues)
```

**Structured Response Format:**
```json
{
  "success": true,
  "processed_files": ["doc1.pdf", "doc2.pdf"],
  "total_files": 2,
  "issues": [
    {
      "type": "error",
      "section": "1",
      "file": "doc1.pdf",
      "message": "Missing content for Annex IV section 1 (system overview)."
    },
    {
      "type": "warning",
      "section": null,
      "file": "doc1.pdf",
      "message": "No mention of transparency or explainability."
    }
  ],
  "summary": {
    "total_issues": 2,
    "errors": 1,
    "warnings": 1
  }
}
```

**Issue Types:**
- `"error"`: Critical issues (missing required sections, contradictions, GDPR violations)
- `"warning"`: Potential issues (missing transparency, bias detection, etc.)

**Section Numbers:**
- `"1"` to `"9"`: Annex IV section numbers
- `null`: Issues not tied to specific sections

### Using Review Functions as a Library

The review functionality can also be used programmatically as a library:

```python
from pathlib import Path
from annex4ac.review import review_documents, analyze_text

# Review multiple PDF files
pdf_files = [Path("doc1.pdf"), Path("doc2.pdf")]
issues = review_documents(pdf_files)
for issue in issues:
    print(f"{issue['type'].upper()}: {issue['message']}")

# Analyze text content directly
text_content = "This AI system processes personal data..."
issues = analyze_text(text_content, "my_document.txt")
for issue in issues:
    print(f"{issue['type'].upper()}: {issue['message']}")
```

**Available Library Functions:**
- `review_documents(pdf_files: List[Path]) -> List[dict]` - Review multiple PDF files
- `review_single_document(pdf_file: Path) -> List[dict]` - Review a single PDF file
- `analyze_text(text: str, filename: str = "document") -> List[dict]` - Analyze text content
- `extract_text_from_pdf(pdf_path: Path) -> str` - Extract text from PDF (low-level)

**Structured Issue Format:**
Each issue is a dictionary with:
- `type`: "error" or "warning"
- `section`: "1"-"9" for Annex IV sections, `null` for general issues
- `file`: filename or `""` for cross-document issues
- `message`: description of the issue

**Error Handling:**
```python
try:
    issues = review_documents([Path("document.pdf")])
except ImportError:
    print("Install PDF libraries: pip install PyPDF2 pdfplumber PyMuPDF")
except Exception as e:
    print(f"Error: {e}")
```

See `examples/review_example.py` for complete usage examples.

---

## 🏷️ High-risk tags (Annex III)

The list of high-risk tags (Annex III) is now loaded dynamically from the official website. If the network is unavailable, a cache or fallback list is used. This affects the auto_high_risk logic in validation.

---

## 🏷️ Schema version in PDF

Each PDF now displays the Annex IV schema version stamp (e.g., v20240613) and the document generation date.

---

## 🔑 Pro-licence & JWT

To generate PDF in Pro mode, a license is required (JWT, RSA signature). The ANNEX4AC_LICENSE key can be checked offline, the public key is stored in the package. See [LICENSE_SYSTEM.md](LICENSE_SYSTEM.md) for detailed information about the license system.

---

## 🛡️ Rule-based validation (Python)

- **High-risk systems**: All 9 sections of Annex IV are mandatory (Art. 11 §1).
- **Limited/minimal risk**: Annex IV is optional but recommended for transparency (Art. 52).
- For high-risk (`risk_level: high`), post_market_plan is required.
- If use_cases contains a high-risk tag (Annex III), risk_level must be high (auto high-risk).
- SARIF report now supports coordinates (line/col) for integration with GitHub Code Scanning.
- **Auto-detection**: Systems with Annex III use_cases are automatically classified as high-risk.

---

## 🐙 GitHub Action example

```yaml
name: Annex IV gate
on: [pull_request]

jobs:
  ai-act-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install annex4ac
      - run: annex4ac validate model.yaml
```

Add `ANNEX4AC_LICENSE` as a secret to use PDF export in CI.

---

## 📄 Offline cache

If Annex IV is temporarily unavailable online, use:

```bash
annex4ac fetch-schema --offline
```

This will load the last saved schema from `~/.cache/annex4ac/` (the cache is updated automatically every 14 days).

---

## ⚙️ Local development

```bash
git clone https://github.com/your‑org/annex4ac
cd annex4ac
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                     # unit tests
python annex4ac.py --help
```

---

## 🔑 Licensing & pricing

| Tier       | Price           | Features                                                     |
| ---------- | --------------- | ------------------------------------------------------------ |
| Community  | **Free**        | `fetch-schema`, `validate`, unlimited public repos           |
| Pro        | **€15 / month** | PDF generation, version history (future SaaS), email support |
| Enterprise | Custom          | Self‑hosted Docker, SLA 99.9 %, custom sections              |

Pay once, use anywhere – CLI, GitHub Action, future REST API.

---

## 📚 References

* Annex IV HTML – [https://artificialintelligenceact.eu/annex/4/](https://artificialintelligenceact.eu/annex/4/)
* Official Journal PDF – [https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689)
* ReportLab docs – [https://www.reportlab.com/documentation](https://www.reportlab.com/documentation)
* Typer docs – [https://typer.tiangolo.com](https://typer.tiangolo.com)
* Pydantic docs – [https://docs.pydantic.dev](https://docs.pydantic.dev)
* PDF/A Standard – [ISO 19005-2:2011](https://www.iso.org/standard/50655.html)
* sRGB Color Space – [IEC 61966-2-1:1999](https://webstore.iec.ch/publication/6169)

---

## 📄 Licensing

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-party Components

* **PyJWT** - MIT License
* **ReportLab** - BSD-style License  
* **Typer** - MIT License
* **Liberation Sans Fonts** - SIL Open Font License 1.1 (included in `fonts/` directory)

The Liberation Sans fonts are used for PDF generation and are licensed under the SIL Open Font License 1.1. See the [LICENSE](LICENSE) file for the complete license text. 

The software assists in preparing documentation, but does not confirm compliance with legal requirements or standards. The user is responsible for the final accuracy and compliance of the documents.
