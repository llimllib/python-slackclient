from slackrtm.client import SlackClient
from slackrtm.channel import Channel
import json
import pytest

@pytest.fixture
def channel_created():
    return json.load(open('tests/data/channel.created.json'))

@pytest.fixture
def im_created():
    return json.load(open('tests/data/im.created.json'))

@pytest.fixture
def group_joined():
    return json.load(open('tests/data/group.joined.json'))

@pytest.fixture
def team_join():
    return json.load(open('tests/data/team.join.json'))

def test_SlackClient(slackclient):
    assert type(slackclient) == SlackClient

def test_SlackClient_process_changes(slackclient, channel_created, im_created):
    slackclient.process_changes(channel_created)
    assert type(slackclient.server.channels['C024BE91L']) == Channel
    slackclient.process_changes(im_created)
    assert type(slackclient.server.channels['D024BE91L']) == Channel

def test_team_join(slackclient, team_join):
    assert team_join["user"]["id"] not in slackclient.server.users
    slackclient.process_changes(team_join)
    assert team_join["user"]["id"] in slackclient.server.users

def test_group_joined(slackclient, group_joined):
    slackclient.process_changes(group_joined)
    assert type(slackclient.server.channels['G18TJFWER']) == Channel
