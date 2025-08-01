from synmax_agent.hyperion import ChatClient


def test_hyperion():
    client = ChatClient()
    client.chat("this is a test message")
