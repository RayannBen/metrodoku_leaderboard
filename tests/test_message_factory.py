from src.message import Message, MetrodokuMessage, MessageFactory
from tests.fixtures import fixture_text, fixture_metrodoku_text, fixture_metrodoku_text_with_previous_message


def test_message_factory_creation():
    message = MessageFactory.create_message(fixture_text)
    assert isinstance(message, Message)
    assert message.content == fixture_text
    assert message.author == "Harvid"
    assert message.timestamp is not None


def test_message_factory_metrodoku_creation():
    message = MessageFactory.create_message(fixture_metrodoku_text)
    assert isinstance(message, MetrodokuMessage)
    assert message.content == fixture_metrodoku_text
    assert message.author == "Harvid"
    assert message.timestamp is not None
    assert message.score == 771

def test_message_factory_metrodoku_with_previous_text(txt=fixture_metrodoku_text_with_previous_message):
    message = MessageFactory.create_message(txt)
    assert isinstance(message, MetrodokuMessage)
    assert message.content == txt
    assert message.author == "Pisspartou"
    assert message.timestamp is not None
    assert message.score == 601
    assert message._extract_grid(txt) == [
        [True, True, True],
        [False, True, True],
        [True, True, True],
    ]