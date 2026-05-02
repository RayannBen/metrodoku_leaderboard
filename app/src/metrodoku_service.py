from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.extract import Extract


DEFAULT_PERIODS = {
    "Semaine (7 jours)": 7,
    "Mois (30 jours)": 30,
    "3 mois (90 jours)": 90,
    "6 mois (180 jours)": 180,
    "Tout": None,
}


@dataclass(frozen=True)
class ParseResult:
    dataframe: pd.DataFrame
    all_messages_count: int
    metrodoku_messages_count: int


class ExtractRepository:
    _EXTRACT_FILENAME_PATTERN = re.compile(
        r"^extract_(\d{2})_(\d{2})(?:_(\d{4}))?\.txt$"
    )

    def __init__(self, data_dir: Path, fallback_path: Path | None = None):
        self.data_dir = data_dir
        self.fallback_path = fallback_path

    def read_content(self, uploaded_file, use_example: bool) -> str | None:
        if uploaded_file is not None:
            return self.decode_whatsapp_export(uploaded_file.getvalue())

        latest_extract_path = self.get_latest_extract_path()
        if use_example and latest_extract_path is not None:
            return latest_extract_path.read_text(encoding="utf-8")

        return None

    def get_latest_extract_path(self) -> Path | None:
        if not self.data_dir.exists():
            return self.fallback_path if self._fallback_exists() else None

        candidates: list[tuple[tuple[int, int, int], Path]] = []
        for path in self.data_dir.glob("extract_*.txt"):
            key = self._extract_sort_key(path)
            if key is not None:
                candidates.append((key, path))

        if not candidates:
            return self.fallback_path if self._fallback_exists() else None

        return max(candidates, key=lambda item: item[0])[1]

    @staticmethod
    def decode_whatsapp_export(raw_bytes: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw_bytes.decode("utf-8", errors="ignore")

    def _fallback_exists(self) -> bool:
        return self.fallback_path is not None and self.fallback_path.exists()

    @classmethod
    def _extract_sort_key(cls, path: Path) -> tuple[int, int, int] | None:
        match = cls._EXTRACT_FILENAME_PATTERN.match(path.name)
        if not match:
            return None

        day, month = int(match.group(1)), int(match.group(2))
        year = int(match.group(3)) if match.group(3) else 0
        if day < 1 or day > 31 or month < 1 or month > 12:
            return None

        return (year, month, day)


class MetrodokuAnalyticsService:
    def __init__(
        self,
        periods: dict[str, int | None] | None = None,
        cheater_score_threshold: int = 900,
        cheater_score_last_digits_mod: int = 100,
        cheater_label: str = "LE TRICHEUR",
    ):
        self.periods = periods or DEFAULT_PERIODS
        self.cheater_score_threshold = cheater_score_threshold
        self.cheater_score_last_digits_mod = cheater_score_last_digits_mod
        self.cheater_label = cheater_label

    def parse_metrodoku(self, content: str) -> ParseResult:
        extract = Extract(content)
        all_messages_count = len(extract.messages)
        metrodoku_messages_count = len(extract.get_all_metrodoku_messages())
        df = extract.to_dataframe()

        if df.empty:
            return ParseResult(
                dataframe=df,
                all_messages_count=all_messages_count,
                metrodoku_messages_count=metrodoku_messages_count,
            )

        working_df = df.copy()
        working_df["timestamp"] = pd.to_datetime(
            working_df["timestamp"], errors="coerce"
        )
        working_df["score"] = pd.to_numeric(working_df["score"], errors="coerce")
        working_df = working_df.dropna(subset=["timestamp", "score", "author"])
        working_df["score"] = working_df["score"].astype(int)
        working_df = self._apply_cheater_rules(working_df)
        working_df["score"] = working_df["score"].astype(int)
        working_df["date"] = working_df["timestamp"].dt.date
        working_df = self._deduplicate_authors_by_date(working_df)

        return ParseResult(
            dataframe=working_df,
            all_messages_count=all_messages_count,
            metrodoku_messages_count=metrodoku_messages_count,
        )

    @staticmethod
    def _deduplicate_authors_by_date(working_df: pd.DataFrame) -> pd.DataFrame:
        working_df = (
            working_df.sort_values("timestamp")
            .drop_duplicates(subset=["author", "date"], keep="first")
            .reset_index(drop=True)
        )

        return working_df

    def build_global_leaderboard(self, df: pd.DataFrame) -> pd.DataFrame:
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

        cheater_mask = leaderboard["author"].str.contains(self.cheater_label, na=False)
        leaderboard.loc[cheater_mask, "total_points"] = 0

        leaderboard.insert(0, "rank", leaderboard.index + 1)
        leaderboard["average_score"] = leaderboard["average_score"].round(1)
        leaderboard["median_score"] = leaderboard["median_score"].round(1)
        return leaderboard

    def build_period_leaderboard(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def filter_by_period(self, df: pd.DataFrame, period_label: str) -> pd.DataFrame:
        days = self.periods[period_label]
        if days is None:
            return df

        end_date = df["timestamp"].max()
        start_date = end_date - pd.Timedelta(days=days)
        return df[df["timestamp"] >= start_date]

    @staticmethod
    def top_per_day(df: pd.DataFrame) -> pd.DataFrame:
        last_date = df["date"].max()
        recent_df = df[df["date"] == last_date]
        return (
            recent_df.groupby("author", as_index=False)
            .first()[["date", "author", "score"]]
            .sort_values("score", ascending=False)
            .rename(columns={"author": "winner", "score": "winning_score"})
        )

    @staticmethod
    def filter_dashboard(
        df: pd.DataFrame,
        selected_authors: list[str],
        start_day,
        end_day,
    ) -> pd.DataFrame:
        return df[
            (df["author"].isin(selected_authors))
            & (df["date"] >= start_day)
            & (df["date"] <= end_day)
        ].copy()

    @staticmethod
    def build_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(["date", "author"], as_index=False)["score"]
            .mean()
            .pivot(index="date", columns="author", values="score")
            .sort_index()
        )

    @staticmethod
    def build_score_distribution(df: pd.DataFrame, bins: int = 9) -> pd.DataFrame:
        distribution = pd.cut(df["score"], bins=bins).value_counts().sort_index()
        return pd.DataFrame(
            {"count": distribution.values}, index=distribution.index.astype(str)
        )

    @staticmethod
    def build_best_score_by_author(df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("author", as_index=False)["score"]
            .max()
            .rename(columns={"score": "best_score"})
            .sort_values("best_score", ascending=False)
            .set_index("author")
        )

    @staticmethod
    def build_games_by_author(df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("author", as_index=False)["score"]
            .count()
            .rename(columns={"score": "games"})
            .sort_values("games", ascending=False)
            .set_index("author")
        )

    def _apply_cheater_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        working_df = df.copy()
        cheaters = set(
            working_df.loc[
                working_df["score"] >= self.cheater_score_threshold,
                "author",
            ].tolist()
        )
        if not cheaters:
            return working_df

        cheater_mask = working_df["author"].isin(cheaters)
        penalized_scores = (
            working_df.loc[cheater_mask, "score"] % self.cheater_score_last_digits_mod
        )
        working_df.loc[cheater_mask, "score"] = penalized_scores.astype(int)
        working_df["author"] = working_df["author"].map(
            lambda name: (
                f"💩 {name} {self.cheater_label} 💩" if name in cheaters else name
            )
        )
        return working_df
