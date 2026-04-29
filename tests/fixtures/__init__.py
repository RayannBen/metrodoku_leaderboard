from datetime import datetime
from src.message import Message

fixture_message = Message("Test content", "Test author", datetime.now())
fixture_text = "17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail"
fixture_metrodoku_text = """17/04/2026, 00:59 - Harvid: métrodoku
17/04/2026
Score : 771/900
🟩🟩🟩
🟩🟩🟩
🟩🟩🟩
https://metrodoku.fr/"""