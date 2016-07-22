import re
from time import time
from Letter import Letter


def parse_ping(message: str) -> Letter:
    command = re.findall(r"PING\s[^\s]*", message)
    if len(command) == 0: return None
    return Letter(time(), "PING", None, None, command[0][6:])


def parse_privmsg(message: str) -> Letter:
    nick = re.findall(r":([\w\-_]+)!", message)
    if not nick: return None
    nick = nick[0]
    tmp = re.findall(r"![^\s]*\s", message)[0]
    text = message[message.index(tmp) + len(tmp):]
    command = re.findall(r"(\w+)\s#", text)
    if command:
        command = command[0]
        if command != "PRIVMSG": return None
        channel = re.findall(r"(#[^\s]+)", text)[0]
        mess = text[text.index(channel) + len(channel) + 2:]
        return Letter(time(), command, channel, nick, mess)
    else:
        my_nick = re.findall(r"PRIVMSG\s([^\s]+)\s:", text)
        if not my_nick: return None
        my_nick = my_nick[0]
        mess = text[text.index(my_nick) + len(my_nick) + 2:]
        return Letter(time(), "PRIVMSG", None, nick, mess)


def parse_nick(message: str) -> Letter:
    nick = re.findall(r":([\w\-_]+)!", message)
    if not nick: return None
    nick = nick[0]
    tmp = re.findall(r"![^\s]*\s", message)[0]
    text = message[message.index(tmp) + len(tmp):]
    new_nick = re.findall(r"NICK\s:([\w\-_]+)", text)
    if not new_nick: return None
    new_nick = new_nick[0]
    return Letter(time(), "NICK", None, nick, new_nick)


def parse_jpk(message: str) -> Letter:
    nick = re.findall(r":([\w\-_]+)!", message)
    if not nick: return None
    nick = nick[0]
    tmp = re.findall(r"![^\s]*\s", message)[0]
    text = message[message.index(tmp) + len(tmp):]
    command = re.findall(r"(\w+)\s#", text)
    if not command: return None
    command = command[0]
    if command != "JOIN" and command != "PART" and command != "KICK": return None
    channel = re.findall(r"(#[^\s]+)", text)[0]
    if command == "KICK":
        mess = text[text.index(channel) + len(channel) + 1:]
    else:
        mess = text[text.index(channel) + len(channel) + 2:]
    return Letter(time(), command, channel, nick, mess)


def parse_quit(message: str) -> Letter:
    nick = re.findall(r":([\w\-_]+)!", message)
    if len(nick) <= 0: return None
    nick = nick[0]
    tmp = re.findall(r"![^\s]*\s", message)[0]
    text = message[message.index(tmp) + len(tmp):]
    command = re.findall(r"(\w+)\s:", text)
    if len(command) <= 0: return None
    command = command[0]
    if command != "QUIT": return None
    return Letter(time(), command, None, nick, None)


def parse_mode(nick: str, message: str) -> Letter:
    if not re.search(re.compile(" MODE " + nick), message): return None
    arg = message[message.index(nick + " :") + len(nick) + 2:]
    return Letter(time(), "MODE", None, nick, arg)


def parse_names(nick, message: str) -> Letter:
    if not re.search(re.compile(nick + " = "), message): return None
    channel = re.findall(r"#[^\s]+", message)[0]
    names = re.split(r"\s[\+@]?", message[message.index(channel) + len(channel) + 2:])
    return Letter(time(), "NAMES", nick, channel, set(names))


def parse_end_names(message: str) -> list:
    if not re.search(r":End of /NAMES list", message): return None
    nick = re.findall(r"\s[^\s]+\s#", message)[0]
    channel = re.findall(r"#[^\s]+", message)[0]
    return Letter(time(), "END NAMES", nick, channel, None)


def parse_end_motd(message: str) -> list:
    if not re.search(r":End of /MOTD command", message): return None
    return Letter(time(), "END MOTD", None, None, None)
