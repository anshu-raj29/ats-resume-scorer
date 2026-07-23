from typing import Optional

import streamlit as st

from frontend.services import direct_service
from frontend.components.dashboard import display_results_dashboard


def _read_jd(jd_file, jd_text: str) -> str:
    """Convert the provided job description into plain text."""

    if jd_text:
        return jd_text.strip()

    if jd_file is None:
        return ""

    if jd_file.name.lower().endswith(".txt"):
        return jd_file.getvalue().decode(
            "utf-8",
            errors="ignore"
        )

    st.warning(
        "Job description files must be `.txt` for now. "
        "Paste the JD text instead for PDF or DOCX files."
    )

    return ""


def _summary_text(analysis: dict) -> str:
    """Generate text summary."""

    score = analysis.get(
        "ATS_score",
        analysis.get("ats_score", 0)
    )

    lines = [
        f"ATS Score: {score:.0f}/100",
        ""
    ]

    if analysis.get("strengths"):

        lines.append("STRENGTHS:")

        lines.extend(
            f"  - {s}"
            for s in analysis["strengths"]
        )

        lines.append("")

    if analysis.get("critical_issues"):

        lines.append("CRITICAL ISSUES:")

        lines.extend(
            f"  - {s}"
            for s in analysis["critical_issues"]
        )

        lines.append("")

    if analysis.get("suggestions"):

        lines.append("SUGGESTIONS:")

        lines.extend(
            f"  - {s}"
            for s in analysis["suggestions"]
        )

    return "\n".join(lines)


def _render_upload_area(analysis_mode: str):

    left, right = st.columns(2)

    with left:

        st.markdown("### 📄 Upload Resume")

        resume_file = st.file_uploader(
            "Choose your resume file",
            type=["pdf", "doc", "docx"],
            help="Supported: PDF, DOC, DOCX (max 5 MB)",
            key="resume_upload",
        )

        if resume_file:

            st.success(
                f"✅ {resume_file.name} "
                f"({resume_file.size / 1024:.1f} KB)"
            )

    jd_file: Optional[object] = None

    jd_text = ""

    with right:

        if analysis_mode == "Job Description Comparison":

            st.markdown("### 📋 Job Description")

            jd_method = st.radio(
                "Input method:",
                [
                    "Paste Text",
                    "Upload .txt File"
                ],
                horizontal=True,
                key="jd_input_method",
            )

            if jd_method == "Upload .txt File":

                jd_file = st.file_uploader(
                    "Choose JD file (.txt only)",
                    type=["txt"],
                    key="jd_upload",
                )

                if jd_file:
                    st.success(
                        f"✅ {jd_file.name}"
                    )

            else:

                jd_text = st.text_area(
                    "Paste job description text:",
                    height=200,
                    placeholder="Paste the JD here...",
                    key="jd_text",
                )

                if jd_text:

                    st.success(
                        f"✅ {len(jd_text)} characters"
                    )

        else:

            st.markdown(
                "### 📋 Job Description"
            )

            st.info(
                "Switch to 'Job Description Comparison' "
                "mode to enable JD matching."
            )

    return resume_file, jd_file, jd_text


def _generate_pdf_direct(analysis: dict):

    from backend.services.report_generator import (
        generate_html_reports
    )

    from backend.services.pdf_export import (
        generate_combined_pdf
    )

    html_docs = generate_html_reports(
        analysis
    )

    pdf_bytes = generate_combined_pdf(
        html_docs
    )

    return pdf_bytes


def _render_export_buttons(
    analysis: dict
):

    st.markdown(
        "### 📥 Export Results"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📑 Generate PDF Report",
            use_container_width=True,
            type="primary"
        ):

            try:

                with st.spinner(
                    "Generating PDF..."
                ):

                    pdf_bytes = (
                        _generate_pdf_direct(
                            analysis
                        )
                    )

                st.session_state[
                    "scorer_pdf_bytes"
                ] = pdf_bytes

            except Exception as exc:

                st.error(
                    f"Could not generate PDF: {exc}"
                )

        if (
            "scorer_pdf_bytes"
            in st.session_state
        ):

            st.download_button(
                "⬇️ Download PDF",
                data=st.session_state[
                    "scorer_pdf_bytes"
                ],
                file_name=(
                    "ats_resume_report.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_report",
            )

    with c2:

        st.download_button(
            "📄 Download Summary (.txt)",
            data=_summary_text(
                analysis
            ),
            file_name="ats_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_summary",
        )


def render():

    st.title(
        "🎯 ATS Resume Scorer"
    )

    st.markdown(
        "Upload your resume — and optionally "
        "a job description — for a "
        "comprehensive analysis."
    )

    with st.sidebar:

        st.markdown("---")

        st.markdown(
            "## 📊 Analysis Options"
        )

        st.info(
            "**General ATS Score**: resume only — "
            "overall compatibility.\n\n"

            "**JD Comparison**: resume + job "
            "description — targeted match analysis."
        )

    st.markdown("---")

    analysis_mode = st.radio(
        "Select Analysis Mode:",
        [
            "General ATS Score",
            "Job Description Comparison"
        ],
        horizontal=True,
    )

    st.markdown("---")

    resume_file, jd_file, jd_text = (
        _render_upload_area(
            analysis_mode
        )
    )

    st.markdown("---")

    if not resume_file:

        st.info(
            "👆 Upload your resume to begin."
        )

        if st.session_state.get(
            "scorer_analysis"
        ):

            display_results_dashboard(
                st.session_state[
                    "scorer_analysis"
                ]
            )

        return

    access_token = (
        st.session_state.get(
            "access_token"
        )
    )

    if not access_token:

        st.warning(
            "⚠️ Sign in from the sidebar "
            "to analyze a resume."
        )

        return

    _, mid, _ = st.columns(
        [1, 2, 1]
    )

    with mid:

        analyze = st.button(
            "🚀 Analyze Resume",
            use_container_width=True,
            type="primary"
        )

    if not analyze:

        if st.session_state.get(
            "scorer_analysis"
        ):

            analysis = (
                st.session_state[
                    "scorer_analysis"
                ]
            )

            display_results_dashboard(
                analysis
            )

            _render_export_buttons(
                analysis
            )

        return

    st.session_state.pop(
        "scorer_pdf_bytes",
        None
    )

    st.session_state.pop(
        "scorer_analysis",
        None
    )

    if (
        analysis_mode
        == "Job Description Comparison"
    ):

        job_description = _read_jd(
            jd_file,
            jd_text
        )

    else:

        job_description = ""

    try:

        with st.spinner(
            "Analyzing your resume... "
            "The AI models may take a little "
            "longer on the first analysis."
        ):

            analysis = (
                direct_service
                .analyze_resume_direct(
                    resume_file=
                    resume_file,

                    job_description=
                    job_description,
                )
            )

    except Exception as exc:

        st.error(
            f"Resume analysis failed: {exc}"
        )

        return

    st.session_state[
        "scorer_analysis"
    ] = analysis

    st.success(
        "✅ Analysis complete!"
    )

    display_results_dashboard(
        analysis
    )

    _render_export_buttons(
        analysis
    )