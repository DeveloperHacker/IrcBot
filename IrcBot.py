from Tools.scripts.treesync import raw_input
from threading import Thread
from time import time, sleep

from Action import RunAction, UpdAction
from Brain import Brain
from IrcClient import IrcClient
from TranslateClient import TranslateClient
from User import User
from WeatherClient import WeatherClient
from teach_file import rand_bye, rand_hello


class IrcBot:

    weather_key = "******"
    translate__key = "***"

    def __init__(self, gtm: int, address: str, port: int, channel: str, nick: str, pword: str, masters: set):
        self.__nick = nick
        self.__masters = masters
        self.__client = IrcClient(address, port, channel, nick, pword)
        self.__client.set_gtm(gtm)
        self.__weather_client = WeatherClient(IrcBot.weather_key)
        self.__translate_client = TranslateClient(IrcBot.translate__key)
        self.__handler = Thread(target=self.__handle)
        self.__commands = [
            ({"quit"}, self.__quit),
            ({"hello", "bye"}, self.__hello),

            ({"weather"}, self.__weather),
            ({"store"}, self.__store),
            ({"format"}, self.__format),
            ({"clear"}, self.__clear),
            ({"print"}, self.__print),

            ({"end"}, self.__end_action)
        ]
        self.__users = {}

    def connected(self):
        return self.__client.connected()

    def connect(self):
        self.__client.connect()
        self.__users = {name: User(name) for name in self.__client.names()}
        for master in self.__masters:
            if master not in self.__users: self.__users[master] = User(master)
            self.__users[master].master = True
        self.__handler.start()

    def disconnect(self):
        self.__client.disconnect()

    def __send(self, treatment: bool, snd_nick: str, message: str, public: bool):
        if public:
            self.__client.send((snd_nick + ", " if treatment else "") + message)
        else:
            self.__client.p_send((snd_nick + ", " if treatment else "") + message, snd_nick)

    def __handle(self):
        while self.connected():
            letter = self.__client.require()
            if letter is None: break
            if letter.name == "PRIVMSG":
                mess = letter.args
                text = Brain.clear_string(mess)
                snd_nick = letter.nick
                if snd_nick == self.__nick: continue
                public = letter.channel is not None
                for nick, user in self.__users.items():
                    if isinstance(user.action, UpdAction): user.action.update(snd_nick, public, mess)
                tags = set(Brain.get_tags(text).keys())
                if len(tags) == 0: continue
                dst_nicks = Brain.get_dst(text, self.__client.names())
                bot_nick = self.__nick.lower()
                for foo in self.__commands:
                    if foo[0] & tags: foo[1](tags, bot_nick, snd_nick, dst_nicks, public, mess)
            elif letter.name == "JOIN":
                user = User(letter.nick)
                if letter.nick in self.__masters: user.master = True
                self.__users[letter.nick] = user
            elif letter.name == "NICK":
                user = self.__users[letter.nick]
                del self.__users[letter.nick]
                user.name = letter.args
                self.__users[letter.args] = user

    def __quit(self, tags: str, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        if bot_nick not in dst_nicks: return False
        user = self.__users[snd_nick]
        if user.action is not None and not user.action.stopped():
            self.__send(True, snd_nick, "я не закончил твоё предыдущее задание: " + user.action.name(), public)
            return False
        if self.__users[snd_nick].master:
            self.__client.send(rand_bye())
            self.disconnect()
        else:
            self.__send(True, snd_nick, "я не хочу уходить!", public)
        return True

    def __hello(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        if bot_nick not in dst_nicks and ("all" not in tags or len(dst_nicks) > 0): return False
        user = self.__users[snd_nick]
        if user.hello and "bye" in tags:
            self.__send(True, snd_nick, rand_bye(), public)
        elif not user.hello and "hello" in tags:
            self.__send(True, snd_nick, rand_hello(), public)
        else:
            return False
        user.hello = not user.hello
        return True

    def __action_user(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool):
        if bot_nick not in dst_nicks or "end" in tags: return None
        user = self.__users[snd_nick]
        if user.action.stopped(): return user
        self.__send(True, snd_nick, "я не закончил твоё предыдущее задание: " + user.action.name(), public)
        return None

    def __weather(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        user = self.__action_user(tags, bot_nick, snd_nick, dst_nicks, public)
        if not user: return False
        cites = Brain.get_args(text, "in")
        if not cites: return False

        def action():
            for i, city in enumerate(set(cites)):
                t_city = self.__translate_client.translate_city(None, "English", city)
                self.__weather_client.update(t_city)
                temperature = self.__weather_client.temperature(t_city)
                description = self.__weather_client.description(t_city)
                humidity = self.__weather_client.humidity(t_city)
                pressure = self.__weather_client.pressure(t_city)
                wind = WeatherClient.format_wind(self.__weather_client.wind(t_city))
                description = self.__translate_client.translate_wd(description)
                self.__send(True, snd_nick, "сегодня в %s %s" % (city, description), public)
                self.__send(False, snd_nick, "Температура воздуха %.0f°C" % temperature, public)
                self.__send(False, snd_nick, "Влажность воздуха %.0f%%" % humidity, public)
                self.__send(False, snd_nick, "Давление %.0f мм рт.ст." % pressure, public)
                self.__send(False, snd_nick, "Ветер %s со скоростью %.0f м/с" % (wind[0], wind[1]), public)
                if i == 10: break
                sleep(2)

        def action_stop():
            self.__send(True, snd_nick, "ок", public)

        user.action = RunAction(action, action_stop, "weather")
        return True

    def __format(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        user = self.__action_user(tags, bot_nick, snd_nick, dst_nicks, public)
        if not user: return False
        if not user.memory or len(user.memory) <= 1:
            self.__send(True, snd_nick, "я не запоминал текст для тебя", public)
            return False

        def action():
            user.memory[1:] = Brain.format_text(user.memory[1:])
            self.__send(True, snd_nick, "я записал новый текст поверх старого", public)

        def action_stop():
            self.__send(True, snd_nick, "больше не форматирую", public)

        user.action = RunAction(action, action_stop, "format")
        return True

    def __clear(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        user = self.__action_user(tags, bot_nick, snd_nick, dst_nicks, public)
        if not user: return False
        if not user.memory or len(user.memory) <= 1:
            self.__send(True, snd_nick, "я не запоминал текст для тебя", public)
            return False

        def action():
            user.memory[1:] = Brain.clear_text(user.memory[1:])
            self.__send(True, snd_nick, "я записал новый текст поверх старого", public)

        def action_stop():
            self.__send(True, snd_nick, "больше не очищаю", public)

        user.action = RunAction(action, action_stop, "format")
        return True

    def __print(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        user = self.__action_user(tags, bot_nick, snd_nick, dst_nicks, public)
        if not user: return False
        if not user.memory or len(user.memory) <= 1:
            self.__send(True, snd_nick, "я не запоминал текст для тебя", public)
            return False

        def action():
            lines = user.memory[1:]
            if "paint" in tags: lines = Brain.paint_text(lines)
            self.__send(True, snd_nick, "", public)
            for i, line in enumerate(lines):
                self.__send(False, snd_nick, line, public)
                if i == 10: break
                sleep(0.5)

        def action_stop():
            self.__send(True, snd_nick, "больше не печатаю", public)

        user.action = RunAction(action, action_stop, "print")
        return True

    def __store(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        user = self.__action_user(tags, bot_nick, snd_nick, dst_nicks, public)
        if not user: return False
        if user.memory and len(user.memory) > 1:
            self.__send(True, snd_nick, "я запишу новый текст поверх старого", public)
        user.memory = [time()]
        self.__send(True, snd_nick, "я готов, пиши", public)

        def action(_snd_nick: str, _public: bool, _text: str):
            if _snd_nick != user.name: return
            user.memory.append(_text)
            if len(user.memory) >= 255:
                self.__send(True, _snd_nick, "у меня память кончается, не могу больше запоминать текст", _public)
                user.action = None

        def action_stop():
            del user.memory[-1]
            self.__send(True, snd_nick, "ок", public)

        user.action = UpdAction(action, action_stop, "store")
        return True

    def __end_action(self, tags: list, bot_nick: str, snd_nick: str, dst_nicks: list, public: bool, text: str) -> bool:
        if bot_nick not in dst_nicks: return False
        user = self.__users[snd_nick]
        if user.action.stopped():
            self.__send(True, snd_nick, "ты мне не давал заданий", public)
            return False
        user.action.stop()
        return True


if __name__ == "__main__":
    bot = IrcBot(3, "irc.esper.net", 6667, "#cc.ru", "PythonBot", "", {"Seryoga"})
    bot.connect()
    connected = True
    while True:
        inp = raw_input("")
        if inp == "close\n" or not bot.connected():
            bot.disconnect()
            break
