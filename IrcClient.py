import re
import socket

import Parser
from Letter import Letter
from enum import Enum, unique
from queue import Queue
from threading import Thread
from time import sleep, time


@unique
class Condition(Enum):
    disconnected = 1
    motd = 2
    names = 3
    connected = 4


class IrcClient:
    def __init__(self, address: str, port: int, channel: str, nick: str, pword: str, timeout=180):
        self.__timeout = timeout
        self.__gtm = 0
        self.__address = address
        self.__port = port
        self.__channel = channel
        self.__nick = nick
        self.__pword = pword
        self.__sock = socket.socket()
        self.__condition = Condition.disconnected
        self.__handler = Thread(target=self.__handle)
        self.__log = open("log.txt", 'a')
        self.__log.write("\r\n")
        self.__buffer = Queue()
        self.__unsolved_string = ""
        self.__names = set()

    def connect(self):
        self.__sock.connect((self.__address, self.__port))
        self.__sock.settimeout(self.__timeout)
        self.__condition = Condition.motd
        self.__handler.start()
        self.__send(Letter(time(), "PASS", None, self.__pword, None) if self.__pword else Letter(time(), "", None, None, None))
        self.__send(Letter(time(), "NICK", None, self.__nick, None))
        self.__send(Letter(time(), "USER", self.__nick, "0 *", self.__nick))
        while self.__condition is Condition.motd: sleep(1)
        self.__send(Letter(time(), "JOIN", self.__channel, None, None))
        while self.__condition is Condition.names: sleep(1)

    def disconnect(self):
        self.__send(Letter(time(), "QUIT", None, None, None))
        self.__condition = Condition.disconnected

    def connected(self) -> bool:
        return self.__condition is Condition.connected

    def send(self, message: str):
        self.__send(Letter(time(), "PRIVMSG", self.__channel, None, message))

    def p_send(self, message: str, nick: str):
        self.__send(Letter(time(), "PRIVMSG", None, nick, message))

    def require(self) -> Letter:
        while self.__buffer.empty():
            if not self.connected(): return None
            sleep(1)
        return self.__buffer.get()

    def names(self) -> set:
        return self.__names

    def __send(self, letter: Letter):
        self.__sock.send(bytes(source=letter.to_str() + "\r\n", encoding="utf8"))
        print("-> " + letter.to_short_str(self.gtm()))
        self.__log.write("-> " + letter.to_large_str(self.gtm()) + "\r\n")
        self.__log.flush()

    def __require(self) -> list:
        data = self.__sock.recv(65536)
        if data is None: return None
        data = data.decode("utf8", errors='replace')
        buff = [str(mess) for mess in re.split(r"\r\n", self.__unsolved_string + data)]
        if len(data) >= 2 and data[-2:] != '\r\n':
            self.__unsolved_string = buff[-1]
            del buff[-1]
        result = []
        for message in buff:
            if message == "": continue
            # self.__log.write(message + "\n")
            # self.__log.flush()
            ping = Parser.parse_ping(message)
            if ping is not None: result.append(ping)
            mode = Parser.parse_mode(self.__nick, message)
            if mode is not None: result.append(mode)
            if self.__condition is Condition.motd:
                end_motd = Parser.parse_end_motd(message)
                if end_motd is not None: result.append(end_motd)
            if self.__condition.value >= Condition.names.value:
                names = Parser.parse_names(self.__nick, message)
                if names is not None: result.append(names)
                end_names = Parser.parse_end_names(message)
                if end_names is not None: result.append(end_names)
                jpk = Parser.parse_jpk(message)
                if jpk is not None: result.append(jpk)
                m = Parser.parse_privmsg(message)
                if m is not None: result.append(m)
                q = Parser.parse_quit(message)
                if q is not None: result.append(q)
                nick = Parser.parse_nick(message)
                if nick is not None: result.append(nick)
        return result

    def __handle(self):
        try:
            while self.__condition is not Condition.disconnected:
                buff = self.__require()
                if buff is None:
                    self.__condition == Condition.disconnected
                    break
                for letter in buff:
                    if letter.name == "PING": self.__send(Letter(time(), "PONG", None, None, letter.args))
                    if self.__condition is Condition.motd:
                        if letter.name == "END MOTD": self.__condition = Condition.names
                    if self.__condition is Condition.names:
                        if letter.name == "NAMES": self.__names = self.__names | letter.args
                        if letter.name == "END NAMES": self.__condition = Condition.connected
                    if letter.name == "JOIN":
                        self.__names.add(letter.nick)
                    if letter.name == "NICK":
                        self.__names.remove(letter.nick)
                        self.__names.add(letter.args)
                    if letter.name == "KICK":
                        nick = re.split(r"\s", letter.args)[0]
                        if nick == self.__nick:
                            self.disconnect()
                        else:
                            self.__names.remove(nick)
                    if letter.name == "QUIT" or letter.name == "PACK": self.__names.remove(letter.nick)
                    self.__buffer.put(letter)
                    print("<- " + letter.to_short_str(self.__gtm))
                    self.__log.write("<- " + letter.to_large_str(self.__gtm) + "\r\n")
                    self.__log.flush()
        except socket.timeout:
            print("Connection timeout")
            self.disconnect()
        else:
            self.__sock.close()

    def set_gtm(self, gtm: int):
        self.__gtm = gtm

    def gtm(self) -> int:
        return self.__gtm
