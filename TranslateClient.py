import re

import requests


class TranslateClient:
    def __init__(self, key: str):
        self.__key = key

    def translate(self, inp_lang: str, otp_lang: str, text: str):
        inp = "" if inp_lang is None else inp_lang.lower()[:2] + "-"
        otp = otp_lang.lower()[:2]
        lang = "&lang=" + inp + otp
        text = "&text=" + text
        key = "key=" + self.__key
        url = "https://translate.yandex.net/api/v1.5/tr.json/translate?" + key + lang + text
        data = str(requests.get(url).json())
        code = int(re.findall(r"\'code\':\s(\d+)", data)[0])
        if code != 200: return [code]
        text = re.findall(r"\'text\':\s\[\'(.+)\'\]", data)[0]
        lang = re.findall(r"\'lang\':\s\'([^\s]+)\'", data)[0]
        inp = lang[:2]
        otp = lang[-2:]
        return [code, inp, otp, text]

    def translate_city(self, inp_lang: str, otp_lang: str, city):
        city = city.lower()
        if city in ["spb", "спб", "питере"]: return "Saint-Petersburg"
        data = self.translate(inp_lang, otp_lang, city)
        return data[-1] if data[0] == 200 else city

    def translate_wd(self, desc) -> str:
        if desc == "clouds": return "облачно"
        if desc == "cloudy": return "пасмурно"
        if desc == "broken clouds": return "облачно с прояснениями"
        if desc == "overcast clouds": return "пасмурно"
        if desc == "thunderstorm": return "гроза"
        data = self.translate("en", "ru", desc)
        if data[0] != 200:
            print(data)
            return desc
        return "%s(%s)" % (data[-1], desc)
