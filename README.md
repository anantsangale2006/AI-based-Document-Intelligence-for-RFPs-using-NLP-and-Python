# AI-Based Document Intelligence for RFPs using NLP and Python

A runnable prototype that reads RFP documents, extracts likely key sections (scope, eligibility, deadline, budget, technical requirements, submission guidelines), and generates a lightweight extractive summary.

## Run on Windows (VS Code / PowerShell)

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. In the terminal, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt activation instead:
   `\.venv\Scripts\activate.bat`

4. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

6. Open the local URL shown in the terminal (usually http://localhost:8501).

## Features
- Upload PDF, DOCX, TXT, or MD.
- Extract key RFP fields with configurable regular-expression rules.
- Produce a simple extractive summary.
- Download extracted fields, summary, and full extracted text.

## Important limitations
- This is a functional baseline/prototype, not a trained AI model.
- Scanned PDFs require OCR, which is not included.
- RFP layouts vary. Extraction results are best-effort and must be checked against the original document.
- The summary is extractive and rule-based, not a generative paraphrase.
