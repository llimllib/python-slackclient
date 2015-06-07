from slackrtm._server import Server, SlackLoginError, User, Bot
from slackrtm._channel import Channel
import json
import pytest

@pytest.fixture
def login_data():
    login_data = open('_pytest/data/rtm.start.json','r').read()
    login_data = json.loads(login_data)
    return login_data

def test_Server(server):
    assert type(server) == Server


def test_Server_parse_channel_data(server, login_data):
    server.parse_channel_data(login_data["channels"])
    assert type(server.channels['C01CX1234']) == Channel

def test_Server_parse_user_data(server, login_data):
    server.parse_user_data(login_data["users"])
    assert type(server.users['U10CX1234']) == User

def test_Server_cantconnect(server):
    with pytest.raises(SlackLoginError):
        reply = server.ping()

def test_Server_bots(server, login_data):
    server.parse_bot_data(login_data['bots'])
    bot = server.bots['B035JM633']
    assert type(bot) == Bot
    assert bot.deleted == False
    assert bot.icons == {"image_48": "https://slack.global.ssl.fastly.net/26133/plugins/bot/assets/bot_48.png"}
    assert bot.id == "B035JM633"
    assert bot.name == "bot"

@pytest.mark.xfail
def test_Server_ping(server, monkeypatch):
    monkeypatch.setattr("websocket.create_connection", lambda: True)
    reply = server.ping()
