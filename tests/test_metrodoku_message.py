from src.message import MetrodokuMessage
from tests.fixtures import fixture_metrodoku_text

def test_metrodoku_message_creation(txt=fixture_metrodoku_text):
    message = MetrodokuMessage.from_txt(txt)

    assert message.content == txt
    assert message.author == "Harvid"
    assert message.timestamp is not None
    assert message._get_score(txt) == 771
    