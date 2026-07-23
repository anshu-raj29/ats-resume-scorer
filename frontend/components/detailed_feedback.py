from typing import Any, Dict, List

import streamlit as st

from frontend.components._helpers import get_severity_style


SEVERITY_ORDER = ["critical", "high", "medium", "low"]


def _value(issue, key, default=None):
    if hasattr(issue, key):
        value = getattr(issue, key)
        return default if value is None else value
    return issue.get(key, default)


def _group_by_severity(issues):
    grouped = {level: [] for level in SEVERITY_ORDER}
    for issue in issues:
        level = (_value(issue, "severity_level", "low") or "low").lower()
        grouped.setdefault(level, []).append(issue)
    return grouped


def _render_issue(issue):
    icon, text_color, bg_color = get_severity_style(_value(issue, "severity_level"))

    title = _value(issue, "issue_title", "Untitled issue")
    impact = _value(issue, "ats_impact", "")
    explanation = _value(issue, "explanation", "")
    where = _value(issue, "where_it_appears", "")
    how_to_fix = _value(issue, "how_to_fix", "")
    action_items = _value(issue, "action_items", []) or []
    example = _value(issue, "example_improvement", "")

    st.markdown(
        f"""
        <div style="border-left:4px solid {text_color}; background-color:{bg_color};
                    padding:0.75rem 1rem; border-radius:6px; margin-bottom:0.5rem;">
            <strong style="color:{text_color};">{icon} {title}</strong>
            <span style="color:#666; margin-left:0.5rem; font-size:0.85rem;">{impact}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Details", expanded=False):
        if explanation:
            st.markdown(f"**What's happening:** {explanation}")
        if where:
            st.markdown(f"**Where it appears:** {where}")
        if how_to_fix:
            st.markdown(f"**How to fix:** {how_to_fix}")
        if action_items:
            st.markdown("**Action items:**")
            for item in action_items:
                st.markdown(f"- {item}")
        if example:
            st.markdown("**Example improvement:**")
            st.code(example, language="text")


def display_detailed_feedback(analysis):
    issues = analysis.get("detailed_feedback") or []
    if not issues:
        return

    st.markdown("### 🔍 Detailed Feedback")
    st.caption(f"{len(issues)} issue(s) flagged — grouped by severity.")

    grouped = _group_by_severity(issues)

    for level in SEVERITY_ORDER:
        items = grouped.get(level, [])
        if not items:
            continue

        st.markdown(f"#### {level.title()} ({len(items)})")
        for issue in items:
            _render_issue(issue)