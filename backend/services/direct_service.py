import streamlit as st

from backend.services.resume_parser import parse_resume_file
from backend.services.resume_analyzer import analyze_full_resume


@st.cache_resource
def load_models():
    """Load AI/NLP models once and reuse them."""

    import spacy
    from sentence_transformers import SentenceTransformer
    from backend.core.config import (
        SPACY_MODEL_PRIMARY,
        SPACY_MODEL_SECONDARY,
        SENTENCE_TRANSFORMER_MODEL,
    )

    try:
        nlp = spacy.load(SPACY_MODEL_PRIMARY)
    except OSError:
        nlp = spacy.load(SPACY_MODEL_SECONDARY)

    embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)

    return nlp, embedder


def analyze_resume_direct(
    resume_file,
    job_description="",
):
    """Analyze resume directly without FastAPI."""

    # Load models
    nlp, embedder = load_models()

    # Read uploaded file
    file_bytes = resume_file.getvalue()
    filename = resume_file.name

    # Parse resume
    resume_text, metadata = parse_resume_file(
        file_bytes,
        filename,
    )

    # Run ATS analysis
    result = analyze_full_resume(
        resume_text=resume_text,
        nlp=nlp,
        embedder=embedder,
        job_description=job_description,
    )

    return result