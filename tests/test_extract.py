from src.message import Message, MetrodokuMessage

from src.extract import Extract
from tests.fixtures import fixture_simple_text_extract, fixture_extract_metrodoku


def test_is_message_first_line():
    extract = Extract("")
    assert extract.is_message_first_line(
        "17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail"
    )
    assert extract.is_message_first_line(
        "17/04/2026, 01:41 - Tekiron: tssskkk tu te gaches ton palisir pour demain"
    )
    assert not extract.is_message_first_line("17/04/2026")
    assert not extract.is_message_first_line("Score : 771/900")
    assert not extract.is_message_first_line("🟩🟩🟩")


def test_extract_simple_content(txt=fixture_simple_text_extract):
    extract = Extract(txt)
    assert extract.content == txt
    assert extract.messages == [
        Message.from_txt(
            "17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail"
        ),
        Message.from_txt(
            "17/04/2026, 01:41 - Tekiron: tssskkk tu te gaches ton palisir pour demain"
        ),
    ]


def test_extract_metrodoku_content(txt=fixture_extract_metrodoku):
    extract = Extract(txt)
    assert extract.content == txt
    assert len(extract.messages) == 3
    assert extract.messages == [
        MetrodokuMessage.from_txt(
            "17/04/2026, 00:59 - Harvid: métrodoku\n17/04/2026\nScore : 771/900\n🟩🟩🟩\n🟩🟩🟩\n🟩🟩🟩\nhttps://metrodoku.fr/"
        ),
        Message.from_txt(
            "17/04/2026, 01:31 - Tekiron: tssskkk tu te gaches ton palisir pour demain"
        ),
        MetrodokuMessage.from_txt(
            "17/04/2026, 12:40 - Pisspartou: métrodoku\n17/04/2026\nScore : 601/900\n🟩🟩🟩\n⬜️🟩🟩\n🟩🟩🟩\nhttps://metrodoku.fr/"
        ),
    ]
