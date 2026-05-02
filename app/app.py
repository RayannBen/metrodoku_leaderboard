from __future__ import annotations

import re
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.extract import Extract


EXAMPLE_PATH = Path("data/extract_02_05.txt")
DATA_DIR = Path("data")
PERIODS = {
    "Semaine (7 jours)": 7,
    "Mois (30 jours)": 30,
    "3 mois (90 jours)": 90,
    "6 mois (180 jours)": 180,
    "Tout": None,
}


def _extract_sort_key_from_title(path: Path) -> tuple[int, int] | None:
    match = re.match(r"^extract_(\d{2})_(\d{2})(?:_\d{4})?\.txt$", path.name)
    if not match:
        return None

    day, month = int(match.group(1)), int(match.group(2))
    if day < 1 or day > 31 or month < 1 or month > 12:
        return None
    return (month, day)


def _get_latest_extract_path() -> Path | None:
    if not DATA_DIR.exists():
        return None

    candidates: list[tuple[tuple[int, int], Path]] = []
    for path in DATA_DIR.glob("extract_*.txt"):
        key = _extract_sort_key_from_title(path)
        if key is not None:
            candidates.append((key, path))

    if not candidates:
        return EXAMPLE_PATH if EXAMPLE_PATH.exists() else None

    return max(candidates, key=lambda item: item[0])[1]


def _apply_custom_ui() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

            :root {
                --bg-soft: #f6f8fb;
                --surface: #ffffff;
                --text-main: #1b2130;
                --text-muted: #5f6780;
                --brand: #1f8a70;
                --brand-dark: #166a56;
                --accent: #ff7f50;
                --border: #e7ebf3;
            }

            .stApp {
                background:
                    radial-gradient(circle at 5% 0%, rgba(31, 138, 112, 0.10), transparent 30%),
                    radial-gradient(circle at 95% 10%, rgba(255, 127, 80, 0.14), transparent 35%),
                    var(--bg-soft);
                color: var(--text-main);
            }

            h1, h2, h3 {
                font-family: 'Space Grotesk', sans-serif;
                letter-spacing: -0.01em;
            }

            p, div, span, label {
                font-family: 'Manrope', sans-serif;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #13263f 0%, #1a3659 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }

            section[data-testid="stSidebar"] * {
                color: #f8fbff;
            }

            section[data-testid="stSidebar"] hr {
                border-color: rgba(255, 255, 255, 0.2);
            }

            div[data-testid="stDataFrame"] {
                border: 1px solid var(--border);
                border-radius: 16px;
                background: var(--surface);
                box-shadow: 0 12px 24px rgba(16, 24, 40, 0.06);
                overflow: hidden;
            }

            .hero {
                padding: 1.2rem 1.3rem;
                border-radius: 18px;
                background: linear-gradient(120deg, #11243a 0%, #1f8a70 50%, #f39c6b 100%);
                color: #ffffff;
                box-shadow: 0 14px 30px rgba(17, 36, 58, 0.26);
                margin-bottom: 1rem;
            }

            .hero h2 {
                margin: 0;
                color: #ffffff;
                font-size: 1.6rem;
            }

            .hero p {
                margin: 0.25rem 0 0 0;
                color: rgba(255, 255, 255, 0.92);
                font-size: 0.97rem;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(180px, 1fr));
                gap: 0.8rem;
                margin: 0.75rem 0 1.15rem 0;
            }

            .metric-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.8rem 0.95rem;
                box-shadow: 0 8px 18px rgba(16, 24, 40, 0.05);
            }

            .metric-label {
                font-size: 0.82rem;
                color: var(--text-muted);
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }

            .metric-value {
                margin-top: 0.2rem;
                font-size: 1.5rem;
                font-weight: 800;
                color: var(--text-main);
            }

            .section-title {
                display: inline-block;
                margin: 0.5rem 0 0.35rem 0;
                padding: 0.2rem 0.55rem;
                border-radius: 999px;
                background: rgba(31, 138, 112, 0.12);
                color: var(--brand-dark);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.03em;
                text-transform: uppercase;
            }

            .stButton > button {
                border-radius: 999px;
            }

            .table-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 16px;
                box-shadow: 0 12px 24px rgba(16, 24, 40, 0.06);
                overflow: hidden;
                margin-top: 0.35rem;
            }

            .table-wrap {
                overflow-x: auto;
            }

            .metro-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                min-width: 640px;
            }

            .metro-table thead th {
                position: sticky;
                top: 0;
                z-index: 1;
                background: #eef3fb;
                color: #2c3550;
                text-align: left;
                font-size: 0.8rem;
                letter-spacing: 0.03em;
                text-transform: uppercase;
                padding: 0.72rem 0.85rem;
                border-bottom: 1px solid var(--border);
                white-space: nowrap;
            }

            .metro-table tbody td {
                padding: 0.72rem 0.85rem;
                border-bottom: 1px solid #f0f3f8;
                color: #283149;
                font-size: 0.93rem;
                white-space: nowrap;
            }

            .metro-table tbody tr:nth-child(even) {
                background: #fbfcff;
            }

            .metro-table tbody tr:hover {
                background: #f4f8ff;
            }

            .badge-rank {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 2rem;
                border-radius: 999px;
                background: #e8f4ef;
                color: #0e6a55;
                font-weight: 700;
                font-size: 0.84rem;
                padding: 0.16rem 0.5rem;
            }

            .value-strong {
                font-weight: 700;
                color: #121b33;
            }

            #MainMenu, footer, header {
                visibility: hidden;
            }

            @media (max-width: 900px) {
                .metric-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero(page: str) -> None:
    if page == "Leaderboard":
        title = "🚇 Leaderboard Metrodoku"
        subtitle = (
            "Classements competitifs: volume global et performance max sur periode."
        )
    else:
        title = "📊 Dashboard Metrodoku"
        subtitle = "Explore les tendances, filtre les joueurs et creuse les insights."

    st.markdown(
        f"""
        <section class="hero">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_global_metrics(
    all_messages_count: int,
    metrodoku_messages_count: int,
    parsed_games_count: int,
) -> None:
    st.markdown(
        f"""
        <section class="metric-grid">
            <article class="metric-card">
                <div class="metric-label">💬 Messages chat</div>
                <div class="metric-value">{all_messages_count}</div>
            </article>
            <article class="metric-card">
                <div class="metric-label">🧩 Messages Metrodoku</div>
                <div class="metric-value">{metrodoku_messages_count}</div>
            </article>
            <article class="metric-card">
                <div class="metric-label">🎮 Parties parsees</div>
                <div class="metric-value">{parsed_games_count}</div>
            </article>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _section_badge(text: str) -> None:
    st.markdown(
        f'<div class="section-title">{text}</div>',
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


def _render_pretty_table(df: pd.DataFrame, columns: list[tuple[str, str]]) -> None:
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


def _decode_whatsapp_export(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


@st.cache_data(show_spinner=False)
def _parse_metrodoku(content: str) -> tuple[pd.DataFrame, int, int]:
    extract = Extract(content)
    all_messages_count = len(extract.messages)
    metrodoku_messages_count = len(extract.get_all_metrodoku_messages())
    df = extract.to_dataframe()

    if df.empty:
        return df, all_messages_count, metrodoku_messages_count

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["timestamp", "score", "author"])
    df["score"] = df["score"].astype(int)
    df["date"] = df["timestamp"].dt.date
    return df, all_messages_count, metrodoku_messages_count


def _build_global_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    leaderboard = (
        df.groupby("author", as_index=False)
        .agg(
            total_points=("score", "sum"),
            games=("score", "count"),
            average_score=("score", "mean"),
            best_score=("score", "max"),
            median_score=("score", "median"),
            latest_score=("score", "last"),
            latest_played_at=("timestamp", "max"),
        )
        .sort_values(
            by=["total_points", "games", "best_score"],
            ascending=[False, False, False],
        )
        .reset_index(drop=True)
    )

    leaderboard.insert(0, "rank", leaderboard.index + 1)
    leaderboard["average_score"] = leaderboard["average_score"].round(1)
    leaderboard["median_score"] = leaderboard["median_score"].round(1)
    return leaderboard


def _build_period_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    leaderboard = (
        df.groupby("author", as_index=False)
        .agg(
            best_score=("score", "max"),
            games=("score", "count"),
            average_score=("score", "mean"),
            total_points=("score", "sum"),
            latest_played_at=("timestamp", "max"),
        )
        .sort_values(
            by=["best_score", "average_score", "games"],
            ascending=[False, False, False],
        )
        .reset_index(drop=True)
    )

    leaderboard.insert(0, "rank", leaderboard.index + 1)
    leaderboard["average_score"] = leaderboard["average_score"].round(1)
    return leaderboard


def _filter_by_period(df: pd.DataFrame, period_label: str) -> pd.DataFrame:
    days = PERIODS[period_label]
    if days is None:
        return df

    end_date = df["timestamp"].max()
    start_date = end_date - pd.Timedelta(days=days)
    return df[df["timestamp"] >= start_date]


def _top_per_day(df: pd.DataFrame) -> pd.DataFrame:
    last_date = df["date"].max()
    recent_df = df[df["date"] == last_date]
    return (
        recent_df.groupby("author", as_index=False)
        .first()[["date", "author", "score"]]
        .sort_values("score", ascending=False)
        .rename(columns={"author": "winner", "score": "winning_score"})
    )


def _read_uploaded_or_example(uploaded_file, use_example: bool) -> str | None:
    if uploaded_file is not None:
        return _decode_whatsapp_export(uploaded_file.getvalue())

    latest_extract_path = _get_latest_extract_path()
    if use_example and latest_extract_path is not None:
        return latest_extract_path.read_text(encoding="utf-8")

    return None


def _render_leaderboard_page(df: pd.DataFrame) -> None:
    _section_badge("� Top score du jour")
    _render_pretty_table(
        _top_per_day(df),
        columns=[
            ("date", "Date"),
            ("winner", "Winner"),
            ("winning_score", "Score"),
        ],
    )

    st.divider()
    _section_badge("�🏁 Classement global")
    st.caption(
        "Base sur la somme de points de toutes les parties: plus de volume = plus haut classement."
    )
    global_lb = _build_global_leaderboard(df)
    _render_pretty_table(
        global_lb,
        columns=[
            ("rank", "Rank"),
            ("author", "Joueur"),
            ("total_points", "Points Totaux"),
            ("games", "Parties"),
            ("best_score", "Best"),
            ("average_score", "Moyenne"),
        ],
    )

    st.divider()
    _section_badge("🗓️ Classement par periode")
    st.caption("Classement base sur le meilleur score sur la periode choisie.")

    period_label = st.radio(
        "Fenetre temporelle",
        options=list(PERIODS.keys()),
        horizontal=True,
    )

    period_df = _filter_by_period(df, period_label)
    if period_df.empty:
        st.info("Aucune partie sur cette periode.")
        return

    period_lb = _build_period_leaderboard(period_df)
    _render_pretty_table(
        period_lb,
        columns=[
            ("rank", "Rank"),
            ("author", "Joueur"),
            ("best_score", "Best Score"),
            ("games", "Parties"),
            ("average_score", "Moyenne"),
            ("total_points", "Points"),
        ],
    )


def _render_dashboard_page(df: pd.DataFrame) -> None:
    _section_badge("🔎 Dashboard exploratoire")
    st.caption("Fouille des donnees avec filtres, tendances et vues detaillees.")

    min_day = df["timestamp"].min().date()
    max_day = df["timestamp"].max().date()

    filter_col_1, filter_col_2 = st.columns([2, 1])
    with filter_col_1:
        selected_authors = st.multiselect(
            "Joueurs",
            options=sorted(df["author"].unique().tolist()),
            default=sorted(df["author"].unique().tolist()),
        )
    with filter_col_2:
        selected_range = st.date_input(
            "Periode",
            value=(min_day, max_day),
            min_value=min_day,
            max_value=max_day,
        )

    if len(selected_range) != 2:
        st.warning("Selectionne une date de debut et de fin.")
        return

    start_day, end_day = selected_range
    filtered = df[
        (df["author"].isin(selected_authors))
        & (df["date"] >= start_day)
        & (df["date"] <= end_day)
    ].copy()

    if filtered.empty:
        st.info("Aucune donnee pour ces filtres.")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎮 Parties", len(filtered))
    m2.metric("👥 Joueurs actifs", filtered["author"].nunique())
    m3.metric("📈 Score moyen", round(float(filtered["score"].mean()), 1))
    m4.metric("🥇 Meilleur score", int(filtered["score"].max()))

    trend_col_1, trend_col_2 = st.columns(2)

    with trend_col_1:
        st.caption("📉 Evolution des scores (journalier)")
        daily = (
            filtered.groupby(["date", "author"], as_index=False)["score"]
            .mean()
            .pivot(index="date", columns="author", values="score")
            .sort_index()
        )
        st.line_chart(daily)

    with trend_col_2:
        st.caption("🎯 Distribution des scores")
        bins = pd.cut(filtered["score"], bins=9)
        distribution = bins.value_counts().sort_index()
        distribution_df = pd.DataFrame(
            {"count": distribution.values}, index=distribution.index.astype(str)
        )
        st.bar_chart(distribution_df)

    st.caption("🔥 Meilleur score par joueur")
    best_score_df = (
        filtered.groupby("author", as_index=False)["score"]
        .max()
        .rename(columns={"score": "best_score"})
        .sort_values("best_score", ascending=False)
        .set_index("author")
    )
    st.bar_chart(best_score_df)

    st.caption("🎲 Volume de parties par joueur")
    games_df = (
        filtered.groupby("author", as_index=False)["score"]
        .count()
        .rename(columns={"score": "games"})
        .sort_values("games", ascending=False)
        .set_index("author")
    )
    st.bar_chart(games_df)

    st.caption("🏆 Top score du jour (filtres dashboard)")
    top_day = _top_per_day(filtered)
    st.dataframe(top_day, hide_index=True, use_container_width=True)

    st.caption("🧾 Donnees detaillees")
    detail = filtered[["timestamp", "author", "score"]].sort_values(
        "timestamp", ascending=False
    )
    st.dataframe(
        detail,
        hide_index=True,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Date et heure",
                format="YYYY-MM-DD HH:mm",
            ),
            "author": "Joueur",
            "score": "Score",
        },
    )


def main() -> None:
    st.set_page_config(
        page_title="Metrodoku Leaderboard", page_icon="🚇", layout="wide"
    )
    _apply_custom_ui()
    st.title("Metrodoku Leaderboard")
    st.caption("Une interface plus propre pour suivre la perf de la team au quotidien.")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choix de page",
            options=["Leaderboard", "Dashboard"],
            index=0,
        )

        st.divider()
        st.header("Source de donnees")
        latest_extract_path = _get_latest_extract_path()
        uploaded_file = st.file_uploader(
            "WhatsApp export (.txt)",
            type=["txt"],
            help="Charge le fichier exporte depuis WhatsApp.",
        )
        use_example = st.checkbox(
            "Utiliser l'extract local le plus recent (data/extract_*.txt)",
            value=uploaded_file is None,
        )
        if latest_extract_path is not None:
            st.caption(f"Extract auto-detecte: {latest_extract_path.name}")
        else:
            st.caption("Aucun fichier extract_*.txt detecte dans data/.")

    content = _read_uploaded_or_example(uploaded_file, use_example)
    _render_hero(page)

    if content is None:
        st.info(
            "📂 Ajoute un fichier .txt WhatsApp ou active les donnees exemple pour commencer."
        )
        return

    try:
        df, all_messages_count, metrodoku_messages_count = _parse_metrodoku(content)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Impossible de parser cet export: {exc}")
        return

    _render_global_metrics(
        all_messages_count=all_messages_count,
        metrodoku_messages_count=metrodoku_messages_count,
        parsed_games_count=len(df),
    )

    if df.empty:
        st.warning("Aucune partie Metrodoku exploitable n'a ete trouvee.")
        return

    if page == "Leaderboard":
        _render_leaderboard_page(df)
    else:
        _render_dashboard_page(df)


if __name__ == "__main__":
    main()
