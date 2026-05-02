from app.src.message import Message, MetrodokuMessage

from app.src.extract import Extract
from tests.fixtures import fixture_simple_text_extract, fixture_extract_metrodoku


def test_is_message_first_line():
    extract = Extract("")
    assert extract.is_message_first_line(
        "17/04/2026, 01:40 - Harvid: jokes on you je suis en télétravail"
    )
    assert extract.is_message_first_line(
        "[14/04/2026 10:31:26] MétroDoKu: Les messages sont chiffrés"
    )
    assert extract.is_message_first_line(
        "\u200e[14/04/2026 10:31:26] MétroDoKu: Les messages sont chiffrés"
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


def test_extract_new_header_format_normalizes_for_message_parsing():
    txt = (
        "[14/04/2026 10:31:26] MétroDoKu: Les messages sont chiffrés\n"
        "[16/04/2026 15:59:57] Rayann: J'avoue tout"
    )

    extract = Extract(txt)

    assert len(extract.messages) == 2
    assert extract.messages[0] == Message.from_txt(
        "14/04/2026, 10:31 - MétroDoKu: Les messages sont chiffrés"
    )
    assert extract.messages[1] == Message.from_txt(
        "16/04/2026, 15:59 - Rayann: J'avoue tout"
    )
