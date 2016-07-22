from time import strftime, gmtime


class Letter:
    def __init__(self, time: float, name: str, channel: str, nick: str, args):
        self.time = time
        self.name = name
        self.channel = channel
        self.nick = nick
        self.args = args

    def to_large_str(self, gtm: int) -> str:
        time = strftime("%a, %d %b %Y %H:%M:%S", gmtime(gtm * 3600 + self.time))
        return "[%s] %s %s %s %s" % (time, self.name, self.channel, self.nick, str(self.args))

    def to_short_str(self, gtm: int) -> str:
        string = [strftime("[%H:%M:%S]", gmtime(gtm * 3600 + self.time))]
        if self.name: string.append(self.name)
        if self.channel: string.append(self.channel)
        if self.nick: string.append(self.nick)
        if self.args: string.append(":" + str(self.args))
        return " ".join(string)

    def to_str(self) -> str:
        string = []
        if self.name: string.append(self.name)
        if self.channel: string.append(self.channel)
        if self.nick: string.append(self.nick)
        if self.args: string.append(":" + str(self.args))
        return " ".join(string)
