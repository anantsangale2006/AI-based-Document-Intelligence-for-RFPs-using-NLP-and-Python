import re
from pathlib import Path
import streamlit as st
import fitz
from docx import Document

st.set_page_config(page_title="RFP Document Intelligence", page_icon="📄", layout="wide")

FIELD_PATTERNS = {
    "Project scope": [r"(?is)(?:scope of work|project scope|scope)\s*[:\-]?\s*(.{0,900}?)(?=\n\s*(?:eligibility|qualification|timeline|deadline|budget|submission|technical requirements|terms and conditions)\b|$)"],
    "Eligibility criteria": [r"(?is)(?:eligibility criteria|eligibility|qualification criteria|qualifications)\s*[:\-]?\s*(.{0,700}?)(?=\n\s*(?:scope|timeline|deadline|budget|submission|technical requirements)\b|$)"],
    "Deadline": [r"(?is)(?:submission deadline|proposal due date|due date|last date|deadline|closing date)\s*[:\-]?\s*([^\n.;]{3,160})"],
    "Budget": [r"(?is)(?:estimated budget|project budget|budget|contract value|cost estimate)\s*[:\-]?\s*([^\n.;]{2,160})"],
    "Technical requirements": [r"(?is)(?:technical requirements|technical specifications|technology requirements)\s*[:\-]?\s*(.{0,700}?)(?=\n\s*(?:eligibility|timeline|deadline|budget|submission|scope)\b|$)"],
    "Submission guidelines": [r"(?is)(?:submission guidelines|proposal submission|how to submit|submission requirements)\s*[:\-]?\s*(.{0,700}?)(?=\n\s*(?:eligibility|timeline|deadline|budget|technical requirements|scope)\b|$)"],
}
IMPORTANT_TERMS = [
    "request for proposal", "scope of work", "eligibility", "deadline", "budget",
    "technical requirements", "submission", "evaluation criteria", "payment terms",
    "deliverables", "experience", "warranty", "penalty", "emd", "tender fee",
]

def read_file(uploaded):
    name = uploaded.name.lower()
    data = uploaded.getvalue()
    if name.endswith(".pdf"):
        with fitz.open(stream=data, filetype="pdf") as doc:
            return "\n".join(page.get_text("text") for page in doc)
    if name.endswith(".docx"):
        import io
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace")
    raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, or MD.")

def extract_fields(text):
    results = {}
    for label, patterns in FIELD_PATTERNS.items():
        match_text = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                match_text = re.sub(r"\s+", " ", match.group(1)).strip(" \t:-")
                if match_text:
                    break
        results[label] = match_text or "Not clearly detected — review the document manually."
    return results

def summarize(text, max_sentences=6):
    # Lightweight extractive summary: ranks sentences by relevant terms and keeps document order.
    sentences = re.split(r"(?<=[.!?])\s+|\n+", re.sub(r"\s+", " ", text))
    sentences = [s.strip() for s in sentences if len(s.strip()) > 35]
    if not sentences:
        return "No readable text was found. If this is a scanned PDF, run OCR first."
    scored = []
    for i, sentence in enumerate(sentences):
        lower = sentence.lower()
        score = sum(2 if term in lower else 0 for term in IMPORTANT_TERMS)
        score += min(len(sentence) / 180, 1)
        if re.search(r"\b(date|days|rupees|inr|₹|must|shall|required|submit|eligible|budget|deadline)\b", lower):
            score += 1
        scored.append((score, i, sentence))
    chosen = sorted(sorted(scored, reverse=True)[:max_sentences], key=lambda x: x[1])
    return "\n".join(f"• {s}" for _, _, s in chosen)

st.title("📄 AI-Based Document Intelligence for RFPs")
st.caption("Upload an RFP to extract key information and create a review-ready summary.")
with st.sidebar:
    st.header("How to use")
    st.markdown("1. Upload a PDF, DOCX, TXT, or MD file.\n2. Review extracted fields.\n3. Verify every result against the original RFP before making a bid decision.")
    st.info("This prototype uses rules and extractive summarization. It does not replace human/legal review.")

uploaded = st.file_uploader("Upload RFP document", type=["pdf", "docx", "txt", "md"])
if uploaded:
    try:
        text = read_file(uploaded)
        if not text.strip():
            st.error("No text could be extracted. This may be a scanned PDF; OCR is not included in this prototype.")
        else:
            st.success(f"Read {len(text):,} characters from **{uploaded.name}**")
            tab1, tab2, tab3 = st.tabs(["Key information", "Summary", "Full extracted text"])
            with tab1:
                fields = extract_fields(text)
                for label, value in fields.items():
                    st.subheader(label)
                    st.write(value)
                st.download_button("Download extracted fields (TXT)",
                    "\n\n".join(f"{k}\n{v}" for k, v in fields.items()),
                    file_name="rfp_extracted_fields.txt", mime="text/plain")
            with tab2:
                summary = summarize(text)
                st.text(summary)
                st.download_button("Download summary", summary, file_name="rfp_summary.txt", mime="text/plain")
            with tab3:
                st.text_area("Extracted document text", text, height=500)
                st.download_button("Download extracted text", text, file_name="rfp_full_text.txt", mime="text/plain")
    except Exception as e:
        st.error(f"Could not process this file: {e}")
else:
    st.markdown("### What this model extracts")
    c1, c2, c3 = st.columns(3)
    c1.info("**Project scope**\n\nWork and deliverables")
    c2.info("**Eligibility**\n\nQualifications and criteria")
    c3.info("**Deadlines & budget**\n\nDates, costs, and submission notes")
    st.write("Supported formats: PDF, DOCX, TXT, and Markdown.")
