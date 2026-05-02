import re
import pandas as pd
from src.message import MessageFactory, Message, MetrodokuMessage
from pathlib import Path


class Extract:
    def __init__(self, content: str):
        self.content = content
        self.messages = self._extract_messages(content)

    @classmethod
    def from_path(cls, path: Path) -> "Extract":
        content = path.read_text()
        return cls(content)

    def _extract_messages(self, content: str) -> list[Message]:
        lines = content.splitlines()
        messages: list[Message] = []
        current_message_lines: list[str] = []

        for line in lines:
            if self.is_message_first_line(line):
                if current_message_lines:
                    messages.append(
                        MessageFactory.create_message("\n".join(current_message_lines))
                    )
                    current_message_lines = []
            current_message_lines.append(line)

        if current_message_lines:
            messages.append(
                MessageFactory.create_message("\n".join(current_message_lines))
            )

        return messages

    def is_message_first_line(self, line: str) -> bool:
        pattern = r"^\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - .+: .+"
        return bool(re.match(pattern, line))

    def get_all_authors(self) -> set[str]:
        return {message.author for message in self.messages}

    def get_all_metrodoku_messages(self) -> list[MetrodokuMessage]:
        return [
            message
            for message in self.messages
            if isinstance(message, MetrodokuMessage)
        ]

    def get_all_metrodoku_messages_per_author(
        self,
    ) -> dict[str, list[MetrodokuMessage]]:
        authors = self.get_all_authors()
        metrodoku_messages_per_author: dict[str, list[MetrodokuMessage]] = {
            author: [] for author in authors
        }
        for message in self.messages:
            if isinstance(message, MetrodokuMessage):
                metrodoku_messages_per_author[message.author].append(message)
        return metrodoku_messages_per_author

    def to_dataframe(self) -> pd.DataFrame:
        data = [message.serialize() for message in self.get_all_metrodoku_messages()]
        return pd.DataFrame(data)
