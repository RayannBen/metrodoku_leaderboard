from datetime import datetime



class Message:
    def __init__(self, content: str, author: str , timestamp: datetime):
        self.content = content
        self.author = author
        self.timestamp = timestamp or datetime.now()

    
    
    @classmethod
    def from_txt(cls, txt: str):
        # Create a temporary instance to use _extract_author, or refactor _extract_author to staticmethod
        author = cls._extract_author(txt)
        timestamp = cls._extract_timestamp(txt)
        return cls(txt, author, timestamp)
    
    @staticmethod
    def _extract_author(txt: str) -> str:
        first_line = txt.splitlines()[0] if txt else ""
        author= first_line.split("-")[1].split(":")[0].strip() if "-" in first_line and ":" in first_line else "Unknown"
        return author
    
    @staticmethod
    def _extract_timestamp(txt: str) -> datetime:
        first_line = txt.splitlines()[0] if txt else ""
        try:
            timestamp_str = first_line.split("-")[0].strip() if "-" in first_line else ""
            return datetime.strptime(timestamp_str, "%d/%m/%Y, %H:%M")
        except (IndexError, ValueError):
            return datetime.now()

    
class MetrodokuMessage(Message):
    def __init__(self, content: str, author: str, timestamp: datetime, score: int ):
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
    

class MessageFactory:
    @classmethod
    def create_message(cls, content) -> Message:
        if cls.is_metrodoku(content):
            return MetrodokuMessage.from_txt(content)
        return Message.from_txt(content)
    
    @classmethod
    def is_metrodoku(cls, content: str) -> bool:
        return "métrodoku" in content
    

