import socket
import re
import yaml

from time import sleep


config = yaml.safe_load(open('config.yml', 'rb'))
HOST = config['HOST']
PORT = config['PORT']
NICK = config['NICK']
PASS = config['PASS']


class Bot(object):
    """"""
    def __init__(self, channel, n_msg_per_sec=100):
        super(Bot, self).__init__()
        self._nickname = NICK
        self.channel = channel
        self.connect(channel)
        # print(NICK, channel, '\n', '-' * (len(NICK + channel) + 1))
        print("{} {}\n{}".format(NICK, channel, '-' * (len(NICK + channel) + 1)))

        self._msg_count = 0
        self.n_msg_per_sec = n_msg_per_sec

    def connect(self, channel):
        self._socket = socket.socket()
        self._socket.connect((HOST, PORT))
        self._socket.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        self._socket.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        self._socket.send("JOIN {}\r\n".format(channel).encode("utf-8"))

    def chat(self, msg):
        self._socket.send("PRIVMSG {} :{}\r\n".format(self.channel, msg))

    def _ping_pong(self, response):
        if response == "PING :tmi.twitch.tv\r\n":
            # send pong back to prevent timeout
            self._socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            return True
        else:
            return False

    def _get_response(self):
        try:
            response = self._socket.recv(1024).decode("utf-8")
        except UnicodeDecodeError as e:
            print('\n\n%s\n\n' % e)
            return False

        if self._ping_pong(response):
            return False
        elif ':tmi.twitch.tv' in response:
            return False
        else:
            return response

    def _process_msg(self, response):
        username = re.search(r"\w+", response).group(0)
        mask = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
        message = mask.sub("", response).strip('\r\n')
        return username, message

    def action(self, username, msg):
        return NotImplementedError()

    def run(self):
        while True:
            response = self._get_response()
            if response:
                username, msg = self._process_msg(response)
                self.action(username, msg)

            sleep(1 / float(self.n_msg_per_sec))
