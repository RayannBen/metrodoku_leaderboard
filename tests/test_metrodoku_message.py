from app.src.message import MetrodokuMessage
from tests.fixtures import (
    fixture_metrodoku_text,
    fixture_metrodoku_text_with_previous_message,
)


def test_metrodoku_message_creation(txt=fixture_metrodoku_text):
    message = MetrodokuMessage.from_txt(txt)

    assert message.content == txt
    assert message.author == "Harvid"
    assert message.timestamp is not None
    assert message._get_score(txt) == 771
    assert message._extract_grid(txt) == [
        [True, True, True],
        [True, True, True],
        [True, True, True],
    ]


def test_metrodoku_message_bad_score():
    bad_score_text = fixture_metrodoku_text_with_previous_message
    message = MetrodokuMessage.from_txt(bad_score_text)
    assert message._get_score(bad_score_text) == 601
    assert message._extract_grid(bad_score_text) == [
        [True, True, True],
        [False, True, True],
        [True, True, True],
    ]
    assert message.author == "Pisspartou"
    assert message.timestamp is not None
    assert message.content == bad_score_text
