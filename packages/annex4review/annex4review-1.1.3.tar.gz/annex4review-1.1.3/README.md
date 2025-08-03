# Annex IV Review (annex4ac)

Анализ PDF документов на соответствие требованиям EU AI Act Annex IV и GDPR.

> **⚠️ Legal Disclaimer:** This software is provided for informational and compliance assistance purposes only. It is not legal advice and should not be relied upon as such. Users are responsible for ensuring their documentation meets all applicable legal requirements and should consult with qualified legal professionals for compliance matters. The authors disclaim any liability for damages arising from the use of this software.

> **🔒 Data Protection:** All processing occurs locally on your machine. No data leaves your system.

---

## 🚀 Quick‑start

```bash
# 1 Install (Python 3.9)
pip install annex4ac

# 2 Review single PDF document
from annex4ac import review_single_document
from pathlib import Path

issues = review_single_document(Path("technical_documentation.pdf"))
for issue in issues:
    print(f"{issue['type']}: {issue['message']}")

# 3 Review multiple PDF documents
from annex4ac import review_documents

issues = review_documents([
    Path("doc1.pdf"), 
    Path("doc2.pdf")
])

# 4 Analyze text content directly
from annex4ac import analyze_text

issues = analyze_text("AI system content...", "document.txt")
```

---

## ✨ Features

### Advanced NLP Analysis
- **Intelligent negation detection**: Uses spaCy and negspaCy for accurate analysis
- **Contradiction detection**: Finds inconsistencies within and between documents
- **Section validation**: Checks all 9 required Annex IV sections
- **GDPR compliance**: Analyzes data protection and privacy issues

### Compliance Checks
- **Missing sections**: Identifies absent Annex IV sections (1-9)
- **High-risk classification**: Detects high-risk use cases without proper labeling
- **Data protection**: Checks GDPR compliance requirements
- **Transparency**: Verifies explainability and bias detection mentions

### Multiple Input Formats
- **PDF files**: Supports PyPDF2, pdfplumber, and PyMuPDF
- **Text content**: Direct text analysis
- **Batch processing**: Review multiple documents simultaneously

---

## 📋 API Reference

### Core Functions

#### `review_documents(pdf_files: List[Path], batch_size: int = 128) -> List[dict]`
Review multiple PDF documents for compliance issues.

**Parameters:**
- `pdf_files`: List of Path objects pointing to PDF files
- `batch_size`: Number of pages to process in each batch (default: 128)

**Returns:**
List of structured issue dictionaries with keys: `type`, `section`, `file`, `message`

#### `review_single_document(pdf_file: Path) -> List[dict]`
Review a single PDF document for compliance issues.

#### `analyze_text(text: str, filename: str = "document") -> List[dict]`
Analyze text content for compliance issues.

#### `extract_text_from_pdf(pdf_path: Path) -> str`
Extract text from PDF file using available libraries.

### HTTP API Support

#### `handle_multipart_review_request(headers: dict, body: bytes) -> dict`
Handle multipart/form-data request for document review.

#### `handle_text_review_request(text_content: str, filename: str = "document.txt") -> dict`
Handle text review request.

#### `create_review_response(issues: List[dict], processed_files: List[str]) -> dict`
Create structured response for review results.

---

## 🔍 Issue Types

### Errors (Critical Issues)
- Missing required Annex IV sections
- Contradictions between documents
- High-risk use cases without proper classification
- GDPR violations (indefinite data retention, missing legal basis)

### Warnings (Recommendations)
- Missing transparency or explainability mentions
- No bias detection or fairness measures
- Missing security or robustness measures
- Only negative mentions of compliance terms

---

## 📊 Example Output

```
============================================================
COMPLIANCE REVIEW RESULTS
============================================================

❌ ERRORS (2):
  1. [doc1.pdf] (Section 1) Missing content for Annex IV section 1 (system overview).
  2. [doc2.pdf] (Section 5) No mention of risk management procedures.

⚠️  WARNINGS (1):
  1. [doc1.pdf] No mention of transparency or explainability.

Found 3 total issue(s): 2 errors, 1 warnings
```

---

## 🛠 Requirements

- Python 3.9
- **PDF Processing**: PyPDF2, pdfplumber, or PyMuPDF
- **NLP Analysis**: spaCy, negspaCy, nltk

---

## 📚 References

* Annex IV HTML – [https://artificialintelligenceact.eu/annex/4/](https://artificialintelligenceact.eu/annex/4/)
* EU AI Act – [https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689)

---

## 📄 Licensing

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The software assists in preparing documentation, but does not confirm compliance with legal requirements or standards. The user is responsible for the final accuracy and compliance of the documents.
