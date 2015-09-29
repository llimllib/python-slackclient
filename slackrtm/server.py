from collections import namedtuple
import json
from ssl import SSLError

# python 2.7.9+ and python 3 have this error
try:
    from ssl import SSLWantReadError
except ImportError:
    SSLWantReadError = SSLError

from websocket import create_connection

from .slackrequest import SlackRequest
from .channel import Channel

User = namedtuple('User', 'server name id real_name tz')
Bot = namedtuple('Bot', 'id name icons deleted')

class Server(object):
    def __init__(self, token, connect=True):
        self.token = token
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = {}
        self.channels = {}
        self.bots = {}
        self.connected = False
        self.pingcounter = 0
        self.api_requester = SlackRequest()

        if connect:
            self.rtm_connect()

    def __eq__(self, compare_str):
        if compare_str == self.domain or compare_str == self.token:
            return True
        else:
            return False

    def __str__(self):
        data = ""
        for key in list(self.__dict__.keys()):
            data += "{0} : {1}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def rtm_connect(self, reconnect=False):
        reply = self.api_requester.do(self.token, "rtm.start")
        if reply.code != 200:
            raise SlackConnectionError
        else:
            login_data = json.loads(reply.read().decode('utf-8'))
            if login_data["ok"]:
                self.ws_url = login_data['url']
                if not reconnect:
                    self.parse_slack_login_data(login_data)
                self.connect_slack_websocket(self.ws_url)
            else:
                raise SlackLoginError

    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data["team"]["domain"]
        self.username = self.login_data["self"]["name"]
        self.parse_channel_data(login_data["channels"])
        self.parse_channel_data(login_data["groups"])
        self.parse_channel_data(login_data["ims"])
        self.parse_user_data(login_data["users"])
        self.parse_bot_data(login_data["bots"])

    def connect_slack_websocket(self, ws_url):
        try:
            self.websocket = create_connection(ws_url)
            self.websocket.sock.setblocking(0)
        except:
            raise SlackConnectionError

    def parse_channel_data(self, channel_data):
        for channel in channel_data:
            if "name" not in channel:
                channel["name"] = channel["id"]
            if "members" not in channel:
                channel["members"] = []

            self.attach_channel(channel['name'], channel['id'], channel['members'])

    def parse_user_data(self, user_data):
        for user in user_data:
            if "tz" not in user:
                user["tz"] = "unknown"
            if "real_name" not in user:
                user["real_name"] = user["name"]

            id = user['id']
            name = user['name']
            real_name = user['real_name']
            tz = user['tz']

            self.users[user['id']] = User(self, name, id, real_name, tz)

    def parse_bot_data(self, bot_data):
        for bot in bot_data:
            self.bots[bot['id']] = Bot(bot['id'], bot['name'], bot.get('icons', ''), bot['deleted'])

    def send_to_websocket(self, data):
        """Send (data) directly to the websocket."""
        try:
            data = json.dumps(data)
            self.websocket.send(data)
        except:
            self.rtm_connect(reconnect=True)

    def ping(self):
        return self.send_to_websocket({"type": "ping"})

    def websocket_safe_read(self):
        """ Returns data if available, otherwise ''. Newlines indicate multiple
            messages
        """
        data = []
        while True:
            try:
                data.append(self.websocket.recv())
            except (SSLError, SSLWantReadError) as e:
                if e.errno == 2:
                    # errno 2 occurs when trying to read or write data, but more
                    # data needs to be received on the underlying TCP transport
                    # before the request can be fulfilled.
                    return data
                raise

    def attach_channel(self, name, id, members=[]):
        self.channels[id] = Channel(self, name, id, members)

    def join_channel(self, name):
        print(self.api_requester.do(self.token,
                                    "channels.join?name={0}".format(name)).read())

    def api_call(self, method, **kwargs):
        reply = self.api_requester.do(self.token, method, **kwargs)
        return reply.read()


class SlackConnectionError(Exception):
    pass


class SlackLoginError(Exception):
    pass
