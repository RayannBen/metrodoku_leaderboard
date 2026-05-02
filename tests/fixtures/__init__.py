from datetime import datetime
from app.src.message import Message

fixture_message = Message("Test content", "Test author", datetime.now())
fixture_text = "17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail"
fixture_metrodoku_text = """17/04/2026, 00:59 - Harvid: métrodoku
17/04/2026
Score : 771/900
🟩🟩🟩
🟩🟩🟩
🟩🟩🟩
https://metrodoku.fr/"""

fixture_metrodoku_text_with_previous_message = """17/04/2026, 12:40 - Pisspartou: Je suis SCANDALISÉ par cette case


métrodoku
17/04/2026
Score : 601/900
🟩🟩🟩
⬜️🟩🟩
🟩🟩🟩
https://metrodoku.fr/"""

fixture_simple_text_extract = """17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail
17/04/2026, 01:41 - Tekiron: tssskkk tu te gaches ton palisir pour demain"""

fixture_extract_metrodoku = """17/04/2026, 00:59 - Harvid: métrodoku
17/04/2026
Score : 771/900
🟩🟩🟩
🟩🟩🟩
🟩🟩🟩
https://metrodoku.fr/
17/04/2026, 01:31 - Tekiron: tssskkk tu te gaches ton palisir pour demain
17/04/2026, 12:40 - Pisspartou: métrodoku
17/04/2026
Score : 601/900
🟩🟩🟩
⬜️🟩🟩
🟩🟩🟩
https://metrodoku.fr/"""
