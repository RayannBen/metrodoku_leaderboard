from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st


def render_pretty_table(df: pd.DataFrame, columns: list[tuple[str, str]]) -> None:
    if df.empty:
        st.info("Aucune donnee a afficher.")
        return

    working_df = df[[col for col, _ in columns]].copy()
    header_html = "".join(f"<th>{escape(label)}</th>" for _, label in columns)

    body_rows = []
    for _, row in working_df.iterrows():
        cells = []
        for col, _ in columns:
            cells.append(f"<td>{_format_value(col, row[col])}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    body_html = "".join(body_rows)

    st.markdown(
        f"""
        <div class="table-card">
            <div class="table-wrap">
                <table class="metro-table">
                    <thead>
                        <tr>{header_html}</tr>
                    </thead>
                    <tbody>
                        {body_html}
                    </tbody>
                </table>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_value(col: str, value: object) -> str:
    if pd.isna(value):
        return "-"

    if col == "rank":
        rank = int(value)
        medal = ""
        if rank == 1:
            medal = " 🥇"
        elif rank == 2:
            medal = " 🥈"
        elif rank == 3:
            medal = " 🥉"
        return f'<span class="badge-rank">#{rank}{medal}</span>'

    if col in {"total_points", "best_score", "games", "winning_score", "score"}:
        return f'<span class="value-strong">{int(value)}</span>'

    if col == "average_score":
        return f"{float(value):.1f}"

    if col == "timestamp":
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return "-"
        return ts.strftime("%Y-%m-%d %H:%M")

    if col == "date":
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return "-"
        return dt.strftime("%Y-%m-%d")

    return escape(str(value))
