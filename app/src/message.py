from datetime import datetime


class Message:
    def __init__(self, content: str, author: str, timestamp: datetime):
        self.content = content
        self.author = author
        self.timestamp = timestamp or datetime.now()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Message):
            return False
        return (
            self.content == value.content
            and self.author == value.author
            and self.timestamp == value.timestamp
        )

    def __repr__(self) -> str:
        return f"Message(author='{self.author}', timestamp={self.timestamp.isoformat()}, content='{self.content}')"

    @classmethod
    def from_txt(cls, txt: str):
        author = cls._extract_author(txt)
        timestamp = cls._extract_timestamp(txt)
        return cls(txt, author, timestamp)

    @staticmethod
    def _extract_author(txt: str) -> str:
        first_line = txt.splitlines()[0] if txt else ""
        author = (
            first_line.split("-")[1].split(":")[0].strip()
            if "-" in first_line and ":" in first_line
            else "Unknown"
        )
        return author

    @staticmethod
    def _extract_timestamp(txt: str) -> datetime:
        first_line = txt.splitlines()[0] if txt else ""
        try:
            timestamp_str = (
                first_line.split("-")[0].strip() if "-" in first_line else ""
            )
            return datetime.strptime(timestamp_str, "%d/%m/%Y, %H:%M")
        except (IndexError, ValueError):
            return datetime.now()


class MetrodokuMessage(Message):
    def __init__(self, content: str, author: str, timestamp: datetime, score: int):
        super().__init__(content, author, timestamp)
        self.score = score

    @classmethod
    def from_txt(cls, txt: str):
        author = cls._extract_author(txt)
        timestamp = cls._extract_timestamp(txt)
        score = cls._get_score(txt)
        return cls(txt, author, timestamp, score)

    @staticmethod
    def _get_score(content: str) -> int:
        for line in content.splitlines():
            if line.startswith("Score :"):
                try:
                    return int(line.split(":")[1].strip().split("/")[0])
                except (IndexError, ValueError):
                    raise ValueError("Invalid score format in Metrodoku message.")
        return 0

    @staticmethod
    def _extract_grid(content: str) -> list[list[bool]]:
        grid_lines = []
        for line in content.splitlines():
            if line.startswith("🟩") or line.startswith("⬜"):
                grid_lines.append(line.strip())
        return [
            [cell == "🟩" for cell in line if cell in ["🟩", "⬜"]]
            for line in grid_lines
        ]

    def __repr__(self) -> str:
        return (
            super().__repr__().replace("Message", "MetrodokuMessage")[:-1]
            + f", score={self.score})"
        )

    def serialize(self) -> dict:
        return {
            "content": self.content,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "grid": self._extract_grid(self.content),
        }


class MessageFactory:
    @classmethod
    def create_message(cls, content) -> Message:
        if cls.is_metrodoku(content):
            return MetrodokuMessage.from_txt(content)
        return Message.from_txt(content)

    @classmethod
    def is_metrodoku(cls, content: str) -> bool:
        return "métrodoku" in content
