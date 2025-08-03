"""
annex4review.py

CLI tool that fetches the latest Annex IV text from an authoritative source, normalises it
into a machine-readable YAML/JSON skeleton, validates user-supplied YAML specs against that
schema and (in the paid tier) renders a complete Annex IV PDF.

Key design goals
----------------
* **Always up-to-date** – every run pulls Annex IV from the EU AI Act website (HTML fallback)
  and fails if HTTP status ≠ 200.
* **No hidden SaaS** – default mode is local/freemium. Setting env `ANNEX4AC_LICENSE` or
  a `--license-key` flag unlocks PDF generation.
* **Plug-n-play in CI** – exit 1 when validation fails so a GitHub Action can block a PR.
* **Zero binaries** – no LaTeX, no system packages, no OPA binary: PDF and rule engine work via pure Python.

Dependencies (add these to requirements.txt or pyproject):
    requests, beautifulsoup4, PyYAML, typer[all], pydantic, Jinja2, reportlab

Usage examples
--------------
$ pip install annex4review  # once published on PyPI
$ annex4review review my_model.yaml                        # CI gate (free)
$ annex4review generate my_model.yaml --output my_annex.pdf  # Pro only

The code is intentionally compact; production users should add logging, retries and
exception handling as required.
"""
from pathlib import Path
from typing import List

import typer

# Import review functions from the review module
from .review import (
    extract_text_from_pdf,
    analyze_documents
)

# Add PDF processing imports for review command
try:
    import PyPDF2
    PDF2_AVAILABLE = True
except ImportError:
    PDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

app = typer.Typer(
    add_completion=False,
    help="Review EU AI Act Annex IV technical documentation. \n\n ⚠️  LEGAL DISCLAIMER: This software is provided for informational and compliance assistance purposes only. It is not legal advice and should not be relied upon as such. Users are responsible for ensuring their documentation meets all applicable legal requirements and should consult with qualified legal professionals for compliance matters. The authors disclaim any liability for damages arising from the use of this software.\n\n🔒 DATA PROTECTION: All processing occurs locally on your machine. No data leaves your system."
)
@app.command()
def review(
    files: List[Path] = typer.Argument(..., exists=True, readable=True, help="One or more PDF files of technical documentation")
):
    """
    Perform an automatic compliance review of technical documentation PDFs (Annex IV & GDPR).
    
    Analyzes PDF files for:
    - Missing required Annex IV sections
    - Compliance keyword coverage (risk, data protection, transparency, etc.)
    - Contradictions between multiple documents
    - Potential compliance issues
    
    ⚠️  This is an automated analysis tool. Results should be reviewed by qualified legal professionals.
    """
    # Check if PDF processing libraries are available
    if not PDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE and not PYMUPDF_AVAILABLE:
        typer.secho("ERROR: No PDF processing library available. Install PyPDF2, pdfplumber, or fitz:", fg=typer.colors.RED, err=True)
        typer.secho("  pip install PyPDF2", fg=typer.colors.YELLOW)
        typer.secho("  or", fg=typer.colors.YELLOW)
        typer.secho("  pip install pdfplumber", fg=typer.colors.YELLOW)
        typer.secho("  or", fg=typer.colors.YELLOW)
        typer.secho("  pip install PyMuPDF", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    
    typer.secho(f"Analyzing {len(files)} PDF file(s)...", fg=typer.colors.BLUE)
    
    # 1. Extract text from PDF files
    docs_texts = []
    for file in files:
        try:
            typer.secho(f"Processing {file.name}...", fg=typer.colors.BLUE)
            text = extract_text_from_pdf(file)
            docs_texts.append((file.name, text))
            typer.secho(f"  ✓ Extracted {len(text)} characters", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"  ✗ Failed to process {file.name}: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
    
    # 2. Analyze documents for issues
    typer.secho("Analyzing documents for compliance issues...", fg=typer.colors.BLUE)
    issues = analyze_documents(docs_texts)
    
    # 3. Output results
    typer.secho("\n" + "="*60, fg=typer.colors.BLUE)
    typer.secho("COMPLIANCE REVIEW RESULTS", fg=typer.colors.BLUE)
    typer.secho("="*60, fg=typer.colors.BLUE)
    
    if not issues:
        typer.secho("✅ No obvious contradictions or compliance issues found.", fg=typer.colors.GREEN)
        typer.secho("\nNote: This automated analysis is not a substitute for legal review.", fg=typer.colors.YELLOW)
        typer.secho("Consult qualified legal professionals for compliance matters.", fg=typer.colors.YELLOW)
    else:
        # Group issues by type
        errors = [issue for issue in issues if issue["type"] == "error"]
        warnings = [issue for issue in issues if issue["type"] == "warning"]
        
        # Display errors first
        if errors:
            typer.secho(f"\n❌ ERRORS ({len(errors)}):", fg=typer.colors.RED)
            for i, issue in enumerate(errors, 1):
                file_info = f" [{issue['file']}]" if issue['file'] else ""
                section_info = f" (Section {issue['section']})" if issue['section'] else ""
                typer.secho(f"  {i}.{file_info}{section_info} {issue['message']}", fg=typer.colors.RED)
        
        # Display warnings
        if warnings:
            typer.secho(f"\n⚠️  WARNINGS ({len(warnings)}):", fg=typer.colors.YELLOW)
            for i, issue in enumerate(warnings, 1):
                file_info = f" [{issue['file']}]" if issue['file'] else ""
                section_info = f" (Section {issue['section']})" if issue['section'] else ""
                typer.secho(f"  {i}.{file_info}{section_info} {issue['message']}", fg=typer.colors.YELLOW)
        
        typer.secho(f"\nFound {len(issues)} total issue(s): {len(errors)} errors, {len(warnings)} warnings", fg=typer.colors.YELLOW)
        typer.secho("\nNote: This automated analysis is not a substitute for legal review.", fg=typer.colors.YELLOW)
        typer.secho("Consult qualified legal professionals for compliance matters.", fg=typer.colors.YELLOW)

if __name__ == "__main__":
    app()
