from app.src.message import Message
from datetime import datetime
from tests.fixtures import fixture_message, fixture_text


def test_message_creation():
    content = "Hello, World!"
    author = "Alice"
    timestamp = datetime.now()

    message = Message(content, author, timestamp)

    assert message.content == content
    assert message.author == author
    assert message.timestamp is not None


def test_fixture_message():
    assert fixture_message.content == "Test content"
    assert fixture_message.author == "Test author"
    assert fixture_message.timestamp is not None


def test_message_from_txt(txt=fixture_text):

    message = Message.from_txt(txt)

    assert message.content == txt
    assert message.author == "Harvid"
    assert message.timestamp == datetime(2026, 4, 17, 1, 40)
